"""Turn an arbitrary photo or scan of a single digit into an MNIST-style tensor.

MNIST digits are size-normalized into a 20x20 box (aspect ratio preserved) and
then placed in a 28x28 field so that the digit's *centre of mass* sits at the
centre. This module reproduces that so inference inputs match the training
distribution.
"""

import cv2
import numpy as np

CANVAS = 28
DIGIT_BOX = 20


class NoDigitFound(ValueError):
    """Raised when no digit-like shape can be located in the image."""


def _extract_ink(gray):
    """Return `(mask, ink)`, both ink-on-black.

    `mask` is a hard 0/255 mask used to locate the digit; `ink` keeps the
    original grey levels inside that mask. The background polarity is inferred
    from the image border, so both dark-ink-on-light-paper and
    light-ink-on-dark-background are handled.
    """
    border = np.concatenate([gray[0, :], gray[-1, :], gray[:, 0], gray[:, -1]])
    background_is_light = np.median(border) >= 128

    polarity = cv2.THRESH_BINARY_INV if background_is_light else cv2.THRESH_BINARY
    _, mask = cv2.threshold(gray, 0, 255, polarity + cv2.THRESH_OTSU)

    ink = cv2.bitwise_not(gray) if background_is_light else gray
    return mask, cv2.bitwise_and(ink, mask)


def _centre_of_mass_offsets(patch, w, h):
    """Offsets that put `patch`'s centre of mass at the centre of the canvas."""
    target = (CANVAS - 1) / 2.0

    moments = cv2.moments(patch)
    if moments['m00'] > 0:
        cx = moments['m10'] / moments['m00']
        cy = moments['m01'] / moments['m00']
    else:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # Clamp so the patch stays fully inside the canvas.
    x_offset = max(0, min(CANVAS - w, int(round(target - cx))))
    y_offset = max(0, min(CANVAS - h, int(round(target - cy))))
    return x_offset, y_offset


def preprocess_array(gray, source='image'):
    """Normalize an already-decoded grayscale `uint8` array.

    Split out from `preprocess_for_mnist` so callers holding pixels rather than
    a path (an upload, a canvas, an MNIST sample) share the same pipeline.
    """
    mask, ink = _extract_ink(gray)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise NoDigitFound(f"Aucun chiffre détecté dans: {source}")

    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)

    # Crop the grey ink rather than the hard mask: downscaling it with
    # INTER_AREA gives the soft antialiased edges the model trained on.
    cropped = ink[y:y + h, x:x + w]

    scale = float(DIGIT_BOX) / max(w, h)
    # A thin stroke (e.g. a "1") rounds its short side to 0 without the clamp,
    # which makes cv2.resize raise.
    new_w = max(1, min(DIGIT_BOX, int(round(w * scale))))
    new_h = max(1, min(DIGIT_BOX, int(round(h * scale))))
    resized = cv2.resize(cropped, (new_w, new_h), interpolation=cv2.INTER_AREA)

    mnist_canvas = np.zeros((CANVAS, CANVAS), dtype=np.uint8)

    x_offset, y_offset = _centre_of_mass_offsets(resized, new_w, new_h)

    mnist_canvas[y_offset:y_offset + new_h, x_offset:x_offset + new_w] = resized
    final_img = mnist_canvas.astype('float32') / 255.0

    return final_img.reshape(1, CANVAS, CANVAS, 1)


def preprocess_for_mnist(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError(f"Impossible de charger l'image: {image_path}")

    return preprocess_array(img, source=image_path)
