package solvers;

import data.QuestionsProtos.QuestionDataSet;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Map;
import java.util.Scanner;

import com.google.protobuf.TextFormat;
import com.google.protobuf.TextFormat.ParseException;

public abstract class Solver {
	protected abstract Map<String, Integer> solve(QuestionDataSet data_set);
	
	private void printStats(QuestionDataSet data_set) {
		if (data_set.hasDescription())
			System.out.println("Solving for dataset: " + data_set.getDescription());
		if (data_set.hasPurpose())
			System.out.println("Purpose: " + data_set.getPurpose().toString());
		System.out.println("Num questions: " + data_set.getEntriesCount() + "\n");
	}
	
	public Map<String, Integer> run(String dataset_path) throws ParseException, FileNotFoundException {
		Scanner input = new Scanner(new File(dataset_path));
		
		StringBuilder input_text = new StringBuilder();
		while (input.hasNextLine()) {
			String line = input.nextLine();
			input_text.append(line);
			input_text.append('\n');
		}
		input.close();
		
		QuestionDataSet.Builder data_set_builder = QuestionDataSet.newBuilder();
		TextFormat.merge(input_text, data_set_builder);
		QuestionDataSet data_set = data_set_builder.build();
		
		return run(data_set);
	}
	
	public Map<String, Integer> run(QuestionDataSet data_set) {
		printStats(data_set);
		return solve(data_set);
	}
	
	/* This gets called after the solver has been run. */
	public void clear() {}
}
