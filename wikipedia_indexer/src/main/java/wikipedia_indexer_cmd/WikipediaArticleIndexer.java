package wikipedia_indexer_cmd;

import utils.Text;
import java.util.List;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;

import de.tudarmstadt.ukp.wikipedia.api.Page;

final class WikipediaArticleIndexer extends WikipediaIndexer {

	public WikipediaArticleIndexer(String indexPath, GeneralConfig config) {
		super(indexPath, config);
	}

	protected void indexPage(IndexWriter writer, Page page) {
		try {
			String content = page.getPlainText();
			List<String> sentences = Text.splitInLines(content);
			StringBuilder article = new StringBuilder();
			int num_words = 0;
			for (String sentence: sentences) {
				if (sentence.split("\\s+").length <= 7) {
					continue;
				}
				if (sentence.trim().length() <= 20) {
					continue;
				}
				if (sentence.trim().charAt(0) == '[') {
					continue;
				}
				article.append(sentence);
				num_words += sentence.split("\\s+").length;
			}
			content = article.toString();
			if (num_words <= 30)
				return;
			
            String title = page.getTitle().getPlainTitle();
            String uri = "https://en.wikipedia.org/wiki/" + page.getTitle().getWikiStyleTitle();

            Document doc = new Document();

            doc.add(new StringField("title", title, Field.Store.YES));
            doc.add(new StringField("uri", uri, Field.Store.YES));
            doc.add(new TextField("contents", content, Field.Store.YES));

            writer.addDocument(doc);
        }
        catch (Exception e) {
        	System.out.println("Failed to parse Wikipedia Page!");
        	e.printStackTrace();
        }
    }
}
