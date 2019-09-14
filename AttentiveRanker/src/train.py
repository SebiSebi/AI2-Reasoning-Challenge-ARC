import argparse
import os
import uuid

import arch, utils
from settings import TRAIN_DATA_PATH, VAL_DATA_PATH
from settings import MODELS_DIR, TOP_N

from keras.callbacks import ModelCheckpoint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--top_n', type=int,
                        required=False, default=TOP_N,
                        help='Number of documents to use.')
    FLAGS, _ = parser.parse_known_args()
    top_n = FLAGS.top_n

    train_dataset = utils.read_dataset(TRAIN_DATA_PATH, top_n)
    train_dataset = utils.augment_with_permutations(train_dataset)
    train_data, train_labels = utils.to_numpy(train_dataset, top_n)
    del train_dataset

    val_dataset = utils.read_dataset(VAL_DATA_PATH, top_n)
    val_data, val_labels = utils.to_numpy(val_dataset, top_n)
    del val_dataset

    model = arch.get_model(top_n)
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['acc'])
    model.summary()

    filepath = os.path.join(
                    MODELS_DIR,
                    "model-" + str(uuid.uuid4()) +
                    "-{epoch:04d}-{val_loss:.4f}-{val_acc:.4f}.hdf5"
    )
    save_model = ModelCheckpoint(filepath, monitor='val_acc', verbose=0,
                                 save_best_only=False, mode='max')
    model.fit(
            train_data, train_labels,
            validation_data=(val_data, val_labels),
            batch_size=128,
            epochs=75,
            verbose=1,
            callbacks=[save_model]
    )


if __name__ == "__main__":
    main()
