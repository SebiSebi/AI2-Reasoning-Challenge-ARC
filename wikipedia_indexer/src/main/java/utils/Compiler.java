package utils;

import utils.Status;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.nio.file.Paths;

public final class Compiler {

	private static final Path BASE_DIR = Paths.get("/", "home", "sebisebi", "Anul4", "Licenta");
	
	/* Each protocol buffer directory is expected to have a Makefile inside. */
	private static final Path[] PROTO_DIRS = new Path[] {
			Paths.get(BASE_DIR.toAbsolutePath().toString(), "protos"),
			Paths.get(BASE_DIR.toAbsolutePath().toString(), "wikipedia_indexer", "protos")
	};
	
	public static Status compileProtos() {
		for (Path proto_dir: PROTO_DIRS) {
			System.out.println("Compiling " + proto_dir.toString() + " ..." + "\n");
			ProcessBuilder builder = new ProcessBuilder("make", "all");
			builder.directory(new File(proto_dir.toString()));
			builder.redirectErrorStream(true);  /* STDERR > STDOUT */
			try {
				Process proc = builder.start();
				proc.waitFor();
				
			    BufferedReader output = new BufferedReader(new InputStreamReader(proc.getInputStream()));
			    String line;
			    while ((line = output.readLine()) != null) {
			    	System.out.println("\t" + line);
			    }
			    
			    System.out.println("");
			    if (proc.exitValue() == 0) {
			    	System.out.println("\tSuccess! (exit code = 0)\n");
			    }
			    else {
			    	System.out.println("\tFailed with exit code " + proc.exitValue() + ".\n");
			    }
			    
			} catch (IOException e) {
				System.err.println(e.getMessage());
				return Status.IO_ERROR;
			} catch (InterruptedException e) {
				System.err.println(e.getMessage());
				return Status.THREAD_INTERRUPTED;
			}
		}
		return Status.OK;
	}
	
	public static void main(String[] args) {
		compileProtos();
	}
}
