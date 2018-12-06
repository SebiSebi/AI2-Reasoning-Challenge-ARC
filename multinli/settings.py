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
            "multinli"
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


TRAIN_DATA_PATH = os.path.join("data", "multinli_1.0_dev_train.jsonl")
VALIDATE_DATA_PATH = os.path.join("data", "multinli_1.0_dev_matched.jsonl")
TEST_DATA_PATH = os.path.join("data", "multinli_1.0_dev_mismatched.jsonl")

PREMISE_LEN = 90
HYPOTHESIS_LEN = 35

WORD_EMBEDDINGS_PATH = os.path.join("data", "glove.840B.300d.txt")
WORD_EMBEDDINGS_DIM = 300
WE_DB = "glove_840B_300d"

# Requires at MySQL 5.0.3 or later.
MYSQL_USER = "root"
MYSQL_PASSWORD = "iepurila123"

USE_MULTINLI_CACHE = True

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
