package data;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

import com.google.protobuf.TextFormat;
import data.QuestionsProtos.QuestionDataSet;


public final class QuestionDB {
	
	public static QuestionDataSet loadDataSet(String file_path) {
		QuestionDataSet.Builder data_set_builder = QuestionDataSet.newBuilder();
		
		// Read file in text format and parse it into a Protocol Buffer object.
		Scanner input = null;
		try {
			input = new Scanner(new File(file_path));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			System.exit(1);
		}
		
		StringBuilder input_text = new StringBuilder();
		
		while (input.hasNextLine()) {
			String line = input.nextLine();
			input_text.append(line);
			input_text.append('\n');
		}
		input.close();
		
		data_set_builder.clear();
		try {
			TextFormat.merge(input_text.toString(), data_set_builder);
		} catch (com.google.protobuf.TextFormat.ParseException e) {
			e.printStackTrace();
			System.exit(1);
		}
		
		return data_set_builder.build();	
	}
}
