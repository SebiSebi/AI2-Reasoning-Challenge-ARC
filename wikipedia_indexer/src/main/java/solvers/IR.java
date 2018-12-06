package solvers;

import data.QuestionsProtos.QuestionDataSet;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.Answer;
import utils.Pair;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
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


public final class IR extends Solver {

	private final static Integer NUM_WORKERS = 10;
	
	private Analyzer analyzer = null;
	private IndexSearcher index_searcher = null;
	
	public enum WikiType {
		WIKI_GENERAL,
		WIKI_ENGLISH
	}
	
	public IR(WikiType wiki_type) {
		String index_path = null;
		if (wiki_type == WikiType.WIKI_GENERAL) {
			index_path = "/data/wikipedia/indexes/wikipedia_index";
			analyzer = new StandardAnalyzer();
		}
		else if (wiki_type == WikiType.WIKI_ENGLISH) {
			index_path = "/home/sebisebi/data/indexes/book_index";
			analyzer = new EnglishAnalyzer();
		}
		
        try {
        	IndexReader reader = DirectoryReader.open(NIOFSDirectory.open(Paths.get(index_path)));
            index_searcher = new IndexSearcher(reader);
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        System.out.println("Solver: Simple Wikipedia IR (without essential terms).");
        System.out.println("Index path: " + index_path);
        if (analyzer instanceof StandardAnalyzer) {
        	System.out.println("Indexing with standard analyzer.");
        }
        else if (analyzer instanceof EnglishAnalyzer) {
        	System.out.println("Indexing with English analyzer.");
        }
        System.out.println("Using " + NUM_WORKERS + " threads.\n");
	}
	
	@Override
	protected Map<String, Integer> solve(QuestionDataSet data_set) {
		if (analyzer == null || index_searcher == null)
			return null;
		
		List <Question> questions = data_set.getEntriesList();
		
		/* Prepare executors and data. */
		int num_workers = NUM_WORKERS;
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
			executor_service.submit(new RunChunk(tasks.get(i - 1), analyzer, index_searcher, "Worker" + i));
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
		return predicted_answers;
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
}


final class RunChunk implements Callable <Pair <Pair<Integer, Integer>, Map<String, Integer> > > {
	private List <Question> questions;
	private Analyzer analyzer = null;
	private IndexSearcher index_searcher = null;
	private String name;
	
	public RunChunk(List <Question> questions, Analyzer analyzer, IndexSearcher index_searcher, String name) {
		this.questions = questions;
		this.analyzer = analyzer;
		this.index_searcher = index_searcher;
		this.name = name;
	}
	
	public Pair <Pair<Integer, Integer>, Map<String, Integer> > call() throws Exception {
		Map<String, Integer> predicted_answers = new HashMap<String, Integer>();
		
		int correct = 0;
		int total = 0;
		for (Question entry: questions) {
			String id = entry.getId();
			String question = entry.getQuestion();
			List<Answer> answers = entry.getAnswersList();
			if (answers.size() != 4) {
				System.err.println("Expected 4 answers!");
				return null;
			}
		
			List<Double> scores = new ArrayList<Double>();
			for (Answer answer: answers) {
				scores.add(getBestScore(question, answer.getText()));
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
	
	private double getBestScore(String question, String answer) {
		String processedQuestion = question;
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
        
        return -1.0;
	}
	
}

