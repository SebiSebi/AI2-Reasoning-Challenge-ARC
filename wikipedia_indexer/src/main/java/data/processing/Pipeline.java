package data.processing;

import data.processing.stages.PipelineStage;
import utils.Pair;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.concurrent.CompletionService;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorCompletionService;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

/**
 * Runs a bunch of data through a pipeline defined by the user.
 * K is the input type.
 * U is the internal type.
 * V is the output type.
 * The pipeline has the following structure:
 * 		a) An input stage K -> U.
 * 		b) Zero or more internal stages (U -> U).
 * 		c) An output stage U -> V.
 */

public class Pipeline<K, U, V> {
	
	private ArrayList<K> inputs;
	private PipelineStage<K, U> input_stage;
	private ArrayList<PipelineStage<U, U>> stages;
	private PipelineStage<U, V> output_stage;
	
	public Pipeline() {
		inputs = new ArrayList<K>();
		input_stage = null;
		stages = new ArrayList<PipelineStage<U, U>>();
		output_stage = null;
	}
	
	private static <I, O> ArrayList<O> applyStage(ArrayList<I> inputs,
												  PipelineStage<I, O> stage,
												  ExecutorService executor) {
		CompletionService<Pair<Integer, O>> executor_service = new ExecutorCompletionService<Pair<Integer, O>>(executor);
		
		/* Submit all inputs for execution. */
		for (int i = 0; i < inputs.size(); i++) {
			executor_service.submit(new PipelineStageRunner<I, O>(inputs.get(i), i, stage));
		}
		
		ArrayList<Pair<Integer, O>> intermediate_data = new ArrayList<Pair<Integer, O>>();
		boolean success = true;
		
		for (int i = 0; i < inputs.size(); i++) {
			try {
				Future<Pair<Integer, O>> result_future = executor_service.take();
				Pair<Integer, O> data = result_future.get();
				if (data.getSecond() != null)
					intermediate_data.add(data);
			} catch (InterruptedException e) {
				success = false;
				// e.printStackTrace();
			} catch (ExecutionException e) {
				success = false;
				// e.printStackTrace();
			} catch (Exception e) {
				success = false;
				// e.printStackTrace();
			}
		}
		if (!success)
			return null;
		if (intermediate_data.size() != inputs.size())
			return null;
		
		/* Sort the results according to the index. */
		Collections.sort(intermediate_data, new Comparator<Pair<Integer, O>> (){
			public int compare(Pair<Integer, O> lhs, Pair<Integer, O> rhs) {
				return lhs.getFirst() - rhs.getFirst();
			}  
		}); 
		
		ArrayList<O> out = new ArrayList<O>();
		for (Pair <Integer, O> x: intermediate_data) {
			out.add(x.getSecond());
		}

		return out;
	}
	
	public ArrayList <V> runAll(int num_workers) throws IllegalStateException, InterruptedException {
		if (input_stage == null || output_stage == null) {
			throw new IllegalStateException("Input stage or output stage not set!");
		}
		ArrayList <V> results = null;
		ExecutorService executor = Executors.newFixedThreadPool(num_workers);
		
		ArrayList<U> data = Pipeline.applyStage(inputs, input_stage, executor);
		if (data != null) {
			for (int i = 0; i < stages.size(); i++) {
				data = Pipeline.applyStage(data, stages.get(i), executor);
				if (data == null)
					break;
			}
			
			if (data != null) {
				results = Pipeline.applyStage(data, output_stage, executor);
			}
		}
		
		executor.shutdown();
		executor.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
		if (!executor.isTerminated()) {
			throw new IllegalStateException("Not all workers have been terminated!");
		}
		
		return results;
	}
	
	public void addInput(K input_data) {
		inputs.add(input_data);
	}
	
	public void setInputStage(PipelineStage<K, U> input_stage) {
		this.input_stage = input_stage;
	}
	
	public void setOutputStage(PipelineStage<U, V> output_stage) {
		this.output_stage = output_stage;
	}
	
	public void addStage(PipelineStage<U, U> stage) {
		this.stages.add(stage);
	}
}
