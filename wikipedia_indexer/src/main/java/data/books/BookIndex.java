package data.books;

import utils.Text;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Scanner;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.IndexWriterConfig.OpenMode;
import org.apache.lucene.store.Directory;
import org.apache.lucene.store.FSDirectory;

public final class BookIndex {
	
	private IndexWriter index_writer = null;
	private Scanner input = null;
	
	private BookIndex(String index_path, String books_path) throws FileNotFoundException {
		 Analyzer analyzer = new EnglishAnalyzer();
		 
		 IndexWriterConfig iwc = new IndexWriterConfig(analyzer);
		 iwc.setOpenMode(OpenMode.CREATE_OR_APPEND);
		 iwc.setRAMBufferSizeMB(1024.0);
		    
		 try {
			 Directory dir = FSDirectory.open(Paths.get(index_path));
		     this.index_writer = new IndexWriter(dir, iwc);
		 } catch (IOException e) {
		     e.printStackTrace();
		 }
		 
		 if (index_writer != null) {
			 System.out.println("[BookIndex] Using analyzer: " + index_writer.getAnalyzer().toString());
			 ArrayList <String> conf = Text.splitInLines(index_writer.getConfig().toString());
			 for (String line: conf) {
				 System.out.println("[BookIndex] " + line);
			 }
			 System.out.println("[BookIndex] Index path: "+ index_path);
		 }
		 
		 this.input = new Scanner(new File(books_path));
		 System.out.println("[BookIndex] Reading from: " + books_path);
	}
	
	public void run(int num_sentences_per_doc, int stride) throws IOException {
		if (index_writer == null || input == null) {
			System.err.println("[BookIndex] IndexWriter or input scanner is null.");
			return;
		}
		if (num_sentences_per_doc < 1) {
			System.err.println("[BookIndex] Invalid number of sentences per document.");
			return;
		}
		if (stride < 1) {
			System.err.println("[BookIndex] Invalid stride.");
			return;
		}
		
		System.out.println("[BookIndex] Indexing ...");
		
		ArrayList <String> data = new ArrayList <String>();
		while (input.hasNextLine()) {
			String line = input.nextLine();
			data.add(line);
		}
		
		System.out.println("[BookIndex] Num lines = " + data.size());
		
		int num_page = 1;
		int total_words = 0;
		int num_docs = 0;
		for (int i = 0; i < data.size(); i += stride) {
			if (i >= num_page * 15000) {
				System.out.println("[BookIndex] " + i + " out of " + data.size() + " sentences.");
				num_page++;
			}
			StringBuilder sb = new StringBuilder();
			for (int j = 0; j < num_sentences_per_doc && i + j < data.size(); j++) {
				sb.append(data.get(i + j).trim());
				sb.append(" ");
			}
			addDocument(sb.toString());
			
			total_words += Text.splitInWords(sb.toString()).size();
			num_docs += 1;
		}
		
		if (num_docs == 0)
			num_docs = 1;
		System.out.println("[BookIndex] Avg words per doc: " + 1.0 * total_words / num_docs);
 	}
	
	private void addDocument(String content) throws IOException {
        Document doc = new Document();
        doc.add(new TextField("contents", content, Field.Store.YES));
        index_writer.addDocument(doc);
	}
	
	public void close() throws IOException {
		index_writer.close();
		input.close();
	}
	
	public void flush() throws IOException {
		index_writer.commit();
	}
	
	public void flushAndClose() throws IOException {
		this.flush();
		this.close();
	}
	
	public static void main(String[] args) throws IOException {
		BookIndex indexer = new BookIndex("/home/sebisebi/data/indexes/arc_index", "/home/sebisebi/data/ARC_Corpus.txt");
		/*
		 * Results: (simple IR, not other optimizations like ET)
		 * (3, 1) => 40.64
		 * (10, 3) => 40.48
		 * (7, 3) => 40.68
		 * (7, 2) => 41.52
		 * (7, 2) + (6, 1) => 41.4    (Winner)
		 * (6, 1) => 41.12
		 * (12, 5) => 39.76
		 * (5, 2) => 39.92
		 * (4, 1) => 40.76
		 * (4, 1) + (8, 2) => (40.4)
		 * 
		 * For ARC Corpus you *should* filter by number of words (remove small sentences).
		 * There are very small, unrelated sentences, like: "To those women, I apologize.".
		 */
		indexer.run(1, 1);
		indexer.flushAndClose();
	}
}
