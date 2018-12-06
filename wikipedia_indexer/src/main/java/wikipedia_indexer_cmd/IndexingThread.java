package wikipedia_indexer_cmd;

import java.io.IOException;
import wikipedia_indexer_cmd.WikipediaIndexer;


public class IndexingThread extends Thread {
	private WikipediaIndexer indexer = null;
	
	public IndexingThread(WikipediaIndexer indexer) {
		this.indexer = indexer;
		System.out.println("IndexingThread created.\n");
	}
	
	public void run() {
		try {
			this.indexer.startIndexing();
		} catch (IOException e) {
			e.printStackTrace();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
}
