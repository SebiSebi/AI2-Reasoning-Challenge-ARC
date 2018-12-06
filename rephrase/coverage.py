import include_sys_path
import json
import rephrase.texts as texts
import tqdm
import rephrase.start_with_be as start_with_be

from rephrase.utils import get_question_type, QType

include_sys_path.void()


def read_data_as_json(file_path):
    json_obj = None
    with open(file_path, 'r') as f:
        json_obj = json.load(f)
    if json_obj is None:
        raise RuntimeError("Failed to parse JSON at {}".format(file_path))
    if 'description' not in json_obj or 'entries' not in json_obj:
        raise ValueError("Missing arguments in question dataset.")
    assert(json_obj['purpose'] in ['UNKNOWN', 'TRAIN', 'VALIDATION', 'TEST'])
    data = json_obj["entries"]

    # Validate data.
    questions = []
    for entry in data:
        questions.append(entry['question'])

    return questions


def get_stats(mapper):
    q = read_data_as_json("data/10_train-v1.1_with_context.json")
    known = {}
    unknown = {}
    tr = tqdm.tqdm(q)
    for question in tr:
        sents = texts.split_in_sentences(question)
        assert(len(sents) >= 1)
        question = sents[-1]
        qtype = get_question_type(question)
        if len(question) < 2:
            continue

        opt = mapper(question)
        if qtype == QType.UNKNOWN:
            unknown[opt] = unknown.get(opt, 0) + 1
        else:
            known[opt] = known.get(opt, 0) + 1

    known = sorted(known.items(), key=lambda x: x[1], reverse=True)
    unknown = sorted(unknown.items(), key=lambda x: x[1], reverse=True)
    print("Known: ")
    for construct, cnt in known[:30]:
        print("\t", construct, ': ', cnt)

    print("")

    print("Unknown: ")
    for construct, cnt in unknown[:30]:
        print("\t", construct, ': ', cnt)


def get_stats_2d():
    get_stats(lambda x: (x[0].lemma_, x[1].lemma_))


def get_stats_1d():
    get_stats(lambda x: (x[0].lemma_,))


def get_stats_POS():
    get_stats(lambda x: (x[0].pos_))


def coverage():
    q = read_data_as_json("data/10_train-v1.1_with_context.json")
    known = 0
    total = 0
    tr = tqdm.tqdm(q, desc='Coverage')
    for question in tr:
        sents = texts.split_in_sentences(question)
        assert(len(sents) >= 1)
        question = sents[-1]
        qtype = get_question_type(question)
        if not qtype == QType.UNKNOWN:
            known += 1
        total += 1

        if total % 10 == 0:
            tr.set_description("Coverage: {0:.3f}%".format(
                                        100.0 * known / total))
            tr.refresh()


def iterate():
    q = read_data_as_json("data/10_train-v1.1_with_context.json")
    for question in q:
        sents = texts.split_in_sentences(question)
        assert(len(sents) >= 1)
        question = sents[-1]
        qtype = get_question_type(question)
        if qtype == QType.START_WITH_BE:
            start_with_be.process(question)


if __name__ == "__main__":
    iterate()
