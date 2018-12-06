package wikipedia_indexer_cmd;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;

import wikipedia_indexer_cmd.WikipediaIndexer;
import wikipedia_indexer_cmd.GeneralConfig;

public class UpdateThread extends Thread {
	private WikipediaIndexer indexer = null;
	private GeneralConfig config = null;
	private int delay_ms = -1;
	
	public UpdateThread(WikipediaIndexer indexer, GeneralConfig config, int delay_ms) {
		this.indexer = indexer;
		this.config = config;
		this.delay_ms = delay_ms;
		System.out.print("UpdateThread created.\n");
	}
	
	public void run() {
		while (config.getStopSignal() == false) {
			// Open file for writing and write.
			try {
				BufferedWriter out = new BufferedWriter(new FileWriter("resources/wikipedia_indexer/status.txt"));
				out.write("Visited " + indexer.getVisitedPages() + " pages.\n");
		        out.write("Analysed " + indexer.getVisitedCategories() + " categories.\n");
		        out.write("Queue size: " + indexer.getRemainingCategories() + "\n");
				out.flush();
				out.close();
				
			} catch (IOException e) {
				e.printStackTrace();
			}
	
			try {
				Thread.sleep(delay_ms);
			} catch (Exception e) {
				e.printStackTrace();
				break;
			}
		}
	}
}
