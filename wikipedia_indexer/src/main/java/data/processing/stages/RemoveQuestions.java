package data.processing.stages;

import java.util.ArrayList;

import utils.Text;

public final class RemoveQuestions implements PipelineStage<String, String> {

	private static double round(double x, int scale) {
	    return Math.round(x * Math.pow(10, scale)) / Math.pow(10, scale);
	}
	
	private boolean isMultipleChoiceAnswer(String line) {
		if (line.length() == 0)
			return false;
		line = line.trim();
		if (line.startsWith("•"))
			return true;
		if (line.startsWith("1."))
			return true;
		if (line.startsWith("1)"))
			return true;
		if (line.startsWith("a."))
			return true;
		if (line.startsWith("a)"))
			return true;
		if (line.startsWith("A."))
			return true;
		if (line.startsWith("A)"))
			return true;
		if (line.startsWith("i)"))
			return true;
		if (line.startsWith("i."))
			return true;
		if (line.startsWith("I)"))
			return true;
		if (line.startsWith("I."))
			return true;
		return false;
	}
	
	@Override
	public String process(String input) {
		ArrayList<String> lines = Text.splitInLines(input);

		int total_lines = lines.size();
		int removed_lines = 0;
		for (int i = 0; i < lines.size(); i++) {
			String line = lines.get(i).trim();
			if (line.length() >= 1 && line.endsWith("?")) {
				lines.set(i, "");
				removed_lines += 1;
				
				/* Remove answers if necessary. */
				String next_line = "";
				if (i + 1 < lines.size())
					next_line = lines.get(i + 1).trim();
				if (isMultipleChoiceAnswer(next_line.trim())) {
					for (int j = 1; j <= 4 && i + j < lines.size(); j++) {
						lines.set(i + j, "");
						removed_lines += 1;
					}
				}
			}
		}
		
		System.out.println("Removed " + removed_lines + "(" + round(100.0 * removed_lines / total_lines, 2) + "%) questions (with answers)");
		
		return String.join("\n", lines);
	}

}
