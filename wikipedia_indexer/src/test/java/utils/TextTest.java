package utils;

import utils.Text;
import static org.junit.Assert.*;
import org.junit.Test;
import java.util.Arrays;


public class TextTest {

	@Test
	public void testSplitInLines() {
		assertEquals(Text.splitInLines("  ").size(), 0);
		assertEquals(
				Text.splitInLines("\t\tI am big.  "),
				Arrays.asList("I am big.")
		);
		assertEquals(
				Text.splitInLines("\t\tThis apple, this is  nice.\t\n\n\nyou cute\n\tGo Steaua!!!\t \n\nWhaaat???!?  "),
				Arrays.asList("This apple, this is  nice.", "you cute", "Go Steaua!!!", "Whaaat???!?")
		);
	}
	
	@Test
	public void testSplitInWords() {
		assertEquals(Text.splitInWords("").size(), 0);
		assertEquals(Text.splitInWords(" ").size(), 0);
		assertEquals(Text.splitInWords("\t \t\n").size(), 0);
		
		assertEquals(
				Text.splitInWords("(I am nice)\nWhat are you [10] doing? I have \"...\" --- 10$."),
				Arrays.asList("(", "I", "am", "nice", ")", "What", "are", "you", "[", "10", "]", "doing", "?", "I", "have", "\"", "...", "\"", "---", "10", "$", ".")
		);
		assertEquals(
				Text.splitInWords("The hour is 11:35p.m."),
				Arrays.asList("The", "hour", "is", "11:35", "p.m.")
		);
		assertEquals(
				Text.splitInWords("The hour is 11:35 p.m."),
				Arrays.asList("The", "hour", "is", "11:35", "p.m.")
		);
		assertEquals(
				Text.splitInWords("The hour is 11:35a.m"),
				Arrays.asList("The", "hour", "is", "11:35", "a.m")
		);
		assertEquals(
				Text.splitInWords("The hour is 11:35a.m."),
				Arrays.asList("The", "hour", "is", "11:35", "a.m.")
		);
		assertEquals(
				Text.splitInWords("What about the dining-table and the 10th dry-cleaning schedule??? Are they still on?!"),
				Arrays.asList("What", "about", "the", "dining-table", "and", "the", "10th", "dry-cleaning", "schedule", "???", "Are", "they", "still", "on", "?!")
		);
		assertEquals(
				Text.splitInWords("Congrats! You finished the race 1st."),
				Arrays.asList("Congrats", "!", "You", "finished", "the", "race", "1st", ".")
		);
	}

}
