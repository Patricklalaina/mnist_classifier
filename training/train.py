"""Train the MNIST classifier and export the artefacts the API serves.

    python train.py              # train, then export samples
    python train.py --samples    # export samples only

Writes `mnist_classifier.keras` and `samples.npz` into `--out` (default
`/models`), which the inference service mounts read-only.
"""

import argparse
import os
import sys
import traceback

import numpy as np
import tensorflow as tf

from dataset import IMG_SHAPE, build_pipelines, load_data

EPOCHS = 6
SAMPLE_COUNT = 300


def build_model():
    return tf.keras.models.Sequential([
        tf.keras.Input(shape=IMG_SHAPE),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        # No activation: these are logits. The API applies the softmax.
        tf.keras.layers.Dense(10),
    ])


def training_part(trainset, testset, epochs=EPOCHS):
    model = build_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(0.001),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()],
    )

    model.fit(
        trainset,
        epochs=epochs,
        validation_data=testset,
    )
    return model


def export_samples(test_set, out_dir, count=SAMPLE_COUNT):
    """Bundle a few test digits so the API can serve examples offline."""
    images, labels = [], []
    for image, label in test_set.take(count).as_numpy_iterator():
        images.append(image[:, :, 0])
        labels.append(label)

    path = os.path.join(out_dir, 'samples.npz')
    np.savez_compressed(path, images=np.array(images, dtype='uint8'),
                        labels=np.array(labels, dtype='uint8'))
    print(f'Exemples enregistrés : {path} ({len(images)} chiffres)')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', default=os.environ.get('OUT_DIR', '/models'),
                        help='répertoire de sortie des artefacts')
    parser.add_argument('--epochs', type=int, default=EPOCHS)
    parser.add_argument('--samples', action='store_true',
                        help="n'exporter que le jeu d'exemples")
    args = parser.parse_args(argv)

    try:
        os.makedirs(args.out, exist_ok=True)
        train_set, test_set, info = load_data()

        if not args.samples:
            train, test = build_pipelines(info, train_set, test_set)
            model = training_part(train, test, epochs=args.epochs)
            path = os.path.join(args.out, 'mnist_classifier.keras')
            model.save(path)
            print(f'Modèle enregistré : {path}')

        export_samples(test_set, args.out)
    except Exception:
        # Print the full traceback: the message alone hides where it came from.
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
