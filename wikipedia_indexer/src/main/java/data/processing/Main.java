package data.processing;

import java.util.ArrayList;

import data.processing.stages.PipelineStage;

public class Main {
	public static void main(String[] args) throws IllegalStateException, InterruptedException {
		Pipeline<String, Integer, Boolean> pipeline = new Pipeline<String, Integer, Boolean>();
		pipeline.setInputStage(new PipelineStage<String, Integer>() {
			public final Integer process(String input) {
				return input.length();
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input * 2;
			}
		});
		
		pipeline.addInput("123");
		pipeline.addInput("sebi1");
		pipeline.addInput("sebi2");
		pipeline.addInput("sebi10000000");
		
		pipeline.setOutputStage(new PipelineStage<Integer, Boolean>() {
			public final Boolean process(Integer input) {
				return (input == 6);
			}
		});
		
		ArrayList<Boolean> data = pipeline.runAll(10);
		for (Boolean x: data) {
			System.out.println(x);
		}
		
		System.out.println("end");
	}
}
