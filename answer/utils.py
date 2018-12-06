import json
import numpy as np
import os
import random

from answer.settings import DEBUG, MODELS_DIR
from answer.texts import num_words


# The input of this function must be a path which points to a
# protocol buffer file (JSONed): QuestionDataSet from questions.proto
# The file is first built by a Java preprocessor function (e.g ContextFetcher)
# which appends the context and TF-IDF scores (these two are mandatory).
# Various python modules are responsible for adding extra
# information (like QA scores).
# The output of this function is an array of entries (one entry per question).
# This function does *not* shuffle the input data at all.
def read_dataset(input_file_path, return_parent_json=False):
    if DEBUG:
        print("Reading input data from {}".format(input_file_path))
    json_obj = None
    with open(input_file_path, 'r') as f:
        json_obj = json.load(f)

    # Basic input validation.
    if json_obj is None:
        raise RuntimeError("Failed to parse JSON: {}".format(input_file_path))
    if 'description' not in json_obj or 'entries' not in json_obj:
        raise ValueError("Missing arguments in question dataset.")
    assert(json_obj['purpose'] in ['UNKNOWN', 'TRAIN', 'VALIDATION', 'TEST'])

    if DEBUG:
        print("Working with {} dataset.".format(json_obj['description']))

    data = json_obj["entries"]  # A list of questions.

    # Apply softmax to each TF-IDF 4-tuple scores (each question).
    # Softmax with e^(Nx) instead of e^(x).
    for entry in data:
        answers = entry['answers']
        scores = [x['tfIdfScore'] for x in answers]
        scores = [np.exp(2.0 * x) for x in scores]
        scores = [1.0 * x / sum(scores) for x in scores]
        assert(len(scores) == 4)
        assert(np.allclose(sum(scores), 1.0))
        for i in range(0, 4):
            answers[i]['tfIdfScore'] = scores[i]

    # Fully validate input data.
    ids = set()
    for entry in data:
        assert('question' in entry)
        assert('id' in entry)
        assert('answers' in entry)

        answers = entry['answers']
        assert(len(answers) == 4)
        assert(np.allclose(sum([x['tfIdfScore'] for x in answers]), 1.0))

        correct = 0
        for answer in answers:
            assert('text' in answer)
            assert('isCorrect' in answer)
            assert(isinstance(answer['isCorrect'], bool))
            assert('context' in answer)
            assert('tfIdfScore' in answer)
            if answer['isCorrect']:
                correct += 1
        # assert(correct == 1)
        assert(entry['id'] not in ids)
        ids.add(entry['id'])
    assert(len(ids) == len(data))

    if DEBUG:
        print("Successfully parsed {} questions from {}\n".format(
                            len(data), input_file_path), flush=True)

    assert(isinstance(data, list))
    assert(isinstance(json_obj, dict))
    if return_parent_json:
        return json_obj
    return data


def pretty_print(json_obj):
    return json.dumps(json_obj, indent=4, sort_keys=True)


def split_data(json_obj, train_file, val_file, test_file,
               validation_split=0.1, test_split=0.1):
    train_obj = {}
    val_obj = {}
    test_obj = {}
    data = json_obj["entries"]
    random.shuffle(data)

    # Check proto at wikipedia_indexer/resources/questions.proto
    train_obj['description'] = json_obj['description']
    train_obj['purpose'] = 'TRAIN'
    train_obj['entries'] = []

    val_obj['description'] = json_obj['description']
    val_obj['purpose'] = 'VALIDATION'
    val_obj['entries'] = []

    test_obj['description'] = json_obj['description']
    test_obj['purpose'] = 'TEST'
    test_obj['entries'] = []

    assert(validation_split >= 0 and test_split >= 0)
    assert(validation_split + test_split < 1.0)
    total = len(data)
    num_val = int(total * validation_split)
    num_test = int(total * test_split)
    num_train = total - num_val - num_test
    assert(num_train >= 1)

    if DEBUG:
        print("Total question: {}".format(total))
        print("Train questions: {}".format(num_train))
        print("Validation questions: {}".format(num_val))
        print("Test questions: {}".format(num_test))

    with open(train_file, 'w') as g:
        train_obj['entries'] = data[0:num_train]
        assert(len(train_obj['entries']) == num_train)
        g.write(pretty_print(train_obj))
        g.flush()

    with open(val_file, 'w') as g:
        val_obj['entries'] = data[num_train:num_train + num_val]
        assert(len(val_obj['entries']) == num_val)
        g.write(pretty_print(val_obj))
        g.flush()

    with open(test_file, 'w') as g:
        test_obj['entries'] = data[num_train + num_val:]
        assert(len(test_obj['entries']) == num_test)
        g.write(pretty_print(test_obj))
        g.flush()

    # Validate split.
    assert(len(train_obj['entries']) == num_train)
    assert(len(val_obj['entries']) == num_val)
    assert(len(test_obj['entries']) == num_test)

    train_ids = set()
    val_ids = set()
    test_ids = set()
    for entry in train_obj['entries']:
        train_ids.add(entry['id'])
    for entry in val_obj['entries']:
        val_ids.add(entry['id'])
    for entry in test_obj['entries']:
        test_ids.add(entry['id'])
    assert(len(train_ids) == num_train)
    assert(len(val_ids) == num_val)
    assert(len(test_ids) == num_test)
    assert(len(train_ids & val_ids) == 0)
    assert(len(train_ids & test_ids) == 0)
    assert(len(val_ids & test_ids) == 0)

    print_data_stats(train_obj['entries'], "Train")
    print_data_stats(val_obj['entries'], "Val")
    print_data_stats(test_obj['entries'], "Test")

    if DEBUG:
        print("Finished splitting data.\n")


def print_data_stats(data, title=""):
    print("")
    print("******************* {} *************************".format(title))
    print("Num questions: {}".format(len(data)))
    print("Correct answer distribution:")
    print("\t A -> {} ".format(
        sum(1 for x in data if x['answers'][0]['isCorrect'] is True)))
    print("\t B -> {} ".format(
        sum(1 for x in data if x['answers'][1]['isCorrect'] is True)))
    print("\t C -> {} ".format(
        sum(1 for x in data if x['answers'][2]['isCorrect'] is True)))
    print("\t D -> {} ".format(
        sum(1 for x in data if x['answers'][3]['isCorrect'] is True)))

    if len(data) >= 1:
        m = 1.0 * max(len(data), 1)

        print("\nAverage question length: {0:.2f} words.".format(
              sum(num_words(x['question']) for x in data) * 1.0 / m))
        print("Average answer length: {0:.2f} words.".format((
                sum(num_words(x['answers'][0]['text']) for x in data) +
                sum(num_words(x['answers'][1]['text']) for x in data) +
                sum(num_words(x['answers'][2]['text']) for x in data) +
                sum(num_words(x['answers'][3]['text']) for x in data)
              ) * 1.0 / (4.0 * m)))
        print("Average context length: {0:.2f} words.".format((
                sum(num_words(x['answers'][0]['context']) for x in data) +
                sum(num_words(x['answers'][1]['context']) for x in data) +
                sum(num_words(x['answers'][2]['context']) for x in data) +
                sum(num_words(x['answers'][3]['context']) for x in data)
             ) * 1.0 / (4.0 * m)))

        print("\nMaximum question length: {} words.".format(
                max(num_words(x['question']) for x in data)))
        print("Maximum answer length: {} words.".format(max(
                max(num_words(x['answers'][0]['text']) for x in data),
                max(num_words(x['answers'][1]['text']) for x in data),
                max(num_words(x['answers'][2]['text']) for x in data),
                max(num_words(x['answers'][3]['text']) for x in data))))
        print("Maximum context length: {} words.".format(max(
                max(num_words(x['answers'][0]['context']) for x in data),
                max(num_words(x['answers'][1]['context']) for x in data),
                max(num_words(x['answers'][2]['context']) for x in data),
                max(num_words(x['answers'][3]['context']) for x in data))))

    correct = 0
    for entry in data:
        scores = []
        for answer in entry['answers']:
            scores.append(answer['tfIdfScore'])
        predicted = np.argmax(scores)
        assert(predicted in [0, 1, 2, 3])
        if entry['answers'][predicted]['isCorrect'] is True:
            correct += 1

    print("TF-IDF only accuracy: {0:.2f}%".format(
                        100.0 * correct / max(1, len(data))))

    print("******************** END *************************")
    print("")


def pick_best_model_from_dir():
    best_acc = -1.0
    best_model = None
    for f in os.listdir(MODELS_DIR):
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
            best_model = os.path.join(MODELS_DIR, f)
    return best_model


# Returns a list of all questions (only these should be used) to let
# the neural network learn question features (e.g. length).
def all_sentences(data):
    sentences = []
    for entry in data:
        sentences.append(entry['question'])
    assert(len(sentences) == len(data))
    assert(None not in sentences)
    return sentences


def show_per_system_stats(data):
    print("\nPer system stats:\n")
    out = {
        'tf_idf_score_input': 'Information retrieval',
        'qa_score_input': 'Plain question answering',
        'scitail_score_input': 'SciTail inference',
        'snli_score_input': 'SNLI inference',
        'multinli_score_input': 'MultiNLI inference',
    }

    for key in data:
        if key not in out:
            continue
        scores = data[key][0:4]
        if key != 'tf_idf_score_input':
            scores = [x[0] for x in scores]
        else:
            scores = [x for x in scores]
        print('\tComponent   {} predicted: {}'.format(
                    out[key].ljust(27),
                    scores
        ))
    print("\n")


if __name__ == "__main__":
    pass
    '''
    from answer.settings import KAGGLE_ALL_PATH
    from answer.settings import KAGGLE_TRAIN_PATH
    from answer.settings import KAGGLE_VAL_PATH, KAGGLE_TEST_PATH
    json_obj = read_dataset(KAGGLE_ALL_PATH, True)
    print_data_stats(json_obj['entries'], "All")
    split_data(json_obj,
               KAGGLE_TRAIN_PATH,
               KAGGLE_VAL_PATH,
               KAGGLE_TEST_PATH,
               validation_split=0.1,
               test_split=0.1)
    '''
