package utils;

import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;

class ExtensionFilenameFilter implements FilenameFilter {
	private String extension;
	
	public ExtensionFilenameFilter(String extension) {
		this.extension = extension.toLowerCase();
	}
	
	public boolean accept(File dir, String name) {
		if (new File(dir, name).isDirectory()) {
			return true;
		}
		if (dir.isHidden()) {
			return false;
		}
		return name.trim().toLowerCase().endsWith(extension);
	}
}

public final class FS {
	
	public static List<File> walkFiles(String start_dir, String extension) throws IOException {
		Queue <File> q = new LinkedList<File>();
		List <File> files = new ArrayList<File>();
		ExtensionFilenameFilter file_filter = new ExtensionFilenameFilter(extension);
		HashSet <String> visited = new HashSet<String>();
		
		q.add(new File(start_dir));
		visited.add(new File(start_dir).getCanonicalPath());
		
		while (!q.isEmpty()) {
			File file = q.poll();
			if (file == null)
				continue;
			File[] contents = file.listFiles(file_filter);
			if (contents == null)
				continue;
			for (File child: contents) {
				String canonical_path = child.getCanonicalPath();
				if (visited.contains(canonical_path))
					continue;
				visited.add(canonical_path);
				if (child.isDirectory())
					q.add(child);
				else {
					files.add(child);
				}
			}
		}
		
		return files;
	}
	
	/*
	public static void main(String[] args) throws IOException {
		List<File> files = walkFiles("resources/books", "pdf");
		for (File x: files) {
			System.out.println(x);
		}
	}*/
}
