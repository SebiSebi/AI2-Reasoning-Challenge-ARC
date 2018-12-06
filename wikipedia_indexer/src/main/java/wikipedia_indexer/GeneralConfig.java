package wikipedia_indexer;

public class GeneralConfig {

	private boolean stop_signal = false;
	
	public GeneralConfig () {
		stop_signal = false;
	}
	
	public synchronized void setStopSignal() {
		this.stop_signal = true;
	}
	
	public synchronized void clearStopSignal() {
		this.stop_signal = false;
	}
	
	public synchronized boolean getStopSignal() {
		return this.stop_signal;
	}
}
