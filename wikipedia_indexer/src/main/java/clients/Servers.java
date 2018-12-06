package clients;

import java.io.File;
import java.io.IOException;
import java.net.ServerSocket;

final class Servers {
	
	private static boolean isTCPOpen(int port) {
		if (port <= 0 || port > 65535)
			return false;
		
		/* Try to start a TCP server on that port. */
		ServerSocket sock = null;
		try {
			sock = new ServerSocket(port);
			sock.setReuseAddress(true);  /* Allow the port to be reused. */
			return true;
		} catch (IOException e) {
		} finally {
			if (sock != null) {
				try {
					sock.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
		
		return false;
	}
	
	public static Process maybeStart(String[] command, String directory, int port) {
		/* Check if port is open. */
		if (!isTCPOpen(port)) {
			return null;
		}
		
		ProcessBuilder builder = new ProcessBuilder(command);
		builder.directory(new File(directory));
		builder.redirectErrorStream(true);  /* STDERR > STDOUT */
		
		Process proc = null;
		try {
			proc = builder.start();
			Thread.sleep(500);
			while (!isTCPOpen(port)) {
				Thread.sleep(75);
			}
			System.out.println("Started ETServer ... ");
		} catch (IOException e) {
			e.printStackTrace();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
		
		return proc;
	}
	
	public static Process maybeStartETServer(int port) {
		return maybeStart(new String[] {"/home/sebisebi/Anul4/Licenta/essential_terms/env/bin/python", "et_server.py"},
					      "/home/sebisebi/Anul4/Licenta/essential_terms",
					      port);
	}
	
	public static void maybeStopServer(Process proc) {
		if (proc == null) {
			return;
		}
		
		/* Send shutdown message. */
		proc.destroy();
		
		try {
			proc.waitFor();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}
	
	public static void main(String[] args) {
		Process proc = maybeStartETServer(11111);
		System.out.println(proc);
		maybeStopServer(proc);
	}
}
