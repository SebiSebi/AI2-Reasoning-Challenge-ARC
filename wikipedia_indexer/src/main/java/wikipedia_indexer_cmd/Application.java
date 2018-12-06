package wikipedia_indexer_cmd;

import org.apache.log4j.BasicConfigurator;
import org.apache.log4j.PropertyConfigurator;

import wikipedia_indexer_cmd.GeneralConfig;
import wikipedia_indexer_cmd.IndexingThread;
import wikipedia_indexer_cmd.ReadConfigThread;
import wikipedia_indexer_cmd.UpdateThread;
import wikipedia_indexer_cmd.WikipediaIndexer;


public class Application {
	public static void main(String[] args) {
		System.out.println("\n\t\t***** Runnnig wikipedia_indexer_cmd.Application *****\n");
		BasicConfigurator.configure();
		PropertyConfigurator.configure("resources/log4j.properties");
		
		GeneralConfig config = new GeneralConfig();
		WikipediaIndexer wikipedia_indexer = new WikipediaArticleIndexer("/home/sebisebi/wikipedia_dumps/test", config);
		ReadConfigThread read_config_thread = new ReadConfigThread(config, 2000);
		UpdateThread update_thread = new UpdateThread(wikipedia_indexer, config, 1000);
		IndexingThread indexing_thread = new IndexingThread(wikipedia_indexer);
		
		/* Print some runtime statistics. */
		Runtime runtime = Runtime.getRuntime();
		System.out.println("************************************");
		System.out.println("Available processors: " + runtime.availableProcessors());
		System.out.println("Maximum heap size: " + (runtime.maxMemory() / (1024 * 1024)) + "MB");
		System.out.println("************************************\n");
		
		/* Start working threads. */
		read_config_thread.start();
		update_thread.start();
		indexing_thread.start();
		
		try {
			read_config_thread.join();
			update_thread.join();
			indexing_thread.join();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
}
