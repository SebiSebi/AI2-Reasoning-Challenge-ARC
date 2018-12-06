package data.processing.stages;

import data.processing.stages.PipelineStage;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.encryption.InvalidPasswordException;
import org.apache.pdfbox.text.PDFTextStripper;

import java.io.File;
import java.io.IOException;

public final class FromPDF implements PipelineStage<File, String> {

	public String process(File input) {
		String text = "";
		try {
			PDDocument document = PDDocument.load(input);
			PDFTextStripper parser = new PDFTextStripper();
			text = parser.getText(document);
			document.close();
		} catch (InvalidPasswordException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
  
		return text;
	}
}
