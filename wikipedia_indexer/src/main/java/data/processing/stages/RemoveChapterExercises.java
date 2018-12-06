package data.processing.stages;

import java.util.ArrayList;

import utils.Text;

public final class RemoveChapterExercises implements PipelineStage<String, String> {
	
	private static double round(double x, int scale) {
	    return Math.round(x * Math.pow(10, scale)) / Math.pow(10, scale);
	}
	
	/* Do end of chapter exercises begin here? */
	private boolean isBegin(String line) {
		if (line.trim().endsWith("End-of-Chapter Material") && line.split(" ").length == 3)
			return true;
		if (line.trim().equals("PROBLEMS") || line.trim().equals("CONCEPT PROBLEMS"))
			return true;
		if (line.trim().equals("NUMERICAL PROBLEMS"))
			return true;
		if (line.trim().endsWith("End-of-Chapter Exercises") && line.split(" ").length == 3)
			return true;
		if (line.trim().endsWith("Review Exercises and Sample Exam"))
			return true;
		if (line.trim().equals("EXERCISES"))
			return true;
		
		if (line.trim().equals("Review Questions"))
			return true;
		if (line.trim().equals("Lesson Exercises"))
			return true;
		if (line.trim().startsWith("Review Questions: Answer the following"))
			return true;
		
		if (line.trim().equals("INTERACTIVE LINK QUESTIONS"))
			return true;
		if (line.trim().equals("REVIEW QUESTIONS"))
			return true;
		if (line.trim().equals("CRITICAL THINKING QUESTIONS"))
			return true;
		
		if (line.trim().equals("Exercises"))
			return true;
		if (line.trim().equals("Problems & Exercises"))
			return true;
		
		return false;
	}
	
	/* Do end of chapter exercises end here? */
	private boolean isEnd(String line) {
		String[] tokens = line.split(" ");
		if (tokens.length == 2 && tokens[0].equals("Chapter") && tokens[1].matches("^\\d+$")) {
			// Chapter 4, Chapter 6, ..., Chapter N
			return true;
		}
		if (tokens.length == 2 && tokens[1].equals("Overview")) 
			return true;
		if (line.trim().equals("LEARNING OBJECTIVES"))
			return true;
		if (line.trim().toLowerCase().equals("learning objectives"))
			return true;
		if (line.trim().equals("Vocabulary") || line.trim().toLowerCase().equals("vocabulary"))
			return true;
		if (line.trim().toLowerCase().equals("points to consider"))
			return true;
		if (line.trim().toLowerCase().equals("image sources"))
			return true;
		if (line.trim().toLowerCase().equals("review answers"))
			return true;
		if (line.trim().toLowerCase().equals("further reading"))
			return true;
		if (line.trim().toLowerCase().equals("answers"))
			return true;
		if (line.trim().toLowerCase().equals("answer"))
			return true;
		if (line.trim().startsWith("Answer Key for Review Questions"))
			return true;
		if (line.trim().toLowerCase().equals("chapter objectives"))
			return true;
		if (line.trim().toLowerCase().equals("introduction"))
			return true;
		if (line.trim().toLowerCase().equals("chapter outline"))
			return true;
		if (line.trim().toLowerCase().startsWith("appendix"))
			return true;
		if (line.trim().toLowerCase().equals("index"))
			return true;
		if (line.trim().toLowerCase().equals("symbols"))
			return true;
		if (tokens.length == 2 && tokens[0].equals("CHAPTER") && tokens[1].matches("^\\d+$")) {
			return true;
		}
		if (line.trim().toLowerCase().equals("answer key"))
			return true;
		if (line.trim().toLowerCase().equals("answers key"))
			return true;
		
		return false;
	}
	
	@Override
	public String process(String input) {
		ArrayList<String> lines = Text.splitInLines(input);
		
		int total_lines = lines.size();
		int removed_lines = 0;
		
		for (int i = 0; i < lines.size(); i++) {
			if (isBegin(lines.get(i).trim())) {
				int j;
				for (j = 0; i + j < lines.size() && j <= 2350; j++) { // 950
					if (isEnd(lines.get(i + j).trim())) {
						break;
					}
					removed_lines++;
					lines.set(i + j, "");
				}
				if (j > 2350) {
					throw new IllegalStateException("Chapter exercises section end not found!");
				}
			}
		}
		
		System.out.println("Removed " + removed_lines + "(" + round(100.0 * removed_lines / total_lines, 2) + "%) lines from chapter exercises.");;
		
		return String.join("\n", lines);
	}
}
