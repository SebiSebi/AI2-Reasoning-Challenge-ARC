import json
import numpy as np
import os
import random
import string

from copy import deepcopy
from settings import DEBUG
from sklearn.feature_extraction.text import TfidfVectorizer


def _text_similarity(text1, text2):
    vect = TfidfVectorizer(stop_words='english')
    try:
        tfidf = vect.fit_transform([text1, text2])
    except:
        return 1.0
    return ((tfidf * tfidf.T).A)[0, 1]


# For stats only. Not to be used as a real model tokenizer.
def _tokenize(sentence):
    aux = sentence
    for x in list(string.punctuation):
        aux = aux.replace(x, ' ')
    # Hack to remove multiple consecutive spaces.
    return [x.strip() for x in ' '.join(aux.split()).strip().split(' ')]


def _num_words(sentence):
    return len(_tokenize(sentence))


def _pretty_print(json_obj):
    return json.dumps(json_obj, indent=4, sort_keys=True)


def _parse_question_to_array(question):
    out = []
    for ans in ["(A)", "(B)", "(C)", "(D)"]:
        idx = question.find(ans)
        assert(idx != -1)
        assert(question[idx] == '(')
        out.append(question[0:idx])
        question = question[idx + 3:]
        assert(ans not in question)
    out.append(question)
    return out


def _parse_terms_to_dict(terms):
    terms = terms.split('|')
    terms = list(map(lambda x: x.strip(string.whitespace), terms))
    out = {}
    for term in terms:
        assert(',' in term)
        idx = term.rfind(',')
        assert(idx != -1)
        val = int(term[idx + 1:])
        word = term[0: idx]
        extra_words = []  # E.g. 35%
        assert(val >= 0 and val <= 5)

        # Remove special characters from end and from beginning.
        for x in "?.,_*!'\"<>=:;":
            word = word.strip(x)

        # Strip words of the form (word).
        while len(word) >= 2 and word[0] == '(' and word[-1] == ')':
            word = word[1:-1]

        # Remove special characters from end and from beginning.
        for x in "?.,_*!'\":;<>=":
            word = word.strip(x)

        if len(word) == 0:
            continue

        if word == "a(n)" or word == "a(an)":
            word = "a"
        elif word[-3:] == "(s)":  # E.g. organism(s)
            word = word[0:-3]
        elif len(word) >= 1 and word[-1] == '%':  # E.g. 35%.
            extra_words.append("percent")
            word = word[:-1]
            int(word)  # Assertion.
        elif word[-2:] == "°C":
            extra_words.append("degrees")
            extra_words.append("celsius")
            word = word[:-2]
        elif word[-2:] == "°F":
            extra_words.append("degrees")
            extra_words.append("fahrenheit")
            word = word[:-2]
        elif word[-1:] == "°":
            extra_words.append("degrees")
            word = word[:-1]

        # Remove special characters from end and from beginning.
        for x in "?.,_*!'\"><();:":
            word = word.strip(x)

        assert(len(word) >= 1 or len(extra_words) >= 1)
        words = [word] + extra_words
        for word in words:
            if word in out:
                out[word] = int((out[word] + val) / 2)
            else:
                out[word] = val

    for word in out:
        assert(out[word] >= 0 and out[word] <= 5)

    return out


def read_as_array(input_path):
    if DEBUG:
        print("Reading tsv file at {}".format(input_path))
    data = []
    skipped = 0
    total = 0
    processed = 0
    no_anwers = 0
    with open(input_path, "r") as f:
        for l in f:
            total += 1
            line = l.strip(string.whitespace).split('\t')
            line = list(map(lambda x: x.strip(string.whitespace), line))
            assert(len(line) == 3)
            question = str(line[0])
            num_annotators = int(line[1])
            terms = str(line[2])
            assert(num_annotators <= 5)
            if num_annotators != 5:
                if DEBUG:
                    print("Skipping question with less than 5 annotators.")
                skipped += 1
                continue
            assert(num_annotators == 5)

            # Parse question. Format Q (A) ... (B) ... (C) ... (D) ...
            parsed_question = None
            if "(A)" in question:
                assert(question.count("(A)") == 1)
                assert(question.count("(B)") == 1)
                assert(question.count("(C)") == 1)
                assert(question.count("(D)") == 1)
                assert(question.count("(E)") == 0)
                parsed_question = _parse_question_to_array(question)
            else:
                # There are questions without answers.
                no_anwers += 1
                assert(question.count("(A)") == 0)
                assert(question.count("(B)") == 0)
                assert(question.count("(C)") == 0)
                assert(question.count("(D)") == 0)
                assert(question.count("(E)") == 0)
                parsed_question = [question, "", "", "", ""]
            parsed_question = list(map(lambda x: x.strip(string.whitespace),
                                       parsed_question))
            assert(len(parsed_question) == 5)
            assert(parsed_question[0] in question)
            assert(parsed_question[1] in question)
            assert(parsed_question[2] in question)
            assert(parsed_question[3] in question)
            assert(parsed_question[4] in question)

            # Parse terms.
            terms = _parse_terms_to_dict(terms)

            data.append({
                'question': parsed_question[0],
                'answers': parsed_question[1:],
                'terms': terms
            })

            processed += 1
    random.shuffle(data)
    validate_input_data(data)

    if DEBUG:
        assert(processed + skipped == total)
        assert(len(data) == processed)
        print("Successfully loaded data from {}".format(input_path))
        print("Skipped questions: {} ({}%)".format(
                    skipped, round(100.0 * skipped / max(total, 1), 2)))
        print("Total questions: {}".format(total))
        print("Processed questions: {} ({}%)".format(
                    processed, round(100.0 * processed / max(total, 1), 2)))
        print("No answer questions: {}".format(no_anwers))
        print("")

    return data


def read_data_from_json(input_path):
    if DEBUG:
        print("Reading data from {}".format(input_path))
    data = None
    with open(input_path, "r") as f:
        data = json.loads(f.read())
    validate_input_data(data)
    return data


def validate_input_data(data):
    assert(data is not None)
    assert(isinstance(data, list))
    for entry in data:
        assert('question' in entry)
        assert('answers' in entry)
        assert('terms' in entry)
        assert(isinstance(entry['question'], str))
        assert(isinstance(entry['answers'], list))
        assert(len(entry['answers']) == 4)
        assert(isinstance(entry['terms'], dict))


def print_data_stats(data, title=""):
    print("")
    print("\n******************* {} *************************".format(title))
    print("Num questions: {}".format(len(data)))
    print("Average num words in question: {0:.2f}".format(
        sum(_num_words(x['question']) for x in data) * 1.0 / len(data)))
    print("Average num words in answer: {0:.2f}".format((
        sum(_num_words(x['answers'][0]) for x in data) +
        sum(_num_words(x['answers'][1]) for x in data) +
        sum(_num_words(x['answers'][2]) for x in data) +
        sum(_num_words(x['answers'][3]) for x in data)) / (4.0 * len(data))))

    print("Num terms: {}".format(sum(len(x['terms']) for x in data)))

    samples = [0, 0, 0, 0, 0, 0]
    for entry in data:
        assert('terms' in entry)
        terms = entry['terms']
        for word in terms:
            samples[terms[word]] += 1

    # Count question duplicates.
    q_set = set()
    for entry in data:
        q_set.add(entry["question"])
    print("Duplicates: {}".format(len(data) - len(q_set)))

    print("Term value count: {}".format(samples))
    print("******************** END *************************\n")


def undersample_dataset(data, prob):
    for entry in data:
        new_terms = {}
        terms = entry["terms"]
        for term in terms:
            if terms[term] == 0 and random.uniform(0, 1) <= prob:
                continue
            new_terms[term] = terms[term]
        entry["terms"] = deepcopy(new_terms)
    return data


# Oversample class with label 0 and 1.
def oversample_dataset(data, labels, cnt):
    if DEBUG:
        print("Oversampling 0 and 1 classes ...", flush=True)

    assert(isinstance(cnt, list))
    assert(isinstance(data, dict))
    for key in data:
        assert(isinstance(data[key], np.ndarray))
    assert(isinstance(labels, np.ndarray))
    assert(len(labels.shape) == 2)

    num_classes = labels.shape[1]
    assert(num_classes == 6)

    for cls in range(0, 2):
        for key in data:
            assert(data[key].shape[0] == labels.shape[0])

        num_entries = labels.shape[0]
        cls_idx = []  # Indexes with the current label.
        for i in range(0, num_entries):
            if labels[i][cls] >= 0.9:
                cls_idx.append(i)
        if len(cls_idx) == 0:  # No elements in this class.
            continue
        idx = 0
        freq = 0
        while freq < cnt[cls]:
            elem = cls_idx[idx]
            assert(labels[elem][cls] >= 0.95)

            for key in data:
                data[key] = np.append(data[key], [data[key][elem]], axis=0)
            labels = np.append(labels, [labels[elem]], axis=0)

            idx = (idx + 1) % len(cls_idx)
            freq += 1

    assert(len(labels.shape) == 2)
    for key in data:
        assert(isinstance(data[key], np.ndarray))
        assert(data[key].shape[0] == labels.shape[0])

    return data, labels


# Makes the frequency of each two labels to be equal. Oversampling only.
def equalize(data, labels):
    if DEBUG:
        print("Equalizing training data ...", flush=True)

    assert(isinstance(data, dict))
    for key in data:
        assert(isinstance(data[key], np.ndarray))
    assert(isinstance(labels, np.ndarray))
    assert(len(labels.shape) == 2)

    num_classes = labels.shape[1]
    assert(num_classes == 6)

    freqs = np.sum(labels, axis=0)
    assert(len(freqs.shape) == 1)
    assert(freqs.shape[0] == num_classes)
    max_freq = int(np.max(freqs))

    for cls in range(0, num_classes):
        for key in data:
            assert(data[key].shape[0] == labels.shape[0])

        # Make freq equal to @max_freq.
        freq = freqs[cls]
        num_entries = labels.shape[0]
        cls_idx = []  # Indexes with the current label.
        for i in range(0, num_entries):
            if labels[i][cls] >= 0.9:
                cls_idx.append(i)
        if len(cls_idx) == 0:  # No elements in this class.
            continue
        idx = 0
        while freq < max_freq:
            elem = cls_idx[idx]
            assert(labels[elem][cls] >= 0.95)

            for key in data:
                data[key] = np.append(data[key], [data[key][elem]], axis=0)
            labels = np.append(labels, [labels[elem]], axis=0)

            idx = (idx + 1) % len(cls_idx)
            freq += 1

    assert(len(labels.shape) == 2)
    for key in data:
        assert(isinstance(data[key], np.ndarray))
        assert(data[key].shape[0] == labels.shape[0])
    freqs = np.sum(labels, axis=0)
    assert(freqs.shape[0] == num_classes)
    for i in range(0, num_classes):
        assert(np.allclose(freqs[i], max_freq))

    return data, labels


def dataset_similarity(data_set1, data_set2, threshold=0.9):
    q1 = set()
    for entry in data_set1:
        q1.add(entry["question"])
    q2 = set()
    for entry in data_set2:
        q2.add(entry["question"])
    similar = 0
    processed = 0
    for q in q1:
        max_sim = None
        for x in q2:
            sim = _text_similarity(q, x)
            if max_sim is None or sim > max_sim:
                max_sim = sim
            if max_sim >= threshold:
                break
        if max_sim >= threshold:
            similar += 1
        processed += 1
        if processed % 35 == 1 and DEBUG:
            print("Processed {} / {}.".format(processed, len(q1)))

    if len(q1) == 0:
        return 0.0
    return 100.0 * similar / len(q1)


def all_sentences(data):
    out = []
    for entry in data:
        out.append(entry["question"])
        for answer in entry["answers"]:
            out.append(answer)
        for term in entry["terms"]:
            out.append(term)
    return out


def pick_best_model_from_dir():
    best_acc = -1.0
    best_model = None
    for f in os.listdir("models/"):
        if not f.endswith(".hdf5"):
            continue
        # Pattern: model.0.653-013.hdf5
        assert(f.startswith("model."))
        acc = float(f[6:11])
        epoch = int(f[12:15])
        assert(epoch >= 1)
        assert(acc >= 0.0 and acc <= 1.0)
        if acc > best_acc:
            best_acc = acc
            best_model = os.path.join("models", f)
    return best_model


def _split_data(input_path, train_out, val_out, test_out,
                validation_split=0.1, test_split=0.1):
    data = read_as_array(input_path)
    assert(data is not None)

    if DEBUG:
        print("Splitting data at {} ...".format(input_path))

    total = len(data)
    num_val = int(len(data) * validation_split)
    num_test = int(len(data) * test_split)
    num_train = total - num_val - num_test
    assert(num_val + num_test < total)
    assert(num_train + num_val + num_test == total)

    train = data[0:num_train]
    val = data[num_train:num_train + num_val]
    test = data[num_train + num_val:]
    assert(len(train) == num_train)
    assert(len(val) == num_val)
    assert(len(test) == num_test)

    with open(train_out, "w") as g:
        g.write(_pretty_print(train))
        g.flush()

    with open(val_out, "w") as g:
        g.write(_pretty_print(val))
        g.flush()

    with open(test_out, "w") as g:
        g.write(_pretty_print(test))
        g.flush()

    if DEBUG:
        print("Train data at {}, size {}.".format(train_out, num_train))
        print("Validation data at {}, size {}.".format(val_out, num_val))
        print("Test data at {}, size {}.".format(test_out, num_test))


if __name__ == "__main__":
    from settings import FULL_DATASET_PATH, TRAIN_DATA_PATH
    from settings import VALIDATION_DATA_PATH, TEST_DATA_PATH

    if False:
        data = read_as_array(FULL_DATASET_PATH)
        print_data_stats(data)
    if False:
        _split_data(FULL_DATASET_PATH,
                    TRAIN_DATA_PATH,
                    VALIDATION_DATA_PATH,
                    TEST_DATA_PATH,
                    validation_split=0.08,
                    test_split=0.13)
