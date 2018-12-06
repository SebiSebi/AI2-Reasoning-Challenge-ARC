.PHONY: all clean

FILES = ../wikipedia_indexer/src/main/java/clients/ETServiceProtos.java ../essential_terms/essential_terms_service_pb2.py ../wikipedia_indexer/src/main/java/clients/AnswerServiceProtos.java ../wikipedia_indexer/src/main/java/clients/AnswerServiceGrpc.java ../wikipedia_indexer/src/main/java/clients/ETServiceGrpc.java ../answer/answer_service_pb2.py ../answer/answer_service_pb2_grpc.py ../essential_terms/essential_terms_service_pb2_grpc.py

all: $(FILES)

../wikipedia_indexer/src/main/java/clients/ETServiceProtos.java: essential_terms_service.proto
	protoc --plugin=protoc-gen-grpc-java=/home/sebisebi/Anul4/Licenta/protoc-gen-grpc-java-1.11.0-linux-x86_64.exe -I=. --java_out=../wikipedia_indexer/src/main/java --grpc-java_out=../wikipedia_indexer/src/main/java  $^

../wikipedia_indexer/src/main/java/clients/ETServiceGrpc.java: essential_terms_service.proto
	protoc --plugin=protoc-gen-grpc-java=/home/sebisebi/Anul4/Licenta/protoc-gen-grpc-java-1.11.0-linux-x86_64.exe -I=. --java_out=../wikipedia_indexer/src/main/java --grpc-java_out=../wikipedia_indexer/src/main/java  $^

../essential_terms/essential_terms_service_pb2.py: essential_terms_service.proto
	python -m grpc_tools.protoc -I. --python_out=../essential_terms --grpc_python_out=../essential_terms $^

../essential_terms/essential_terms_service_pb2_grpc.py: essential_terms_service.proto
	python -m grpc_tools.protoc -I. --python_out=../essential_terms --grpc_python_out=../essential_terms $^

../answer/answer_service_pb2.py: answer_service.proto
	python -m grpc_tools.protoc -I. --python_out=../answer --grpc_python_out=../answer $^

../answer/answer_service_pb2_grpc.py: answer_service.proto
	python -m grpc_tools.protoc -I. --python_out=../answer --grpc_python_out=../answer $^

../wikipedia_indexer/src/main/java/clients/AnswerServiceProtos.java: answer_service.proto
	protoc --plugin=protoc-gen-grpc-java=/home/sebisebi/Anul4/Licenta/protoc-gen-grpc-java-1.11.0-linux-x86_64.exe -I=. --java_out=../wikipedia_indexer/src/main/java --grpc-java_out=../wikipedia_indexer/src/main/java  $^

../wikipedia_indexer/src/main/java/clients/AnswerServiceGrpc.java: answer_service.proto
	protoc --plugin=protoc-gen-grpc-java=/home/sebisebi/Anul4/Licenta/protoc-gen-grpc-java-1.11.0-linux-x86_64.exe -I=. --java_out=../wikipedia_indexer/src/main/java --grpc-java_out=../wikipedia_indexer/src/main/java  $^


clean:
	rm $(FILES) 
