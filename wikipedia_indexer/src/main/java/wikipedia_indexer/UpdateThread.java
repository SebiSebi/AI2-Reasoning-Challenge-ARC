package wikipedia_indexer;

import wikipedia_indexer.WikipediaIndexer;
import javax.swing.JTextArea;


public class UpdateThread extends Thread {
	private WikipediaIndexer indexer = null;
	private GeneralConfig config = null;
	private JTextArea textLog = null;
	
	public UpdateThread(WikipediaIndexer indexer, GeneralConfig config) {
		this.indexer = indexer;
		this.config = config;
		System.out.print("UpdateThread created.\n");
	}
	
	public void setTextLog(JTextArea textLog) {
		this.textLog = textLog;
	}
	
	public void run() {
		while (config.getStopSignal() == false) {
			if (textLog != null) {
				textLog.setText("Visited " + indexer.getVisitedPages() + " pages.\n");
	            textLog.append("Analysed " + indexer.getVisitedCategories() + " categories.\n");
	            textLog.append("Queue size: " + indexer.getRemainingCategories() + "\n");
			}
			
			try {
				Thread.sleep(2 * 1000);  // Every 2 seconds.
			}
			catch (Exception e) {
				e.printStackTrace();
			}
		}
	}
}
