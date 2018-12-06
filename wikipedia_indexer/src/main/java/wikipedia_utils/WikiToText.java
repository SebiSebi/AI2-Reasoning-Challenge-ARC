package wikipedia_utils;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collection;
import java.util.HashSet;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.LinkedBlockingQueue;

import de.tudarmstadt.ukp.wikipedia.api.Category;
import de.tudarmstadt.ukp.wikipedia.api.DatabaseConfiguration;
import de.tudarmstadt.ukp.wikipedia.api.Page;
import de.tudarmstadt.ukp.wikipedia.api.WikiConstants;
import de.tudarmstadt.ukp.wikipedia.api.Wikipedia;
import de.tudarmstadt.ukp.wikipedia.api.exception.WikiApiException;
import de.tudarmstadt.ukp.wikipedia.api.exception.WikiInitializationException;
import de.tudarmstadt.ukp.wikipedia.api.exception.WikiTitleParsingException;

import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;

/**
* Converts Wikipedia data to plain text and writes it to a file,
* one sentence per line. One can restrict the number of sentences
* generated as well as the main categories to analyze.
*/
public final class WikiToText {

	private static Wikipedia initWiki() {
		// Configure the database connection parameters
        DatabaseConfiguration dbConfig = new DatabaseConfiguration();
        dbConfig.setHost("localhost");
        dbConfig.setDatabase("wikipedia_db");  // wikipedia_db_en_march_2018
        dbConfig.setUser("root");	// stefan
        dbConfig.setPassword("iepurila123");  // sparql
        dbConfig.setLanguage(WikiConstants.Language.english);

        Wikipedia wiki = null;
        try {
        	wiki = new Wikipedia(dbConfig);
        } catch (WikiInitializationException e) {
            e.printStackTrace();
        }
        
        return wiki;
    }

	private static String run(Collection<String> main_categories, int max_pages_to_analyze, String output_file) throws IOException {
		Wikipedia wiki = initWiki();
		if (wiki == null)
			return "Could not initialize Wikipedia.";
	
		// Open file for writing.
		BufferedWriter out = new BufferedWriter(new FileWriter(output_file));
		
		LinkedBlockingQueue<Category> categories = new LinkedBlockingQueue<Category>();
		HashSet<Long> visited_categories = new HashSet<Long>();
		HashSet<Integer> visited_pages = new HashSet<Integer>();
		
		for (String cat: main_categories) {
			try {
	            categories.add(wiki.getCategory(cat));
	        } catch (WikiApiException e) {
	        	System.err.println("[ERROR] Category not found: " + cat);
	        }
		}
		
		Properties corenlp_props = new Properties();
		corenlp_props.setProperty("annotators", "tokenize, ssplit");
		corenlp_props.setProperty("tokenize.options", "normalizeOtherBrackets=false");
		corenlp_props.setProperty("tokenize.options", "normalizeParentheses=false");
        StanfordCoreNLP pipeline = new StanfordCoreNLP(corenlp_props);
        
		int page_count = 0;
		long lines_written = 0;
		while(categories.size() > 0 && visited_pages.size() < max_pages_to_analyze) {
	        Category current_category = categories.remove();
	        if(visited_categories.contains(current_category.__getId())) {
	        	continue;
	        }
	        visited_categories.add(current_category.__getId());
	        
	        Set<Category> child_categories = current_category.getChildren();
	        categories.addAll(child_categories);
	        
	        String category_title = "UNKNOWN";
	        try {
				category_title = current_category.getTitle().getPlainTitle();
			} catch (WikiTitleParsingException e) {
				e.printStackTrace();
			}
	        
	        Set<Integer> page_ids;
			try {
				page_ids = current_category.getArticleIds();
			} catch (WikiApiException e) {
				System.err.println("[ERROR] Cannot fetch pages for " + category_title);
				continue;
			}
	
	        for (int page_id : page_ids) {
	            Page page;
				try {
					page = wiki.getPage(page_id);
				} catch (WikiApiException e) {
					System.err.println("[ERROR] Cannot fetch page with id: " + page_id);
					continue;
				}
	            if (visited_pages.contains(page.getPageId())) {
	            	continue;
	            }
	            visited_pages.add(page.getPageId());
	            
	            String content = null;
	            try {
					content = page.getPlainText();
				} catch (WikiApiException e) {
					String title = "UNKNOWN";
					try {
						 title = page.getTitle().getPlainTitle();
					} catch (WikiTitleParsingException e2) {
					}
					System.err.println("[ERROR] Cannot fetch content for page: " + title);
				}
	            
	            if (content != null) {
	            	// Parse content and save to file.
	            	lines_written += analyze_page_and_write(content, pipeline, out);
	            	
	            }
	            
	            if (visited_pages.size() >= max_pages_to_analyze)
	            	break;
	        }
	
	        // System.out.println("Indexed " + page_ids.size() + " pages for: " + category_title);
	        
	        if (visited_pages.size() > page_count + 5000) {
	            page_count = visited_pages.size();
	            System.out.println("\nVisited " + page_count + " pages.");
	            System.out.println("Analysed " + visited_categories.size() + " categories.");
	            System.out.println("Queue size: " + categories.size() + "\n");
	            out.flush();
	        }
	    }
		
		out.flush();
		out.close();
		
		System.out.println("\nVisited " + visited_pages.size() + " pages.");
        System.out.println("Analysed " + visited_categories.size() + " categories.");
        System.out.println("Queue size: " + categories.size());
        System.out.println("\nWritten " + lines_written + " lines.");
        
		return "OK";
	}
	
	private static long analyze_page_and_write(String content, StanfordCoreNLP pipeline, BufferedWriter out) {
		// Remove short sentences.
		ArrayList<String> contents = new ArrayList<String>();
		for (String data: content.split("[\\r\\n]+")) {
			if (data.split("\\s+").length >= 25) {
				contents.add(data);
			}
		}
		content = String.join("\n", contents);
		
		Annotation doc = pipeline.process(content);
		List<CoreMap> sentences = doc.get(CoreAnnotations.SentencesAnnotation.class);
		/**
		 * Each sentence is a map of tokens. A token is a CoreLabels
		 * with properties like lemma, POS, etc.
		 */
		long num_lines = 0;
		for(CoreMap sentence: sentences){
			List<CoreLabel> labels = sentence.get(CoreAnnotations.TokensAnnotation.class);
			if (labels.size() <= 8)
	        	continue;
	        String data = edu.stanford.nlp.ling.Sentence.listToString(labels).trim();
	        if (data.substring(data.length() - 1).equals("?")) {
	        	// Skip questions.
	        	continue;
	        }
	        try {
				out.write(data + "\n");
				num_lines++;
			} catch (IOException e) {
				e.printStackTrace();
			}
	    }
		 
		return num_lines;
	}

	public static void main(String[] args) throws IOException {
		String status = run(Arrays.asList("Science", "Biology", "Chemistry", "Earth", "Life", "Physics", "Elementary particles", "Astronomy", "Earth sciences", "Cell_biology"),
				            500000,  // max_num_pages_to_analyze,
				            "/data/test.txt");
		if (!status.equals("OK")) {
			System.err.println("\nFailed with: " + status);
		}
		else {
			System.out.println("\nDone!");
		}
	}

}
