'''
    Exports predict-like functions from QA module.
    This must be the only entry in the QA module (from the outside world).
'''

import hashlib
import os
import qa.two_way as two_way

from copy import copy
from qa.decorators import with_caching
from qa.utils import pick_best_model_from_dir


class QA(object):

    def __init__(self, preselected_model=None):
        # Prepare the model. Load it and wait for predict requests.
        self.weights_file = preselected_model
        if preselected_model is None:
            self.weights_file = pick_best_model_from_dir()
        print("[NLI] QA using model {}\n".format(self.weights_file))
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

    @with_caching('QA_predict_batch')
    def predict_batch(self, request):
        # Compute hashes in order to make sure the request has not
        # been modified at all (the order of answers must be the same).
        h = hashlib.sha256(str(request).encode('utf-8')).hexdigest()
        QA.validate_request(copy(request))

        res = two_way.predict_batch(request, self.weights_file, verbose=True)
        assert(h == hashlib.sha256(str(request).encode('utf-8')).hexdigest())
        assert(res.shape == (len(request), 4))

        return res

    def __str__(self):
        return "[ QA model at " + os.path.basename(self.weights_file) + " ]"
