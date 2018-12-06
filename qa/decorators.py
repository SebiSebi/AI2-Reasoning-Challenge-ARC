import hashlib
import os
import pickle

from qa.settings import USE_QA_CACHE, CACHING_DIR


def with_caching(prefix_name):

    def with_caching_decorator(func):

        def wrapper(*args, **kwargs):
            h = None
            res = None
            if USE_QA_CACHE:
                vals = '::!::'.join([str(x) for x in args])
                vals += '+'.join([str(k) + str(v) for k, v in kwargs.items()])
                h = hashlib.sha256(vals.encode('utf-8')).hexdigest()
                assert(isinstance(h, str))

                # Search for entry in cached files.
                file_path = os.path.join(CACHING_DIR, prefix_name, h + ".bin")
                if os.path.isfile(file_path):
                    print("[QA-Cache] Using cached result.")
                    with open(file_path, "rb") as f:
                        res = pickle.loads(f.read())

            is_new = False
            if res is None:
                res = func(*args, **kwargs)
                is_new = True

            if USE_QA_CACHE and is_new:
                # Save res in cache using h.
                file_path = os.path.join(CACHING_DIR, prefix_name, h + ".bin")
                with open(file_path, "wb") as g:
                    g.write(pickle.dumps(res))
                    g.flush()
                print("[QA-Cache] Result has been cached.")

            return res

        return wrapper

    return with_caching_decorator
