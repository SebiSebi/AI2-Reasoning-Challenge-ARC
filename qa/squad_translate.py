import json
import numpy as np
import random

from copy import deepcopy
from qa.settings import ENGLISH_WORDS_LIST_PATH
from qa.utils import pretty_print, text_similaritiy


def _get_all_answers(qas):
    assert(isinstance(qas, list))
    all_answers = []
    for question in qas:
        assert(isinstance(question, dict))
        answers = question["answers"]
        assert(answers is not None)
        assert(isinstance(answers, list))

        answers = [x["text"] for x in answers]
        answers = list(set(answers))
        all_answers += answers
    return list(set(all_answers))


def _is_correct(answer, correct_answers):
    for correct_answer in correct_answers:
        if correct_answer is None:
            continue
        sim = text_similaritiy(answer, correct_answer)
        if sim >= 0.10:
            return True
    return False


# @param all_answers: a list of all answers from the same paragraph.
# @param correct_answers: a list of correct answers for a question.
def _fetch_wrong_answer(all_answers, correct_answers):
    for i in range(0, 12):
        answer = random.choice(all_answers)
        if not _is_correct(answer, correct_answers):
            return answer
    return None


# @param all_answers: a list of all answers from the same paragraph.
# @param correct_answers: a list of correct answers for a question.
def _fetch_wrong_answers(all_answers, correct_answers):
    assert(isinstance(all_answers, list))
    assert(isinstance(correct_answers, list))
    assert(len(correct_answers) <= len(all_answers))

    a1 = None
    a2 = None
    a3 = None
    a1 = _fetch_wrong_answer(all_answers, correct_answers)
    a2 = _fetch_wrong_answer(all_answers, correct_answers + [a1])
    a3 = _fetch_wrong_answer(all_answers, correct_answers + [a1, a2])
    return a1, a2, a3


def _build_answer(a, context, isCorrect):
    x = {}
    x["text"] = a
    x["context"] = context
    x["isCorrect"] = isCorrect
    return deepcopy(x)


# @param answers: a list of answer dict (with question, text, isCorrect).
# @param correct_answers: a list of correct answers for the question.
# @param context: the context of the questiond
# @param random_answers: a set of answers that have been chosen at random.
def _check_if_answers_are_valid(answers, correct_answers, context,
                                random_answers):
    assert(isinstance(answers, list))
    assert(isinstance(correct_answers, list))
    assert(isinstance(context, str))

    assert(len(answers) == 4)
    for answer in answers:
        assert(isinstance(answer["text"], str))
        assert(isinstance(answer["context"], str))
        assert(isinstance(answer["isCorrect"], bool))

    assert(sum(1 for x in answers if x["isCorrect"] is True) == 1)
    for answer in answers:
        if answer["isCorrect"]:
            assert(answer["text"] in correct_answers)
            assert(answer["text"] not in random_answers)
        else:
            assert(answer["text"] not in correct_answers)
        if answer["text"] not in random_answers:
            assert(answer["text"] in context)
        else:
            assert(answer["isCorrect"] is False)
        assert(answer["context"] == context)


def _get_num_question(dataset):
    assert(dataset is not None)
    assert(isinstance(dataset, list))
    cnt = 0
    for entry in dataset:
        for paragraph in entry["paragraphs"]:
            cnt += len(paragraph["qas"])
    return cnt


def _build_random_answer(word_list):
    words = []
    l = np.random.randint(1, 6)
    for i in range(0, l):
        words.append(random.choice(word_list))
    answer = ' '.join(words)
    return answer


def squad_translate(input_path, output_path, random_answer_prob=-1):
    data = None
    with open(input_path, "r") as f:
        data = json.loads(f.read())
    print("[SQuAD_T] Working with SQuAD version {}".format(data["version"]))

    # Load the list of valid English words.
    english_words_list = []
    with open(ENGLISH_WORDS_LIST_PATH, "r") as g:
        for line in g:
            english_words_list.append(line.strip())
    print("[SQuAD_T] Loaded {} English words.".format(len(english_words_list)))
    print("", flush=True)

    data = data["data"]
    skipped = 0
    processed_questions = 0
    num_random_answers = 0
    total_question = _get_num_question(data)
    res = {}
    res["description"] = "SQuAD"
    res["purpose"] = "VALIDATION"
    res["entries"] = []
    for entry in data:
        # title = entry["title"]
        paragraphs = entry["paragraphs"]
        for paragraph in paragraphs:
            context = paragraph["context"]
            qas = paragraph["qas"]
            all_answers = _get_all_answers(qas)
            for _x in all_answers:
                assert(_x in context)
            for question in qas:
                processed_questions += 1
                if processed_questions % 100 == 0:
                    print("[SQuAD_T] Processed {} out of {} questions.".format(
                                    processed_questions,
                                    total_question))
                id = question["id"]
                title = question["question"]
                answers = question["answers"]
                answers = [x["text"] for x in answers]
                answers = list(set(answers))

                # Need to fetch three more wrong answers.
                a2, a3, a4 = _fetch_wrong_answers(all_answers, answers)
                if a2 is None or a3 is None or a4 is None:
                    skipped += 1
                    continue
                a1 = random.choice(answers)
                assert(a1 in context)
                assert(a2 in context)
                assert(a3 in context)
                assert(a4 in context)

                # Induce random answers with a given probability.
                random_answers = []
                if np.random.random_sample() <= random_answer_prob:
                    a2 = _build_random_answer(english_words_list)
                    num_random_answers += 1
                    random_answers.append(a2)
                if np.random.random_sample() <= random_answer_prob:
                    a3 = _build_random_answer(english_words_list)
                    num_random_answers += 1
                    random_answers.append(a3)
                if np.random.random_sample() <= random_answer_prob:
                    a4 = _build_random_answer(english_words_list)
                    num_random_answers += 1
                    random_answers.append(a4)

                a1 = _build_answer(a1, context, True)
                a2 = _build_answer(a2, context, False)
                a3 = _build_answer(a3, context, False)
                a4 = _build_answer(a4, context, False)

                x = [a1, a2, a3, a4]
                random.shuffle(x)
                _check_if_answers_are_valid(x, answers, context,
                                            set(random_answers))

                res["entries"].append(deepcopy({
                    "question": title,
                    "answers": x,
                    "id": id
                }))

    print("[SQuAD_T] Total questions: {}".format(processed_questions))
    print("[SQuAD_T] Skipped: {}".format(skipped))
    print("[SQuAD_T] Output questions: {}".format(len(res["entries"])))
    print("[SQuAD_T] Num random answers: {} ({}%)".format(
            num_random_answers,
            round(100.0 * num_random_answers / (4.0 * len(res["entries"])))))
    with open(output_path, "w") as g:
        g.write(pretty_print(res))
        g.flush()
