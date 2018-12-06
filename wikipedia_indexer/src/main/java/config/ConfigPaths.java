package config;

import java.nio.file.Path;
import java.nio.file.Paths;


public final class ConfigPaths {
	final static public Path GLOBAL_DATA_DIR = Paths.get("/", "home", "sebisebi", "data");
	
	final static public Path WIKIPEDIA_ENGLISH_ARTICLE_INDEX_PATH = Paths.get(GLOBAL_DATA_DIR.toString(), "indexes", "wikipedia_english_article_index");

	final static public Path BOOK_INDEX_PATH = Paths.get(GLOBAL_DATA_DIR.toString(), "indexes", "book_index");
	
	final static public Path ARC_INDEX_PATH = Paths.get(GLOBAL_DATA_DIR.toString(), "indexes", "arc_index");
	
	/* All question dataset paths must point to files in protobuf format. */
	final static public Path KAGGLE_ALLEN_AI_TRAIN_DATASET_PATH =  Paths.get("resources", "questions", "KaggleAllenAI", "kaggle_allen_ai_training_set.prototext");
	final static public Path KAGGLE_ALLEN_AI_TEST_DATASET_PATH =  Paths.get("resources", "questions", "KaggleAllenAI", "kaggle_allen_ai_test_set.prototext");
	
	/* ARC Easy */
	final static public Path ARC_EASY_TRAIN_DATASET_PATH = Paths.get("resources", "questions", "ARC-V1-Feb2018-2", "ARC-Easy", "ARC-Easy-Train.prototext");
	final static public Path ARC_EASY_VAL_DATASET_PATH = Paths.get("resources", "questions", "ARC-V1-Feb2018-2", "ARC-Easy", "ARC-Easy-Dev.prototext");
	final static public Path ARC_EASY_TEST_DATASET_PATH = Paths.get("resources", "questions", "ARC-V1-Feb2018-2", "ARC-Easy", "ARC-Easy-Test.prototext");
	
	/* ARC Challenge */
	final static public Path ARC_CHALLENGE_TRAIN_DATASET_PATH = Paths.get("resources", "questions", "ARC-V1-Feb2018-2", "ARC-Challenge", "ARC-Challenge-Train.prototext");
	final static public Path ARC_CHALLENGE_VAL_DATASET_PATH = Paths.get("resources", "questions", "ARC-V1-Feb2018-2", "ARC-Challenge", "ARC-Challenge-Dev.prototext");
	final static public Path ARC_CHALLENGE_TEST_DATASET_PATH = Paths.get("resources", "questions", "ARC-V1-Feb2018-2", "ARC-Challenge", "ARC-Challenge-Test.prototext");
}
