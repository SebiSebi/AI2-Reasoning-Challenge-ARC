package data.translators;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.ParseException;
import java.util.Scanner;

import org.json.JSONArray;
import org.json.JSONObject;

import com.google.protobuf.TextFormat;

import data.QuestionsProtos.Answer;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.QuestionDataSet;

/**
 * ARC data sets are formatted in JSON lines.
 */
final class ARC {
	
	private static final boolean DEBUG = true;
	
	private static String normAnswer(String ans) {
		ans = ans.trim();
		if (ans.equals("1"))
			return "A";
		if (ans.equals("2"))
			return "B";
		if (ans.equals("3"))
			return "C";
		if (ans.equals("4"))
			return "D";
		return ans;
	}
	
	/* Fills:
	 * 		1) question text;
	 * 		2) question ID;
	 * 		3) answer text;
	 * 		4) if it is correct or not.
	 * Does not fill: answer context, essentialness data.
	 */
	public static void JSONlToProtoBuf(String input_file_path, String output_file_path) throws ParseException, IOException {
		if (DEBUG) {
			System.out.println("[ARC] Converting from JSONL to Protocol Buffer... \n");
		}
		
		Scanner input = new Scanner(new File(input_file_path));
		
		int num_lines = 0;
		QuestionDataSet.Builder data_set_builder = QuestionDataSet.newBuilder();
		data_set_builder.setDescription("ARC-Easy Feb2018 Challange")
						.setPurpose(QuestionDataSet.Purpose.TRAIN);
		
		while (input.hasNextLine()) {
			String line = input.nextLine();
			JSONObject obj = new JSONObject(line);
			JSONArray choices = obj.getJSONObject("question").getJSONArray("choices");
			if (choices.length() != 4) {
				System.out.println("[ARC] Skipping question with more/less than 4 answers!");
				continue;
			}
			
			String id = obj.getString("id").trim();
			String question = obj.getJSONObject("question").getString("stem");
			String correctAnswer = normAnswer(obj.getString("answerKey").trim());
			
			if (!correctAnswer.matches("A|B|C|D")) {
				input.close();
				throw new ParseException("[ARC] Invalid correct answer!", 0);
			}
			
			String answerA = choices.getJSONObject(0).getString("text").trim();
			String answerB = choices.getJSONObject(1).getString("text").trim();
			String answerC = choices.getJSONObject(2).getString("text").trim();
			String answerD = choices.getJSONObject(3).getString("text").trim();
			
			String labelA = normAnswer(choices.getJSONObject(0).getString("label").trim());
			String labelB = normAnswer(choices.getJSONObject(1).getString("label").trim());
			String labelC = normAnswer(choices.getJSONObject(2).getString("label").trim());
			String labelD = normAnswer(choices.getJSONObject(3).getString("label").trim());
			
			
			if (!labelA.equals("A") || !labelB.equals("B") || !labelC.equals("C") || !labelD.equals("D")) {
				input.close();
				throw new ParseException("[ARC] Invalid label!", 0);
			}
			
			data_set_builder.addEntries(Question.newBuilder()
					.setQuestion(question)
					.setId(id)
					.addAnswers(Answer.newBuilder()
									.setText(answerA)
									.setIsCorrect(correctAnswer.equals("A"))
									.build())
					.addAnswers(Answer.newBuilder()
									.setText(answerB)
									.setIsCorrect(correctAnswer.equals("B"))
									.build())
					.addAnswers(Answer.newBuilder()
									.setText(answerC)
									.setIsCorrect(correctAnswer.equals("C"))
									.build())
					.addAnswers(Answer.newBuilder()
									.setText(answerD)
									.setIsCorrect(correctAnswer.equals("D"))
									.build())
					.build());
			num_lines++;
		}
		
		QuestionDataSet data_set = data_set_builder.build();
		String output = TextFormat.printToString(data_set);
		
		// Write ratings in text format to file.
		BufferedWriter out = new BufferedWriter(new FileWriter(output_file_path));
		
		out.write(output);
		out.newLine();
		out.flush();
		out.close();
		
		if (DEBUG) {
			System.out.println("[ARC] Output size: " + (output.length() + 1) + " bytes.");
			System.out.println("[ARC] Processed " + num_lines + " questions.");
		}
		
		input.close();
	}
	
	public static void main(String[] args) throws ParseException, IOException {
		JSONlToProtoBuf(
				"resources/questions/ARC-V1-Feb2018-2/ARC-Challenge/ARC-Challenge-Test.jsonl",
				"resources/questions/ARC-V1-Feb2018-2/ARC-Challenge/ARC-Challenge-Test.prototext"
		);
	}
	
}
