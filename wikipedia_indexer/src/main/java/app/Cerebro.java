package app;

import app.AnswerThread;
import config.ConfigPaths;
import data.QuestionDB;
import data.QuestionsProtos.Answer;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.QuestionDataSet;

import java.util.Random;

import java.awt.EventQueue;
import javax.swing.JFrame;
import javax.swing.JTextArea;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.JTextField;
import javax.swing.JButton;
import java.awt.event.ActionListener;
import java.awt.event.WindowEvent;
import java.awt.event.ActionEvent;
import javax.swing.JSlider;
import java.awt.Font;
import javax.swing.JLabel;
import javax.swing.SwingConstants;
import javax.swing.JProgressBar;

public class Cerebro {

	private static final boolean DEBUG = true;
	
	private QuestionDataSet question_set = null;
	private Random rnd = null;
	private AnswerThread answer_thread = null;
	
	private JFrame frame;
	
	private JTextArea question_textbox = null;
	private String question_text = "";
	
	private String answer1_text = "";
	private String answer2_text = "";
	private String answer3_text = "";
	private String answer4_text = "";
	
	private JTextField answer1_textfield = null;
	private JTextField answer2_textfield = null;
	private JTextField answer3_textfield = null;
	private JTextField answer4_textfield = null;
	
	private JButton submit_button = null;
	private JButton random_button = null;
	
	private JSlider slider1 = null;
	private JSlider slider2 = null;
	private JSlider slider3 = null;
	private JSlider slider4 = null;
	
	private JProgressBar progress_bar = null;
	private JLabel correct_answer_label = null;
	
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					Cerebro window = new Cerebro();
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
	public Cerebro() {
		/* Firstly, read all the questions from the easy data set. */
		question_set = QuestionDB.loadDataSet(ConfigPaths.ARC_EASY_VAL_DATASET_PATH.toString());
		if (DEBUG) {
			System.out.println("Loaded question dataset: " + question_set.getDescription() + " (" + question_set.getPurpose() + ").");
		}
		
		/* Seed the number generator. */
		rnd = new Random();
		
		/* Start answering thread. */
		answer_thread = new AnswerThread();
		answer_thread.start();
		
		/* Run application (and event queue). */
		initialize();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frame = new JFrame();
		frame.setBounds(100, 100, 740, 450);
		frame.setTitle("Multi-choice question answering");
		frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frame.getContentPane().setLayout(null);
		frame.addWindowListener(new java.awt.event.WindowAdapter() {
			public void windowClosing(WindowEvent winEvt) {
				answer_thread.set_should_stop();
				answer_thread.fire_event();
				try {
					answer_thread.join();
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
		    }
		});
		  
		question_textbox = new JTextArea();
		question_textbox.setFont(new Font("Dialog", Font.PLAIN, 14));
		question_textbox.getDocument().addDocumentListener(new DocumentListener() {
			@Override
	        public void removeUpdate(DocumentEvent e) {
				question_text = question_textbox.getText();
	        }

	        @Override
	        public void insertUpdate(DocumentEvent e) {
	        	question_text = question_textbox.getText();
	        }

	        @Override
	        public void changedUpdate(DocumentEvent e) {
	        	question_text = question_textbox.getText();
	        }
		});
		
		question_textbox.setToolTipText("Insert question here");
		question_textbox.setText("Question text");
		question_textbox.setRows(7);
		question_textbox.setLineWrap(true);
		question_textbox.setWrapStyleWord(true);
		question_textbox.setBounds(60, 67, 620, 75);
		frame.getContentPane().add(question_textbox);
		
		answer1_textfield = new JTextField();
		answer1_textfield.setBounds(60, 180, 500, 19);
		frame.getContentPane().add(answer1_textfield);
		answer1_textfield.setColumns(10);
		answer1_textfield.getDocument().addDocumentListener(new DocumentListener() {
			@Override
	        public void removeUpdate(DocumentEvent e) {
				answer1_text = answer1_textfield.getText();
	        }

	        @Override
	        public void insertUpdate(DocumentEvent e) {
	        	answer1_text = answer1_textfield.getText();
	        }

	        @Override
	        public void changedUpdate(DocumentEvent e) {
	        	answer1_text = answer1_textfield.getText();
	        }
		});
		
		answer2_textfield = new JTextField();
		answer2_textfield.setBounds(60, 220, 500, 19);
		frame.getContentPane().add(answer2_textfield);
		answer2_textfield.setColumns(10);
		answer2_textfield.getDocument().addDocumentListener(new DocumentListener() {
			@Override
	        public void removeUpdate(DocumentEvent e) {
				answer2_text = answer2_textfield.getText();
	        }

	        @Override
	        public void insertUpdate(DocumentEvent e) {
	        	answer2_text = answer2_textfield.getText();
	        }

	        @Override
	        public void changedUpdate(DocumentEvent e) {
	        	answer2_text = answer2_textfield.getText();
	        }
		});
		
		answer3_textfield = new JTextField();
		answer3_textfield.setBounds(60, 260, 500, 19);
		frame.getContentPane().add(answer3_textfield);
		answer3_textfield.setColumns(10);
		answer3_textfield.getDocument().addDocumentListener(new DocumentListener() {
			@Override
	        public void removeUpdate(DocumentEvent e) {
				answer3_text = answer3_textfield.getText();
	        }

	        @Override
	        public void insertUpdate(DocumentEvent e) {
	        	answer3_text = answer3_textfield.getText();
	        }

	        @Override
	        public void changedUpdate(DocumentEvent e) {
	        	answer3_text = answer3_textfield.getText();
	        }
		});
		
		answer4_textfield = new JTextField();
		answer4_textfield.setBounds(60, 300, 500, 19);
		frame.getContentPane().add(answer4_textfield);
		answer4_textfield.setColumns(10);
		answer4_textfield.getDocument().addDocumentListener(new DocumentListener() {
			@Override
	        public void removeUpdate(DocumentEvent e) {
				answer4_text = answer4_textfield.getText();
	        }

	        @Override
	        public void insertUpdate(DocumentEvent e) {
	        	answer4_text = answer4_textfield.getText();
	        }

	        @Override
	        public void changedUpdate(DocumentEvent e) {
	        	answer4_text = answer4_textfield.getText();
	        }
		});
		
		slider1 = new JSlider();
		slider1.setToolTipText("Prob(Answer = correct)");
		slider1.setBounds(572, 180, 117, 16);
		frame.getContentPane().add(slider1);
		
		slider2 = new JSlider();
		slider2.setToolTipText("Prob(Answer = correct)");
		slider2.setBounds(572, 220, 117, 16);
		frame.getContentPane().add(slider2);
		
		slider3 = new JSlider();
		slider3.setToolTipText("Prob(Answer = correct)");
		slider3.setBounds(572, 260, 117, 16);
		frame.getContentPane().add(slider3);
		
		slider4 = new JSlider();
		slider4.setToolTipText("Prob(Answer = correct)");
		slider4.setBounds(572, 300, 117, 16);
		frame.getContentPane().add(slider4);
		
		progress_bar = new JProgressBar();
		progress_bar.setValue(50);
		progress_bar.setBounds(60, 412, 135, 14);
		progress_bar.setVisible(false);
		
		slider1.setValue(0);
		slider2.setValue(0);
		slider3.setValue(0);
		slider4.setValue(0);
		
		answer_thread.set_slider(0, slider1);
		answer_thread.set_slider(1, slider2);
		answer_thread.set_slider(2, slider3);
		answer_thread.set_slider(3, slider4);
		answer_thread.set_progress_bar(progress_bar);
		
		submit_button = new JButton("Submit");
		submit_button.setBounds(60, 367, 135, 25);
		frame.getContentPane().add(submit_button);
		answer_thread.set_submit_button(submit_button);
		submit_button.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent ev) {
				submit_button.setEnabled(false);
				slider1.setValue(0);
				slider2.setValue(0);
				slider3.setValue(0);
				slider4.setValue(0);
				
				
				answer_thread.set_question(Question.newBuilder()
						.setQuestion(question_text)
						.setId("cerebro_test")
						.addAnswers(Answer.newBuilder()
								.setText(answer1_text)
								.setIsCorrect(false)
								.build())
						.addAnswers(Answer.newBuilder()
								.setText(answer2_text)
								.setIsCorrect(false)
								.build())
						.addAnswers(Answer.newBuilder()
								.setText(answer3_text)
								.setIsCorrect(false)
								.build())
						.addAnswers(Answer.newBuilder()
								.setText(answer4_text)
								.setIsCorrect(false)
								.build())
						.build());
				answer_thread.fire_event();
			}
		});
		
		random_button = new JButton("Pick random question");
		random_button.setBounds(227, 367, 200, 25);
		frame.getContentPane().add(random_button);
		
		correct_answer_label = new JLabel("");
		correct_answer_label.setHorizontalAlignment(SwingConstants.LEFT);
		correct_answer_label.setVerticalAlignment(SwingConstants.TOP);
		correct_answer_label.setBounds(546, 367, 180, 15);
		frame.getContentPane().add(correct_answer_label);
		
		frame.getContentPane().add(progress_bar);
		random_button.addActionListener(new ActionListener() {
			public void actionPerformed(ActionEvent ev) {
				if (question_set != null && rnd != null) {
					int len = question_set.getEntriesCount();
					int index = rnd.nextInt(len);
					Question q = question_set.getEntries(index);
					
					question_textbox.setText(q.getQuestion().trim());
					answer1_textfield.setText(q.getAnswers(0).getText().trim());
					answer2_textfield.setText(q.getAnswers(1).getText().trim());
					answer3_textfield.setText(q.getAnswers(2).getText().trim());
					answer4_textfield.setText(q.getAnswers(3).getText().trim());
					
					String correct = "";
					if (q.getAnswers(0).getIsCorrect()) {
						correct = "A";
					}
					else if (q.getAnswers(1).getIsCorrect()) {
						correct = "B";
					}
					else if (q.getAnswers(2).getIsCorrect()) {
						correct = "C";
					}
					else if (q.getAnswers(3).getIsCorrect()) {
						correct = "D";
					}
					
					correct_answer_label.setText("Correct answer is " + correct);
				}
			}
		});
	}
}
