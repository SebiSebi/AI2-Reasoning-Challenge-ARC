import argparse
import numpy as np
import os

import arch, utils
from settings import BASE_DIR, TOP_N
from settings import EASY_TRAIN_DATA_PATH
from settings import EASY_VAL_DATA_PATH
from settings import EASY_TEST_DATA_PATH
from settings import CHALLENGE_TRAIN_DATA_PATH
from settings import CHALLENGE_VAL_DATA_PATH
from settings import CHALLENGE_TEST_DATA_PATH


def bool_type(v):
    if v.lower() in ['yes', 'true', 't']:
        return True
    elif v.lower() in ['no', 'false', 'f']:
        return False
    else:
        raise argparse.ArgumentTypeError(
                'Boolean value expected (yes, no, true, false, t, f).'
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', type=str, required=True,
                        choices=[
                            "easy_train",
                            "easy_val",
                            "easy_test",
                            "challenge_train",
                            "challenge_val",
                            "challenge_test"
                        ],
                        help='The dataset to predict.')
    parser.add_argument('-wav', '--without_answer_verifier',
                        type=bool_type, required=False, default=False,
                        help='Disables the answer verifier.')
    FLAGS, _ = parser.parse_known_args()
    dataset = FLAGS.dataset
    data_path = None
    if dataset == "easy_train":
        data_path = EASY_TRAIN_DATA_PATH
    elif dataset == "easy_val":
        data_path = EASY_VAL_DATA_PATH
    elif dataset == "easy_test":
        data_path = EASY_TEST_DATA_PATH
    elif dataset == "challenge_train":
        data_path = CHALLENGE_TRAIN_DATA_PATH
    elif dataset == "challenge_val":
        data_path = CHALLENGE_VAL_DATA_PATH
    elif dataset == "challenge_test":
        data_path = CHALLENGE_TEST_DATA_PATH
    assert(data_path is not None and isinstance(data_path, str))
    print("Running on dataset {}".format(data_path))

    model_weights = None
    if not FLAGS.without_answer_verifier:
        if "easy" in dataset:
            model_weights = os.path.join(BASE_DIR, "final_models", "model-easy-ed1b54b7-cfd3-455d-b72f-7ffb952bdb63-0063-0.7115-0.7319.hdf5")  # noqa: E501
        elif "challenge" in dataset:
            model_weights = os.path.join(BASE_DIR, "final_models", "model-challenge-c28b1d46-f046-4a76-8d09-b3ed3b7f3e95-0040-1.2552-0.4712.hdf5")  # noqa: E501
    else:
        if "easy" in dataset:
            model_weights = os.path.join(BASE_DIR, "final_models",
                                         "without_answer_verifier",
                                         "model-easy-06add213-e604-4407-8ebc-7476d9c6e3fe-0040-0.8303-0.6896.hdf5")  # noqa: E501
        elif "challenge" in dataset:
            model_weights = os.path.join(BASE_DIR, "final_models",
                                         "without_answer_verifier",
                                         "model-challenge-f04c456f-8ed8-4e6c-96d1-7ee58003c69c-0066-1.3518-0.3424.hdf5")  # noqa: E501
    assert(model_weights is not None)
    if "easy" in dataset:
        assert("easy" in model_weights)
    else:
        assert("challenge" in dataset)
        assert("challenge" in model_weights)
    print("Using weights {}".format(os.path.basename(model_weights)))

    dataset = utils.read_dataset(
                    data_path, TOP_N,
                    mask_Ranking=False,
                    mask_answer_verifier=FLAGS.without_answer_verifier
    )
    data, labels = utils.to_numpy(dataset, TOP_N)
    del dataset

    model = arch.get_model(TOP_N)
    model.compile(loss='categorical_crossentropy',
                  optimizer='adam',
                  metrics=['acc'])
    model.load_weights(model_weights)
    model.summary()
    y = model.predict(data, batch_size=1024)
    assert(y.shape == (labels.shape[0], 4))

    num_questions = labels.shape[0]
    correct = 0
    for i in range(0, num_questions):
        expected = np.argmax(labels[i])
        predicted = np.argmax(y[i])
        if expected == predicted:
            correct += 1
    print("Accuracy: {0:.4f}%".format(100.0 * correct / num_questions))


if __name__ == "__main__":
    main()
