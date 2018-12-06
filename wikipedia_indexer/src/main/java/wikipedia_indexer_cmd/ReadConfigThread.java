package wikipedia_indexer_cmd;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;
import wikipedia_indexer_cmd.GeneralConfig;


public final class ReadConfigThread extends Thread {

	private GeneralConfig config = null;
	private int delay_ms = -1;
	
	public ReadConfigThread(GeneralConfig config2, int delay_ms) {
		this.config = config2;
		this.delay_ms = delay_ms;
		System.out.println("ReadConfigThread created.");
	}
	
	public void run() {
		boolean should_stop = false;
		
		while (!should_stop) {
			// Read configuration file.
			try {
				Scanner input = new Scanner(new File("resources/flags/should_stop_wiki_indexer.txt"));
				if (input.hasNextLine()) {
					String line = input.nextLine();
					if (line.equals("True") || line.equals("true"))
						should_stop = true;
				}
				input.close();
			} catch (FileNotFoundException e) {
				e.printStackTrace();
				should_stop = true;
			}
			
			// Wait for delay_ms before the next attempt.
			try {
				Thread.sleep(delay_ms);
			}
			catch (Exception e) {
				e.printStackTrace();
				should_stop = true;
			}
		}
		
		// Set should stop signal.
		System.out.println("Stopping ...");
		config.setStopSignal();
	}
}
