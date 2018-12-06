package data.processing.stages;

import java.util.ArrayList;

import utils.Text;

public final class RemoveGlossary implements PipelineStage<String, String> {

	private static double round(double x, int scale) {
	    return Math.round(x * Math.pow(10, scale)) / Math.pow(10, scale);
	}
	
	public String process(String input) {
		ArrayList<String> lines = Text.splitInLines(input);

		int total_lines = lines.size();
		int removed_lines = 0;
		for (int i = 0; i < lines.size(); i++) {
			if (lines.get(i).trim().toLowerCase().equals("vocabulary") ||
				lines.get(i).trim().toLowerCase().equals("key terms") ||
				lines.get(i).trim().toLowerCase().equals("glossary")) {
				int j;
				for (j = 0; i + j < lines.size() && j <= 600; j++) {
					if (lines.get(i + j).trim().toLowerCase().equals("review answers"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("chapter summary"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("summary"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("key equations"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("key concepts and summary"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("points to consider"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("learning objectives"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("lesson objectives"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("chapter review"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("image sources"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("section summary"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("conceptual questions"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("a"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("appendices"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("review questions"))
						break;
					if (lines.get(i + j).trim().toLowerCase().equals("objectives"))
						break;
					removed_lines++;
					lines.set(i + j, "");
				}
				if (j > 600) {
					throw new IllegalStateException("Glossary section end not found!");
				}
			}
		}
		
		System.out.println("Removed " + removed_lines + "(" + round(100.0 * removed_lines / total_lines, 2) + "%) lines from glossary.");;
		
		return String.join("\n", lines);
	}
}
