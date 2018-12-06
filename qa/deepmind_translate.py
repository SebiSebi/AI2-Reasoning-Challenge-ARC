import os
import random
import re

from copy import deepcopy
from qa.utils import pretty_print


def _is_correct(answer, correct_answers):
    for correct_answer in correct_answers:
        if correct_answer is None:
            continue
        if answer == correct_answer:
            return True
        if answer in correct_answer or correct_answer in answer:
            return True
    return False


# @param all_answers: a list of all answers from the same paragraph.
# @param correct_answers: a list of correct answers for a question.
def _fetch_wrong_answer(all_answers, correct_answers):
    for i in range(0, 25):
        answer = random.choice(all_answers)
        if not _is_correct(answer, correct_answers):
            return answer
    return None


def _fetch_wrong_answers(all_answers, correct_answers):
    assert(isinstance(all_answers, list))
    assert(isinstance(correct_answers, list))
    assert(len(correct_answers) <= len(all_answers))
    assert(len(correct_answers) == 1)

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
def _check_if_answers_are_valid(answers, correct_answers, context, question):
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
        else:
            assert(answer["text"] not in correct_answers)
        assert(answer["text"] in context or answer["text"] in question)
        assert(answer["context"] == context)


def _process_file(input_file_path):
    entity_regex = re.compile("^@entity[0-9]+$")
    not_found_entities = 0
    total_num_entities = 0
    with open(input_file_path, "r") as f:
        lines = []
        for line in f:
            lines.append(line.rstrip())
        story_url = lines[0]
        assert(len(lines[1]) == 0)
        story = lines[2]
        assert(len(lines[3]) == 0)
        question = lines[4]
        assert(len(lines[5]) == 0)
        answer = lines[6]
        assert(len(lines[7]) == 0)
        entities = {}
        for line in lines[8:]:
            assert(line.startswith("@entity"))
            idx = line.find(":")
            name = line[0:idx]
            real_name = line[idx + 1:]
            assert(entity_regex.fullmatch(name))
            if not (name in story or name in question or name in answer):
                not_found_entities += 1
            total_num_entities += 1
            entities[name] = real_name
        assert(len(entities) >= 1)
        if total_num_entities >= 13:
            assert(not_found_entities <= total_num_entities * 0.2)

        assert("http://web.archive.org/" in story_url)
        assert("@entity" in answer)
        assert(len(answer.split()) == 1)
        assert(answer in entities)
        assert(entity_regex.fullmatch(answer))

        # Remove entities from story, question, answer.
        for entity in sorted(list(entities.keys()), key=len, reverse=True):
            story = story.replace(entity, entities[entity])
            question = question.replace(entity, entities[entity])
        answer = entities[answer]
        assert("@entity" not in story)
        assert("@entity" not in question)
        assert("@entity" not in answer)

        # Deal with @placeholder in question.
        assert("@placeholder" in question)
        assert(question.count("@placeholder") == 1)
        question = question.replace("@placeholder", "@ placeholder")
        assert(question.count("@ placeholder") == 1)

        # story, question, answer
        # print(question, " | ", answer)
        entities = list(entities.values())
        assert(answer in entities)
        entities = list(filter(lambda x: x in story, entities))

        a2, a3, a4 = _fetch_wrong_answers(entities, [answer])
        if a2 is None or a3 is None or a4 is None:
            return None
        a1 = answer

        a1 = _build_answer(a1, story, True)
        a2 = _build_answer(a2, story, False)
        a3 = _build_answer(a3, story, False)
        a4 = _build_answer(a4, story, False)

        x = [a1, a2, a3, a4]
        random.shuffle(x)
        _check_if_answers_are_valid(x, [answer], story, question)

        return deepcopy({
            "question": question,
            "answers": x,
        })

    assert(False)


def deepmind_translate(input_path, output_path, purpose):
    assert(purpose in ["TRAIN", "VALIDATION", "TEST"])
    res = {}
    res["description"] = "DeepMind QA"
    res["purpose"] = purpose
    res["entries"] = []

    files = [os.path.join(input_path, f) for f in os.listdir(input_path)]
    files = [f for f in files if os.path.isfile(f)]
    idx = 0
    skipped = 0
    processed_questions = 0
    for input_file in files:
        if processed_questions % 1000 == 1:
            print("[DeepMind_T] Processed {} out of {} questions.".format(
                        processed_questions,
                        len(files)))
        processed_questions += 1

        entry = _process_file(input_file)
        if entry is None:
            skipped += 1
            continue
        assert("id" not in entry)
        idx += 1
        entry["id"] = purpose + "_" + str(idx)
        res["entries"].append(entry)

    assert(processed_questions == len(files))
    assert(skipped + len(res["entries"]) == processed_questions)

    print("[DeepMind_T] Total questions: {}".format(processed_questions))
    print("[DeepMind_T] Skipped: {}".format(skipped))
    print("[DeepMind_T] Output questions: {}".format(len(res["entries"])))

    with open(output_path, "w") as g:
        g.write(pretty_print(res))
        g.flush()
