import no_gpu

import essential_terms_service_pb2_grpc
import grpc
import hashlib
import logging
import os
import pickle
import random
import signal
import time

from concurrent import futures
from decorators import with_proto_compression
from essential_terms_service_pb2 import ETScoresResponse

no_gpu.void()  # Unused warning.

server = None
should_stop = False


class ETServicer(essential_terms_service_pb2_grpc.ETServiceServicer):
    def __init__(self):
        pass

    @staticmethod
    def get_message_hash(msg):
        h = msg.SerializeToString()
        h = hashlib.md5(h).hexdigest()
        return h

    @staticmethod
    def cache_response(msg, resp):
        h = ETServicer.get_message_hash(msg)
        file_path = os.path.join("cached_responses", h + ".bin")
        if os.path.isfile(file_path):
            return
        print("[ET] Response has been cached.", flush=True)

        with open(file_path, "wb") as g:
            g.write(pickle.dumps(resp))
            g.flush()

    @staticmethod
    def get_cached_response(msg):
        h = ETServicer.get_message_hash(msg)
        file_path = os.path.join("cached_responses", h + ".bin")
        if not os.path.isfile(file_path):
            return None
        obj = None
        with open(file_path, "rb") as f:
            obj = pickle.loads(f.read())
        return obj

    @with_proto_compression
    def GetEssentialnessScores(self, req, context):
        # Generate data array compatible with the rest of the service.
        data = []
        for entry in req.entries:
            answers = []
            terms = {}
            for answer in entry.answers:
                answers.append(answer)
            for term in entry.terms:
                terms[term] = 0
            if len(answers) != 4:
                return ETScoresResponse(exit_code="Expected 4 answers!")
            data.append({
                'question': entry.question,
                'answers': answers,
                'terms': terms
            })
        print("[ET][GetEssentialnessScores] Processing {} questions.".format(
                len(data)), flush=True)

        scores = None

        # Check if the message is cached.
        cached_resp = ETServicer.get_cached_response(req)
        if cached_resp is not None:
            print("[ET][GetEssentialnessScores] Loaded cached response.")
            scores = cached_resp
        else:
            try:
                from main import predict_batch
                scores = predict_batch(data)
                print("[ET][GetEssentialnessScores] NN prediction completed.",
                      flush=True)
                ETServicer.cache_response(req, scores)
            except Exception as e:
                msg = "Prediction failed: " + str(e) + " @" + str(type(e))
                return ETScoresResponse(exit_code=msg)

        if scores is None:
            msg = "Prediction failed: scores is None!"
            return ETScoresResponse(exit_code=msg)
        if len(scores) != len(data):
            msg = "Prediction failed: invalid scores length!"
            return ETScoresResponse(exit_code=msg)

        resp = ETScoresResponse()
        resp.exit_code = "OK"
        for i in range(0, len(data)):
            entry = resp.entries.add()
            entry.question = data[i]["question"]
            for answer in data[i]["answers"]:
                entry.answers.append(answer)
            for word in scores[i]:
                entry.scores[word] = scores[i][word]
            for word in data[i]["terms"]:
                if word not in entry.scores:
                    resp.exit_code = "Not all scores have been computed!"
        return resp

    @with_proto_compression
    def GetEssentialnessScoresFake(self, req, context):
        # Generate data array compatible with the rest of the service.
        data = []
        for entry in req.entries:
            answers = []
            terms = {}
            for answer in entry.answers:
                answers.append(answer)
            for term in entry.terms:
                terms[term] = 0
            if len(answers) != 4:
                return ETScoresResponse(exit_code="Expected 4 answers!")
            data.append({
                'question': entry.question,
                'answers': answers,
                'terms': terms
            })
        print("[ET][GetEssentialnessScoresFake] Processing {} entries.".format(
                len(data)), flush=True)

        resp = ETScoresResponse()
        resp.exit_code = "OK"
        for i in range(0, len(data)):
            entry = resp.entries.add()
            entry.question = data[i]["question"]
            for answer in data[i]["answers"]:
                entry.answers.append(answer)
            for word in data[i]["terms"]:
                entry.scores[word] = random.uniform(0, 1)
            for word in data[i]["terms"]:
                if word not in entry.scores:
                    resp.exit_code = "Not all scores have been computed!"
        return resp


def _stop(sig, frame):
    global server
    global should_stop

    print("[ET] Stopped caused by signal {}".format(sig), flush=True)
    logging.info("[ET] Stopped caused by signal {}".format(sig))
    if server is not None:
        server.stop(0)
        server = None
    should_stop = True


def _serve(port):
    global server
    global should_stop

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    essential_terms_service_pb2_grpc.add_ETServiceServicer_to_server(
        ETServicer(), server)
    server.add_insecure_port("[::]:{}".format(port))
    server.start()
    print("[ET] Listening on port {} ... ".format(port), flush=True)
    logging.info("[ET] Listening on port {} ... ".format(port))

    try:
        while not should_stop:
            time.sleep(0.35)  # sleep for 1 second.
        if server is not None:
            server.stop(0)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    logging.basicConfig(filename='et_server.log', level=logging.DEBUG)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    _serve(11111)
