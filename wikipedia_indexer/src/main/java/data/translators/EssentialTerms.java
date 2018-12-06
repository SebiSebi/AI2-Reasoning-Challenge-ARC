package data.translators;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;

import org.json.JSONArray;
import org.json.JSONObject;

import com.google.protobuf.TextFormat;

import data.QuestionsProtos.Answer;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.QuestionDataSet;

/**
 * Original data set is in TSV format. Python code (see essential_terms)
 * builds a JSON from it (be aware that about 200 questions have been removed
 * from the original data set because they are duplicates).
 */
final class EssentialTerms {
	
	private static final boolean DEBUG = true;
	
	/*
	 * Fills:
	 * 		1) question text;
	 * 		2) question ID;
	 * 		3) answer text (all answers are false);
	 * 		4) Terms without scores.
	 */
	public static void JSONtoProtoBuf(String input_path, String output_path) throws IOException {
		if (DEBUG)
			System.out.println("[ET] Converting from JSON to ProtoBuf format ... ");
		
		Scanner input = new Scanner(new File(input_path));
		
		StringBuilder input_text = new StringBuilder();
		while (input.hasNextLine()) {
			String line = input.nextLine();
			input_text.append(line);
			input_text.append('\n');
		}
		input.close();
		
		QuestionDataSet.Builder data_set_builder = QuestionDataSet.newBuilder();
		data_set_builder.setDescription("Essential Terms (Allen AI)")
						.setPurpose(QuestionDataSet.Purpose.ALL);

		JSONArray data = new JSONArray(input_text.toString());
		int num_questions = 0;
		for (int i = 0; i < data.length(); i++) {
			JSONObject entry = data.getJSONObject(i);
			if (!entry.has("question"))
				throw new IOException("[ET] No 'question' field in entry!");
			if (!entry.has("answers"))
				throw new IOException("[ET] No 'answers' field in entry!");
			if (!entry.has("terms"))
				throw new IOException("[ET] No 'terms' field in entry!");
			
			JSONArray answers = entry.getJSONArray("answers");
			if (answers.length() != 4)
				throw new IOException("[ET] Expected 4 answers!");
			
			String question = entry.getString("question");
			String answerA = answers.getString(0);
			String answerB = answers.getString(1);
			String answerC = answers.getString(2);
			String answerD = answers.getString(3);
			
			ArrayList<String> terms = new ArrayList<String>();
			for (int j = 0; j < entry.getJSONObject("terms").names().length(); j++) {
				terms.add(entry.getJSONObject("terms").names().getString(j));
			}
			
			data_set_builder.addEntries(Question.newBuilder()
					.setQuestion(question)
					.setId("essentials-terms2-#" + num_questions)
					.addAnswers(Answer.newBuilder()
									.setText(answerA)
									.setIsCorrect(false)
									.build())
					.addAnswers(Answer.newBuilder()
									.setText(answerB)
									.setIsCorrect(false)
									.build())
					.addAnswers(Answer.newBuilder()
									.setText(answerC)
									.setIsCorrect(false)
									.build())
					.addAnswers(Answer.newBuilder()
									.setText(answerD)
									.setIsCorrect(false)
									.build())
					.addAllTerms(terms)
					.build());
			num_questions++;
		}
		
		if (num_questions != data.length())
			throw new IOException("[ET] Invalid dataset!");
		
		QuestionDataSet data_set = data_set_builder.build();
		String output = TextFormat.printToString(data_set);
		
		// Write ratings in text format to file.
		BufferedWriter out = new BufferedWriter(new FileWriter(output_path));
		
		out.write(output);
		out.newLine();
		out.flush();
		out.close();
		
		if (DEBUG) {
			System.out.println("\n[ET] Output size: " + (output.length() + 1) + " bytes.");
			System.out.println("[ET] Processed " + num_questions + " questions.");
		}
		
		input.close();
	}
	
	public static void main(String[] args) throws IOException {
		JSONtoProtoBuf(
				"resources/questions/Essential-Terms-Set/essential_terms_dataset2.json",
				"resources/questions/Essential-Terms-Set/essential_terms_dataset2.prototext"
		);
	}
}
