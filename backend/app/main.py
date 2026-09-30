"""FastAPI inference service for the MNIST classifier."""

from __future__ import annotations

import base64
import binascii

import cv2
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .inference import MODEL_PATH, classify, model_available
from .preprocessing import CANVAS, NoDigitFound, preprocess_array
from .samples import random_sample
from .schemas import Health, Prediction, Sample

app = FastAPI(
    title='MNIST inference',
    description='Classifie un chiffre manuscrit.',
    version='1.0.0',
)

# The browser talks to this service through the frontend's nginx proxy in
# production; CORS is here so `npm run dev` can reach it directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
    allow_methods=['GET', 'POST'],
    allow_headers=['*'],
)

MAX_BYTES = 8 * 1024 * 1024


class DataUrlRequest(BaseModel):
    image: str


def to_png_data_url(gray: np.ndarray) -> str:
    ok, buf = cv2.imencode('.png', gray)
    if not ok:
        raise HTTPException(500, "Échec de l'encodage PNG.")
    return 'data:image/png;base64,' + base64.b64encode(buf.tobytes()).decode('ascii')


def decode_image(raw: bytes) -> np.ndarray:
    gray = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise HTTPException(400, 'Image illisible ou format non reconnu.')
    return gray


def run(gray: np.ndarray, source: str) -> Prediction:
    if not model_available():
        raise HTTPException(503, f'Modèle introuvable ({MODEL_PATH}). Lancez le service training.')
    try:
        tensor = preprocess_array(gray, source=source)
    except NoDigitFound as exc:
        raise HTTPException(422, str(exc)) from exc

    digit, probabilities = classify(tensor)
    preview = (tensor.reshape(CANVAS, CANVAS) * 255).astype('uint8')
    return Prediction(
        digit=digit,
        confidence=probabilities[digit],
        probabilities=probabilities,
        preview=to_png_data_url(preview),
    )


@app.get('/health', response_model=Health)
def health() -> Health:
    return Health(status='ok', model_loaded=model_available(), model_path=MODEL_PATH)


@app.post('/predict', response_model=Prediction)
async def predict(file: UploadFile = File(...)) -> Prediction:
    """Classify an uploaded image file."""
    raw = await file.read()
    if not raw:
        raise HTTPException(400, 'Fichier vide.')
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, 'Image trop volumineuse (8 Mo maximum).')
    return run(decode_image(raw), file.filename or 'upload')


@app.post('/predict/data-url', response_model=Prediction)
def predict_data_url(body: DataUrlRequest) -> Prediction:
    """Classify a `data:image/png;base64,...` payload, as sent by the drawing pad."""
    payload = body.image.split(',', 1)[-1]
    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(400, 'Data URI invalide.') from exc
    if len(raw) > MAX_BYTES:
        raise HTTPException(413, 'Image trop volumineuse (8 Mo maximum).')
    return run(decode_image(raw), 'dessin')


@app.get('/samples/random', response_model=Sample)
def sample() -> Sample:
    """Return a random MNIST test digit with its true label."""
    picked = random_sample()
    if picked is None:
        raise HTTPException(503, "Jeu d'exemples absent. Lancez le service training.")
    image, label = picked
    # Upscale so the pipeline does the same work it would on a real photo.
    big = cv2.resize(image, (280, 280), interpolation=cv2.INTER_CUBIC)
    return Sample(image=to_png_data_url(big), label=label)
