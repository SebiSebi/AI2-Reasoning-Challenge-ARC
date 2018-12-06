import os


DEBUG = True

# This is the root path of the project.
ROOT_DIR = os.path.abspath(os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            ".."
))

# This is the current directory (absolute path).
BASE_DIR = os.path.abspath(os.path.join(
            ROOT_DIR,
            "qa"
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

CACHING_DIR = os.path.abspath(os.path.join(
            BASE_DIR,
            "cached"
))

# **************************************************************
# *                     Datasets paths here.                   *
# **************************************************************

KaggleAllenAI = os.path.join(DATA_DIR, "questions", "KaggleAllenAI")
ARC_Easy = os.path.join(DATA_DIR, "questions", "ARC", "Easy")
ARC_Challenge = os.path.join(DATA_DIR, "questions", "ARC", "Challenge")
SQUAD = os.path.join(DATA_DIR, "questions", "SQuAD")

TRAIN_DATA_PATH = [
    # os.path.join(ARC_Challenge, "ARC-Challenge-Train.json"),
    os.path.join(ARC_Easy, "ARC-Easy-Train.json"),
    # os.path.join(KaggleAllenAI, "kaggle_allen_ai_train.json")
    # os.path.join(SQUAD, "10_train-v1.1_with_context.json"),
]

VALIDATE_DATA_PATH = [
    # os.path.join(ARC_Easy, "ARC-Easy-Dev.json"),
    # os.path.join(ARC_Easy, "ARC-Easy-Test.json"),
    # os.path.join(KaggleAllenAI, "kaggle_allen_ai_val.json"),
    # os.path.join(KaggleAllenAI, "kaggle_allen_ai_test.json")
    os.path.join(SQUAD, "10_dev-v1.1_with_context.json")
]

TEST_DATA_PATH = [
    # os.path.join(KaggleAllenAI, "with_context_test.json"),
    # os.path.join(ARC_Easy, "ARC-Easy-Test.json"),
    # os.path.join(SQUAD, ""),
]

# **************************************************************
# *                        END datasets                        *
# **************************************************************

QUESTION_LEN = 60
ANSWER_LEN = 30
CONTEXT_LEN = 275
MAX_WORD_LEN = 17

CHAR_EMBEDDINGS_PATH = os.path.join(DATA_DIR, "glove.char.35D.txt")
CHAR_EMBEDDINGS_DIM = 35

WORD_EMBEDDINGS_PATH = os.path.join(DATA_DIR, "glove.6B.50d.txt")
WORD_EMBEDDINGS_DIM = 50
WE_DB = "glove_6B_50d"

# Requires at MySQL 5.0.3 or later.
MYSQL_USER = "root"
MYSQL_PASSWORD = "iepurila123"

ENGLISH_WORDS_LIST_PATH = os.path.join(DATA_DIR, "english_words.txt")
ENTITY_LIST_PATH = os.path.join(DATA_DIR, "entities.json")

USE_QA_CACHE = True

'''
CREATE DATABASE glove_6B_50d CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE TABLE Embeddings (word varchar(250), vector mediumtext NOT NULL,
                         PRIMARY KEY (word)) ENGINE=MyISAM
                         CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
MySQL Embeddings table schema:
+--------+--------------+------+-----+---------+-------+
| Field  | Type         | Null | Key | Default | Extra |
+--------+--------------+------+-----+---------+-------+
| word   | varchar(250) | NO   | PRI | NULL    |       |
| vector | mediumtext   | NO   |     | NULL    |       |
+--------+--------------+------+-----+---------+-------+
'''
