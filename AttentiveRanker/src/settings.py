import os


# This is the current directory (absolute path).
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODELS_DIR = os.path.abspath(os.path.join(BASE_DIR, "models"))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "data"))

EASY_TRAIN_DATA_PATH = os.path.join(DATA_DIR, "easy_train.json")
EASY_VAL_DATA_PATH = os.path.join(DATA_DIR, "easy_validation.json")
EASY_TEST_DATA_PATH = os.path.join(DATA_DIR, "easy_test.json")

CHALLENGE_TRAIN_DATA_PATH = os.path.join(DATA_DIR, "challenge_train.json")
CHALLENGE_VAL_DATA_PATH = os.path.join(DATA_DIR, "challenge_validation.json")
CHALLENGE_TEST_DATA_PATH = os.path.join(DATA_DIR, "challenge_test.json")

TRAIN_DATA_PATH = EASY_TRAIN_DATA_PATH
VAL_DATA_PATH = EASY_VAL_DATA_PATH
TEST_DATA_PATH = EASY_TEST_DATA_PATH


NUM_SOURCES = 2  # Book collection and ARC_Corpus
TOP_N = 20  # From each source, first TOP_N entries will be kept.
NUM_FEATURES = 4  # (position, TF-IDF, BERT, BinaryAnswer - correct or not)
