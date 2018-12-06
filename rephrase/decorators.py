import hashlib
import os
import pickle

from rephrase.settings import USE_QTS_CACHE, CACHING_DIR


def with_caching(func):

    def wrapper(*args, **kwargs):
        h = None
        res = None
        if USE_QTS_CACHE:
            vals = str(args) + str(kwargs)
            h = hashlib.sha256(vals.encode('utf-8')).hexdigest()
            assert(isinstance(h, str))

            # Search for entry in cached files.
            file_path = os.path.join(CACHING_DIR, h + ".bin")
            if os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    res = pickle.loads(f.read())

        is_new = False
        if res is None:
            res = func(*args, **kwargs)
            is_new = True

        if USE_QTS_CACHE and is_new:
            # Save res in cache using h.
            file_path = os.path.join(CACHING_DIR, h + ".bin")
            with open(file_path, "wb") as g:
                g.write(pickle.dumps(res))
                g.flush()

        return res

    return wrapper
