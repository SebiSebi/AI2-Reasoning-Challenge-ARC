package wikipedia_indexer_cmd;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;

import de.tudarmstadt.ukp.wikipedia.api.Page;

final class WikipediaParagraphIndexer extends WikipediaIndexer {
	public WikipediaParagraphIndexer(String indexPath, GeneralConfig config) {
		super(indexPath, config);
	}

	protected void indexPage(IndexWriter writer, Page page) {
        try {
            String content = page.getPlainText();
            String title = page.getTitle().getPlainTitle();
            String uri = "https://en.wikipedia.org/wiki/" + page.getTitle().getWikiStyleTitle();

            // index each paragraph separately
            for(String paragraph : content.split("\n")) {
                if(paragraph.split("\\ ").length < 6) {
                    continue; // skip short paragraphs
                }
                
                Document doc = new Document();

                doc.add(new StringField("title", title, Field.Store.YES));
                doc.add(new StringField("uri", uri, Field.Store.YES));
                doc.add(new TextField("contents", paragraph, Field.Store.YES));

                writer.addDocument(doc);
            }

        }
        catch (Exception e) {
        	System.out.println("Failed to parse Wikipedia Page!");
        	e.printStackTrace();
        }
    }
}
