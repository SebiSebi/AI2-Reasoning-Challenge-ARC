package wikipedia_indexer;

import de.tudarmstadt.ukp.wikipedia.api.*;
import de.tudarmstadt.ukp.wikipedia.api.exception.WikiApiException;
import de.tudarmstadt.ukp.wikipedia.api.exception.WikiInitializationException;
import de.tudarmstadt.ukp.wikipedia.api.exception.WikiTitleParsingException;
import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.nio.file.Paths;
import java.sql.Timestamp;
import java.util.*;
import java.util.concurrent.LinkedBlockingQueue;

public class WikipediaIndexer {

	private Wikipedia wiki = null;
	private GeneralConfig config = null;
	private String indexPath = "";
	private Queue<Category> categories = null;
	private Set<Long> visitedCategories = null;
	private Set<Integer> visitedPages = null;
	private final String binary_storage_file = "resources/WikipediaIndexer.bin";
	private final String integrity_file = "resources/WikipediaIndexer_hash.txt";
	
	public WikipediaIndexer(String indexPath, GeneralConfig config) {
		initWiki();
		this.indexPath = indexPath;
		this.config = config;
	}
	
	private void initWiki() {
        if(wiki == null) {
            // Configure the database connection parameters
            DatabaseConfiguration dbConfig = new DatabaseConfiguration();
            dbConfig.setHost("localhost");
            dbConfig.setDatabase("wikipedia_db");  // wikipedia_db_en_march_2018
            dbConfig.setUser("root");	// stefan
            dbConfig.setPassword("iepurila123");  // sparql
            dbConfig.setLanguage(WikiConstants.Language.english);

            try {
                wiki = new Wikipedia(dbConfig);
            } catch (WikiInitializationException e1) {
                System.out.println("Could not initialize Wikipedia.");
                e1.printStackTrace();
                System.exit(1);
            }
        }
    }
	
	public void startIndexing() throws IOException, InterruptedException {
	    categories = new LinkedBlockingQueue<Category>();
	    visitedCategories = Collections.synchronizedSet(new HashSet<Long>());
	    visitedPages = Collections.synchronizedSet(new HashSet<Integer>());
	
	    Directory dir = null;
	    IndexWriter writer = null;
	    Analyzer analyzer = new StandardAnalyzer();
	    IndexWriterConfig iwc = new IndexWriterConfig(analyzer);
	
	    iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);
	    iwc.setRAMBufferSizeMB(1024.0);
	    
	    try {
	        dir = FSDirectory.open(Paths.get(indexPath));
	        writer = new IndexWriter(dir, iwc);
	    } catch (IOException e) {
	        e.printStackTrace();
	        System.exit(1);
	    }
	    
	    restoreOldState();
	    if (!checkIntegrity()) {
	    	System.out.println("\n\nWikipediaIndexer is corrupted! Force stopping... \n");
	    	System.exit(1);
	    }
	
	    System.out.println("Hashes:");
	    System.out.println(visitedPages.hashCode());
	    System.out.println(visitedCategories.hashCode());
	    System.out.println(categories.size());
	    System.out.println("");
	    
	    try {
	    	categories.add(wiki.getCategory("Science"));
	    } catch (WikiApiException e) {
	        e.printStackTrace();
	    }
	    
	    int count = 1, pageCount = 0;
	    count = Math.max(visitedPages.size() / 50000 - 1, 1);  // MODIFY BELOW!!!
	    // IF modify THEN MODIFY BELOW!!! !!! !!!
	    
	    // We start from the "science" category, index its pages and then expand children categories (BFS)
	    while(categories.size() > 0) {
	        Category currentCategory = categories.remove();
	        if(visitedCategories.contains(currentCategory.__getId())) {
	        	continue;
	        }
	
	        visitedCategories.add(currentCategory.__getId());
	        Set<Category> childCategories = currentCategory.getChildren();
	        categories.addAll(childCategories);
	        Set<Page> pages;
	        try {
	            pages = currentCategory.getArticles();
	        } catch (WikiApiException e) {
	            e.printStackTrace();
	            continue;
	        }
	
	        for (Page page : pages) {
	            try {
	                if(visitedPages.contains(page.getPageId()))
	                    continue;
	
	                visitedPages.add(page.getPageId());
	                indexPage(writer, page);
	                
	            } catch (Exception e) {
	                e.printStackTrace();
	            }
	        }
	
	        try {
	            System.out.println("Indexed " + pages.size() + " pages for: " + currentCategory.getTitle().getPlainTitle());
	        } catch (WikiTitleParsingException e) {
	            e.printStackTrace();
	        }
	
	        // Notify us when reaching another 15,000 pages indexed
	        if(visitedPages.size() > pageCount + 15000) {
	            pageCount = visitedPages.size();
	            System.out.println("\nVisited " + visitedPages.size() + " pages.");
	            System.out.println("Analysed " + visitedCategories.size() + " categories.");
	            System.out.println("Queue size: " + categories.size() + "\n");
	        }
	        
	        // Create a backup every 50,000 pages
	        if(visitedPages.size() > count * 50000 || config.getStopSignal()) {
	            writer.close();
	            
	            Date now = new Timestamp(Calendar.getInstance().getTime().getTime());
	            System.out.println("Written an index version. (" + count + ") " + now);
	            saveCurrentState();
	            
	            Thread.sleep(60 * 1000);  // Sleep for 60 seconds.
	            
	            if (config.getStopSignal() == true)
	            	break;
	            
	            System.out.println("Resumed activity.");
	            count++;
	            iwc = new IndexWriterConfig(analyzer);
	            dir = FSDirectory.open(Paths.get(indexPath));
	            writer = new IndexWriter(dir, iwc);
	            iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);
	            iwc.setRAMBufferSizeMB(1024.0);
	        }
	    }
	    
	    writer.close();
	    saveCurrentState();
	}

	private void indexPage(IndexWriter writer, Page page) {
        try {
            String content = page.getPlainText();
            String title = page.getTitle().getPlainTitle();
            String uri = "https://en.wikipedia.org/wiki/" + page.getTitle().getWikiStyleTitle();

            // index each paragraph separately
            for(String paragraph : content.split("\n")) {
                if(paragraph.split("\\ ").length < 6) {
                    continue; // skip short paragraphs
                }
                
                Document doc = new Document();

                doc.add(new StringField("title", title, Field.Store.YES));
                doc.add(new StringField("uri", uri, Field.Store.YES));
                doc.add(new TextField("contents", paragraph, Field.Store.YES));

                writer.addDocument(doc);
            }

        }
        catch (Exception e) {
        	System.out.println("Failed to parse Wikipedia Page!");
        	e.printStackTrace();
        }
    }
	
	private void saveCurrentState() {
		FileOutputStream f = null;
		ObjectOutputStream serializer = null;
		try {
			f = new FileOutputStream(new File(binary_storage_file));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			return;
		}
		try {
			serializer = new ObjectOutputStream(f);
		} catch (IOException e) {
			e.printStackTrace();
			try {
				f.close();
			} catch (IOException e1) {
				e1.printStackTrace();
				return;
			}
			return;
		}
		
		List<String> category_titles = new ArrayList<String>();
		for (Category x: categories) {
			try {
				category_titles.add(x.getTitle().toString());
			} catch (WikiTitleParsingException e) {
				e.printStackTrace();
			}
		}
		
		try {
			serializer.writeObject(visitedPages);
			serializer.writeObject(visitedCategories);
			serializer.writeObject(category_titles);
			System.out.println("Successfully wrote objects to file");
		} catch (IOException e) {
			e.printStackTrace();
		}

		try {
			serializer.close();
			f.close();
		} catch (IOException e) {
			e.printStackTrace();
			return ;
		}
		
		/* Save integrity data. */
		try {
			BufferedWriter out = new BufferedWriter(new FileWriter(integrity_file));
			out.write(Integer.toString(visitedPages.hashCode()));
			out.newLine();
			out.write(Integer.toString(visitedCategories.hashCode()));
			out.newLine();
			out.write(Integer.toString(category_titles.hashCode()) + " " + categories.size());
			out.flush();
			out.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private void restoreOldState() {
		ObjectInputStream in = null;
		try {
			in = new ObjectInputStream(new FileInputStream("resources/WikipediaIndexer.bin"));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			return;
		} catch (IOException e) {
			e.printStackTrace();
			return;
		}
		
		try {
			visitedPages = Collections.synchronizedSet((Set<Integer>)in.readObject());
			visitedCategories = Collections.synchronizedSet((Set<Long>)in.readObject());
			List<String> category_titles = (List<String>)in.readObject();
			for (String title: category_titles) {
				categories.add(wiki.getCategory(title));
			}
			System.out.println(category_titles);
		} catch (ClassNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (WikiApiException e) {
			e.printStackTrace();
		}
		
		try {
			in.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private boolean checkIntegrity() {
		Scanner input = null;
		try {
			input = new Scanner(new File(integrity_file));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			return false;
		}
		
		List<String> lines = new ArrayList<String>();
		while (input.hasNextLine())
			lines.add(input.nextLine());
		
		if (lines.size() != 3) {
			input.close();
			return false;
		}
		
		if (visitedPages.hashCode() != Integer.parseInt(lines.get(0))) {
			input.close();
			return false;
		}
		
		if (visitedCategories.hashCode() != Integer.parseInt(lines.get(1))) {
			input.close();
			return false;
		}
		
		List<String> category_titles = new ArrayList<String>();
		for (Category x: categories) {
			try {
				category_titles.add(x.getTitle().toString());
			} catch (WikiTitleParsingException e) {
				e.printStackTrace();
				input.close();
				return false;
			}
		}
		
		if (!(Integer.toString(category_titles.hashCode()) + " " + categories.size()).equals(lines.get(2))) {
			input.close();
			return false;
		}
		
		input.close();
		return true;
	}
	
	public int getVisitedPages() {
		if (visitedPages == null)
			return 0;
		return visitedPages.size();
	}
	
	public int getVisitedCategories() {
		if (visitedCategories == null)
			return 0;
		return visitedCategories.size();
	}
	
	public int getRemainingCategories() {
		if (categories == null)
			return 0;
		return categories.size();
	}
}
