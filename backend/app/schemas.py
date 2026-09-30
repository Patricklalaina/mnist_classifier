"""Response bodies for the inference API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: str = Field(examples=['ok'])
    model_loaded: bool
    model_path: str


class Prediction(BaseModel):
    digit: int = Field(ge=0, le=9, description='Chiffre prédit')
    confidence: float = Field(ge=0, le=1, description='Probabilité du chiffre prédit')
    probabilities: list[float] = Field(description='Probabilité de chacun des dix chiffres')
    preview: str = Field(description="L'image 28x28 vue par le modèle, en data URI PNG")


class Sample(BaseModel):
    image: str = Field(description='Chiffre du jeu de test MNIST, en data URI PNG')
    label: int = Field(ge=0, le=9, description='Étiquette réelle')
