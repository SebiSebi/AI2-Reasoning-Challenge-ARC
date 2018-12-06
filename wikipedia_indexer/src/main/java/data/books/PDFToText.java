package data.books;

import data.processing.Pipeline;
import data.processing.stages.FromPDF;
import data.processing.stages.PipelineStage;
import data.processing.stages.RemoveChapterExercises;
import data.processing.stages.RemoveGlossary;
import data.processing.stages.RemoveQuestions;
import data.processing.stages.RemoveShortSentences;
import data.processing.stages.RemoveURLSentences;
import data.processing.stages.StripFigureKeyword;
import data.processing.stages.ToSentences;
import utils.Text;
import utils.FS;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;


class PDFToText {
	
	static {
	    System.setProperty("org.apache.commons.logging.Log", "org.apache.commons.logging.impl.NoOpLog");
	}
	
	static void removeGlossary(String path) {
		File file = new File(path);
		FromPDF stage = new FromPDF();
		String content = stage.process(file);
		String out = new RemoveGlossary().process(content);
		System.out.println(out.length());
	}
	
	static void removeExercises(String path) {
		System.out.println(path);
		File file = new File(path);
		FromPDF stage = new FromPDF();
		String content = stage.process(file);
		String out = new RemoveGlossary().process(content);
		out = new RemoveChapterExercises().process(out);
		out = new RemoveQuestions().process(out);
		out = new StripFigureKeyword().process(out);
		out = new RemoveURLSentences().process(out);
		out = new RemoveShortSentences(9).process(out);
		// System.out.println(out.length());
	}
	
	public static void work(String input_dir, String output_path) throws IOException, IllegalStateException, InterruptedException {	
		Pipeline<File, String, String> pipeline = new Pipeline<File, String, String>();
		pipeline.setInputStage(new FromPDF());
		
		pipeline.addStage(new RemoveGlossary());
		pipeline.addStage(new RemoveChapterExercises());
		pipeline.addStage(new RemoveQuestions());
		pipeline.addStage(new StripFigureKeyword());
		pipeline.addStage(new RemoveURLSentences());
		pipeline.addStage(new ToSentences());
		pipeline.addStage(new RemoveShortSentences(9));
		
		pipeline.setOutputStage(new PipelineStage<String, String>() {
			public final String process(String input) {
				return input;
			}
		});
		
		List<File> paths = FS.walkFiles(input_dir, "pdf");
		for (File file: paths) {
			pipeline.addInput(file);
		}
		
		ArrayList<String> data = pipeline.runAll(1);
		
		BufferedWriter out = new BufferedWriter(new FileWriter(output_path));
		for (String doc: data) {
			ArrayList<String> lines = Text.splitInLines(doc);
			for (String line: lines) {
				if (line.isEmpty())
					continue;
				out.write(line.trim() + "\n");
			}
		}
		out.flush();
		out.close();
		
		System.out.println("Done. Data written to " + output_path);
	}
	
	public static void main(String[] args) throws IOException, IllegalStateException, InterruptedException {
		// File file = new File("resources/books/CK12/CK12_Biology.pdf");
		// File file = new File("resources/books/openstax.org/Astronomy-LR.pdf");
		// removeGlossary("/home/sebisebi/Anul4/Licenta/books/CK12/CK12_Biology.pdf");
		// removeExercises("/home/sebisebi/Anul4/Licenta/books/CK12/Concepts_b_v8_vdt.pdf");
		
		work("/home/sebisebi/Anul4/Licenta/books/", "resources/books/all.txt");
		
		/*
		BufferedWriter out = new BufferedWriter(new FileWriter("resources/books/CK12/CK12_Biology.txt"));
		out.write(content);
		out.flush();
		out.close();
		System.out.println(content.length());
		*/
	}
}
