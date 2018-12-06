package data;


import com.google.protobuf.TextFormat;
import data.ConcretenessRatingsProtos.Ratings;
import data.ConcretenessRatingsProtos.Entry;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.text.ParseException;
import java.util.Scanner;


public final class ConcretenessRatings {
	private static final boolean DEBUG = true;
	private static Ratings word_ratings = null;
	
	private static void csvToProtoBuf() throws ParseException, IOException {
		if (DEBUG) {
			System.out.println("Converting from CSV to Protocol Buffer... \n");
		}
		
		Scanner input = new Scanner(new File("resources/concretness_ratings.csv"));
		
		// Read header line.
		if (!input.hasNextLine()) {
			input.close();
			throw new ParseException("Header line is missing!", 0);
		}
		
		String[] header = input.nextLine().split(",");
		if (DEBUG) {
			System.out.println("Headers: " + String.join(" | ", header) + "\n");
		}
		
		final int N = 9;  // Number of items on line.
		int num_lines = 0;
		Ratings.Builder rating_builder = Ratings.newBuilder();
		while (input.hasNextLine()) {
			String[] line = input.nextLine().split(",");
			if (line.length != N) {
				input.close();
				throw new ParseException("Incorrect number of items on line!", 0);
			}
			String word = line[0];
			boolean bigram = false;
			if (line[1].trim().equals("1"))
				bigram = true;
			double rating = Double.parseDouble(line[2]);
			if (rating < 0.0 || rating > 5.0) {
				input.close();
				throw new ParseException("Found invalid rating value!", 0);
			}
			
			// Add new entry to protocol buffer DB.
			rating_builder = rating_builder.putRatingsMap(word, Entry.newBuilder()
					.setBigram(bigram)
					.setRating(rating)
					.setRatingSd(Double.parseDouble(line[3]))
					.setUnknown(Integer.parseInt(line[4]))
					.setNumPersons(Integer.parseInt(line[5]))
					.setKnownPercentage(Double.parseDouble(line[6]))
					.setFrequencyCount(Long.parseLong(line[7]))
					.setType(line[8])
					.build());
			
			num_lines++;
		}
		
		Ratings ratings = rating_builder.build();
		String output = TextFormat.printToString(ratings);
		
		// Write ratings in text format to file.
		BufferedWriter out = new BufferedWriter(new FileWriter("resources/concretness_ratings.prototext"));
		
		out.write(output);
		out.newLine();
		out.flush();
		out.close();
		
		if (DEBUG) {
			System.out.println("Output size: " + (output.length() + 1) + " bytes.");
			System.out.println("Processed " + num_lines + " entries.");
		}
		
		input.close();
	}
	
	private static void loadRatings() {
		Ratings.Builder rating_builder = Ratings.newBuilder();
		
		// Read file in text format and parse it into a Protocol Buffer object.
		Scanner input = null;
		try {
			input = new Scanner(new File("resources/concretness_ratings.prototext"));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			System.exit(1);
		}
		
		StringBuilder input_text = new StringBuilder();
		
		while (input.hasNextLine()) {
			String line = input.nextLine();
			input_text.append(line);
			input_text.append('\n');
		}
		input.close();
		
		rating_builder.clear();
		try {
			TextFormat.merge(input_text.toString(), rating_builder);
		} catch (com.google.protobuf.TextFormat.ParseException e) {
			e.printStackTrace();
			System.exit(1);
		}
		
		word_ratings = rating_builder.build();
	}
	
	public static Ratings getRatings() {
		if (word_ratings == null)
			loadRatings();
		return word_ratings;
	}
	
	public static double getWordConcretness(String word) throws IllegalArgumentException {
		Ratings ratings = getRatings();
		return ratings.getRatingsMapOrThrow(word).getRating();
	}
}
