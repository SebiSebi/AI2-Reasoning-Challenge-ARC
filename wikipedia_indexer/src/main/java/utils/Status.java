package utils;

public enum Status {
	OK,
	IO_ERROR,  // See IOException.
	THREAD_INTERRUPTED,  // A call .wait() throws InterruptedException.
}
