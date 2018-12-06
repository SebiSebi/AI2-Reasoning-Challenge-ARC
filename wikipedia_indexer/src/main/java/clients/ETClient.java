package clients;

import clients.ETServiceProtos.ETScoresCompressedResponse;
import clients.ETServiceProtos.ETScoresRequest;
import clients.ETServiceProtos.ETScoresResponse;

import java.util.Iterator;
import java.util.concurrent.TimeUnit;

import clients.ETServiceGrpc.ETServiceBlockingStub;
import data.QuestionsProtos.Answer;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.QuestionDataSet;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import com.google.protobuf.TextFormat;
import utils.Text;
import utils.compress.GZip;
import utils.Compiler;

/**
 * Interacts with the server for terms essentialness.
 */
public final class ETClient {
	
	private static final Integer ET_SERVER_PORT = 11111;
	
	public static ETScoresResponse getETScores(QuestionDataSet data_set) {
		Compiler.compileProtos();
		
		ETScoresRequest.Builder req_builder = ETScoresRequest.newBuilder();
		for (Question q: data_set.getEntriesList()) {
			ETScoresRequest.Entry.Builder entry = ETScoresRequest.Entry.newBuilder();
			entry.setQuestion(q.getQuestion());
			for (Answer answer: q.getAnswersList())
				entry.addAnswers(answer.getText());
			if (q.getTermsCount() >= 1) {
				entry.addAllTerms(q.getTermsList());
			}
			else {
				// Split question in words and add them to term list.
				entry.addAllTerms(Text.splitInWords(q.getQuestion()));
			}
			req_builder.addEntries(entry.build());
		}
		return getETScores(req_builder.build());
	}
	
	public static ETScoresResponse getETScores(ETScoresRequest req) {
		System.out.println("Sending request to ET server.");
		
		ETScoresResponse resp = null;
		ManagedChannel channel = null;
		try {
			@SuppressWarnings("deprecation")
			ManagedChannelBuilder<?> channelBuilder = ManagedChannelBuilder.forAddress("localhost", ET_SERVER_PORT).usePlaintext(true);
			channel = channelBuilder.build();
			ETServiceBlockingStub stub = ETServiceGrpc.newBlockingStub(channel);
			Iterator<ETScoresCompressedResponse> compressed_resp = stub.withCompression("gzip").getEssentialnessScores(req);
			StringBuilder decompressed_data = new StringBuilder();
			while (compressed_resp.hasNext()) {
				decompressed_data.append(GZip.decompress(compressed_resp.next().getData().toByteArray()));
			}
			try {
				ETScoresResponse.Builder resp_builder = ETScoresResponse.newBuilder();
				TextFormat.merge(decompressed_data.toString(), resp_builder);
				resp = resp_builder.build();
			} catch (com.google.protobuf.TextFormat.ParseException e) {
				System.err.println("Cannot parse ETServer response (wrong format): " + e.toString());
				resp = null;
			}
		} catch (Exception e) {
			e.printStackTrace();
		} finally {
			if (channel != null) {
				try {
					channel.shutdown().awaitTermination(600, TimeUnit.SECONDS);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
		}
		
		if (resp == null)
			return null;

		System.out.println("ET Server response received. Checking data ...");
		
		if (!resp.getExitCode().toLowerCase().equals("ok")) {
			System.err.println("Non-zero exit code => " + resp.getExitCode());
			return null;
		}
		
		if (req.getEntriesCount() != resp.getEntriesCount()) {
			return null;
		}
		
		for (int i = 0; i < req.getEntriesCount(); i++) {
			ETScoresRequest.Entry req_entry = req.getEntries(i);
			ETScoresResponse.Entry resp_entry = resp.getEntries(i);
			
			if (!req_entry.getQuestion().equals(resp_entry.getQuestion())) {
				return null;
			}
			
			if (!req_entry.getAnswersList().equals(resp_entry.getAnswersList())) {
				return null;
			}
			
			for (String term: req_entry.getTermsList()) {
				if (!resp_entry.getScoresMap().containsKey(term)) {
					return null;
				}
			}
		}
		
		System.out.println("Response OK. Proceeding ... ");
		
		return resp;
	}
}
