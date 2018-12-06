import numpy as np
import qa.tokenizers as tokenizers
import tqdm


from autocorrect import spell
from keras.callbacks import ModelCheckpoint
from keras.preprocessing.sequence import pad_sequences
from qa.arch import define_model, attention_heatmap
from qa.char_embeddings_loader import CharEmbeddings
from qa.utils import read_data_as_json, print_data_stats
from qa.utils import pick_best_model_from_dir, all_sentences
from qa.settings import TRAIN_DATA_PATH
from qa.settings import VALIDATE_DATA_PATH
from qa.settings import TEST_DATA_PATH
from qa.settings import DEBUG, QUESTION_LEN, ANSWER_LEN, CONTEXT_LEN
from qa.settings import WORD_EMBEDDINGS_PATH, WORD_EMBEDDINGS_DIM
from qa.settings import CHAR_EMBEDDINGS_PATH, CHAR_EMBEDDINGS_DIM, MAX_WORD_LEN
from qa.word_embeddings_loader import WordEmbeddings


# Returns a pair of numpy arrays (word emb, char emb).
def to_seq(text, sentence_len, tokenizer, ce_loader):
    seq = tokenizer.texts_to_sequences([text])
    seq = pad_sequences(seq, maxlen=sentence_len, padding='post',
                        truncating='post', value=0)[0]
    word_emb = np.copy(seq)

    seq = seq.tolist()
    assert(len(seq) == sentence_len)
    concat_letters = np.zeros((sentence_len, MAX_WORD_LEN), dtype=np.int32)
    words = []
    for idx in seq:
        words.append(tokenizer.index_to_word(idx))

    for w_index in range(0, len(words)):
        word = words[w_index]
        letters = np.zeros((MAX_WORD_LEN,), dtype=np.int32)

        word = list(word)[0:MAX_WORD_LEN]
        for l_index in range(0, len(word)):
            letter = word[l_index]
            letters[l_index] = ce_loader.get_index(letter)

        concat_letters[w_index] = letters

    # type(word_emb) = numpy.ndarray
    letters = concat_letters.reshape((sentence_len * MAX_WORD_LEN,))

    return word_emb, letters


def preprocess_data(data, tokenizer, ce_loader, shuffle=False,
                    oversample=True):
    q = None
    a = None
    c = None
    q_char = None
    a_char = None
    c_char = None
    labels = None
    if oversample:
        q = np.zeros((6 * len(data), QUESTION_LEN))
        a = np.zeros((6 * len(data), ANSWER_LEN))
        c = np.zeros((6 * len(data), CONTEXT_LEN))

        q_char = np.zeros((6 * len(data), QUESTION_LEN * MAX_WORD_LEN))
        a_char = np.zeros((6 * len(data), ANSWER_LEN * MAX_WORD_LEN))
        c_char = np.zeros((6 * len(data), CONTEXT_LEN * MAX_WORD_LEN))

        labels = np.zeros((6 * len(data), 2))
    else:
        q = np.zeros((4 * len(data), QUESTION_LEN))
        a = np.zeros((4 * len(data), ANSWER_LEN))
        c = np.zeros((4 * len(data), CONTEXT_LEN))

        q_char = np.zeros((4 * len(data), QUESTION_LEN * MAX_WORD_LEN))
        a_char = np.zeros((4 * len(data), ANSWER_LEN * MAX_WORD_LEN))
        c_char = np.zeros((4 * len(data), CONTEXT_LEN * MAX_WORD_LEN))

        labels = np.zeros((4 * len(data), 2))

    idx = 0
    for entry in tqdm.tqdm(data, desc="Preprocess data", leave=False):
        question = entry['question']
        answers = entry['answers']
        assert(len(answers) == 4)

        # Answers *must* be taken in order (from 0 to 4)!
        # Otherwise predict batch won't work.
        for i in range(0, 4):
            answer = answers[i]

            q[idx], q_char[idx] = to_seq(question, QUESTION_LEN,
                                         tokenizer, ce_loader)
            a[idx], a_char[idx] = to_seq(answer['text'], ANSWER_LEN,
                                         tokenizer, ce_loader)
            c[idx], c_char[idx] = to_seq(answer['context'], CONTEXT_LEN,
                                         tokenizer, ce_loader)

            if answer['isCorrect'] is True:
                labels[idx][1] = 1
            else:
                labels[idx][0] = 1

            idx += 1

    if oversample:
        for step in range(0, 2):
            for entry in tqdm.tqdm(data, desc="Oversample {}".format(step),
                                   leave=False):
                question = entry['question']
                answers = entry['answers']
                assert(len(answers) == 4)

                for i in range(0, 4):
                    answer = answers[i]
                    if answer['isCorrect'] is False:
                        continue

                    q[idx], q_char[idx] = to_seq(question, QUESTION_LEN,
                                                 tokenizer, ce_loader)
                    a[idx], a_char[idx] = to_seq(answer['text'], ANSWER_LEN,
                                                 tokenizer, ce_loader)
                    c[idx], c_char[idx] = to_seq(answer['context'],
                                                 CONTEXT_LEN,
                                                 tokenizer, ce_loader)
                    labels[idx][1] = 1
                    idx += 1

    assert(q.shape[0] == a.shape[0])
    assert(q.shape[0] == c.shape[0])
    assert(a.shape[0] == labels.shape[0])
    assert(q.shape[0] == q_char.shape[0])
    assert(a.shape[0] == a_char.shape[0])
    assert(c.shape[0] == c_char.shape[0])

    if shuffle:
        p = np.random.permutation(q.shape[0])
        q = q[p]
        a = a[p]
        c = c[p]
        q_char = q_char[p]
        a_char = a_char[p]
        c_char = c_char[p]
        labels = labels[p]

    if oversample:
        assert(idx == 6 * len(data))
        s = np.sum(labels, axis=0)
        assert(np.allclose(s[0], s[1]))
        assert(np.allclose(np.sum(labels, axis=1), np.ones((6 * len(data),))))
    else:
        assert(idx == 4 * len(data))
        s = np.sum(labels, axis=0)
        # assert(np.allclose(s[0], 3.0 * s[1]))

    out = {
        'q_input': q,
        'a_input': a,
        'c_input': c,
        'q_char_input': q_char,
        'a_char_input': a_char,
        'c_char_input': c_char
    }
    assert(len(out) == 6)

    return out, labels


def build_embeddings_matrix(tokenizer):
    word_index = tokenizer.word_index()
    embedder = WordEmbeddings(WORD_EMBEDDINGS_PATH, WORD_EMBEDDINGS_DIM, True)
    dim = embedder.get_embedding_len()
    embeddings_matrix = np.zeros((len(word_index) + 1, dim), dtype=np.float32)
    emb_found = 0
    for word in tqdm.tqdm(word_index, desc="Building emb matrix"):
        index = word_index[word]
        w_vector = embedder.get_vector(word)
        if w_vector is None:
            w_vector = embedder.get_vector(word.lower())
        if w_vector is None:
            corrected_word = spell(word)
            assert(isinstance(corrected_word, str))
            w_vector = embedder.get_vector(corrected_word)

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
    train_data = []
    for path in TRAIN_DATA_PATH:
        train_data += read_data_as_json(path)

    # Read validation data.
    val_data = []
    for path in VALIDATE_DATA_PATH:
        val_data += read_data_as_json(path)

    # Read test data.
    test_data = []
    for path in TEST_DATA_PATH:
        test_data += read_data_as_json(path)

    # train_data = train_data[0:250]
    # val_data = val_data[0:50]

    if DEBUG:
        print_data_stats(train_data, "Train")
        print_data_stats(val_data, "Validate")
        print_data_stats(test_data, "Test")

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = tokenizers.SpacyTokenizer()
    tokenizer.fit_on_texts(all_sentences(train_data) +
                           all_sentences(val_data) +
                           all_sentences(test_data))
    if DEBUG:
        print("Num words: {}\n".format(len(tokenizer.word_counts())))

    # Load char embeddings.
    ce_loader = CharEmbeddings(CHAR_EMBEDDINGS_PATH, CHAR_EMBEDDINGS_DIM)

    # Convert data into list of sequences of indices.
    (train_data,
     train_labels) = preprocess_data(train_data, tokenizer, ce_loader)

    if DEBUG:
        print("Train data preprocessing complete.", flush=True)

    (val_data,
     val_labels) = preprocess_data(val_data, tokenizer, ce_loader)

    if DEBUG:
        print("Val data preprocessing complete.", flush=True)

    (test_data,
     test_labels) = preprocess_data(test_data, tokenizer, ce_loader)

    if DEBUG:
        print("Test data preprocessing complete.\n", flush=True)

    embeddings_matrix = build_embeddings_matrix(tokenizer)
    num_words = len(tokenizer.word_counts())
    model = define_model(num_words, embeddings_matrix, ce_loader,
                         "train", WORD_EMBEDDINGS_DIM)
    model.summary()

    weights_file = pick_best_model_from_dir()
    print("Pretrain from {}".format(weights_file))
    model.load_weights(weights_file, by_name=True)

    filepath = "models/" + "model.{val_acc:.3f}-{epoch:03d}.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=0,
                                 save_best_only=True, mode='max')
    model.fit(train_data, train_labels,
              batch_size=170, epochs=350,
              verbose=1,
              validation_data=(val_data, val_labels),
              callbacks=[checkpoint],
              shuffle=True)  # Shuffles training data before training.

    score = model.evaluate(test_data, test_labels, verbose=0)
    if score:
        print('Test loss:', score[0])
        print('Test accuracy:', score[1])


def binary_test(paths, weights_file=None):
    assert(isinstance(paths, list))

    # Read test data.
    test_data = []
    for path in paths:
        test_data += read_data_as_json(path)

    if DEBUG:
        print_data_stats(test_data, "Binary accuracy")

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = tokenizers.SpacyTokenizer()
    tokenizer.fit_on_texts(all_sentences(test_data))
    if DEBUG:
        print("Num words: {}".format(len(tokenizer.word_counts())))

    # Load char embeddings.
    ce_loader = CharEmbeddings(CHAR_EMBEDDINGS_PATH, CHAR_EMBEDDINGS_DIM)

    # Convert data into list of sequences of indices.
    (test_data,
     test_labels) = preprocess_data(test_data, tokenizer, ce_loader,
                                    shuffle=False, oversample=True)

    embeddings_matrix = build_embeddings_matrix(tokenizer)
    num_words = len(tokenizer.word_counts())
    model = define_model(num_words, embeddings_matrix, ce_loader,
                         "test", WORD_EMBEDDINGS_DIM)
    model.summary()

    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))
    model.load_weights(weights_file, by_name=True)

    num_tests = test_labels.shape[0]
    y = model.predict(test_data, batch_size=64)
    assert(y.shape[0] == num_tests)

    correct = 0
    total = 0
    for i in range(0, num_tests):
        expected = np.argmax(test_labels[i])
        predicted = np.argmax(y[i])

        if predicted == expected:
            correct += 1
        total += 1
    assert(total == num_tests)

    if total == 0:
        total = 1
    print("\nEvaluated on {} questions.".format(num_tests))
    print("Accuracy: {0:.3f}%".format(100.0 * correct / total))


def test_4way(paths, weights_file=None):
    assert(isinstance(paths, list))

    # Read test data.
    test_data = []
    for path in paths:
        test_data += read_data_as_json(path)

    if DEBUG:
        print_data_stats(test_data, "4way accuracy")

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = tokenizers.SpacyTokenizer()
    tokenizer.fit_on_texts(all_sentences(test_data))
    if DEBUG:
        print("Num words: {}".format(len(tokenizer.word_counts())))

    # Load char embeddings.
    ce_loader = CharEmbeddings(CHAR_EMBEDDINGS_PATH, CHAR_EMBEDDINGS_DIM)

    # Convert data into list of sequences of indices.
    (test_data,
     test_labels) = preprocess_data(test_data, tokenizer, ce_loader,
                                    shuffle=False, oversample=False)

    embeddings_matrix = build_embeddings_matrix(tokenizer)
    num_words = len(tokenizer.word_counts())
    model = define_model(num_words, embeddings_matrix, ce_loader,
                         "test", WORD_EMBEDDINGS_DIM)
    model.summary()

    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))
    model.load_weights(weights_file, by_name=True)

    num_tests = test_labels.shape[0]
    y = model.predict(test_data, batch_size=64)
    assert(y.shape[0] == num_tests)
    assert(num_tests % 4 == 0)

    correct = 0
    total = 0
    for i in range(0, num_tests, 4):
        for j in range(1, 4):
            assert(np.allclose(test_data["q_input"][i],
                               test_data["q_input"][i + j]))
            assert(np.allclose(test_data["q_char_input"][i],
                               test_data["q_char_input"][i + j]))

        expected = test_labels[i: i + 4, 1]
        assert(np.allclose(np.sum(expected), 1.0))
        expected = np.argmax(expected)

        predicted = y[i: i + 4, 1]
        predicted = np.argmax(predicted)

        if predicted == expected:
            correct += 1
        total += 1

    assert(total == num_tests / 4)
    if total == 0:
        total = 1
    print("\nEvaluated on {} questions.".format(total))
    print("Accuracy: {0:.3f}%".format(100.0 * correct / total))


def plot_attention_heatmap(paths, choice="smallest_context",
                           weights_file=None):
    assert(isinstance(paths, list))
    assert(choice in ["smallest_context", "random"])

    # Read test data.
    test_data = []
    for path in paths:
        test_data += read_data_as_json(path)
    data = None

    if choice == "smallest_context":
        min_len = None
        for entry in test_data:
            assert(len(entry["answers"]) == 4)
            context = entry["answers"][0]["context"]
            for i in range(0, 4):
                assert(context == entry["answers"][i]["context"])
            if min_len is None or len(context) < min_len:
                min_len = len(context)
                data = entry
    elif choice == "random":
        import random
        data = random.choice(test_data)

    assert(data is not None)
    context = data["answers"][0]["context"]
    question_text = data["question"]
    test_data = [data]

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = tokenizers.SpacyTokenizer()
    tokenizer.fit_on_texts(all_sentences(test_data))
    if DEBUG:
        print("Num words: {}".format(len(tokenizer.word_counts())))

    # Load char embeddings.
    ce_loader = CharEmbeddings(CHAR_EMBEDDINGS_PATH, CHAR_EMBEDDINGS_DIM)

    (test_data, labels) = preprocess_data(test_data, tokenizer, ce_loader,
                                          shuffle=False, oversample=False)
    idx = None
    for i in range(0, 4):
        if labels[i][1] >= 0.9:
            idx = i
            break
    assert(data["answers"][idx]["isCorrect"] is True)

    q = test_data["q_input"]
    a = test_data["a_input"]
    c = test_data["c_input"]

    q = np.reshape(q[idx], (1, -1))
    a = np.reshape(a[idx], (1, -1))
    c = np.reshape(c[idx], (1, -1))

    embeddings_matrix = build_embeddings_matrix(tokenizer)
    num_words = len(tokenizer.word_counts())
    model = attention_heatmap(num_words, embeddings_matrix,
                              "attention_heatmap", WORD_EMBEDDINGS_DIM)
    model.summary()

    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))
    model.load_weights(weights_file, by_name=True)

    inv_index = {}
    index = tokenizer.word_index()
    for word in index:
        inv_index[index[word]] = word
    seq = tokenizer.texts_to_sequences([context])[0]
    context = []
    for idx in seq:
        context.append(inv_index[idx])

    y = model.predict({'q_input': q, 'a_input': a, 'c_input': c})
    assert(y.shape[0] == 1)
    y = y[0]
    scores = []
    for i in range(0, len(context)):
        scores.append((context[i], y[i][0]))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:20]

    print("\nQuestion: " + question_text + "\n")
    print(' '.join(context))

    x = [score[0] for score in scores]
    y = [score[1] for score in scores]

    import matplotlib.pyplot as plt
    plt.figure()
    plt.bar(range(len(x)), y, align='center')
    plt.title("Attention scores")
    plt.xticks(range(len(x)), x, rotation=45,
               horizontalalignment='right')
    plt.tight_layout()
    plt.show()


# This should be use by external clients (like export.QA).
# Returns a list of lists (of 4 elements).
def predict_batch(request, weights_file, verbose=False):
    assert(isinstance(request, list))
    assert(isinstance(weights_file, str))
    assert(isinstance(verbose, bool))

    num_questions = len(request)
    if verbose:
        print_data_stats(request, "QA Predict batch request")

    # Fit a tokenizer on all data. Each word gets assigned a number
    # between 1 and num_words.
    tokenizer = tokenizers.SpacyTokenizer()
    tokenizer.fit_on_texts(all_sentences(request))
    if verbose:
        print("Num words: {}".format(len(tokenizer.word_counts())))

    # Load char embeddings.
    ce_loader = CharEmbeddings(CHAR_EMBEDDINGS_PATH, CHAR_EMBEDDINGS_DIM)

    # Convert data into list of sequences of indices.
    (test_data, _) = preprocess_data(request, tokenizer, ce_loader,
                                     shuffle=False, oversample=False)

    embeddings_matrix = build_embeddings_matrix(tokenizer)
    num_words = len(tokenizer.word_counts())
    model = define_model(num_words, embeddings_matrix, ce_loader,
                         "test", WORD_EMBEDDINGS_DIM)
    model.load_weights(weights_file, by_name=True)
    # model.summary()

    num_tests = num_questions * 4
    y = model.predict(test_data, batch_size=64)
    assert(y.shape[0] == num_tests)
    assert(num_tests % 4 == 0)

    res = np.zeros((num_questions, 4))
    idx = 0
    for i in range(0, num_tests, 4):
        for j in range(1, 4):
            assert(np.allclose(test_data["q_input"][i],
                               test_data["q_input"][i + j]))
            assert(np.allclose(test_data["q_char_input"][i],
                               test_data["q_char_input"][i + j]))

        assert(i % 4 == 0)
        res[idx] = y[i: i + 4, 1]
        assert(idx == (i >> 2))
        idx += 1

    assert(idx == num_questions)
    print("\n[QA] Batch predicted {} questions.".format(num_questions))

    assert(res.shape == (num_questions, 4))
    return res


def main():
    # import tensorflow as tf
    # from keras.backend.tensorflow_backend import set_session
    # config = tf.ConfigProto()
    # config.gpu_options.per_process_gpu_memory_fraction = 0.85
    # set_session(tf.Session(config=config))

    # train()
    # binary_test(VALIDATE_DATA_PATH)
    # test_4way(VALIDATE_DATA_PATH)
    test_4way(VALIDATE_DATA_PATH, "squad_models/model.0.780-017.hdf5")
    # plot_attention_heatmap(VALIDATE_DATA_PATH, "random")


if __name__ == "__main__":
    main()
