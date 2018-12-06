import numpy as np
import random
import spacy

from copy import deepcopy
from keras.callbacks import ModelCheckpoint
from keras.losses import categorical_crossentropy
from keras.layers import Embedding, Input, LSTM, Dense
from keras.layers import concatenate, Dropout, Flatten
from keras.models import Model
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer
from keras.utils import plot_model
from utils import all_sentences, dataset_similarity
from utils import pick_best_model_from_dir
from utils import read_data_from_json, print_data_stats
from settings import DEBUG, TRAIN_DATA_PATH
from settings import VALIDATION_DATA_PATH, TEST_DATA_PATH
from settings import QUESTION_LEN, ANSWER_LEN, TERM_LEN, NUM_CLASSES
from settings import WORD_EMBEDDINGS_DIM, WORD_EMBEDDINGS_PATH
from settings import POS_EMBEDDINGS_DIM, POLY_FEATURES
from settings import NER_COUNT, DEP_EMBEDDINGS_DIM
from word_embeddings_loader import WordEmbeddings
from word_features import WordFeatures


def to_seq(sentence, tokenizer, length):
    seq = tokenizer.texts_to_sequences([sentence])
    seq = pad_sequences(seq, maxlen=length, padding='post',
                        truncating='post', value=0)[0]
    return seq


# Adds value, value ^ 2, value ^ 3, ...
def expand(value):
    x = np.zeros((POLY_FEATURES,), dtype=np.float32)
    for i in range(1, POLY_FEATURES + 1):
        x[i - 1] = np.power(value, 1.0 * i)
    return x


def preprocess_data(data, tokenizer, wf, title=""):
    num_entries = 0
    for entry in data:
        num_entries += len(entry['terms'])
    if DEBUG:
        print("Preprocessing {} data ...".format(title))
        print("Total num inputs: {}".format(num_entries))

    q = np.zeros((num_entries, QUESTION_LEN), dtype=np.float32)
    answers = np.zeros((num_entries, 4 * ANSWER_LEN), dtype=np.float32)
    terms = np.zeros((num_entries, 1), dtype=np.float32)
    labels = np.zeros((num_entries, NUM_CLASSES), dtype=np.float32)
    is_science_term = np.zeros((num_entries,), dtype=np.float32)
    is_stop_term = np.zeros((num_entries,), dtype=np.float32)
    concretness_rating = np.zeros((num_entries, POLY_FEATURES),
                                  dtype=np.float32)
    pos_embeddings = np.zeros((num_entries, POS_EMBEDDINGS_DIM),
                              dtype=np.float32)
    deg_centrality = np.zeros((num_entries, POLY_FEATURES),
                              dtype=np.float32)
    close_centrality = np.zeros((num_entries, POLY_FEATURES),
                                dtype=np.float32)
    eigen_centrality = np.zeros((num_entries, POLY_FEATURES),
                                dtype=np.float32)
    pmi_values = np.zeros((num_entries, 12), dtype=np.float32)
    ner_values = np.zeros((num_entries, NER_COUNT), dtype=np.float32)
    # is_upper?, is_currency?, like_num?
    bool_features = np.zeros((num_entries, 3), dtype=np.float32)
    dep_embeddings = np.zeros((num_entries, DEP_EMBEDDINGS_DIM),
                              dtype=np.float32)

    idx = 0
    words = []
    for entry in data:
        question = to_seq(entry["question"], tokenizer, QUESTION_LEN)
        aux = []
        for answer in entry["answers"]:
            x = to_seq(answer, tokenizer, ANSWER_LEN)
            # TODO(sebisebi): maybe insert a separator
            aux.append(np.trim_zeros(x))
        answer = np.concatenate(aux)
        num_zeros_needed = 4 * ANSWER_LEN - answer.shape[0]
        answer = np.pad(answer, (0, num_zeros_needed), 'constant')

        for term in entry["terms"]:
            words.append(term)
            t = to_seq(term, tokenizer, TERM_LEN)[0]
            val = entry["terms"][term]
            assert(0 <= val and val <= 5)

            q[idx] = np.copy(question)
            answers[idx] = np.copy(answer)
            terms[idx] = np.array([t])
            labels[idx][val] = 1.0
            if wf.is_science_term(term):
                is_science_term[idx] = 1
            else:
                is_science_term[idx] = 0
            concretness_rating[idx] = expand(
                                wf.get_concretness_rating(term) / 5.0)
            pos_embeddings[idx] = wf.get_POS_embedding(term, entry)

            if wf.is_stop_word(term, entry):
                is_stop_term[idx] = 1.0
            else:
                is_stop_term[idx] = 0.0
            deg_centrality[idx] = expand(wf.get_degree_centrality(term, entry))
            close_centrality[idx] = expand(wf.get_closeness_centrality(term,
                                                                       entry))
            eigen_centrality[idx] = expand(wf.get_eigen_centrality(term,
                                                                   entry))
            pmi_values[idx] = np.concatenate((
                wf.get_PMI(term, entry, use_question=True),
                wf.get_PMI(term, entry, use_question=False)
            )).flatten()

            ner_values[idx] = np.copy(wf.get_one_hot_NER(term, entry))
            bool_features[idx] = np.copy(wf.get_bool_features(term, entry))
            dep_embeddings[idx] = np.copy(wf.get_DEP_embedding(term, entry))

            idx += 1
    assert(idx == num_entries)

    if DEBUG:
        num_science_terms = np.sum(is_science_term)
        print("Found {} ({}%) science terms.".format(
                    int(num_science_terms),
                    round(100.0 * num_science_terms / max(num_entries, 1), 2)))
        print("Mean concretness rating: {} out of 5.0".format(
                    round(np.mean(concretness_rating[:, 0]) * 5.0, 3)))

        num_stop_terms = np.count_nonzero(is_stop_term)
        print("Found {} ({}%) stop terms.".format(
                    int(num_stop_terms),
                    round(100.0 * num_stop_terms / max(num_entries, 1), 2)))

        emb_found = sum(1 for y in pos_embeddings if not np.allclose(
                                             y, np.zeros(POS_EMBEDDINGS_DIM,)))
        print("Found {} ({}%) POS embeddings.".format(
                    int(emb_found),
                    round(100.0 * emb_found / max(num_entries, 1), 2)))

        deg_cen_found = sum(1 for y in deg_centrality if not np.allclose(
                                                                y[0], 0.0))
        print("Found {} ({}%) degree centrality values.".format(
                    int(deg_cen_found),
                    round(100.0 * deg_cen_found / max(num_entries, 1), 2)))

        close_cen_found = sum(1 for y in close_centrality if not np.allclose(
                                                                y[0], 0.0))
        print("Found {} ({}%) closeness centrality values.".format(
                    int(close_cen_found),
                    round(100.0 * close_cen_found / max(num_entries, 1), 2)))

        eigen_cen_found = sum(1 for y in eigen_centrality if not np.allclose(
                                                                y[0], 0.0))
        print("Found {} ({}%) eigenvector centrality values.".format(
                    int(eigen_cen_found),
                    round(100.0 * eigen_cen_found / max(num_entries, 1), 2)))

        emb_found = sum(1 for y in dep_embeddings if not np.allclose(
                                             y, np.zeros(DEP_EMBEDDINGS_DIM,)))
        print("Found {} ({}%) DEP embeddings.".format(
                    int(emb_found),
                    round(100.0 * emb_found / max(num_entries, 1), 2)))

    if DEBUG:
        print("")

    out = {
        'question_input': q,
        'answers_input': answers,
        'term_input': terms,
        'is_science_term_input': is_science_term,
        'is_stop_term_input': is_stop_term,
        'concretness_rating_input': concretness_rating,
        'pos_embeddings_input':  pos_embeddings,
        'deg_centrality_input': deg_centrality,
        'close_centrality_input': close_centrality,
        'eigen_centrality_input': eigen_centrality,
        'pmi_values_input': pmi_values,
        'ner_values_input': ner_values,
        'bool_features_input': bool_features,
        'dep_embeddings_input': dep_embeddings
    }
    return out, labels, words


def build_embeddings_matrix(tokenizer):
    word_index = tokenizer.word_index
    embedder = WordEmbeddings(WORD_EMBEDDINGS_PATH, WORD_EMBEDDINGS_DIM, True)
    dim = embedder.get_embedding_len()
    embeddings_matrix = np.zeros((len(word_index) + 1, dim), dtype=np.float32)
    emb_found = 0
    for word in word_index:
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


def define_model(num_words, embeddings_matrix, scope, embedding_dim=64):
    # (batch, input_len) => (batch, input_len, embedding_dim)
    question_input = Input(shape=(QUESTION_LEN,), name="question_input")
    answer_input = Input(shape=(4 * ANSWER_LEN,), name="answers_input")
    term_input = Input(shape=(1,), name="term_input")
    is_science_term_input = Input(shape=(1,), name="is_science_term_input")
    is_stop_term_input = Input(shape=(1,), name="is_stop_term_input")
    concretness_rating_input = Input(shape=(POLY_FEATURES,),
                                     name="concretness_rating_input")
    pos_embeddings_input = Input(shape=(POS_EMBEDDINGS_DIM,),
                                 name="pos_embeddings_input")
    deg_centrality_input = Input(shape=(POLY_FEATURES,),
                                 name="deg_centrality_input")
    close_centrality_input = Input(shape=(POLY_FEATURES,),
                                   name="close_centrality_input")
    eigen_centrality_input = Input(shape=(POLY_FEATURES,),
                                   name="eigen_centrality_input")
    pmi_values_input = Input(shape=(12,), name="pmi_values_input")
    ner_values_input = Input(shape=(NER_COUNT,), name="ner_values_input")
    bool_features_input = Input(shape=(3,), name="bool_features_input")
    dep_embeddings_input = Input(shape=(DEP_EMBEDDINGS_DIM,),
                                 name="dep_embeddings_input")

    # 0 index is used for masking.
    question_emb = Embedding(input_dim=num_words + 1,
                             output_dim=embedding_dim,
                             weights=[embeddings_matrix],
                             input_length=QUESTION_LEN,
                             name="embedding_question_" + scope,
                             mask_zero=True,
                             trainable=False)(question_input)
    answer_emb = Embedding(input_dim=num_words + 1,
                           output_dim=embedding_dim,
                           weights=[embeddings_matrix],
                           input_length=4 * ANSWER_LEN,
                           name="embedding_answer_" + scope,
                           mask_zero=True,
                           trainable=False)(answer_input)
    term_emb = Embedding(input_dim=num_words + 1,
                         output_dim=embedding_dim,
                         weights=[embeddings_matrix],
                         input_length=1,
                         name="embedding_term_" + scope,
                         mask_zero=False,
                         trainable=False)(term_input)

    q_lstm = LSTM(60, recurrent_dropout=0.40, name="lstm_1")(question_emb)
    a_lstm = LSTM(25, recurrent_dropout=0.40, name="lstm_2")(answer_emb)
    term = Flatten(name="flatten_1")(term_emb)

    output_1 = concatenate([q_lstm, a_lstm, term], name="concatenate_1")
    qat = Dense(90, activation='relu', name="dense_1")(output_1)
    qat = Dropout(0.4, name="dropout_1")(qat)

    centrality = concatenate([
        is_stop_term_input,
        deg_centrality_input,
        close_centrality_input,
        eigen_centrality_input,
    ], name="concatenate_2")

    f1 = concatenate([
        is_science_term_input, concretness_rating_input,
        pos_embeddings_input, centrality, pmi_values_input,
        is_stop_term_input, ner_values_input,
        bool_features_input, dep_embeddings_input

    ], name="concatenate_3")
    f1 = Dropout(0.4, name="dropout_2")(f1)
    f2 = Dense(135, activation='relu', name="dense_2")(f1)
    f2 = Dropout(0.4, name="dropout_3")(f2)
    f3 = Dense(135, activation='relu', name="dense_3")(f2)
    f3 = Dropout(0.3, name="dropout_4")(f3)

    output_3 = concatenate([qat, f3], name="concatenate_4")
    output_3 = Dropout(0.35, name="dropout_5")(output_3)
    output_4 = Dense(100, activation='relu', name="dense_4")(output_3)

    output = Dense(NUM_CLASSES, activation='softmax', name="dense_5")(output_4)
    model = Model(inputs=[
                        question_input, answer_input, term_input,
                        is_science_term_input, is_stop_term_input,
                        concretness_rating_input,
                        pos_embeddings_input,
                        deg_centrality_input,
                        close_centrality_input,
                        eigen_centrality_input,
                        pmi_values_input,
                        ner_values_input,
                        bool_features_input,
                        dep_embeddings_input],
                  outputs=[output])
    model.compile(loss=categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def train():
    train_data = read_data_from_json(TRAIN_DATA_PATH)
    val_data = read_data_from_json(VALIDATION_DATA_PATH)
    test_data = read_data_from_json(TEST_DATA_PATH)

    # train_data = undersample_dataset(train_data, prob=0.68)
    # val_data = undersample_dataset(val_data, prob=0.68)
    # test_data = undersample_dataset(test_data, prob=0.68)

    # train_data = train_data[:2]
    # val_data = val_data[:2]
    # test_data = test_data[:1]

    if DEBUG:
        print_data_stats(train_data, "Train")
        print_data_stats(val_data, "Validation")
        print_data_stats(test_data, "Test")
        if False:
            print(dataset_similarity(val_data, train_data))  # 0.5714%
            print(dataset_similarity(test_data, train_data))   # 2.112%

    # Tokenize data (rudimentary tokenizer).
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(train_data) +
                           all_sentences(val_data) +
                           all_sentences(test_data))

    if DEBUG:
        print("Tokenizer found {} words.".format(len(tokenizer.word_counts)))
        print("")

    # Convert to Keras input arrays (or dict).
    wf = WordFeatures()
    wf.train_PMI(train_data + val_data + test_data)

    train_data, train_labels, _ = preprocess_data(train_data, tokenizer, wf,
                                                  "train")
    val_data, val_labels, _ = preprocess_data(val_data, tokenizer, wf,
                                              "validation")
    test_data, test_labels, _ = preprocess_data(test_data, tokenizer, wf,
                                                "test")

    # Equalize training data labels to the same frequency.
    if False:
        from utils import equalize
        train_data, train_labels = equalize(train_data, train_labels)
        if DEBUG:
            print("Train data has been equalized. New freq: {}.".format(
                np.asarray(np.sum(train_labels, axis=0), dtype=np.int32)))
    if False:
        from utils import oversample_dataset
        train_data, train_labels = oversample_dataset(train_data, train_labels,
                                                      [6000, 8000])
        if DEBUG:
            print("Train data has been oversampled. New freq: {}.".format(
                np.asarray(np.sum(train_labels, axis=0), dtype=np.int32)))

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "train", WORD_EMBEDDINGS_DIM)
    model.summary()
    plot_model(model, to_file='model.png', show_shapes=True)

    filepath = "models/" + "model.{val_acc:.3f}-{epoch:03d}.hdf5"
    checkpoint = ModelCheckpoint(filepath, monitor='val_acc',
                                 verbose=0, mode='max',
                                 save_best_only=True, save_weights_only=True)
    model.fit(train_data, train_labels,
              batch_size=4000, epochs=450,
              verbose=2,
              validation_data=(val_data, val_labels),
              callbacks=[checkpoint])
    score = model.evaluate(test_data, test_labels, verbose=0)
    if score:
        print('Test loss:', score[0])
        print('Test accuracy:', score[1])


def test(weights_file=None):
    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))

    test_data = read_data_from_json(TEST_DATA_PATH)

    if DEBUG:
        print_data_stats(test_data, "Test")

    # Tokenize data (rudimentary tokenizer).
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(test_data))

    if DEBUG:
        print("Tokenizer found {} words.".format(len(tokenizer.word_counts)))
        print("")

    # Convert to Keras input arrays (or dict).
    wf = WordFeatures()
    wf.train_PMI(test_data)

    test_data, test_labels, _ = preprocess_data(test_data, tokenizer, wf,
                                                "test")

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "test", WORD_EMBEDDINGS_DIM)
    model.load_weights(weights_file, by_name=True)
    model.summary()

    num_tests = test_data["question_input"].shape[0]
    y = model.predict(test_data)
    assert(y.shape[0] == num_tests)

    correct = 0
    total = 0
    exp_acc = 0.0
    lin_acc = 0.0
    for i in range(0, num_tests):
        predicted = np.argmax(y[i])
        expected = np.argmax(test_labels[i])

        # Expected value (treat y[i] as a random variable).
        value = np.dot(y[i], [0, 1, 2, 3, 4, 5])
        expected_value = np.dot(test_labels[i], [0, 1, 2, 3, 4, 5])
        exp_acc += (np.exp(abs(value - expected_value)) - 1.0)
        lin_acc += abs(value - expected_value)
        if predicted == expected:
            correct += 1
        total += 1
    assert(total == num_tests)
    print("\nEvaluated on {} terms.".format(total))
    print("Accuracy: {0:.3f}%".format(100 * correct / total))
    print("Exp accuracy: {0:.3f}".format(exp_acc / total))
    print("Linear accuracy: {0:.3f}".format(lin_acc / total))


def binary_test(weights_file=None):
    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))

    test_data = read_data_from_json(TEST_DATA_PATH)
    # test_data = undersample_dataset(test_data, prob=0.84)

    if DEBUG:
        print_data_stats(test_data, "Test")

    # Tokenize data (rudimentary tokenizer).
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(test_data))

    if DEBUG:
        print("Tokenizer found {} words.".format(len(tokenizer.word_counts)))
        print("")

    # Convert to Keras input arrays (or dict).
    wf = WordFeatures()
    wf.train_PMI(test_data)

    test_data, test_labels, words = preprocess_data(test_data, tokenizer, wf,
                                                    "test")

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "test", WORD_EMBEDDINGS_DIM)
    model.load_weights(weights_file, by_name=True)
    model.summary()

    num_tests = test_data["question_input"].shape[0]
    y = model.predict(test_data)
    assert(y.shape[0] == num_tests)

    correct = 0
    total = 0
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    correct_confidence = 0.0
    wrong_confidence = 0.0
    false_positive_words = []
    for i in range(0, num_tests):
        # Expected value (treat y[i] as a random variable).
        value = np.dot(y[i], [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

        if value >= 0.5:
            predicted = 1
        else:
            predicted = 0
        confidence = None
        if predicted == 1:
            confidence = np.dot(y[i], [0, 0, 0, 1, 1, 1])
        else:
            confidence = np.dot(y[i], [1, 1, 1, 0, 0, 0])

        expected_value = np.argmax(test_labels[i])
        if expected_value >= 2.5:
            expected = 1
        else:
            expected = 0

        if predicted == expected:
            correct += 1
            correct_confidence += confidence
        else:
            wrong_confidence += confidence

        if predicted == 1:
            if expected == 1:
                true_positive += 1
            else:
                false_positive += 1
                false_positive_words.append(words[i])
        else:
            if expected == 0:
                true_negative += 1
            else:
                false_negative += 1
        total += 1
    assert(total == num_tests)
    assert(correct == true_positive + true_negative)
    precision = 100.0 * true_positive / (true_positive + false_positive)
    recall = 100.0 * true_positive / (true_positive + false_negative)
    f1 = 2.0 * precision * recall / (precision + recall)
    print("")
    print("            |  Correct class  |")
    print("            |    1   |    0   |")
    print("Predicted 1 |{}  |{}  |".format(
            str(true_positive).rjust(6), str(false_positive).rjust(6)))
    print("Predicted 0 |{}  |{}  |".format(
            str(false_negative).rjust(6), str(true_negative).rjust(6)))

    print("\nEvaluated on {} terms.".format(total))
    print("Binary accuracy: {0:.3f}%".format(100 * correct / total))
    print("Precision: {0:.3f}%".format(precision))
    print("Recall: {0:.3f}%".format(recall))
    print("F1: {0:.3f}".format(f1 / 100.0))
    if correct >= 1:
        print("Correct confidence {0:.3f}%".format(
            100.0 * correct_confidence / correct))
    if correct < total:
        print("Wrong confidence {0:.3f}%".format(
            100.0 * wrong_confidence / (total - correct)))
    print("")
    random.shuffle(false_positive_words)
    print("Some false positive words: ", str(false_positive_words[:10]))


def predict(entry, sort=False, weights_file=None, show_plot=True):
    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))

    assert("question" in entry)
    question = entry["question"]
    if "terms" not in entry:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(question)
        entry["terms"] = {}
        for token in doc:
            entry["terms"][token.text] = 0
    data = [entry]

    # Tokenize data (rudimentary tokenizer).
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(data))

    # Convert to Keras input arrays (or dict).
    wf = WordFeatures()
    wf.train_PMI(data)
    data, _, words = preprocess_data(data, tokenizer, wf, "predict")

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "predict", WORD_EMBEDDINGS_DIM)
    model.load_weights(weights_file, by_name=True)

    y = model.predict(data)

    idx = 0
    essentiality = []
    for word in entry["terms"]:
        value = np.dot(y[idx], [0, 1, 2, 3, 4, 5])
        essentiality.append(value / 5.0)
        idx += 1

    if sort:
        zipped = list(zip(words, essentiality))
        zipped.sort(key=lambda x: x[1], reverse=True)
        words = [x[0] for x in zipped]
        essentiality = [x[1] for x in zipped]

    import matplotlib.pyplot as plt
    plt.bar(range(len(words)), essentiality, align='center')
    plt.title("Predicted values")
    plt.xticks(range(len(words)), words, rotation=45,
               horizontalalignment='right')
    plt.tight_layout()
    if show_plot:
        plt.show()


def predict_from_dataset(dataset="val", index=None, sort=False):
    assert(dataset in ["train", "val", "test"])
    data = None
    if dataset == "train":
        data = read_data_from_json(TRAIN_DATA_PATH)
    elif dataset == "val":
        data = read_data_from_json(VALIDATION_DATA_PATH)
    elif dataset == "test":
        data = read_data_from_json(TEST_DATA_PATH)
    assert(data is not None)
    if index is None:
        entry = random.choice(data)
    else:
        entry = data[index]

    entry_copy = deepcopy(entry)
    predict(entry, sort=sort, show_plot=False)
    entry = entry_copy

    idx = 0
    essentiality = []
    words = []
    for word in entry["terms"]:
        value = entry["terms"][word]
        essentiality.append(value / 5.0)
        words.append(word)
        idx += 1

    if sort:
        zipped = list(zip(words, essentiality))
        zipped.sort(key=lambda x: x[1], reverse=True)
        words = [x[0] for x in zipped]
        essentiality = [x[1] for x in zipped]

    print("\nQuestion: {}\n".format(entry["question"]))

    import matplotlib.pyplot as plt
    plt.figure()
    plt.bar(range(len(words)), essentiality, align='center')
    plt.title("Correct values")
    plt.xticks(range(len(words)), words, rotation=45,
               horizontalalignment='right')
    plt.tight_layout()
    plt.show()


def plot_pmi_values(dataset="val", index=None, sort=False):
    assert(dataset in ["train", "val", "test"])
    data = None
    if dataset == "train":
        data = read_data_from_json(TRAIN_DATA_PATH)
    elif dataset == "val":
        data = read_data_from_json(VALIDATION_DATA_PATH)
    elif dataset == "test":
        data = read_data_from_json(TEST_DATA_PATH)
    assert(data is not None)
    if index is None:
        entry = random.choice(data)
    else:
        entry = data[index]

    entry_copy = deepcopy(entry)
    predict(entry, sort=sort, show_plot=False)
    entry = entry_copy

    wf = WordFeatures()
    wf.train_PMI([entry])

    from pmi_utils import reduce_positive_avg
    idx = 0
    values = []
    words = []
    for word in entry["terms"]:
        pmi_values = wf.get_PMI(word, entry, use_question=True,
                                reduce_f=reduce_positive_avg)
        values.append(pmi_values[1])
        words.append(word)
        idx += 1

    if sort:
        zipped = list(zip(words, values))
        zipped.sort(key=lambda x: x[1], reverse=True)
        words = [x[0] for x in zipped]
        values = [x[1] for x in zipped]

    print("\nQuestion: {}\n".format(entry["question"]))

    import matplotlib.pyplot as plt
    plt.figure()
    plt.bar(range(len(words)), values, align='center')
    plt.title("PMI values")
    plt.xticks(range(len(words)), words, rotation=45,
               horizontalalignment='right')
    plt.tight_layout()
    plt.show()


def predict_batch(data, weights_file=None):
    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))

    # Tokenize data (rudimentary tokenizer).
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(data))

    # Convert to Keras input arrays (or dict).
    wf = WordFeatures()
    wf.train_PMI(data)
    data2, _, words = preprocess_data(data, tokenizer, wf, "predict_batch")

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "predict_batch", WORD_EMBEDDINGS_DIM)
    model.load_weights(weights_file, by_name=True)

    y = model.predict(data2, batch_size=128)

    idx = 0
    out = []
    for entry in data:
        out_set = {}
        for _ in entry["terms"]:
            value = np.dot(y[idx], [0, 1, 2, 3, 4, 5])
            word = words[idx]
            assert(word not in out_set)
            out_set[word] = value / 5.0
            idx += 1
        out.append(out_set)

    num_entries = 0
    for entry in data:
        num_entries += len(entry['terms'])
    assert(num_entries == idx)

    assert(len(data) == len(out))
    for i in range(0, len(data)):
        assert(len(out[i]) == len(data[i]["terms"]))
    for out_set in out:
        num_entries -= len(out_set)
    assert(num_entries == 0)

    return out


def plot_F1_scores(dataset, weights_file=None):
    assert(dataset in ["val", "test"])
    if weights_file is None:
        weights_file = pick_best_model_from_dir()
        if DEBUG:
            print("Best model detected: {}".format(weights_file))
    data = None
    if dataset == "val":
        data = read_data_from_json(VALIDATION_DATA_PATH)
    elif dataset == "test":
        data = read_data_from_json(TEST_DATA_PATH)
    assert(data is not None)

    if DEBUG:
        print_data_stats(data, "F1 scores data")

    # Tokenize data (rudimentary tokenizer).
    tokenizer = Tokenizer()
    tokenizer.fit_on_texts(all_sentences(data))

    if DEBUG:
        print("Tokenizer found {} words.".format(len(tokenizer.word_counts)))
        print("")

    # Convert to Keras input arrays (or dict).
    wf = WordFeatures()
    wf.train_PMI(data)
    data, labels, words = preprocess_data(data, tokenizer, wf, "F1 scores")

    embeddings_matrix = build_embeddings_matrix(tokenizer)

    num_words = len(tokenizer.word_counts)
    model = define_model(num_words, embeddings_matrix,
                         "F1_scores_data", WORD_EMBEDDINGS_DIM)
    model.load_weights(weights_file, by_name=True)
    model.summary()

    num_tests = data["question_input"].shape[0]
    y = model.predict(data)
    assert(y.shape[0] == num_tests)

    threshold = 0.0
    f1 = []
    thresholds = []
    best_f1 = None
    best_threshold = None
    acc_at_max_f1 = None
    while threshold <= 1.0:
        correct = 0
        total = 0
        true_positive = 0
        false_positive = 0
        true_negative = 0
        false_negative = 0
        for i in range(0, num_tests):
            # Expected value (treat y[i] as a random variable).
            value = np.dot(y[i], [0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

            if value >= threshold:
                predicted = 1
            else:
                predicted = 0

            expected_value = np.argmax(labels[i])
            if expected_value >= 2.5:
                expected = 1
            else:
                expected = 0

            if predicted == expected:
                correct += 1

            if predicted == 1:
                if expected == 1:
                    true_positive += 1
                else:
                    false_positive += 1
            else:
                if expected == 0:
                    true_negative += 1
                else:
                    false_negative += 1
            total += 1

        assert(total == num_tests)
        assert(correct == true_positive + true_negative)
        if true_positive + false_positive == 0:
            threshold += 0.001
            continue
        if true_positive + false_negative == 0:
            threshold += 0.001
            continue
        precision = 1.0 * true_positive / (true_positive + false_positive)
        recall = 1.0 * true_positive / (true_positive + false_negative)
        f1_score = 2.0 * precision * recall / (precision + recall)
        if best_f1 is None or f1_score > best_f1:
            best_f1 = f1_score
            best_threshold = threshold
            acc_at_max_f1 = 1.0 * correct / max(total, 1.0)
        f1.append(f1_score)
        thresholds.append(threshold)
        threshold += 0.001
    print("Best F1 score: {}, at t = {}".format(
                round(best_f1, 3),
                round(best_threshold, 4)))
    print("Accuracy at max F1: {}".format(round(acc_at_max_f1, 3)))

    import matplotlib.pyplot as plt
    plt.title("F1 score")
    plt.xlabel("Threshold")
    plt.ylabel("F1")
    plt.plot(thresholds, f1)
    plt.show()


def main():
    # train()
    # test()
    # binary_test()
    '''
    predict({
        "question": "One way animals usually respond to a sudden drop "
                    "in temperature is by",
        "answers": ["sweating", "shivering", "blinking", "salivating"]
    }, sort=True)
    '''
    # predict_from_dataset(dataset="val", sort=True)
    # plot_pmi_values(dataset="val")
    plot_F1_scores(dataset="test")


if __name__ == "__main__":
    main()
