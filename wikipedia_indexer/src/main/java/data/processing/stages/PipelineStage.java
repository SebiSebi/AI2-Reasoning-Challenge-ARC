package data.processing.stages;


public interface PipelineStage<T, U> {
	
	/* It is guaranteed that input is not null. You *must not* modify the input object. */
	abstract public U process(T input);
}
