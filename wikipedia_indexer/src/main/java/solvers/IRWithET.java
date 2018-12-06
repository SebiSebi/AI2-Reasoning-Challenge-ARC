package solvers;

import data.QuestionsProtos.QuestionDataSet;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.Answer;
import clients.ETClient;
import clients.ETServiceProtos.ETScoresResponse;
import utils.charts.LineChart;
import utils.Pair;
import utils.Text;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.CompletionService;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorCompletionService;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.NIOFSDirectory;


public final class IRWithET extends Solver {
	
	private Analyzer analyzer = null;
	private IndexSearcher index_searcher = null;
	private Integer num_workers = null;
	
	private Type type = null;
	private Double fixed_threshold = null;
	
	public enum Type {
		DISPLAY_LOWER_THERSHOLD_LIMIT_GRAPH,  /* Accuracy versus terms(essentialness >= threshold). */
		FIXED_THRESHOLD_QUERY,  /* Given a fixed threshold, compute accuracy for terms(essentialness >= fixed_threshold). */
		BOOSTED_QUERY  /* Term's essentialness is fed into Lucene Query as a boosting factor. */
	}
	
	private IRWithET(String index_path, Type type, Integer num_workers, Double fixed_threshold) {
		this.type = type;
		this.num_workers = num_workers;
		this.fixed_threshold = fixed_threshold;
		
		analyzer = new EnglishAnalyzer();
		
        try {
        	IndexReader reader = DirectoryReader.open(NIOFSDirectory.open(Paths.get(index_path)));
            index_searcher = new IndexSearcher(reader);
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        System.out.println("Solver: Wikipedia IR with essential terms.");
        System.out.println("Index path: " + index_path);
        if (analyzer instanceof StandardAnalyzer) {
        	System.out.println("Indexing with standard analyzer.");
        }
        else if (analyzer instanceof EnglishAnalyzer) {
        	System.out.println("Indexing with English analyzer.");
        }
        System.out.println("Using " + this.num_workers + " threads.\n");
	}
	
	public static final class Builder {
		private final static Integer DEFAULT_NUM_WORKERS = 10;
		
		private String index_path = null;
		private Type type = null;
        private Integer num_workers = null;
        private Double fixed_threshold = null;
        
		public Builder () {
			index_path = null;
			type = null;
			num_workers = DEFAULT_NUM_WORKERS;
			fixed_threshold = null;
		}
		
		public Builder withType(Type type) {
			this.type = type;
			return this;
		}
		
		public Builder withIndex(String index_path) {
			this.index_path = index_path;
			return this;
		}
		
		public Builder withNumWorkers(Integer num_workers) {
			this.num_workers = num_workers;
			return this;
		}
		
		public Builder withFixedThreshold(Double fixed_threshold) {
			this.fixed_threshold = fixed_threshold;
			return this;
		}
		
		public IRWithET build() {
			if (index_path == null) {
				throw new IllegalStateException("Index path not set!");
			}
			if (type == null) {
				throw new IllegalStateException("Type not set!");
			}
			
			if (type == Type.FIXED_THRESHOLD_QUERY && fixed_threshold == null) {
				throw new IllegalStateException("Fixed threshold not set!");
			}
			
			return new IRWithET(index_path, type, num_workers, fixed_threshold);
		}
	}
	
	@Override
	public void clear() {
		if (index_searcher != null) {
			try {
				index_searcher.getIndexReader().close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
	}
	
	@Override
	protected Map<String, Integer> solve(QuestionDataSet data_set) {
		if (analyzer == null || index_searcher == null)
			return null;
		
		ETScoresResponse data = ETClient.getETScores(data_set);
		if (data == null || data.getEntriesCount() != data_set.getEntriesCount()) {
			System.err.println("\nCannot fetch essentialness scores!");
			return null;
		}
		
		/* Augment Question data set with essentialness scores. */
		data_set = augmentWithScores(data_set, data);
		if (data_set == null) {
			System.err.println("Failed to augment dataset with scores.");
			return null;
		}
		System.out.println("Done augmenting data with essentialness scores.\n");
		
		switch(this.type) {
			case DISPLAY_LOWER_THERSHOLD_LIMIT_GRAPH:
				double step = 0.02;
				ArrayList<Double> thresholds = new ArrayList<Double>();
				ArrayList<Double> accs = new ArrayList<Double>();
				for (double threshold = 0; threshold <= 1.0; threshold += step) {
					Pair<Double, Map<String, Integer> > local_res = solveWithThreshold(data_set, threshold);
					if (local_res == null) {
						thresholds.add(threshold);
						accs.add(-0.5);
					}
					else {
						thresholds.add(threshold);
						accs.add(local_res.getFirst());
					}
				}
				
				for (int i = 0; i < thresholds.size(); i++) {
					System.out.println("WikipediaWithET local result (" + thresholds.get(i) + ", " + accs.get(i) + ")");
				}
				
				LineChart<Double> chart = new LineChart<Double>(
				         "Accuracy vs ET threshold" ,
				         null,
				         "Essentialness Threshold",
				         "Acc",
				         (Double[])thresholds.toArray(new Double[] {}),
				         (Double[])accs.toArray(new Double[] {})
				);
				chart.display();

				return null;
			
			case FIXED_THRESHOLD_QUERY:
			case BOOSTED_QUERY:
				System.out.println("Threshold fixed at " + this.fixed_threshold);
				Pair<Double, Map<String, Integer> > res = solveWithThreshold(data_set, this.fixed_threshold);
				if (res == null)
					return null;
				return res.getSecond();
			default:
				throw new IllegalStateException("Invalid IRWithET.Type set. Default reached.");
		}
	}
	
	private QuestionDataSet augmentWithScores(QuestionDataSet data_set, ETScoresResponse scores) {
		if (data_set.getEntriesCount() != scores.getEntriesCount())
			return null;
		
		for (int i = 0; i < data_set.getEntriesCount(); i++) {
			if (!data_set.getEntries(i).getQuestion().equals(scores.getEntries(i).getQuestion())) {
				return null;
			}
		}
		
		List<Question> questions = data_set.getEntriesList();
		QuestionDataSet.Builder dataset_builder = data_set.toBuilder();
		dataset_builder.clearEntries();
		
		for (int i = 0; i < scores.getEntriesCount(); i++) {
			ETScoresResponse.Entry entry = scores.getEntries(i);
			Question.Builder builder = questions.get(i).toBuilder();
			
			builder.putAllEtScores(entry.getScoresMap());
			
			dataset_builder.addEntries(builder.build());
		}
		
		QuestionDataSet new_data_set = dataset_builder.build();
		if (new_data_set.getEntriesCount() != data_set.getEntriesCount())
			return null;
		
		for (int i = 0; i < data_set.getEntriesCount(); i++) {
			if (!data_set.getEntries(i).getQuestion().equals(new_data_set.getEntries(i).getQuestion())) {
				return null;
			}
			if (!data_set.getEntries(i).getAnswersList().equals(new_data_set.getEntries(i).getAnswersList())) {
				return null;
			}
		}
		return new_data_set;
	}
	
	private Pair<Double, Map<String, Integer> > solveWithThreshold(QuestionDataSet data_set, Double threshold) {
		List <Question> questions = data_set.getEntriesList();
		
		/* Prepare executors and data. */
		ExecutorService executor = Executors.newFixedThreadPool(num_workers);
		CompletionService<Pair <Pair<Integer, Integer>, Map<String, Integer> > > executor_service = new ExecutorCompletionService<Pair <Pair<Integer, Integer>, Map<String, Integer> > >(executor);
		List <List<Question> > tasks = new ArrayList <List<Question> >();
		int start_index = 0, num_questions = questions.size();
		int chunk_size = num_questions / num_workers;
		for (int worker = 1; worker <= num_workers; worker++) {
			List <Question> split = new ArrayList <Question> ();
			int end_index = start_index + chunk_size - 1;
			if (end_index >= num_questions)
				end_index = num_questions - 1;
			if (worker == num_workers)  // Last worker
				end_index = num_questions - 1;
			
			for (int i = start_index; i <= end_index; i++)
				split.add(questions.get(i));
			
			start_index = end_index + 1;
			tasks.add(split);
		}
		
		/* Submit tasks. */
		for (int i = 1; i <= num_workers; i++) {
			executor_service.submit(new RunChunkWithET(tasks.get(i - 1), analyzer,
													   index_searcher, "Worker" + i, threshold,
													   this.type));
		}
		
		Map<String, Integer> predicted_answers = new HashMap<String, Integer>();
		int correct = 0;
		int total = 0;
		
		/* Wait for tasks to finish. */
		for (int i = 1; i <= num_workers; i++) {
			try {
				Future<Pair <Pair<Integer, Integer>, Map<String, Integer> > > result_future = executor_service.take();
				Pair <Pair<Integer, Integer>, Map<String, Integer> >  data = result_future.get();
				if (data != null) {
					correct += data.getFirst().getFirst();
					total += data.getFirst().getSecond();
					Map<String, Integer> results = data.getSecond();
					predicted_answers.putAll(results);
				}
			} catch (InterruptedException e) {
				e.printStackTrace();
			} catch (ExecutionException e) {
				e.printStackTrace();
			}
		}
		
		/* Stop all working threads. */
		executor.shutdown();
		try {
			executor.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		if (!executor.isTerminated()) {
			throw new IllegalStateException("Not all workers have been terminated!");
		}
		
		/* Check for integrity. */
		if (total != data_set.getEntriesCount()) {
			System.err.println("Got fewer predicted answers than expected!");
			return null;
		}
			
		for (Question entry: data_set.getEntriesList()) {
			String id = entry.getId();
			if (!predicted_answers.containsKey(id)) {
				System.err.println("Missing answer for question with id " + id);
				return null;
			}
		}
		
		if (predicted_answers.size() != data_set.getEntriesCount()) {
			System.err.println("Got fewer predicted answers than expected!");
			return null;
		}
		
		System.out.println("\nAll done. Processed " + data_set.getEntriesCount() + " questions.");
		System.out.println("Global accuracy: " + 100.0 * correct / data_set.getEntriesCount());
		return Pair.makePair(100.0 * correct / data_set.getEntriesCount(), predicted_answers);
	}
}


final class RunChunkWithET implements Callable <Pair <Pair<Integer, Integer>, Map<String, Integer> > > {
	private List <Question> questions = null;
	private Analyzer analyzer = null;
	private IndexSearcher index_searcher = null;
	private String name = null;
	private Double threshold = null;
	private IRWithET.Type type = null;
	
	public RunChunkWithET(List <Question> questions, Analyzer analyzer,
			              IndexSearcher index_searcher, String name, Double threshold,
			              IRWithET.Type type) {
		this.questions = questions;
		this.analyzer = analyzer;
		this.index_searcher = index_searcher;
		this.name = name;
		this.threshold = threshold;
		this.type = type;
	}
	
	public Pair <Pair<Integer, Integer>, Map<String, Integer> > call() throws Exception {
		Map<String, Integer> predicted_answers = new HashMap<String, Integer>();

		int correct = 0;
		int total = 0;
		for (Question entry: questions) {
			String id = entry.getId();
			List <String> question;
			if (entry.getTermsCount() >= 1) {
				question = entry.getTermsList();
			}
			else {
				question = Text.splitInWords(entry.getQuestion());
			}
			
			List<Answer> answers = entry.getAnswersList();
			if (answers.size() != 4) {
				System.err.println("Expected 4 answers!");
				return null;
			}
		
			List<Double> scores = new ArrayList<Double>();
			for (Answer answer: answers) {
				scores.add(getBestScore(question, answer.getText(), entry.getEtScoresMap(), threshold));
				// scores.add(Math.random());
			}
			
			int chosen_answer = -1;
			Double best_score = null;
			for (int i = 0; i < 4; i++) {
				if (best_score == null || scores.get(i) > best_score) {
					best_score = scores.get(i);
					chosen_answer = i;
				}
			}
			
			if (answers.get(chosen_answer).getIsCorrect())
				correct++;
			predicted_answers.put(id, chosen_answer);
			
			total++;
			if (total % 10 == 0) {
				double acc = 100.0 * correct / total;
				synchronized(System.out) {
					System.out.println("[" + name + "] Processed " + total + " questions. Accuracy: " + acc);
				}
			}
		}
		if (total != questions.size())
			return null;
		
		System.out.println("[" + name + "] Worker accuracy: " + 100.0 * correct / total);
		
		return Pair.makePair(Pair.makePair(correct, total), predicted_answers);
	}

	private String eliminateAlphanum(String phrase) {
        return phrase.replaceAll("[^a-zA-Z0-9 ]", "").replaceAll(" +", " ").trim().toLowerCase();
    }
	
	private String escapeForLucene(String phrase) {
		return QueryParser.escape(phrase).toLowerCase();
		// ArrayList <String> to_replace = new ArrayList<String>(
		// 		Arrays.asList("+", "-", "&&", "||", "!", "(" ,")", "{", "}", "[", "]", "^", "\"", "~", "*", "?", ":", "\\"));
		//
		// for (String el: to_replace)
		// phrase = phrase.replace(el, "");
		// return phrase.trim();
    }
	
	private double getBestScore(List<String> question, String answer, Map <String, Double> scores,
								Double threshold) {
		if (this.type == IRWithET.Type.BOOSTED_QUERY) {
			StringBuilder qbuilder = new StringBuilder();
			for (String term: question) {
				if (!scores.containsKey(term)) {
					throw new NullPointerException();
				}
				if (escapeForLucene(term).isEmpty())
					continue;
				double score = scores.get(term);
				qbuilder.append(escapeForLucene(term));
				if (score >= 0.9)
					qbuilder.append("^4");
				else if (score >= 0.7)
					qbuilder.append("^2");
				qbuilder.append(' ');
			}
			String processedQuestion = qbuilder.toString().trim();
			
			if (processedQuestion.length() <= 2) {
				return Math.random();
			}
			
			StringBuilder abuilder = new StringBuilder();		
			for (String term: Text.splitInWords(answer)) {
				if (escapeForLucene(term).isEmpty())
					continue;
				abuilder.append(escapeForLucene(term));
				abuilder.append(' ');
			}
			String processedAnswer = abuilder.toString().trim();
	        
	        processedQuestion = "(" + processedQuestion + ")";
	        processedAnswer = "(" + processedAnswer + ")";
	        
	        if (processedAnswer.length() <= 2 && processedQuestion.length() <= 2) {
	        	return Math.random();
	        }
			if (processedQuestion.length() <= 2) {
				return Math.random();
			}
	     
	        String query_string;
	        if (processedAnswer.length() <= 2)
	        	query_string = processedQuestion;
	        else
	        	query_string = processedQuestion + " AND " + processedAnswer;
	        
	        QueryParser queryParser = new QueryParser("contents", analyzer);
			try {
				Query query = queryParser.parse(query_string);
				TopDocs hits = index_searcher.search(query, 1);
				return hits.getMaxScore();
			} catch (ParseException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		else {
			StringBuilder qbuilder = new StringBuilder();
			for (String term: question) {
				if (!scores.containsKey(term)) {
					throw new NullPointerException();
				}
				if (scores.get(term) >= threshold) {
					qbuilder.append(term);
					qbuilder.append(' ');
				}
			}
			String processedQuestion = qbuilder.toString().trim();
			
			if (processedQuestion.length() <= 2) {
				return Math.random();
			}
			
	        String processedAnswer = answer;
	
	        processedQuestion = eliminateAlphanum(processedQuestion);
	        processedAnswer = eliminateAlphanum(processedAnswer);
	        
	        processedQuestion = "(" + processedQuestion + ")";
	        processedAnswer = "(" + processedAnswer + ")";
	        
	        if (processedAnswer.length() <= 2 && processedQuestion.length() <= 2) {
	        	return Math.random();
	        }
			if (processedQuestion.length() <= 2) {
				return Math.random();
			}
			
	        String query_string;
	        if (processedAnswer.length() <= 2)
	        	query_string = processedQuestion;
	        else
	        	query_string = processedQuestion + " AND " + processedAnswer;
	        
	        QueryParser queryParser = new QueryParser("contents", analyzer);
			try {
				Query query = queryParser.parse(query_string);
				TopDocs hits = index_searcher.search(query, 1);
				return hits.getMaxScore();
			} catch (ParseException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
        
        return -1.0;
	}
	
}

