import include_sys_path
import hashlib
import numpy as np
import os
import multinli.main as main
import tqdm

from copy import copy
from multinli.decorators import with_caching
from multinli.texts import split_in_sentences
from multinli.utils import pick_best_model_from_dir
from rephrase.question_to_sentence import QTS

include_sys_path.void()


class MultiNLI(object):

    def __init__(self, preselected_model=None):
        # Prepare the model. Load it and wait for predict requests.
        self.weights_file = preselected_model
        if preselected_model is None:
            self.weights_file = pick_best_model_from_dir()
        print("[NLI] MultiNLI using model {}\n".format(self.weights_file))
        assert(isinstance(self.weights_file, str))

    # Raises error in case of failure. Must *not* modify data param.
    @staticmethod
    def validate_request(data):
        assert(isinstance(data, list))

        ids = set()
        for entry in data:
            assert('question' in entry)
            assert('id' in entry)
            assert('answers' in entry)
            answers = entry['answers']
            assert(len(answers) == 4)
            correct = 0
            for answer in answers:
                assert('text' in answer)
                assert('isCorrect' in answer)
                assert('context' in answer)
                assert(isinstance(answer['isCorrect'], bool))
                if answer['isCorrect']:
                    correct += 1
            # assert(correct == 1)
            assert(entry['id'] not in ids)
            ids.add(entry['id'])
        assert(len(ids) == len(data))

    def get_weights_file(self):
        return self.weights_file

    # From question proto (JSON) to NLI models input format.
    @staticmethod
    def transform_input(data):
        req = []
        batch = []
        for entry in tqdm.tqdm(data, desc="[NLI] Transform request"):
            question = QTS.process(entry["question"])
            # In the male, __________ go through meiosis, which occurs
            # in the __________.'
            assert(question.count("@placeholder") >= 1)

            for answer in entry["answers"]:
                context = split_in_sentences(answer['context'])
                # context.append(answer['context'])
                for sent in context:
                    req.append({
                        'sentence1': str(sent),
                        'sentence2': question.replace("@placeholder",
                                                      answer["text"]),
                    })
                batch.append(len(context))
        assert(sum(batch) == len(req))
        assert(len(batch) == 4 * len(data))

        return req, batch

    @with_caching('MultiNLI_predict_batch')
    def predict_batch(self, request):
        # Compute hashes in order to make sure the request has not
        # been modified at all (the order of answers must be the same).
        h = hashlib.sha256(str(request).encode('utf-8')).hexdigest()
        MultiNLI.validate_request(copy(request))

        data, batch_size = MultiNLI.transform_input(request)

        res = main.predict_batch(data, self.weights_file, verbose=True)
        assert(len(res) == sum(batch_size))
        assert(len(res) == len(data))

        scores = []
        idx = 0
        start = 0
        for entry in request:
            local_scores = []
            for _ in range(0, 4):
                local_scores.append(res[start:start + batch_size[idx]])
                start += batch_size[idx]
                idx += 1

            # Reduce scores.
            local_scores = [sorted(x, reverse=True) for x in local_scores]
            local_scores = [(
                    1.0 * sum(x) / max(len(x), 1)) for x in local_scores]

            scores.append(local_scores)
        assert(len(scores) == len(request))
        assert(start == len(res))
        assert(idx == len(batch_size))

        assert(h == hashlib.sha256(str(request).encode('utf-8')).hexdigest())
        res = np.array(scores, dtype=np.float32)
        assert(res.shape == (len(request), 4))

        return res

    def __str__(self):
        return "[ MultiNLI model " + os.path.basename(self.weights_file) + " ]"
