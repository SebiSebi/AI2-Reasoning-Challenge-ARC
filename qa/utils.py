import json
import os
import string
import time

from qa.settings import DEBUG, MODELS_DIR
from random import shuffle
from sklearn.feature_extraction.text import TfidfVectorizer


# Warning this shuffles answers order!
def read_data_as_json(file_path, return_parent_json=False):
    if DEBUG:
        print("Reading data from {}".format(file_path))
    json_obj = None
    with open(file_path, 'r') as f:
        json_obj = json.load(f)
    if json_obj is None:
        raise RuntimeError("Failed to parse JSON at {}".format(file_path))
    if 'description' not in json_obj or 'entries' not in json_obj:
        raise ValueError("Missing arguments in question dataset.")
    assert(json_obj['purpose'] in ['UNKNOWN', 'TRAIN', 'VALIDATION', 'TEST'])
    if DEBUG:
        print("Working with {} dataset.".format(json_obj['description']))
    data = json_obj["entries"]

    # Validate data.
    ids = set()
    for entry in data:
        assert('question' in entry)
        assert('id' in entry)
        assert('answers' in entry)
        answers = entry['answers']
        shuffle(answers)
        assert(len(answers) == 4)
        correct = 0
        for answer in answers:
            assert('text' in answer)
            assert('isCorrect' in answer)
            assert('context' in answer)
            assert(isinstance(answer['isCorrect'], bool))
            if answer['isCorrect']:
                correct += 1
        assert(correct == 1)
        assert(entry['id'] not in ids)
        ids.add(entry['id'])

    if DEBUG:
        print("Successfully parsed data at {}\n".format(file_path), flush=True)

    if return_parent_json:
        return data, json_obj
    return data


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

    print("******************** END *************************")
    print("")


def pretty_print(json_obj):
    return json.dumps(json_obj, indent=4, sort_keys=True)


def split_data(json_obj, data, train_file, val_file, test_file,
               validation_split=0.1, test_split=0.1):
    train_obj = {}
    val_obj = {}
    test_obj = {}

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
        g.write(pretty_print(train_obj))
        g.flush()

    with open(val_file, 'w') as g:
        val_obj['entries'] = data[num_train:num_train + num_val]
        g.write(pretty_print(val_obj))
        g.flush()

    with open(test_file, 'w') as g:
        test_obj['entries'] = data[num_train + num_val:]
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

    if DEBUG:
        print("Finished splitting data.\n")


def tokenize(sentence):
    aux = sentence
    for x in list(string.punctuation):
        aux = aux.replace(x, ' ')
    # Hack to remove multiple consecutive spaces.
    return [x.strip() for x in ' '.join(aux.split()).strip().split(' ')]


def num_words(sentence):
    return len(tokenize(sentence))


# Returns a list of all sentences from questions, answers and contexts.
def all_sentences(data):
    sentences = []
    for entry in data:
        sentences.append(entry['question'])
        for answer in entry['answers']:
            sentences.append(answer['text'])
            sentences.append(answer['context'])
    assert(len(sentences) == 9 * len(data))
    assert(None not in sentences)
    return sentences


def lemmatize(data, lemmatizer):
    start = time.time()
    cnt = 0
    for entry in data:
        entry['question'] = lemmatizer.sequence_lemmas(entry['question'])
        for answer in entry['answers']:
            answer['text'] = lemmatizer.sequence_lemmas(answer['text'])
            answer['context'] = lemmatizer.sequence_lemmas(answer['context'])
        cnt += 1
        if cnt % 10 == 0 and DEBUG:
            end = time.time()
            d = end - start
            num = cnt * 9
            print("Lemmatization speed: {0:.2g} sent. / sec".format(num / d))
    return data


def text_similaritiy(text1, text2):
    vect = TfidfVectorizer(stop_words='english')
    try:
        tfidf = vect.fit_transform([text1, text2])
    except Exception as e:
        return 1.0
    return ((tfidf * tfidf.T).A)[0, 1]


def _combine_datasets(paths):
    obj = {}
    obj['description'] = 'All combined'
    obj['purpose'] = 'TRAIN'
    obj['entries'] = []

    data = []
    for path in paths:
        data += read_data_as_json(path, False)
    obj['entries'] = data

    return obj


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


if __name__ == "__main__":
    pass
    '''
    obj = _combine_datasets([
        "data/questions/All/ARC-Challenge-Dev.json",
        "data/questions/All/ARC-Challenge-Train.json",
        "data/questions/All/ARC-Easy-Test.json",
        "data/questions/All/with_context.json",
        "data/questions/All/ARC-Challenge-Test.json",
        "data/questions/All/ARC-Easy-Dev.json",
        "data/questions/All/ARC-Easy-Train.json"
    ])
    with open("data/questions/All/all.json", "w") as g:
        g.write(pretty_print(obj))
        g.flush()
    '''
    '''
    data, json_obj = read_data_as_json("data/questions/All/all.json", True)
    print_data_stats(data)
    split_data(json_obj, data,
               "data/questions/All/all_train.json",
               "data/questions/All/all_val.json",
               "data/questions/All/all.json_test.json",
               validation_split=0.08,
               test_split=0.08)
    '''
