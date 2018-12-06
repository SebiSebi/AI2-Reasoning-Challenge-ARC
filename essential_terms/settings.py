import os


DEBUG = True
GLOBAL_DATA_DIR = os.path.join("/", "home", "sebisebi", "data")

FULL_DATASET_PATH = os.path.join("data", "essential_terms_dataset2.tsv")

TRAIN_DATA_PATH = os.path.join("data", "essential_terms_train.json")
VALIDATION_DATA_PATH = os.path.join("data", "essential_terms_val.json")
TEST_DATA_PATH = os.path.join("data", "essential_terms_test.json")

QUESTION_LEN = 60
ANSWER_LEN = 15
TERM_LEN = 3
NUM_CLASSES = 6

# Requires at MySQL 5.0.3 or later.
MYSQL_USER = "root"
MYSQL_PASSWORD = "iepurila123"

WORD_EMBEDDINGS_PATH = os.path.join(GLOBAL_DATA_DIR, "GloVe",
                                    "glove.6B.50d.txt")
WORD_EMBEDDINGS_DIM = 50
WE_DB = "glove_6B_50d"

SCIENCE_TERMS_LIST_PATH = os.path.join("data", "science_terms_list.txt")
CONCRETNESS_RATINGS_PATH = os.path.join("data", "concretness_ratings.json")
POS_EMBEDDINGS_PATH = os.path.join("data", "pos_embeddings.bin")
POS_EMBEDDINGS_DIM = 5
DEP_EMBEDDINGS_PATH = os.path.join("data", "dep_embeddings.bin")
DEP_EMBEDDINGS_DIM = 9

PMI_DB = "pmi_data"

POLY_FEATURES = 4
SMART_STOP_LIST_PATH = os.path.join("data", "SmartStopList.txt")
NER_LIST_PATH = os.path.join("data", "NER_to_ID.json")
NER_COUNT = 21  # Number of named entities used in the engine.

'''
CREATE DATABASE pmi_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE TABLE unigrams (word varchar(50), logp DECIMAL(30,15) NOT NULL,
                       PRIMARY KEY (word)) ENGINE=MyISAM
                       CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
'''
