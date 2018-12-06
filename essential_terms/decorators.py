import gzip

from essential_terms_service_pb2 import ETScoresCompressedResponse
from google.protobuf import text_format


def with_proto_compression(func):

    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        text = text_format.MessageToString(res)

        # Send chunks of max 1MB.
        chunk_size = 1024 * 1024
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i: i + chunk_size])

        for chunk in chunks:
            compressed = ETScoresCompressedResponse()
            compressed.data = gzip.compress(chunk.encode('utf-8'))
            yield compressed

    return wrapper
