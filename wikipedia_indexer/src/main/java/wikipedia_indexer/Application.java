package wikipedia_indexer;

import java.awt.EventQueue;

import javax.swing.JFrame;
import javax.swing.JOptionPane;

import javax.swing.JButton;
import java.awt.event.ActionListener;
import java.awt.event.ActionEvent;
import javax.swing.JLabel;
import javax.swing.JTextField;
import javax.swing.JTextArea;
import java.awt.Font;

public class Application {
	static private WikipediaIndexer indexer = null;
	static private UpdateThread update_thread = null;
	static private IndexingThread indexing_thread = null;
	static private GeneralConfig config = null;
	
	private JFrame frame;
	private boolean indexing_started = false;
	private JTextField txtIndexing;
	private JButton btnStartIndexing, btnStopIndexing;
	private JTextArea textLog = null;
	
	
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		config = new GeneralConfig();
		indexer = new WikipediaIndexer("/home/sebisebi/wikipedia_dumps/lucene_index", config);
		update_thread = new UpdateThread(indexer, config);
		indexing_thread = new IndexingThread(indexer);
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					Application window = new Application();
					window.frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public Application() {
		initialize();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frame = new JFrame();
		frame.setBounds(100, 100, 450, 300);
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.getContentPane().setLayout(null);
		
		btnStartIndexing = new JButton("Start indexing");
		btnStartIndexing.setBounds(83, 201, 145, 37);
		frame.getContentPane().add(btnStartIndexing);
		
		btnStopIndexing = new JButton("Stop indexing");
		btnStopIndexing.setEnabled(false);
		btnStopIndexing.setBounds(258, 201, 145, 37);
		frame.getContentPane().add(btnStopIndexing);
		
		JLabel lblIndexing = new JLabel("Indexing:");
		lblIndexing.setBounds(33, 37, 70, 15);
		frame.getContentPane().add(lblIndexing);
		
		txtIndexing = new JTextField();
		txtIndexing.setText("False");
		txtIndexing.setBounds(104, 35, 114, 19);
		frame.getContentPane().add(txtIndexing);
		txtIndexing.setColumns(10);
		
		textLog = new JTextArea();
		textLog.setFont(new Font("Utopia", Font.PLAIN, 18));
		textLog.setBounds(12, 77, 426, 112);
		frame.getContentPane().add(textLog);
		
		btnStartIndexing.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent ev) {
				if (indexing_started) {
					JOptionPane.showMessageDialog(null, "Process already started!");
					return;
				}
				indexing_started = true;
				btnStartIndexing.setEnabled(false);
				
				/* Run all necessary threads. */
				update_thread.setTextLog(textLog);
				update_thread.start();
				indexing_thread.start();
				
				txtIndexing.setText("True");
				btnStopIndexing.setEnabled(true);
			}
		});
		
		btnStopIndexing.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent ev) {
				if (!indexing_started) {
					JOptionPane.showMessageDialog(null, "Process has not started yet!");
					return;
				}
				indexing_started = false;
				btnStopIndexing.setEnabled(false);
				
				config.setStopSignal();
				
				try {
					update_thread.join();
					indexing_thread.join();
					txtIndexing.setText("Done!");
					textLog.append("\n Done!");
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
		});
	}
}
