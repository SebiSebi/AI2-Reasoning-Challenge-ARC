import os

USE_QTS_CACHE = True

# This is the root path of the project.
ROOT_DIR = os.path.abspath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            ".."
))

# This is the current directory (absolute path).
BASE_DIR = os.path.abspath(os.path.join(
            ROOT_DIR,
            "rephrase"
))

# The local data (e.g rephrase/data) - absolute path.
DATA_DIR = os.path.abspath(os.path.join(
            BASE_DIR,
            "data"
))

CACHING_DIR = os.path.abspath(os.path.join(
            BASE_DIR,
            "cached"
))

PAST_TENSE_VERB_LIST = os.path.join(DATA_DIR, "verbs_past_tense.txt")
PAST_PARTICIPLE_VERB_LIST = os.path.join(DATA_DIR, "verbs_past_participle.txt")
VERB_LIST = os.path.join(DATA_DIR, "verb_list.txt")
