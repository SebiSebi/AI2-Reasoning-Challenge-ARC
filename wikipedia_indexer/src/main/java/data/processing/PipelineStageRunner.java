package data.processing;

import data.processing.stages.PipelineStage;
import java.util.concurrent.Callable;
import utils.Pair;


final class PipelineStageRunner<T, U> implements Callable <Pair <Integer, U> > {
	private T input;
	private PipelineStage<T, U> stage;
	private Integer index;
	
	public PipelineStageRunner(T input, Integer index, PipelineStage<T, U> stage) {
		this.input = input;
		this.stage = stage;
		this.index = index;
	}
	
	public Pair<Integer, U> call() {
		/* This is the entry point for the stage. */
		
		if (input == null) {
			throw new IllegalStateException("Stage input data is not set!");
		}
		if (stage == null) {
			throw new IllegalStateException("Stage not set in stage runner!");
		}
		
		U out = stage.process(input);
		return Pair.makePair(this.index, out);
	}
}
