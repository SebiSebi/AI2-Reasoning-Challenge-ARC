import include_sys_path  # This must be the first imported module.

import answer.answer_service_pb2_grpc as answer_service_pb2_grpc
import grpc
import json
import logging
import numpy as np
import signal
import time

from answer.answer_service_pb2 import AnswerResponse
from concurrent import futures

include_sys_path.void()

server = None
should_stop = False


class AnswerServicer(answer_service_pb2_grpc.AnswerServiceServicer):
    def __init__(self):
        pass

    def Answer(self, req, context):
        json_string = req.json_question_dataset

        scores = None
        try:
            data = json.loads(json_string)["entries"]

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

            print("[Anwer] Processing {} questions.".format(len(data)),
                  flush=True)

            from answer.models import Cerebro
            model = Cerebro()
            scores = model.predict_batch(data)
            print("[Answer] Cerebro prediction completed.", flush=True)
        except Exception as e:
            msg = "Prediction failed: " + str(e) + " @" + str(type(e))
            return AnswerResponse(exit_code=msg)

        if scores is None:
            msg = "Prediction failed: scores is None!"
            return AnswerResponse(exit_code=msg)

        resp = AnswerResponse()
        resp.scores.extend(scores)
        resp.exit_code = "OK"
        return resp


def _stop(sig, frame):
    global server
    global should_stop

    print("[Answer] Stopped caused by signal {}".format(sig), flush=True)
    logging.info("[Answer] Stopped caused by signal {}".format(sig))
    if server is not None:
        server.stop(0)
        server = None
    should_stop = True


def _serve(port):
    global server
    global should_stop

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    answer_service_pb2_grpc.add_AnswerServiceServicer_to_server(
        AnswerServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    server.start()
    print("[Answer] Listening on port {} ... ".format(port), flush=True)
    logging.info("[Answer] Listening on port {} ... ".format(port))

    try:
        while not should_stop:
            time.sleep(0.35)  # sleep for 1 second.
        if server is not None:
            server.stop(0)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    logging.basicConfig(filename='answer_server.log', level=logging.DEBUG)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    _serve(22222)
