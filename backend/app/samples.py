"""Serve MNIST test digits bundled at training time."""

from __future__ import annotations

import os
import random

import numpy as np

SAMPLES_PATH = os.environ.get('SAMPLES_PATH', '/models/samples.npz')

_samples = None


def load_samples():
    """Memoised `(images, labels)`, or `None` when the bundle is absent.

    The bundle is written by the training service, so the API never needs
    `tensorflow_datasets` or a network round-trip to serve an example.
    """
    global _samples
    if _samples is None:
        if not os.path.exists(SAMPLES_PATH):
            return None
        with np.load(SAMPLES_PATH) as data:
            _samples = (data['images'], data['labels'])
    return _samples


def random_sample():
    loaded = load_samples()
    if loaded is None:
        return None
    images, labels = loaded
    i = random.randrange(len(images))
    return images[i], int(labels[i])
