.PHONY: all clean

FILES = ../src/main/java/data/QuestionsProtos.java ../src/main/java/data/ConcretenessRatingsProtos.java

all: $(FILES)

../src/main/java/data/QuestionsProtos.java: ../protos/questions.proto
	protoc -I=../protos --java_out=../src/main/java ../protos/questions.proto

../src/main/java/data/ConcretenessRatingsProtos.java: ../protos/concretness_ratings.proto
	protoc -I=../protos --java_out=../src/main/java ../protos/concretness_ratings.proto

clean:
	rm $(FILES) 
