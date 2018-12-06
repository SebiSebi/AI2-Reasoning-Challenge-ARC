package wikipedia_indexer;

import java.io.IOException;

public class IndexingThread extends Thread {
	private WikipediaIndexer indexer = null;
	
	public IndexingThread(WikipediaIndexer indexer) {
		this.indexer = indexer;
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
