import include_sys_path
import numpy as np
import tensorflow as tf
import tqdm

from keras.backend.tensorflow_backend import set_session
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from nlp_inference.arch import define_model
from nlp_inference.utils import read_data_as_json, print_data_stats
from nlp_inference.utils import remove_unlabeled_data, all_sentences
from nlp_inference.utils import pick_best_model_from_dir
from nlp_inference.settings import TRAIN_DATA_PATH
from nlp_inference.settings import VALIDATE_DATA_PATH
from nlp_inference.settings import TEST_DATA_PATH
from nlp_inference.settings import DEBUG, PREMISE_LEN, HYPOTHESIS_LEN
from nlp_inference.settings import WORD_EMBEDDINGS_PATH, WORD_EMBEDDINGS_DIM
from nlp_inference.word_embeddings_loader import WordEmbeddings

include_sys_path.void()


def preprocess_data(data, tokenizer):
    assert(isinstance(data, list))

    premise = np.zeros((len(data), PREMISE_LEN))
    hypothesis = np.zeros((len(data), HYPOTHESIS_LEN))
    idx = 0
    for entry in tqdm.tqdm(data, desc="Preprocessing data", leave=False):
        seq = tokenizer.texts_to_sequences([entry['sentence1']])
        seq = pad_sequences(seq, maxlen=PREMISE_LEN, padding='post',
                            truncating='post', value=0)[0]
        # type(seq) = numpy.ndarray
        premise[idx] = seq

        seq = tokenizer.texts_to_sequences([entry['sentence2']])
        seq = pad_sequences(seq, maxlen=HYPOTHESIS_LEN, padding='post',
                            truncating='post', value=0)[0]
        # type(seq) = numpy.ndarray
        hypothesis[idx] = seq
        idx += 1
    assert(idx == len(data))

    return premise, hypothesis


def extract_labels(data):
    assert(isinstance(data, list))
    labels = np.zeros((len(data), 3))
    to_label = {
        'entailment': 0,
        'neutral': 1,
        'contradiction': 2
    }
    idx = 0
    for entry in data:
        label = to_label[entry['gold_label']]
        labels[idx][label] = 1
        idx += 1
    assert(len(data) == idx)

    return labels


def build_embeddings_matrix(tokenizer):
    word_index = tokenizer.word_index
    embedder = WordEmbeddings(WORD_EMBEDDINGS_PATH, WORD_EMBEDDINGS_DIM, True)
    dim = embedder.get_embedding_len()
    assert(dim == WORD_EMBEDDINGS_DIM)

    embeddings_matrix = np.zeros((len(word_index) + 1, dim), dtype=np.float32)
    emb_found = 0
    for word in tqdm.tqdm(word_index, desc="Building emb matrix"):
        index = word_index[word]
        w_vector = embedder.get_vector(word)
        if w_vector is None:
            w_vector = np.zeros((dim,))
        else:
            emb_found += 1
        assert(w_vector.shape[0] == dim)
        embeddings_matrix[index] = w_vector
    if DEBUG:
        num_words = len(word_index)
        if num_words == 0:
            num_words = 1
        print("Found {0:.2f}% embeddings.".format(
                                100.0 * emb_found / num_words))
    return embeddings_matrix


def train():
    # Read train data.
    train_data = read_data_as_json(TRAIN_DATA_PATH)
    train_data = remove_unlabeled_data(train_data)

    # Read validation data.
    val_data = read_data_as_json(VALIDATE_DATA_PATH)
    val_data = remove_unlabeled_data(val_data)

    # Read test data.
    test_data = read_data_as_json(TEST_DATA_PATH)
    test_data = remove_unlabeled_data(test_data)

    if DEBUG:
        print_data_stats(train_data, "Train")
        print_data_stats(val_data, "Validate")
        print_data_stats(test_data, "Test")

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(train_data) +
                           all_sentences(val_data) +
                           all_sentences(test_data))
    if DEBUG:
        print("Num words: {}".format(len(tokenizer.word_counts)))

    # Convert data into list of sequences of indices.
    train_premise, train_hypothesis = preprocess_data(train_data, tokenizer)
    train_labels = extract_labels(train_data)
    val_premise, val_hypothesis = preprocess_data(val_data, tokenizer)
    val_labels = extract_labels(val_data)
    test_premise, test_hypothesis = preprocess_data(test_data, tokenizer)
    test_labels = extract_labels(test_data)

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "train", WORD_EMBEDDINGS_DIM)
    model.summary()

    filepath = "models/" + "model.{val_acc:.3f}-{epoch:03d}.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=0,
                                 save_best_only=True, mode='max')
    model.fit(
        {'p_input': train_premise, 'h_input': train_hypothesis},
        train_labels,
        batch_size=320, epochs=100,
        verbose=1,
        validation_data=(
            {'p_input': val_premise, 'h_input': val_hypothesis},
            val_labels
        ),
        callbacks=[checkpoint]
    )
    score = model.evaluate(
            {'p_input': test_premise, 'h_input': test_hypothesis},
            test_labels,
            verbose=0
    )
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])


def test(input_path, weights_file=None):
    # Read test data.
    test_data = read_data_as_json(input_path)
    test_data = remove_unlabeled_data(test_data)

    if DEBUG:
        print_data_stats(test_data, "Test")

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(test_data))
    if DEBUG:
        print("Num words: {}".format(len(tokenizer.word_counts)))

    # Convert data into list of sequences of indices.
    test_premise, test_hypothesis = preprocess_data(test_data, tokenizer)

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "test", WORD_EMBEDDINGS_DIM)

    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))
    model.load_weights(weights_file, by_name=True)
    model.summary()

    num_tests = len(test_data)
    y = model.predict({'p_input': test_premise, 'h_input': test_hypothesis})
    assert(y.shape[0] == num_tests)
    assert(num_tests > 0)
    to_label = {
        'entailment': 0,
        'neutral': 1,
        'contradiction': 2
    }
    correct = 0
    total = 0
    correct_confidence = 0
    wrong_confidence = 0
    for i in range(0, num_tests):
        predicted = np.argmax(y[i])
        expected = to_label[test_data[i]['gold_label']]
        confidence = y[i][predicted]
        if predicted == expected:
            correct += 1
            correct_confidence += confidence
        else:
            wrong_confidence += confidence
        total += 1
    assert(total == num_tests)
    print("Accuracy {0:.3f}".format(correct / total))
    if correct >= 1:
        print("Correct confidence {0:.3f}%".format(
            correct_confidence / correct * 100.0))
    if correct < total:
        print("Wrong confidence {0:.3f}%".format(
            wrong_confidence / (total - correct) * 100.0))


def predict(premise, hypothesis, weights_file=None):
    data = [{
        'sentence1': premise,
        'sentence2': hypothesis
    }]

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(data))
    if DEBUG:
        print("Num words: {}".format(len(tokenizer.word_counts)))

    # Convert data into list of sequences of indices.
    test_premise, test_hypothesis = preprocess_data(data, tokenizer)

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "test", WORD_EMBEDDINGS_DIM)
    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))
    model.load_weights(weights_file, by_name=True)
    model.summary()

    y = model.predict({'p_input': test_premise, 'h_input': test_hypothesis})
    assert(len(data) == 1)
    assert(y.shape[0] == 1)

    from_label = {
        0: 'entailment',
        1: 'neutral',
        2: 'contradiction'
    }
    predicted = np.argmax(y[0])
    confidence = y[0][predicted]
    predicted = from_label[predicted]
    print(predicted, confidence)


def predict_batch(test_data, weights_file, verbose=False):
    assert(isinstance(test_data, list))
    assert(isinstance(weights_file, str))
    assert(isinstance(verbose, bool))

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(test_data))
    if verbose:
        print("Num words: {}".format(len(tokenizer.word_counts)))

    # Convert data into list of sequences of indices.
    test_premise, test_hypothesis = preprocess_data(test_data, tokenizer)

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "test", WORD_EMBEDDINGS_DIM)

    model.load_weights(weights_file, by_name=True)
    model.summary()

    num_tests = len(test_data)
    y = model.predict({'p_input': test_premise, 'h_input': test_hypothesis})
    assert(y.shape[0] == num_tests)
    assert(num_tests > 0)

    res = []
    for i in range(0, num_tests):
        predicted = y[i]
        # [2.3905272e-10 2.9231341e-08 1.0000000e+00]
        x = 1.0 - np.dot(predicted, [0.0, 1.0, 2.0]) / 2.0
        if x <= 0.0:
            x = 0.0
        if x >= 1.0:
            x = 1.0
        res.append(x)

    for x in res:
        assert(x >= 0.0 and x <= 1.0)
    assert(len(res) == len(test_data))
    assert(len(res) == num_tests)
    assert(len(test_data) == num_tests)

    return res


def main():
    # train()
    test(TEST_DATA_PATH)
    # predict("Today is raining in my town.",
    #         "The weather is very sunny today.")


if __name__ == "__main__":
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 0.8
    set_session(tf.Session(config=config))
    main()
