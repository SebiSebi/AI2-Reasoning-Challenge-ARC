import itertools
import json
import numpy as np
import uuid

from settings import NUM_SOURCES, NUM_FEATURES


# Returns a list of entries. To be fed into @to_numpy to extract tensors
# that can be directly wired to Keras @fit.
def read_dataset(file_path, top_n, mask_IR=False,
                 mask_Ranking=False, mask_answer_verifier=False):
    assert(isinstance(top_n, int))
    assert(top_n >= 1)

    data = None
    with open(file_path, 'r') as f:
        data = json.load(f)
    assert(data is not None)
    assert(len(data) == 1)
    assert("data" in data)

    def chunks(array, n):
        """Yield successive n-sized chunks from array."""
        for i in range(0, len(array), n):
            yield array[i:i + n]

    def keep_top_n(array):
        assert(isinstance(array, list))
        assert(len(array) >= top_n * NUM_SOURCES)
        assert(len(array) % NUM_SOURCES == 0)
        chunk_size = len(array) // NUM_SOURCES
        array = list(chunks(array, chunk_size))
        assert(len(array) == NUM_SOURCES)
        for chunk_id in range(0, NUM_SOURCES):
            array[chunk_id] = array[chunk_id][:top_n]
        processed_array = []
        for chunk_id in range(0, NUM_SOURCES):
            assert(len(array[chunk_id]) == top_n)
            processed_array += array[chunk_id]
        assert(len(processed_array) == top_n * NUM_SOURCES)
        return processed_array

    data = data["data"]
    assert(isinstance(data, list))
    for entry in data:
        assert(len(entry) == 6)
        assert("question_id" in entry)
        assert("answers" in entry)
        assert("correct_answer" in entry)
        assert("question_text" in entry)
        assert("answers_text" in entry)
        assert("documents" in entry)
        assert(entry["correct_answer"] in [0, 1, 2, 3])
        assert(isinstance(entry["answers"], list))
        assert(len(entry["answers"]) == 4)
        assert(isinstance(entry["documents"], list))
        assert(len(entry["documents"]) == 4)
        assert(isinstance(entry["question_text"], str))
        assert(len(entry["answers_text"]) == 4)
        for answer_text in entry["answers_text"]:
            assert(isinstance(answer_text, str))

        # Keep only TOP_N entries from each source.
        for idx in [0, 1, 2, 3]:
            entry["answers"][idx] = keep_top_n(entry["answers"][idx])
            assert(len(entry["answers"][idx]) == top_n * NUM_SOURCES)
            entry["documents"][idx] = keep_top_n(entry["documents"][idx])
            assert(len(entry["documents"][idx]) == top_n * NUM_SOURCES)

        for answer in entry["answers"]:
            assert(isinstance(answer, list))
            assert(len(answer) == top_n * NUM_SOURCES)
            for local_answer in answer:
                assert(isinstance(local_answer, list))
                assert(len(local_answer) == NUM_FEATURES)
                if mask_IR:
                    local_answer[1] = 0.0
                if mask_Ranking:
                    local_answer[2] = 0.0
                if mask_answer_verifier:
                    local_answer[3] = 0.0
            assert([x[0] for x in answer] == NUM_SOURCES * list(range(1, top_n + 1)))  # noqa: E501

    return data


# Augment the dataset with all answer permutations such that the neural
# network cannot learn how to decide based on positions.
# Returns the newly constructed dataset.
def augment_with_permutations(dataset):
    assert(isinstance(dataset, list))
    augmented = []
    for entry in dataset:
        assert(len(entry) == 6)
        assert("question_id" in entry)
        assert("answers" in entry)
        assert("correct_answer" in entry)
        assert("question_text" in entry)
        assert("answers_text" in entry)
        assert("documents" in entry)
        for answer_text in entry["answers_text"]:
            assert(isinstance(answer_text, str))

        correct_answer = entry["correct_answer"]
        answers = entry["answers"]
        documents = entry["documents"]
        answers_text = entry["answers_text"]
        assert(correct_answer in [0, 1, 2, 3])
        assert(isinstance(answers, list) and len(answers) == 4)
        assert(isinstance(documents, list) and len(documents) == 4)
        for perm in itertools.permutations([0, 1, 2, 3]):
            permuted_answers = [answers[i] for i in perm]
            permuted_answers_text = [answers_text[i] for i in perm]
            permuted_documents = [documents[i] for i in perm]
            permuted_correct_answer = perm.index(correct_answer)
            assert(permuted_correct_answer in [0, 1, 2, 3])
            augmented.append({
                    "question_id": entry["question_id"],
                    "correct_answer": permuted_correct_answer,
                    "answers": permuted_answers,
                    "question_text": entry["question_text"],
                    "documents": permuted_documents,
                    "answers_text": permuted_answers_text
            })
    assert(len(augmented) == 24 * len(dataset))
    for entry in augmented:
        assert(len(entry) == 6)
        assert("question_id" in entry)
        assert("answers" in entry)
        assert("correct_answer" in entry)
        assert("question_text" in entry)
        assert("answers_text" in entry)
        assert("documents" in entry)
        for answer_text in entry["answers_text"]:
            assert(isinstance(answer_text, str))

    return augmented


# Returns a dictionary of entries (for answers) and their labels. To be
# directly wired into Keras methods (fit, predict, etc.).
# Does not shuffle the questions.
def to_numpy(dataset, top_n):
    assert(isinstance(dataset, list))
    assert(isinstance(top_n, int))
    assert(top_n >= 1)

    answer_a = np.zeros((len(dataset), NUM_SOURCES * top_n, NUM_FEATURES),
                        dtype="float")
    answer_b = np.zeros((len(dataset), NUM_SOURCES * top_n, NUM_FEATURES),
                        dtype="float")
    answer_c = np.zeros((len(dataset), NUM_SOURCES * top_n, NUM_FEATURES),
                        dtype="float")
    answer_d = np.zeros((len(dataset), NUM_SOURCES * top_n, NUM_FEATURES),
                        dtype="float")
    labels = np.zeros((len(dataset), 4), dtype="int32")

    def process_answer(answer):
        assert(isinstance(answer, list))
        answer = np.array(answer, dtype="float")
        assert(answer.shape == (NUM_SOURCES * top_n, NUM_FEATURES))
        answer[:, 0] *= (1.0 / top_n)
        return answer

    for (idx, entry) in enumerate(dataset):
        answers = entry["answers"]
        correct_answer = entry["correct_answer"]

        answer_a[idx] = process_answer(answers[0])
        answer_b[idx] = process_answer(answers[1])
        answer_c[idx] = process_answer(answers[2])
        answer_d[idx] = process_answer(answers[3])

        labels[idx][correct_answer] = 1

    assert(isinstance(answer_a, np.ndarray))
    assert(isinstance(answer_b, np.ndarray))
    assert(isinstance(answer_c, np.ndarray))
    assert(isinstance(answer_d, np.ndarray))
    assert(isinstance(labels, np.ndarray))
    return {
            "answer_a": answer_a,
            "answer_b": answer_b,
            "answer_c": answer_c,
            "answer_d": answer_d
    }, labels


# Returns (epoch, val_loss, val_acc) given a saved model's filename.
def parse_model_filename(file_name):
    assert(isinstance(file_name, str))
    prefix_len = len("model-") + len(str(uuid.uuid4())) + 1
    assert(len(file_name) >= prefix_len)
    metrics = file_name[prefix_len:-5]
    assert(len(metrics) == 18)
    metrics = metrics.split('-')
    assert(len(metrics) == 3)
    epoch = int(metrics[0])
    val_loss = float(metrics[1])
    val_acc = float(metrics[2])
    assert(epoch >= 0)
    assert(val_acc >= 0.0 and val_acc <= 1.0)
    assert(val_loss > 0.0)
    return epoch, val_loss, val_acc
