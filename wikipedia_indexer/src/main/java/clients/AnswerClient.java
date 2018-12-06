package clients;

import java.util.List;
import java.util.concurrent.TimeUnit;

import com.google.protobuf.InvalidProtocolBufferException;
import com.google.protobuf.util.JsonFormat;

import clients.AnswerServiceGrpc.AnswerServiceBlockingStub;
import clients.AnswerServiceProtos.AnswerRequest;
import clients.AnswerServiceProtos.AnswerResponse;
import data.QuestionsProtos.QuestionDataSet;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import utils.Compiler;

public final class AnswerClient {
	private static final Integer SERVER_PORT = 22222;
	
	public static List<Double> predict(QuestionDataSet dataset) {
		Compiler.compileProtos();
		System.out.println("Sending request to Cerebro server.");
		
		String json = null;
		try {
			json = JsonFormat.printer().print(dataset);
		} catch (InvalidProtocolBufferException e) {
			e.printStackTrace();
		}
		if (json == null) {
			return null;
		}
		
		AnswerRequest req = AnswerRequest.newBuilder().setJsonQuestionDataset(json).build();
		AnswerResponse resp = null;
		ManagedChannel channel = null;
		try {
			@SuppressWarnings("deprecation")
			ManagedChannelBuilder<?> channelBuilder = ManagedChannelBuilder.forAddress("localhost", SERVER_PORT).usePlaintext(true);
			channel = channelBuilder.build();
			AnswerServiceBlockingStub stub = AnswerServiceGrpc.newBlockingStub(channel);
			resp = stub.withCompression("gzip").answer(req);
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (channel != null) {
				try {
					channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
		}
		
		if (resp == null) {
			return null;
		}
		
		return resp.getScoresList();
	}
}
