"""MNIST loading and the `tf.data` pipelines used for training."""

import tensorflow as tf
import tensorflow_datasets as tfds

BATCH_SIZE = 128
IMG_SHAPE = (28, 28, 1)


def load_data() -> tuple:
    (ds_train, ds_test), ds_info = tfds.load(
        'mnist',
        split=['train', 'test'],
        shuffle_files=True,
        as_supervised=True,
        with_info=True,
    )

    return ds_train, ds_test, ds_info


def normalize_img(image, label):
    """Normalizes images: `uint8` -> `float32` in [0, 1]."""
    return tf.cast(image, tf.float32) / 255., label


def build_pipelines(ds_info, train, test, batch_size=BATCH_SIZE):
    ds_train = train.map(normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    ds_train = ds_train.cache()
    ds_train = ds_train.shuffle(ds_info.splits['train'].num_examples)
    ds_train = ds_train.batch(batch_size)
    ds_train = ds_train.prefetch(tf.data.AUTOTUNE)

    ds_test = test.map(
        normalize_img, num_parallel_calls=tf.data.AUTOTUNE)
    ds_test = ds_test.batch(batch_size)
    ds_test = ds_test.cache()
    ds_test = ds_test.prefetch(tf.data.AUTOTUNE)

    return ds_train, ds_test
