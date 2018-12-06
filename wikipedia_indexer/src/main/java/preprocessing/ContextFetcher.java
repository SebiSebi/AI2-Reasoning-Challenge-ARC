package preprocessing;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.en.EnglishAnalyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.NIOFSDirectory;

import com.google.protobuf.InvalidProtocolBufferException;
import com.google.protobuf.util.JsonFormat;

import clients.ETClient;
import clients.ETServiceProtos.ETScoresResponse;
import config.ConfigPaths;
import data.QuestionDB;
import data.QuestionsProtos.Answer;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.QuestionDataSet;
import utils.Text;
import utils.Pair;

/**
 * Given a data set in protobuf format, expand it with contexts fetched
 * from the best source available. Fetching strategy may change over time.
 * Below is a history of various types:
 * 		1) Wikipedia indexed by paragraphs with Lucene StandardAnalyzer.
 * 		2) Book collection (7 sentences) with query boosting (essentialness).
 */
public final class ContextFetcher {

	private String dataset_path = null;
	private Analyzer analyzer = null;
	private List <IndexSearcher> index_searchers = null;
	private List <Integer> top_n = null;
	
	/* It receives a list of <index_path, top_n> indexes. */
	public ContextFetcher(String dataset_path,
						  List< Pair<String, Integer> > indexes) {
		this.dataset_path = dataset_path;
		
		analyzer = new EnglishAnalyzer();
		index_searchers = new ArrayList <IndexSearcher>();
		top_n = new ArrayList <Integer>();
		
        try {
        	for (Pair<String, Integer> index: indexes) {
	        	IndexReader reader = DirectoryReader.open(NIOFSDirectory.open(Paths.get(index.getFirst())));
	            index_searchers.add(new IndexSearcher(reader));
	            top_n.add(index.getSecond());
        	}
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        System.out.println("Using " + index_searchers.size() + " indexes.");
        for (int i = 0; i < index_searchers.size(); i++) {
        	String index_path = indexes.get(i).getFirst();
        	Integer num_docs = index_searchers.get(i).getIndexReader().numDocs();
        	System.out.println("\tIndex path: " + index_path + " (" + num_docs + " documents).");
        }
        System.out.println("");
        
        if (analyzer instanceof StandardAnalyzer) {
        	System.out.println("Indexing with standard analyzer.");
        }
        else if (analyzer instanceof EnglishAnalyzer) {
        	System.out.println("Indexing with English analyzer.");
        }
	}
	
	private boolean isValidState() {
		if (this.dataset_path == null || this.analyzer == null)
			return false;
		if (this.index_searchers.isEmpty())
			return false;
		
		for (IndexSearcher x: this.index_searchers) {
			if (x == null)
				return false;
		}
		
		if (this.index_searchers.size() != this.top_n.size())
			return false;
		for (Integer x: this.top_n) {
			if (x <= 0)
				return false;
		}
		
		return true;
	}
	
	private int getNumberOfCorrectAnswers(Question question) {
		int count = 0;
	    for (Answer answer: question.getAnswersList()) {
	    	if (answer.getIsCorrect())
	    		count++;
	    }
	    return count;
	}    
	
	public QuestionDataSet run() throws ParseException, InvalidProtocolBufferException {
		if (!isValidState()) {
			throw new IllegalStateException("Invalid ContextFetcher state!");
		}
		
		QuestionDataSet questions = QuestionDB.loadDataSet(dataset_path);
		System.out.println("Fetching contexts for " + questions.getDescription() + " dataset");
		System.out.println("Dataset purpose: " + questions.getPurpose());
		System.out.println("Total number of questions: " + questions.getEntriesCount() + ".\n");
		
		ETScoresResponse data = ETClient.getETScores(questions);
		if (data == null || data.getEntriesCount() != questions.getEntriesCount()) {
			System.err.println("\nCannot fetch essentialness scores!");
			return null;
		}
		
		/* Augment Question data set with essentialness scores. */
		questions = augmentWithScores(questions, data);
		if (questions == null) {
			System.err.println("Failed to augment dataset with scores.");
			return null;
		}
		System.out.println("Done augmenting data with essentialness scores.\n");
		
		/* Build another protobuf with contexts added. */
		QuestionDataSet.Builder builder = QuestionDataSet.newBuilder(questions);
    	builder.clearEntries();  /* Keep description and purpose. */
    	
    	int num_processed = 0;
    	int empty_contexts = 0;
    	for (Question question : questions.getEntriesList()) {
    		if (question.getQuestion().isEmpty()) {
             	throw new ParseException("Found empty question!");
            }
    		if (question.getId().isEmpty()) {
             	throw new ParseException("Found empty question ID!");
            }
            if (question.getAnswersCount() != 4) {
            	throw new ParseException("Incorrect number of answers!");
            }
            if (getNumberOfCorrectAnswers(question) != 1) {
            	throw new ParseException("Incorrect number of correct answers!");
            }
            
            Question.Builder question_builder = Question.newBuilder(question);
            question_builder.clearAnswers();  /* Keep question test and ID. */
           
            for (Answer answer: question.getAnswersList()) {
            	Pair <String, Double> res = fetchContext(question.getQuestion(), answer.getText(), question.getEtScoresMap());
            	String context = res.getFirst();
            	Double score = res.getSecond();
            	if (context.isEmpty())
            		empty_contexts++;
            	question_builder.addAnswers(Answer.newBuilder(answer).setContext(context).setTfIdfScore(score).build());
            }
            
            builder.addEntries(question_builder.build());
            
            num_processed++;
            if (num_processed % 50 == 0) {
            	System.out.println("Processed " + num_processed + " questions.");
            }
            // break;
    	}
    	
    	System.out.println("Found " + empty_contexts + " empty contexts");
    	
    	QuestionDataSet augmented_dataset = builder.build();
    	checkSimilarDatasets(questions, augmented_dataset);
    	return augmented_dataset;
	}

	private void checkSimilarDatasets(QuestionDataSet d1, QuestionDataSet d2) {
		if (d1.getEntriesCount() != d2.getEntriesCount()) {
			throw new IllegalStateException("Different num questions in datasets!");
		}
		
		for (int i = 0; i < d1.getEntriesCount(); i++) {
			Question q1 = d1.getEntries(i);
			Question q2 = d2.getEntries(i);
			
			if (!q1.getQuestion().equals(q2.getQuestion())) {
				throw new IllegalStateException("Different questions in datasets!");
			}
			if (!q1.getId().equals(q2.getId())) {
				throw new IllegalStateException("Different question IDs in datasets!");
			}
			
			for (int j = 0; j < 4; j++) {
				Answer a1 = q1.getAnswers(j);
				Answer a2 = q2.getAnswers(j);
				
				if (!a1.getText().equals(a2.getText())) {
					throw new IllegalStateException("Different answers in question!");
				}
				if (a1.getIsCorrect() != a2.getIsCorrect()) {
					throw new IllegalStateException("Different answers in question!");
				}
			}
		}
		
		System.out.println("\nAugmented dataset seems OK.\n");
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
	
	private String escapeForLucene(String phrase) {
		return QueryParser.escape(phrase).toLowerCase();
    }
	
	private Pair<String, Double> fetchContext(String question, String answer, Map <String, Double> scores) {
		StringBuilder qbuilder = new StringBuilder();
		for (String term: Text.splitInWords(question)) {
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
			return Pair.makePair("", 0.0);
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
        	return Pair.makePair("", 0.0);
        }
        if (processedQuestion.length() <= 2) {
        	return Pair.makePair("", 0.0);
        }
        
        String query_string;
        if (processedAnswer.length() <= 2)
        	query_string = processedQuestion;
        else
        	query_string = processedQuestion + " AND " + processedAnswer;
        
        QueryParser queryParser = new QueryParser("contents", analyzer);
        StringBuilder sb = new StringBuilder();
        double scores_sum = 0.0;
        int num_scores = 0;
		try {
			for (int i = 0; i < index_searchers.size(); i++) {
				final IndexSearcher index_searcher = index_searchers.get(i);
				final Integer max_num_docs = top_n.get(i);
				
				final Query query = queryParser.parse(query_string);
				final TopDocs hits = index_searcher.search(query, max_num_docs);
				
				if (hits.scoreDocs.length == 0) {
					continue;
				}
				if (hits.scoreDocs.length > max_num_docs) {
					throw new IllegalStateException("Index searcher returned more documents than requested!");
				}
				
				// Compute average TF-IDF scores (best scores only).
				scores_sum += hits.getMaxScore();
				num_scores += 1;
				
				for (final ScoreDoc hit: hits.scoreDocs) {
					Document doc = index_searcher.doc(hit.doc);
					String content = doc.getFields().get(0).stringValue().trim();
					
					sb.append(content);
					sb.append(' ');
				}
			}
		} catch (ParseException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		if (num_scores == 0)
			num_scores = 1;

		return Pair.makePair(sb.toString().trim(), 1.0 * scores_sum / num_scores);
	}
	
	public static void main(String[] args) throws ParseException, IOException {
		List< Pair <String, Integer> > indexes = new ArrayList< Pair <String, Integer> >();
		indexes.add(Pair.makePair(ConfigPaths.BOOK_INDEX_PATH.toString(), 1));
		indexes.add(Pair.makePair(ConfigPaths.ARC_INDEX_PATH.toString(), 1));
		ContextFetcher context_fetcher = new ContextFetcher(
				ConfigPaths.ARC_CHALLENGE_VAL_DATASET_PATH.toString(),
				indexes
		);

		QuestionDataSet dataset = context_fetcher.run();
		
		/* Save data set in JSON format. */
		FileWriter output = new FileWriter(new File("resources/test.json"));
		String json = JsonFormat.printer().print(dataset);
    	output.write(json);
    	output.flush();
		output.close();
	}
}
