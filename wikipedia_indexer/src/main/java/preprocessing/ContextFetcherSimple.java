package preprocessing;

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

import data.QuestionsProtos.Answer;
import data.QuestionsProtos.Question;
import data.QuestionsProtos.QuestionDataSet;
import utils.Pair;
import utils.Text;

public final class ContextFetcherSimple {

	private Question question = null;
	private Analyzer analyzer = null;
	private List <IndexSearcher> index_searchers = null;
	private List <Integer> top_n = null;
	
	/* It receives a list of <index_path, top_n> indexes. */
	public ContextFetcherSimple(Question question,
						  		List< Pair<String, Integer> > indexes) {
		this.question = question;
		
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
		if (this.question == null || this.analyzer == null)
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
	
	public QuestionDataSet run() throws ParseException, InvalidProtocolBufferException {
		if (!isValidState()) {
			throw new IllegalStateException("Invalid ContextFetcher state!");
		}
		
		QuestionDataSet questions = QuestionDataSet.newBuilder()
				.addEntries(question)
				.setDescription("Cerebro")
				.setPurpose(QuestionDataSet.Purpose.TEST)
				.build();
		System.out.println("Fetching contexts for " + questions.getDescription() + " dataset");
		System.out.println("Dataset purpose: " + questions.getPurpose());
		System.out.println("Total number of questions: " + questions.getEntriesCount() + ".\n");
		
		/* Build another protobuf with contexts added. */
		QuestionDataSet.Builder builder = QuestionDataSet.newBuilder(questions);
    	builder.clearEntries();  /* Keep description and purpose. */
    	
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
            
            Question.Builder question_builder = Question.newBuilder(question);
            question_builder.clearAnswers();  /* Keep question test and ID. */
           
            for (Answer answer: question.getAnswersList()) {
            	Pair <String, Double> res = fetchContext(question.getQuestion(), answer.getText());
            	String context = res.getFirst();
            	Double score = res.getSecond();
            	question_builder.addAnswers(Answer.newBuilder(answer).setContext(context).setTfIdfScore(score).build());
            }
            
            builder.addEntries(question_builder.build());
    	}
    	
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
	
	private String escapeForLucene(String phrase) {
		return QueryParser.escape(phrase).toLowerCase();
    }
	
	private Pair<String, Double> fetchContext(String question, String answer) {
		StringBuilder qbuilder = new StringBuilder();
		for (String term: Text.splitInWords(question)) {
			if (escapeForLucene(term).isEmpty())
				continue;
			qbuilder.append(escapeForLucene(term));
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
}
