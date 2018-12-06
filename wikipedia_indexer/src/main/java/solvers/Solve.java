package solvers;

import config.ConfigPaths;

import utils.Pair;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;


class Solve {
	
	private static final String SUBMISSION_FILE = "resources/questions/KaggleAllenAI/kaggle_submit_answers.csv";
	// private static final String INPUT_FILE = "resources/questions/Essential-Terms-Set/essential_terms_dataset2.prototext";
	// private static final String INPUT_FILE = "resources/questions/KaggleAllenAI/kaggle_allen_ai_training_set.prototext";
	
	private static void saveToFile(Map<String, Integer> data, String path) throws IOException {	
		List <Pair<String, String> > answers = new ArrayList<Pair<String, String> >();
		for (Map.Entry<String, Integer> entry: data.entrySet()) {
			String id = entry.getKey();
			Integer value = entry.getValue();
			String answer = null;
			
			if (value == 0)
				answer = "A";
			else if (value == 1)
				answer = "B";
			else if (value == 2)
				answer = "C";
			else if (value == 3)
				answer = "D";
			else {
				throw new IOException("Invalid answer!");
			}
			
			answers.add(Pair.makePair(id, answer));
		}
		
		Collections.sort(answers, new Comparator<Pair <String, String> > (){
			public int compare(Pair <String, String>  lhs, Pair <String, String> rhs) {
				return lhs.getFirst().compareTo(rhs.getFirst());
			}  
		});
		
		/* Write data to file in KaggleAllenAI format. */
		BufferedWriter out = new BufferedWriter(new FileWriter(path));
		out.write("id,correctAnswer\n");
		for (Pair <String, String> entry: answers) {
			out.write(entry.getFirst() + "," + entry.getSecond() + "\n");
		}
		
		out.flush();
		out.close();
		
		System.out.println("\nResults saved to " + path);
	}
	
	public static void main(String[] args) throws IOException {
		Solver solver = new IRWithET.Builder()
							.withType(IRWithET.Type.BOOSTED_QUERY)
							.withIndex(ConfigPaths.ARC_INDEX_PATH.toString())
							.withNumWorkers(6)
							.build();
		Map<String, Integer> answers = solver.run(ConfigPaths.ARC_EASY_VAL_DATASET_PATH.toString());
		solver.clear();
		
		if (answers != null)
			saveToFile(answers, SUBMISSION_FILE);
	}
}
