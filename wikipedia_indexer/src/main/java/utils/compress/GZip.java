package utils.compress;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.zip.GZIPInputStream;
import java.util.zip.GZIPOutputStream;
import java.nio.charset.StandardCharsets;

import org.apache.commons.io.IOUtils;

/**
 * Compressing data (UTF-8) in the GZIP file format.
 */
public final class GZip {
	
	public static byte[] compress(String data) throws IOException {
		ByteArrayOutputStream out = new ByteArrayOutputStream();
		GZIPOutputStream gzip_stream = new GZIPOutputStream(out);
		
		gzip_stream.write(data.getBytes(StandardCharsets.UTF_8));
		gzip_stream.flush();  /* Automatically called by close. Do it manually to make sure this is true in further versions. */
		gzip_stream.finish();
		gzip_stream.close();
		
		out.flush();
		byte[] compressed_data = out.toByteArray();
		out.close();
		
		return compressed_data;	
	}
	
	@SuppressWarnings("deprecation")
	public static String decompress(byte[] data) throws IOException {
		ByteArrayInputStream in = new ByteArrayInputStream(data);
		GZIPInputStream gzip_stream = new GZIPInputStream(in);
		byte[] bytes = IOUtils.toByteArray(gzip_stream);
		return IOUtils.toString(bytes, "UTF-8");
	}
	
	public static void main(String[] args) throws IOException {
		byte[] compressed = GZip.compress("sebi are mere");
		System.out.println(GZip.decompress(compressed));
	}
}
