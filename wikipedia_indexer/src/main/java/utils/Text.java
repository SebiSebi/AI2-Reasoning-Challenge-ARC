package utils;

import java.io.StringReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.PTBTokenizer;

public final class Text {
	public static ArrayList<String> splitInLines(String text) {
		List<String> lines = (Arrays.asList(text.split("[\\r\\n]+")));
		ArrayList<String> out = new ArrayList<String>();
		for (String line: lines) {
			if (line.trim().length() > 0) {
				out.add(line.trim());
			}
		}
		return out;
	}
	
	public static ArrayList<String> splitInWords(String text) {
		DocumentPreprocessor dp = new DocumentPreprocessor(new StringReader(text));
		String options = "americanize=false,tokenizeNLs=false,ptb3Escaping=false,ptb3Dashes=False";
		dp.setTokenizerFactory(PTBTokenizer.PTBTokenizerFactory.newWordTokenizerFactory(options));
		ArrayList<String> words = new ArrayList<String>();
		for (List<HasWord> sentence : dp) {
            for (HasWord word: sentence) {
            	words.add(word.word().trim());
            }
        }
        return words;
	}
	
	public static void main(String[] args) {
		String text = "What about the dining-table and the 10th dry-cleaning schedule??? Are they on?!";
		System.out.println(splitInWords(text));
	}
}
