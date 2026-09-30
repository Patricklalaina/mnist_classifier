"""Model loading and classification."""

from __future__ import annotations

import os
import threading

import numpy as np

MODEL_PATH = os.environ.get('MODEL_PATH', '/models/mnist_classifier.keras')

_model = None
_lock = threading.Lock()


def get_model():
    """Load the Keras model once, on first use.

    Importing TensorFlow costs several seconds, so it is deferred out of module
    import to keep container start-up (and `/health`) responsive.
    """
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                import tensorflow as tf
                _model = tf.keras.models.load_model(MODEL_PATH)
    return _model


def model_available() -> bool:
    return os.path.exists(MODEL_PATH)


def classify(tensor: np.ndarray) -> tuple[int, list[float]]:
    """Return `(digit, probabilities)` for a prepared `(1, 28, 28, 1)` tensor."""
    import tensorflow as tf

    logits = get_model().predict(tensor, verbose=0)
    # The network emits logits (trained with from_logits=True), so squash them
    # before anything is reported as a confidence.
    probabilities = tf.nn.softmax(logits[0]).numpy()
    return int(np.argmax(probabilities)), [float(p) for p in probabilities]
