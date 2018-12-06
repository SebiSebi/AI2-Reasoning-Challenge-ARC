package data.processing.stages;


public final class ToSentences implements PipelineStage<String, String> {
	
	@Override
	public String process(String input) {
		String in = input.replaceAll("[\\t\\n\\r]+"," ");
		in = in.replace('?', '.');
		in = in.replace('!', '.');
		
		String[] sentences = in.split("\\.");
		
		System.out.println("Converted text to " + sentences.length + " sentences.");
		
		return String.join(".\n", sentences);
	}
}
