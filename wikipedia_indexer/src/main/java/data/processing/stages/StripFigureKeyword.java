package data.processing.stages;

import java.util.ArrayList;

import utils.Text;

// This stage strips "Figure x:" keyword from image descriptions.
public final class StripFigureKeyword implements PipelineStage<String, String> {

	private static double round(double x, int scale) {
	    return Math.round(x * Math.pow(10, scale)) / Math.pow(10, scale);
	}
	
	@Override
	public String process(String input) {
		ArrayList<String> lines = Text.splitInLines(input);

		int total_lines = lines.size();
		int stripped_lines = 0;
		for (int i = 0; i < lines.size(); i++) {
			String line = lines.get(i).trim();
			if (line.matches("^Figure \\d+:.*$")) {
				line = line.replaceFirst("Figure \\d+:", "").trim();
				lines.set(i, line);
				stripped_lines += 1;
			}
			else if (line.matches("^figure \\d+:.*$")) {
				line = line.replaceFirst("figure \\d+:", "").trim();
				lines.set(i, line);
				stripped_lines += 1;
			}
			else if (line.matches("^(F|f)igure \\d+.+\\d+.*$")) {
				line = line.replaceFirst("(F|f)igure \\d+.+\\d+", "").trim();
				lines.set(i, line);
				stripped_lines += 1;
			}
		}
		
		System.out.println("Stripped " + stripped_lines + "(" + round(100.0 * stripped_lines / total_lines, 2) + "%) @figure descriptions.");
		
		return String.join("\n", lines);
	}

}
