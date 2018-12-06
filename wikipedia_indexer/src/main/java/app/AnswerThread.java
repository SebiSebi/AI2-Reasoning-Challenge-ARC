package app;

import data.QuestionsProtos.Question;
import data.QuestionsProtos.QuestionDataSet;
import preprocessing.ContextFetcherSingle;
import preprocessing.ContextFetcherSimple;
import utils.Pair;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Semaphore;

import javax.swing.JButton;
import javax.swing.JProgressBar;
import javax.swing.JSlider;

import org.apache.lucene.queryparser.classic.ParseException;

import com.google.protobuf.InvalidProtocolBufferException;

import clients.AnswerClient;
import config.ConfigPaths;

final class AnswerThread extends Thread {
	
	private boolean should_stop;
	private Semaphore sem = null;
	private Question q = null;
	private JButton submit_button = null;
	private ArrayList<JSlider> sliders = null;
	private JProgressBar progress_bar = null;
	
	public AnswerThread() {
		should_stop = false;
		sem = new Semaphore(0);
		sliders = new ArrayList<JSlider>();
		sliders.add(null);  // answer A
		sliders.add(null);  // answer B
		sliders.add(null);  // answer C
		sliders.add(null);  // answer D
	}
	
	private synchronized boolean should_stop() {
		return this.should_stop;
	}
	
	public synchronized void set_should_stop() {
		this.should_stop = true;
	}
	
	public synchronized void set_question(Question q) {
		this.q = q;
	}
	
	public void set_submit_button(JButton submit_button) {
		this.submit_button = submit_button;
	}
	
	public void set_slider(int index, JSlider slider) {
		sliders.set(index, slider);
	}
	
	public void set_progress_bar(JProgressBar progress_bar) {
		this.progress_bar = progress_bar;
	}
	
	public synchronized void fire_event() {
		sem.release();
	}
	
	public void run() {
		synchronized(System.out) {
			System.out.println("Answering thread running.");
		}
		
		while (!this.should_stop()) {
			try {
				sem.acquire();
			} catch (InterruptedException e) {
				continue;
			}
			
			if (this.should_stop()) { 
				break;
			}
			
			/* A new question event. */
			progress_bar.setVisible(true);
			progress_bar.setValue(10);
			
			List< Pair <String, Integer> > indexes = new ArrayList< Pair <String, Integer> >();
			indexes.add(Pair.makePair(ConfigPaths.BOOK_INDEX_PATH.toString(), 1));
			indexes.add(Pair.makePair(ConfigPaths.ARC_INDEX_PATH.toString(), 1));
			
			QuestionDataSet dataset = null;
			try {
				dataset = new ContextFetcherSingle(q, indexes).run();
			} catch (InvalidProtocolBufferException e) {
				e.printStackTrace();
			} catch (ParseException e) {
				e.printStackTrace();
			}
			
			progress_bar.setValue(65);
			
			if (dataset != null) {
				System.out.println(dataset.getEntries(0));
				System.out.println(dataset.getEntries(0).getEtScoresMap());
				System.out.println("");
				
				List<Double> scores = AnswerClient.predict(dataset);
				progress_bar.setValue(100);
				
				if (scores == null) {
					System.err.println("Cannot connect to Cerebro");
				}
				else if (scores.size() != 4) {
					System.err.println("Expected 4 scores from Cerebro. Received " + scores.size() + ".");
				}
				else {
					System.out.println(scores);
					for (int i = 0; i < 4; i++) {
						sliders.get(i).setValue((int)(scores.get(i) * 100.0));
					}
				}
			}
			
			progress_bar.setVisible(false);
			submit_button.setEnabled(true);
		}
		
		synchronized(System.out) {
			System.out.println("Stopping answering thread ...");
		}
	}
}
