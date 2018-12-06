package data.processing.stages;

import java.util.ArrayList;

import utils.Text;

// Removes sentences that contain URLs (one or more).
public class RemoveURLSentences implements PipelineStage<String, String> {

	private static double round(double x, int scale) {
	    return Math.round(x * Math.pow(10, scale)) / Math.pow(10, scale);
	}
	
	@Override
	public String process(String input) {
		ArrayList<String> lines = Text.splitInLines(input);

		int total_lines = lines.size();
		int removed_lines = 0;
		for (int i = 0; i < lines.size(); i++) {
			String line = lines.get(i).trim();
			if (line.matches("^.*(https?|ftp|file|smtp)://.*/.*$")) {
				lines.set(i, "");
				removed_lines += 1;
			}
		}
		
		System.out.println("Stripped " + removed_lines + "(" + round(100.0 * removed_lines / total_lines, 2) + "%) sentences with URLs.");
		
		return String.join("\n", lines);
	}
	
}
