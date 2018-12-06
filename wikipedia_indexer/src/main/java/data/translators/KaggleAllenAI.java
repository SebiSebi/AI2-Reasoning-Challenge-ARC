package data.translators;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.text.ParseException;
import java.util.Scanner;

import com.google.protobuf.TextFormat;

import data.QuestionsProtos.Answer;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.QuestionDataSet;

/**
 * Kaggle Allen AI dataset is in CSV format.
 * Convert between CSV and main Question protobuf.
 */
final class KaggleAllenAI {

	private static final boolean DEBUG = true;

	/* Fills:
	 * 		1) question text;
	 * 		2) question ID;
	 * 		3) answer text;
	 * 		4) if it is correct or not.
	 * Does not fill: answer context, essentialness data.
	 * Requires correct answer column. To be used for training dataset only.
	 * Kaggle test and validation datasets are 6-columns only (use function below this one).
	 */
	public static void csvToProtoBuf(String input_file_path, String output_file_path) throws ParseException, IOException {
		if (DEBUG) {
			System.out.println("[Kaggle] Converting from CSV to Protocol Buffer... \n");
		}
		
		Scanner input = new Scanner(new File(input_file_path));
		
		// Read header line.
		if (!input.hasNextLine()) {
			input.close();
			throw new ParseException("[Kaggle] Header line is missing!", 0);
		}
		
		String[] header = input.nextLine().split("\t");
		if (DEBUG) {
			System.out.println("[Kaggle] Headers: " + String.join(" | ", header) + "\n");
		}
		
		int num_lines = 0;
		QuestionDataSet.Builder data_set_builder = QuestionDataSet.newBuilder();
		data_set_builder.setDescription("Kaggle: The Allen AI Science Challenge")
						.setPurpose(QuestionDataSet.Purpose.TRAIN);
		
		while (input.hasNextLine()) {
			String[] line = input.nextLine().split("\t");
			
			if (line.length != 7) {
				input.close();
				throw new ParseException("[Kaggle] Wrong number of arguments in line!", 0);
			}
			
			String id = line[0].trim();
			String question = line[1].trim();
			String correctAnswer = line[2].trim();
			String answerA = line[3].trim();
			String answerB = line[4].trim();
			String answerC = line[5].trim();
			String answerD = line[6].trim();
			
			if (correctAnswer.length() != 1) {
				input.close();
				throw new ParseException("[Kaggle] Invalid correct answer!", 0);
			}
			
			if (!correctAnswer.matches("A|B|C|D")) {
				input.close();
				throw new ParseException("[Kaggle] Invalid correct answer!", 0);
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
			System.out.println("[Kaggle] Output size: " + (output.length() + 1) + " bytes.");
			System.out.println("[Kaggle] Processed " + num_lines + " questions.");
		}
		
		input.close();
	}
	
	/* Fills:
	 * 		1) question text;
	 * 		2) question ID;
	 * 		3) answer text;
	 * Does not fill: if it is correct or not, answer context, essentialness data.
	 * All answers are considered to be false.
	 * Does not require correct answer column. To be used for test / validation datasets.
	 */
	public static void csvToProtoBufNoCorrectAnswer(String input_file_path, String output_file_path) throws ParseException, IOException {
		if (DEBUG) {
			System.out.println("[Kaggle] Converting from CSV to Protocol Buffer without any correct answer ... \n");
		}
		
		Scanner input = new Scanner(new File(input_file_path));
		
		// Read header line.
		if (!input.hasNextLine()) {
			input.close();
			throw new ParseException("[Kaggle] Header line is missing!", 0);
		}
		
		String[] header = input.nextLine().split("\t");
		if (DEBUG) {
			System.out.println("[Kaggle] Headers: " + String.join(" | ", header) + "\n");
		}
		
		int num_lines = 0;
		QuestionDataSet.Builder data_set_builder = QuestionDataSet.newBuilder();
		data_set_builder.setDescription("Kaggle: The Allen AI Science Challenge")
						.setPurpose(QuestionDataSet.Purpose.TRAIN);
		
		while (input.hasNextLine()) {
			String[] line = input.nextLine().split("\t");
			
			if (line.length != 6) {
				input.close();
				throw new ParseException("[Kaggle] Wrong number of arguments in line!", 0);
			}
			
			String id = line[0].trim();
			String question = line[1].trim();
			String answerA = line[2].trim();
			String answerB = line[3].trim();
			String answerC = line[4].trim();
			String answerD = line[5].trim();
			
			data_set_builder.addEntries(Question.newBuilder()
					.setQuestion(question)
					.setId(id)
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
			System.out.println("[Kaggle] Output size: " + (output.length() + 1) + " bytes.");
			System.out.println("[Kaggle] Processed " + num_lines + " questions.");
		}
		
		input.close();
	}
	
	public static void main(String[] args) throws ParseException, IOException {
		csvToProtoBufNoCorrectAnswer(
				"resources/questions/KaggleAllenAI/kaggle_allen_ai_test_set.tsv",
			   	"resources/questions/KaggleAllenAI/kaggle_allen_ai_test_set.prototext"
	    );
		// csvToProtoBuf("resources/questions/kaggle_allen_ai_training_set2.tsv", "");
	}
}
