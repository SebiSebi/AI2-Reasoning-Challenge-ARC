import os


DEBUG = True
SHOW_PER_SYSTEM_STATS = True
NUM_CLASSES = 2

# This is the root path of the project.
ROOT_DIR = os.path.abspath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            ".."
))

# This is the current directory (absolute path).
BASE_DIR = os.path.abspath(os.path.join(
            ROOT_DIR,
            "answer"
))

# The local data (e.g answers/data) - absolute path.
DATA_DIR = os.path.abspath(os.path.join(
            BASE_DIR,
            "data"
))

MODELS_DIR = os.path.abspath(os.path.join(
            BASE_DIR,
            "models"
))

# **************************************************************
# *                     Datasets paths here.                   *
# **************************************************************

KAGGLE_ALL_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "KaggleAllenAI",
            "kaggle_allen_ai_with_context.json"
)
KAGGLE_TRAIN_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "KaggleAllenAI",
            "kaggle_allen_ai_train.json"
)
KAGGLE_VAL_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "KaggleAllenAI",
            "kaggle_allen_ai_val.json"
)
KAGGLE_TEST_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "KaggleAllenAI",
            "kaggle_allen_ai_test.json"
)
KAGGLE_CONTEST_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "KaggleAllenAI",
            "kaggle_allen_ai_contest.json"
)

ARC_EASY_TRAIN_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "ARC",
            "Easy",
            "ARC-Easy-Train.json"
)

ARC_EASY_VAL_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "ARC",
            "Easy",
            "ARC-Easy-Dev.json"
)

ARC_EASY_TEST_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "ARC",
            "Easy",
            "ARC-Easy-Test.json"
)

ARC_CHALLENGE_TRAIN_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "ARC",
            "Challenge",
            "ARC-Challenge-Train.json"
)

ARC_CHALLENGE_VAL_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "ARC",
            "Challenge",
            "ARC-Challenge-Dev.json"
)

ARC_CHALLENGE_TEST_PATH = os.path.join(
            DATA_DIR,
            "questions",
            "ARC",
            "Challenge",
            "ARC-Challenge-Test.json"
)

TRAIN_PATH = [
        ARC_EASY_TRAIN_PATH,
]

VAL_PATH = [
        ARC_EASY_VAL_PATH
]

TEST_PATH = [
        ARC_EASY_TEST_PATH
]

# **************************************************************
# *                        END datasets                        *
# **************************************************************

QUESTION_LEN = 35

WORD_EMBEDDINGS_PATH = os.path.join(DATA_DIR, "glove.6B.50d.txt")
WORD_EMBEDDINGS_DIM = 50
WE_DB = "glove_6B_50d"

# Requires at MySQL 5.0.3 or later.
MYSQL_USER = "root"
MYSQL_PASSWORD = "iepurila123"

ENTITY_LIST_PATH = os.path.join(DATA_DIR, "entities.json")
