import answer.tokenizers as tokenizers
import numpy as np
import os
import random
import tqdm

from answer.settings import DEBUG, NUM_CLASSES, QUESTION_LEN, MODELS_DIR
from answer.settings import WORD_EMBEDDINGS_DIM, WORD_EMBEDDINGS_PATH
from answer.settings import SHOW_PER_SYSTEM_STATS
from answer.utils import print_data_stats, pick_best_model_from_dir
from answer.utils import all_sentences, show_per_system_stats
from answer.word_embeddings_loader import WordEmbeddings
from autocorrect import spell
from copy import deepcopy
from keras.callbacks import ModelCheckpoint
from keras.losses import categorical_crossentropy
from keras.layers import Input, Dense, Concatenate, Embedding, LSTM, Dropout
from keras.models import Model
from keras.preprocessing.sequence import pad_sequences
from multinli.export import MultiNLI
from nlp_inference.export import SNLI
from qa.export import QA
from scitail.export import SciTail


class Cerebro(object):
    '''
        Implements a regression model over:
        1) IR scores.
        2) QA model scores.
        3) NLP inference scores.
    '''
    def __init__(self):
        print("***************************************************")
        print("*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*")
        print("**               Running Cerebro                 **")
        print("*~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~*")
        print("***************************************************")

    def get_second_best_from_array(self, scores, index):
        assert(len(scores) == 4)
        assert(abs(sum(scores) - 1.0) <= 0.001)

        score = scores[index]
        scores = scores[0:index] + scores[index + 1:]
        scores = sorted(scores, reverse=True)
        assert(len(scores) == 3)
        assert(abs(score + sum(scores) - 1.0) <= 0.001)

        second_best = scores[0]
        diff = score - second_best
        assert(-1.0 <= diff and diff <= 1.0)

        if np.allclose(diff, 0.0):
            return 0.0

        if diff > 0:
            return np.log(1.0 + 2.0 * diff * (np.exp(1.0) - 1.0))

        return -np.log(1.0 - 2.0 * diff * (np.exp(1.0) - 1.0))

    def get_second_best_score(self, answers, index):
        assert(isinstance(answers, list))
        assert(len(answers) == 4)
        assert(isinstance(index, int))
        assert(0 <= index and index <= 3)

        scores = [x['tfIdfScore'] for x in answers]
        assert(len(scores) == 4)
        assert(abs(sum(scores) - 1.0) <= 0.001)

        score = scores[index]
        scores = scores[0:index] + scores[index + 1:]
        scores = sorted(scores, reverse=True)
        assert(len(scores) == 3)
        assert(abs(score + sum(scores) - 1.0) <= 0.001)

        second_best = scores[0]
        diff = score - second_best
        assert(-1.0 <= diff and diff <= 1.0)

        if np.allclose(diff, 0.0):
            return 0.0

        if diff > 0:
            return np.log(1.0 + 2.0 * diff * (np.exp(1.0) - 1.0))

        return -np.log(1.0 - 2.0 * diff * (np.exp(1.0) - 1.0))

    def to_seq(self, text, tokenizer):
        assert(isinstance(text, str))

        seq = tokenizer.texts_to_sequences([text])
        seq = pad_sequences(seq, maxlen=QUESTION_LEN, padding='pre',
                            truncating='pre', value=0)[0]
        # type(seq) = numpy.ndarray
        seq = seq.astype(np.int32).tolist()
        return np.array(seq, dtype=np.int32)

    # Returns a dict to be fed in Keras along with labels.
    # Data is not shuffled at all.
    def preprocess_data(self, data, tokenizer, title, oversample=False):
        assert(isinstance(data, list))
        assert(isinstance(title, str))
        assert(isinstance(oversample, bool))
        assert(isinstance(tokenizer, tokenizers.Tokenizer))

        num_entries = len(data)
        if DEBUG:
            print("Preprocessing {} data ...".format(title))
            print("Total num inputs: {}".format(num_entries))

        tf_idf_score = None
        second_best_tf_idf = None
        questions = None
        qa_score = None
        scitail_score = None
        snli_score = None
        multinli_score = None
        qtype = None
        labels = None
        if oversample:
            tf_idf_score = np.zeros((6 * num_entries,), dtype=np.float32)
            second_best_tf_idf = np.zeros((6 * num_entries,), dtype=np.float32)
            questions = np.zeros((6 * num_entries, QUESTION_LEN))
            qa_score = np.zeros((6 * num_entries, 2), dtype=np.float32)
            scitail_score = np.zeros((6 * num_entries, 2), dtype=np.float32)
            snli_score = np.zeros((6 * num_entries, 2), dtype=np.float32)
            multinli_score = np.zeros((6 * num_entries, 2), dtype=np.float32)
            qtype = np.zeros((6 * num_entries, 37), dtype=np.float32)
            labels = np.zeros((6 * num_entries, 2))
        else:
            tf_idf_score = np.zeros((4 * num_entries,), dtype=np.float32)
            second_best_tf_idf = np.zeros((4 * num_entries,), dtype=np.float32)
            questions = np.zeros((4 * num_entries, QUESTION_LEN))
            qa_score = np.zeros((4 * num_entries, 2), dtype=np.float32)
            scitail_score = np.zeros((4 * num_entries, 2), dtype=np.float32)
            snli_score = np.zeros((4 * num_entries, 2), dtype=np.float32)
            multinli_score = np.zeros((4 * num_entries, 2), dtype=np.float32)
            qtype = np.zeros((4 * num_entries, 37), dtype=np.float32)
            labels = np.zeros((4 * num_entries, 2))

        assert(tf_idf_score is not None)
        assert(labels is not None)
        assert(questions is not None)
        assert(qa_score is not None)
        assert(scitail_score is not None)
        assert(snli_score is not None)
        assert(multinli_score is not None)
        assert(qtype is not None)

        idx = 0
        for entry in data:
            answers = entry['answers']
            assert(len(answers) == 4)

            q_seq = self.to_seq(entry['question'], tokenizer)
            # q_type = QTS.get_qtype_as_int(entry['question'])
            q_type = 0
            assert(0 <= q_type and q_type <= 36)

            for i in range(0, 4):
                answer = answers[i]

                tf_idf_score[idx] = answer['tfIdfScore']
                second_best_tf_idf[idx] = self.get_second_best_score(
                                                deepcopy(answers), i)
                questions[idx] = np.copy(q_seq)
                qtype[idx][q_type] = 1.0
                qa_score[idx] = answer['qaScore']
                scitail_score[idx] = answer['scitailScore']
                snli_score[idx] = answer['snliScore']
                multinli_score[idx] = answer['multinliScore']

                if answer['isCorrect'] is True:
                    labels[idx][1] = 1
                else:
                    labels[idx][0] = 1

                idx += 1
        if oversample:
            for step in range(0, 2):
                for entry in data:
                    answers = entry['answers']
                    assert(len(answers) == 4)

                    q_seq = self.to_seq(entry['question'], tokenizer)
                    # q_type = QTS.get_qtype_as_int(entry['question'])
                    q_type = 0
                    assert(0 <= q_type and q_type <= 36)

                    for i in range(0, 4):
                        answer = answers[i]
                        if not answer['isCorrect']:
                            continue

                        tf_idf_score[idx] = answer['tfIdfScore']
                        second_best_tf_idf[idx] = self.get_second_best_score(
                                                    deepcopy(answers), i)
                        questions[idx] = np.copy(q_seq)
                        qtype[idx][q_type] = 1.0
                        qa_score[idx] = answer['qaScore']
                        scitail_score[idx] = answer['scitailScore']
                        snli_score[idx] = answer['snliScore']
                        multinli_score[idx] = answer['multinliScore']

                        labels[idx][1] = 1
                        idx += 1

        if oversample:
            assert(idx == 6 * num_entries)
            assert(np.sum(labels, axis=0)[0] == np.sum(labels, axis=0)[1])
        else:
            assert(idx == 4 * num_entries)

        out = {
            'tf_idf_score_input': tf_idf_score,
            'second_best_tf_idf_input': second_best_tf_idf,
            'question_input': questions,
            'qa_score_input': qa_score,
            'scitail_score_input': scitail_score,
            'snli_score_input': snli_score,
            'multinli_score_input': multinli_score,
            'qtype_input': qtype

        }
        return out, labels

    @staticmethod
    def build_embeddings_matrix(tokenizer):
        word_index = tokenizer.word_index()
        assert(len(tokenizer.word_index()) == len(tokenizer.word_counts()))
        embedder = WordEmbeddings(WORD_EMBEDDINGS_PATH,
                                  WORD_EMBEDDINGS_DIM,
                                  True)  # Use MySQL for word embeddings.
        dim = embedder.get_embedding_len()
        assert(dim == WORD_EMBEDDINGS_DIM)

        embeddings_matrix = np.zeros((len(word_index) + 1, dim),
                                     dtype=np.float32)
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

    def define_model(self, embeddings_matrix, scope):
        assert(scope in ["train", "test"])
        assert(embeddings_matrix.shape[1] == WORD_EMBEDDINGS_DIM)

        tf_idf_score_input = Input(shape=(1,), name="tf_idf_score_input")
        second_best_tf_idf_input = Input(shape=(1,),
                                         name="second_best_tf_idf_input")
        question_input = Input(shape=(QUESTION_LEN,), name="question_input")
        qa_score_input = Input(shape=(2,), name="qa_score_input")
        scitail_score_input = Input(shape=(2,), name="scitail_score_input")
        snli_score_input = Input(shape=(2,), name="snli_score_input")
        multinli_score_input = Input(shape=(2,), name="multinli_score_input")
        qtype_input = Input(shape=(37,), name="qtype_input")

        question = Embedding(input_dim=embeddings_matrix.shape[0],
                             output_dim=embeddings_matrix.shape[1],
                             weights=[embeddings_matrix],
                             input_length=QUESTION_LEN,
                             name="embedding_q_" + scope,
                             mask_zero=True,
                             trainable=False)(question_input)
        question = LSTM(10, recurrent_dropout=0.5, name="lstm_1")(question)
        question = Dropout(0.5, name="dropout_1")(question)

        inputs = Concatenate(axis=-1, name="concatenate_1")([
                    tf_idf_score_input,
                    second_best_tf_idf_input,
                    qa_score_input,
                    scitail_score_input,
                    snli_score_input,
                    multinli_score_input,
                    # qtype_input
                    # question,
        ])
        inputs = Dropout(0.4)(inputs)

        output_1 = Dense(5, activation='relu', name="dense_1")(inputs)
        output_1 = Dropout(0.4, name="dropout_2")(output_1)

        output_2 = Dense(20, activation='relu', name="dense_2")(output_1)
        output_2 = Dropout(0.35, name="dropout_3")(output_2)

        output = Dense(NUM_CLASSES, activation='softmax', name="dense_5")(
                                                                    output_2)
        model = Model(inputs=[
                        tf_idf_score_input,
                        second_best_tf_idf_input,
                        question_input,
                        qa_score_input,
                        scitail_score_input,
                        snli_score_input,
                        multinli_score_input,
                        qtype_input
                      ], outputs=[output])
        model.compile(loss=categorical_crossentropy,
                      optimizer='adam',
                      metrics=['accuracy'])
        return model

    def augment_with_qa(self, data, orig):
        assert(isinstance(data, list))
        qa = QA()
        res = qa.predict_batch(orig)
        assert(len(res.shape) == 2)
        assert(res.shape == (len(data), 4))

        m = len(data)
        for i in range(0, m):
            scores = np.exp(res[i]).tolist()
            scores = [1.0 * x / sum(scores) for x in scores]
            assert(len(scores) == 4)
            for j in range(0, 4):
                second_best = self.get_second_best_from_array(scores, j)
                data[i]["answers"][j]["qaScore"] = np.array(
                                                [scores[j], second_best])

        correct = 0
        for i in range(0, m):
            scores = [x["qaScore"][1] for x in data[i]["answers"]]
            x = np.argmax(scores)
            assert(x in [0, 1, 2, 3])
            if data[i]["answers"][x]["isCorrect"]:
                correct += 1
        if DEBUG:
            print("[Answer] QA only acc: {0:.2f}%".format(100.0 * correct / m))

        return data

    def augment_with_scitail(self, data, orig):
        assert(isinstance(data, list))

        scitail = SciTail()
        res = scitail.predict_batch(orig)
        assert(len(res.shape) == 2)
        assert(res.shape == (len(data), 4))

        m = len(data)
        for i in range(0, m):
            scores = np.exp(res[i]).tolist()
            scores = [1.0 * x / sum(scores) for x in scores]
            assert(len(scores) == 4)
            for j in range(0, 4):
                second_best = self.get_second_best_from_array(scores, j)
                data[i]["answers"][j]["scitailScore"] = np.array(
                                                    [scores[j], second_best])

        correct = 0
        for i in range(0, m):
            scores = [x["scitailScore"][0] for x in data[i]["answers"]]
            x = np.argmax(scores)
            assert(x in [0, 1, 2, 3])
            if data[i]["answers"][x]["isCorrect"]:
                correct += 1
        if DEBUG:
            print("[Answer] SciTail only acc: {0:.2f}%".format(
                                                    100.0 * correct / m))

        return data

    def augment_with_snli(self, data, orig):
        assert(isinstance(data, list))

        snli = SNLI()
        res = snli.predict_batch(orig)
        assert(len(res.shape) == 2)
        assert(res.shape == (len(data), 4))

        m = len(data)
        for i in range(0, m):
            scores = np.exp(res[i]).tolist()
            scores = [1.0 * x / sum(scores) for x in scores]
            assert(len(scores) == 4)
            for j in range(0, 4):
                second_best = self.get_second_best_from_array(scores, j)
                data[i]["answers"][j]["snliScore"] = np.array(
                                                    [scores[j], second_best])

        correct = 0
        for i in range(0, m):
            scores = [x["snliScore"][0] for x in data[i]["answers"]]
            x = np.argmax(scores)
            assert(x in [0, 1, 2, 3])
            if data[i]["answers"][x]["isCorrect"]:
                correct += 1
        if DEBUG:
            print("[Answer] SNLI only acc: {0:.2f}%".format(
                                                    100.0 * correct / m))

        return data

    def augment_with_multinli(self, data, orig):
        assert(isinstance(data, list))

        multinli = MultiNLI()
        res = multinli.predict_batch(orig)
        assert(len(res.shape) == 2)
        assert(res.shape == (len(data), 4))

        m = len(data)
        for i in range(0, m):
            scores = np.exp(res[i]).tolist()
            scores = [1.0 * x / sum(scores) for x in scores]
            assert(len(scores) == 4)
            for j in range(0, 4):
                second_best = self.get_second_best_from_array(scores, j)
                data[i]["answers"][j]["multinliScore"] = np.array(
                                                    [scores[j], second_best])

        correct = 0
        for i in range(0, m):
            scores = [x["multinliScore"][0] for x in data[i]["answers"]]
            x = np.argmax(scores)
            assert(x in [0, 1, 2, 3])
            if data[i]["answers"][x]["isCorrect"]:
                correct += 1
        if DEBUG:
            print("[Answer] MultiNLI only acc: {0:.2f}%".format(
                                                    100.0 * correct / m))

        return data

    def augment_data(self, data):
        assert(isinstance(data, list))

        orig = deepcopy(data)
        data = self.augment_with_qa(data, orig)
        data = self.augment_with_scitail(data, orig)
        data = self.augment_with_snli(data, orig)
        data = self.augment_with_multinli(data, orig)

        return data

    def train(self, train_data, val_data, test_data):
        assert(isinstance(train_data, list))
        assert(isinstance(val_data, list))
        assert(isinstance(test_data, list))

        # train_data = train_data[0:50]
        # val_data = val_data[0:5]
        # test_data = test_data[0:5]

        all_data = self.augment_data(train_data + val_data + test_data)
        train_data = all_data[0:len(train_data)]
        val_data = all_data[len(train_data):len(train_data) + len(val_data)]
        test_data = all_data[len(train_data) + len(val_data):]
        assert(len(train_data + val_data + test_data) == len(all_data))

        if DEBUG:
            print_data_stats(train_data, "Train")
            print_data_stats(val_data, "Val")
            print_data_stats(test_data, "Test")

        # Fit a tokenizer on all data. Each word gets assigned a number
        # between 1 and num_words.
        tokenizer = tokenizers.SpacyTokenizer()
        tokenizer.fit_on_texts(all_sentences(train_data) +
                               all_sentences(val_data) +
                               all_sentences(test_data))
        if DEBUG:
            print("Num words: {}\n".format(len(tokenizer.word_counts())))

        train_data, train_labels = self.preprocess_data(train_data,
                                                        tokenizer,
                                                        "train",
                                                        oversample=True)
        val_data, val_labels, = self.preprocess_data(val_data,
                                                     tokenizer,
                                                     "val",
                                                     oversample=True)
        test_data, test_labels = self.preprocess_data(test_data,
                                                      tokenizer,
                                                      "test",
                                                      oversample=True)

        embeddings_matrix = Cerebro.build_embeddings_matrix(tokenizer)
        num_words = len(tokenizer.word_counts())
        assert(embeddings_matrix.shape[0] == num_words + 1)

        model = self.define_model(embeddings_matrix, scope="train")
        model.summary()

        filepath = "models/" + "model.{val_acc:.3f}-{epoch:03d}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='val_acc',
                                     verbose=0, mode='max',
                                     save_best_only=True,
                                     save_weights_only=True)
        model.fit(train_data, train_labels,
                  batch_size=random.randint(50, 1000), epochs=300,
                  verbose=2,
                  validation_data=(val_data, val_labels),
                  callbacks=[checkpoint],
                  shuffle=True)
        score = model.evaluate(test_data, test_labels, verbose=0)
        if score:
            print('Test loss:', score[0])
            print('Test accuracy:', score[1])

    def binary_test(self, test_data, weights_file=None):
        assert(isinstance(test_data, list))
        assert(isinstance(weights_file, str) or weights_file is None)

        test_data = self.augment_data(test_data)

        if DEBUG:
            print_data_stats(test_data, "Binary accuracy")

        tokenizer = tokenizers.SpacyTokenizer()
        tokenizer.fit_on_texts(all_sentences(test_data))
        if DEBUG:
            print("Num words: {}\n".format(len(tokenizer.word_counts())))

        test_data, test_labels = self.preprocess_data(test_data,
                                                      tokenizer,
                                                      "Binary acc",
                                                      oversample=True)

        embeddings_matrix = Cerebro.build_embeddings_matrix(tokenizer)
        num_words = len(tokenizer.word_counts())
        assert(embeddings_matrix.shape[0] == num_words + 1)

        model = self.define_model(embeddings_matrix, scope="test")
        if weights_file is None:
            weights_file = pick_best_model_from_dir()
            if DEBUG:
                print("Best model detected: {}".format(weights_file))
        model.load_weights(weights_file, by_name=True)
        model.summary()

        num_tests = test_labels.shape[0]
        y = model.predict(test_data)
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
        print("\nEvaluated on {} questions.".format(test_labels.shape[0]))
        print("Accuracy: {0:.3f}%".format(100.0 * correct / total))

    def test_4way(self, test_data, weights_file=None):
        assert(isinstance(test_data, list))
        assert(isinstance(weights_file, str) or weights_file is None)

        test_data = self.augment_data(test_data)

        if DEBUG:
            print_data_stats(test_data, "Binary accuracy")

        tokenizer = tokenizers.SpacyTokenizer()
        tokenizer.fit_on_texts(all_sentences(test_data))
        if DEBUG:
            print("Num words: {}\n".format(len(tokenizer.word_counts())))

        test_data, test_labels = self.preprocess_data(test_data,
                                                      tokenizer,
                                                      "Binary acc",
                                                      oversample=False)

        embeddings_matrix = Cerebro.build_embeddings_matrix(tokenizer)
        num_words = len(tokenizer.word_counts())
        assert(embeddings_matrix.shape[0] == num_words + 1)

        model = self.define_model(embeddings_matrix, scope="test")
        if weights_file is None:
            weights_file = pick_best_model_from_dir()
            if DEBUG:
                print("Best model detected: {}".format(weights_file))
        model.load_weights(weights_file, by_name=True)
        model.summary()

        num_tests = test_labels.shape[0]
        y = model.predict(test_data)
        assert(y.shape[0] == num_tests)
        assert(num_tests % 4 == 0)

        correct = 0
        total = 0
        for i in range(0, num_tests, 4):
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

    def predict(self, test_data, weights_file=None):
        assert(isinstance(test_data, list))
        assert(isinstance(weights_file, str) or weights_file is None)

        # Extract ids.
        ids = []
        for entry in test_data:
            ids.append(entry["id"])

        # Augment data.
        test_data = self.augment_data(test_data)

        if DEBUG:
            print_data_stats(test_data, "Binary accuracy")

        tokenizer = tokenizers.SpacyTokenizer()
        tokenizer.fit_on_texts(all_sentences(test_data))
        if DEBUG:
            print("Num words: {}\n".format(len(tokenizer.word_counts())))

        test_data, _ = self.preprocess_data(test_data,
                                            tokenizer,
                                            "Predict",
                                            oversample=False)

        embeddings_matrix = Cerebro.build_embeddings_matrix(tokenizer)
        num_words = len(tokenizer.word_counts())
        assert(embeddings_matrix.shape[0] == num_words + 1)

        model = self.define_model(embeddings_matrix, scope="test")
        if weights_file is None:
            weights_file = pick_best_model_from_dir()
            if DEBUG:
                print("Best model detected: {}".format(weights_file))
        model.load_weights(weights_file, by_name=True)
        model.summary()

        num_tests = len(ids) * 4
        y = model.predict(test_data)
        assert(y.shape[0] == num_tests)
        assert(num_tests % 4 == 0)

        total = 0
        correct_answers = []
        for i in range(0, num_tests, 4):
            predicted = y[i: i + 4, 1]
            predicted = np.argmax(predicted)
            correct_answers.append(predicted)
            total += 1

        assert(total == len(correct_answers))
        assert(len(ids) == len(correct_answers))
        assert(total == num_tests / 4)

        rez = list(zip(ids, correct_answers))
        rez = sorted(rez, key=lambda x: x[0])
        return rez

    def predict_batch(self, test_data, weights_file=None):
        assert(isinstance(test_data, list))
        assert(isinstance(weights_file, str) or weights_file is None)

        # Extract ids.
        ids = []
        for entry in test_data:
            ids.append(entry["id"])

        # Augment data.
        test_data = self.augment_data(test_data)

        tokenizer = tokenizers.SpacyTokenizer()
        tokenizer.fit_on_texts(all_sentences(test_data))

        test_data, _ = self.preprocess_data(test_data,
                                            tokenizer,
                                            "Predict",
                                            oversample=False)

        embeddings_matrix = Cerebro.build_embeddings_matrix(tokenizer)
        num_words = len(tokenizer.word_counts())
        assert(embeddings_matrix.shape[0] == num_words + 1)

        model = self.define_model(embeddings_matrix, scope="test")
        if weights_file is None:
            weights_file = pick_best_model_from_dir()
            if DEBUG:
                print("Best model detected: {}".format(weights_file))
        model.load_weights(weights_file, by_name=True)
        model.summary()

        num_tests = len(ids) * 4
        y = model.predict(test_data)
        assert(y.shape[0] == num_tests)
        assert(num_tests % 4 == 0)

        rez = []
        for i in range(0, num_tests, 4):
            predicted = y[i: i + 4, 1].tolist()
            scores = [np.exp(2.0 * x) for x in predicted]
            scores = [1.0 * x / sum(scores) for x in scores]
            assert(len(scores) == 4)
            assert(np.allclose(sum(scores), 1.0))
            rez = rez + scores

        if SHOW_PER_SYSTEM_STATS:
            show_per_system_stats(test_data)

        assert(isinstance(rez, list))
        return rez

    def get_4way_accuracy(self, test_data, test_labels, model,
                          weights_file=None):
        assert(model is not None)
        assert(isinstance(weights_file, str) and weights_file is not None)

        model.load_weights(weights_file, by_name=True)

        num_tests = test_labels.shape[0]
        y = model.predict(test_data)
        assert(y.shape[0] == num_tests)
        assert(num_tests % 4 == 0)

        correct = 0
        total = 0
        for i in range(0, num_tests, 4):
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
        return 100.0 * correct / total

    def find_best(self, test_data, val_data):
        assert(isinstance(test_data, list))
        assert(isinstance(val_data, list))

        test_data = self.augment_data(test_data)

        if DEBUG:
            print_data_stats(test_data, "Binary accuracy")

        tokenizer = tokenizers.SpacyTokenizer()
        tokenizer.fit_on_texts(all_sentences(test_data))
        if DEBUG:
            print("Num words: {}\n".format(len(tokenizer.word_counts())))

        test_data, test_labels = self.preprocess_data(test_data,
                                                      tokenizer,
                                                      "Binary acc",
                                                      oversample=False)

        embeddings_matrix = Cerebro.build_embeddings_matrix(tokenizer)
        num_words = len(tokenizer.word_counts())
        assert(embeddings_matrix.shape[0] == num_words + 1)

        model = self.define_model(embeddings_matrix, scope="test")
        model.summary()

        models = []
        for f in os.listdir(MODELS_DIR):
            if not f.endswith(".hdf5"):
                continue
            weights_file = os.path.join(MODELS_DIR, f)

            try:
                model.load_weights(weights_file, by_name=True)

                num_tests = test_labels.shape[0]
                y = model.predict(test_data)
                assert(y.shape[0] == num_tests)
                assert(num_tests % 4 == 0)

                correct = 0
                total = 0
                for i in range(0, num_tests, 4):
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
                acc = 100.0 * correct / total
                print("Model: {}, acc: {}".format(weights_file, acc))
                models.append((acc, weights_file))
            except Exception as e:
                print(str(e))

        val_data = self.augment_data(val_data)

        tokenizer = tokenizers.SpacyTokenizer()
        tokenizer.fit_on_texts(all_sentences(val_data))

        val_data, val_labels = self.preprocess_data(val_data,
                                                    tokenizer,
                                                    "Binary acc",
                                                    oversample=False)

        embeddings_matrix = Cerebro.build_embeddings_matrix(tokenizer)
        num_words = len(tokenizer.word_counts())
        assert(embeddings_matrix.shape[0] == num_words + 1)

        models = sorted(models, key=lambda x: x[0], reverse=True)
        for acc, weights_file in models:
            val_acc = self.get_4way_accuracy(val_data, val_labels,
                                             model, weights_file)
            print(weights_file, acc, val_acc)

    # Prints questions that are answered incorrectly by the information
    # retrieval, but correctly using the combined model.
    def print_diff(self, data, weights_file=None):
        assert(isinstance(data, list))
        assert(isinstance(weights_file, str) or weights_file is None)

        data = self.augment_data(data)

        if DEBUG:
            print_data_stats(data, "Print Diff")

        tokenizer = tokenizers.SpacyTokenizer()
        tokenizer.fit_on_texts(all_sentences(data))
        if DEBUG:
            print("Num words: {}\n".format(len(tokenizer.word_counts())))

        test_data, test_labels = self.preprocess_data(data,
                                                      tokenizer,
                                                      "Print Diff",
                                                      oversample=False)

        embeddings_matrix = Cerebro.build_embeddings_matrix(tokenizer)
        num_words = len(tokenizer.word_counts())
        assert(embeddings_matrix.shape[0] == num_words + 1)

        model = self.define_model(embeddings_matrix, scope="test")
        if weights_file is None:
            weights_file = pick_best_model_from_dir()
            if DEBUG:
                print("Best model detected: {}".format(weights_file))
        model.load_weights(weights_file, by_name=True)
        model.summary()

        num_tests = test_labels.shape[0]
        y = model.predict(test_data)
        assert(y.shape[0] == num_tests)
        assert(num_tests % 4 == 0)

        for i in range(0, num_tests, 4):
            expected = test_labels[i: i + 4, 1]
            assert(np.allclose(np.sum(expected), 1.0))
            expected = np.argmax(expected)

            predicted = y[i: i + 4, 1]
            predicted = np.argmax(predicted)

            if predicted == expected:
                entry = data[int(i / 4)]
                question_text = entry["question"]
                tf_idf_scores = [x['tfIdfScore'] for x in entry["answers"]]
                assert(len(tf_idf_scores) == 4)
                assert(abs(sum(tf_idf_scores) - 1.0) <= 0.001)

                if np.argmax(tf_idf_scores) != predicted:
                    print(question_text)
