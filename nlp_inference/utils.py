import json
import os

from random import shuffle
from nlp_inference.settings import DEBUG, MODELS_DIR
from nlp_inference.texts import num_words


# Reads data in the original SNLI format (JSON lines).
def read_data_as_json(file_path):
    if DEBUG:
        print("[NLPI] Reading data from {}".format(file_path))
    data = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            data.append(json.loads(line))

    # Validate data.
    for entry in data:
        assert('sentence1' in entry)
        assert('sentence2' in entry)
        assert('gold_label' in entry)
        assert(entry['gold_label'] in ['contradiction', 'neutral',
                                       'entailment', '-'])
    shuffle(data)
    assert(isinstance(data, list))
    return data


def print_data_stats(data, title=""):
    print("")
    print("******************* {} *************************".format(title))
    print("Num entries: {}".format(len(data)))
    print("Contradictions: {}".format(
        sum(1 for x in data if x['gold_label'] == 'contradiction')))
    print("Entailments: {}".format(
        sum(1 for x in data if x['gold_label'] == 'entailment')))
    print("Neutral: {}".format(
        sum(1 for x in data if x['gold_label'] == 'neutral')))
    print("Non labeled: {}".format(
        sum(1 for x in data if x['gold_label'] == '-')))
    print("Averange num words in sentence 1: {}".format(
        sum(num_words(x['sentence1']) for x in data) * 1.0 / len(data)))
    print("Averange num words in sentence 2: {}".format(
        sum(num_words(x['sentence2']) for x in data) * 1.0 / len(data)))

    print("******************** END *************************")
    print("", flush=True)


def pretty_print(json_obj):
    print(json.dumps(json_obj, indent=4, sort_keys=True))


def remove_unlabeled_data(data):
    new_data = []
    cnt_removed = 0
    for entry in data:
        if entry['gold_label'] in ['contradiction', 'neutral', 'entailment']:
            new_data.append(entry)
        else:
            cnt_removed += 1
    if DEBUG:
        print("[NLPI] Removed {0:.2f}% unlabeled entries.\n".format(
                                100.0 * cnt_removed / len(data)))
    return new_data


# Returns a list of all sentences.
def all_sentences(data):
    sentences = []
    for entry in data:
        sentences.append(entry['sentence1'])
        sentences.append(entry['sentence2'])
    assert(len(sentences) == 2 * len(data))
    return sentences


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
