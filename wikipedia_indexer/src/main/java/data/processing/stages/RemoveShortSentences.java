package data.processing.stages;

import java.util.ArrayList;
import java.util.concurrent.atomic.AtomicInteger;

import utils.Text;

public final class RemoveShortSentences implements PipelineStage<String, String> {
	
	private AtomicInteger num_min_words = null;
	
	public RemoveShortSentences(int num_min_words) {
		// Each sentence with less than num_min_words will be removed.
		this.num_min_words = new AtomicInteger(num_min_words);
	}
	
	@Override
	public String process(String input) {
		ArrayList<String> lines = Text.splitInLines(input);

		for (int i = 0; i < lines.size(); i++) {
			String line = lines.get(i).trim();
			if (line.isEmpty() || Text.splitInWords(line).size() < num_min_words.get()) {
				lines.set(i, "");
			}
		}
		
		System.out.println("Removed short sentences.");
		
		return String.join("\n", lines);
	}
	
}
