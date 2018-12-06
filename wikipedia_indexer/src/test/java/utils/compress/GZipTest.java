package utils.compress;

import static org.junit.Assert.*;
import java.io.IOException;
import java.util.Random;
import org.junit.Test;


public class GZipTest {
	
	private final char[] symbols = "abcdefghijklmnopqrstuvwxyz".toCharArray();
	 
	@Test
	public void testEdgeCases() throws IOException {
		assertEquals(GZip.decompress(GZip.compress("")), "");
		assertEquals(GZip.decompress(GZip.compress("a")), "a");
		assertEquals(GZip.decompress(GZip.compress("Z")), "Z");
		assertEquals(GZip.decompress(GZip.compress("1")), "1");
		assertEquals(GZip.decompress(GZip.compress("[3]")), "[3]");
		assertEquals(GZip.decompress(GZip.compress("ĝa")), "ĝa");
		assertEquals(GZip.decompress(GZip.compress("Þ, Ə")), "Þ, Ə");
		assertEquals(GZip.decompress(GZip.compress("\"")), "\"");
		
		/* Test long string. */
		StringBuilder sb = new StringBuilder();
		Random rnd = new Random();
		for (int i = 1; i <=  35 * 1024 * 1024; i++) {
			sb.append(symbols[rnd.nextInt(symbols.length)]);
		}
		String data = sb.toString();
		
		assertEquals(GZip.decompress(GZip.compress(data)), data);
	}

	@Test
	public void testLongStringWithOneChar() throws IOException {
		final Integer len = 20 * 1024 * 1024;
		
		StringBuilder sb = new StringBuilder();
		for (int i = 1; i <=  len; i++) {
			sb.append('a');
		}
		String data = sb.toString();
		byte[] compressed = GZip.compress(data);
		
		assertTrue(compressed.length <= (int)(len * 0.1));  /* 90% compression. */
		assertEquals(GZip.decompress(compressed), data);
	}
	
	@Test
	public void testVariousUnicode() throws IOException {
		assertEquals(GZip.decompress(GZip.compress("ŷ")), "ŷ");
		assertEquals(GZip.decompress(GZip.compress("ॹ")), "ॹ");
		assertEquals(GZip.decompress(GZip.compress("இ")), "இ");
		assertEquals(GZip.decompress(GZip.compress("⭖")), "⭖");
		assertEquals(GZip.decompress(GZip.compress("Ⱗ")), "Ⱗ");
		assertEquals(GZip.decompress(GZip.compress("㋦")), "㋦");
		assertEquals(GZip.decompress(GZip.compress("㎣")), "㎣");
		assertEquals(GZip.decompress(GZip.compress("𑀆")), "𑀆");
		assertEquals(GZip.decompress(GZip.compress("ǆ")), "ǆ");
		assertEquals(GZip.decompress(GZip.compress("🦖")), "🦖");
		assertEquals(GZip.decompress(GZip.compress("1⭖1")), "1⭖1");
		assertEquals(GZip.decompress(GZip.compress("𝍢a𝍢")), "𝍢a𝍢");
		assertEquals(GZip.decompress(GZip.compress("ლ,ᔑ•ﺪ͟͠•ᔐ.ლ")), "ლ,ᔑ•ﺪ͟͠•ᔐ.ლ");
	}
	
	@Test
	public void testEncoding() throws IOException {
		{
			byte[] compressed = GZip.compress("112");
			int n = compressed.length;
			assertEquals(compressed[0], 31);
			assertEquals(compressed[n - 1], 0);
			assertEquals(compressed[n - 2], 0);
			assertEquals(compressed[n - 3], 0);
			assertEquals(compressed[n - 4], 3);
			assertEquals(compressed[n - 5], (byte)(212));  /* byte is unsigned. */
			assertEquals(compressed[n - 6], 98);
			assertEquals(compressed[n - 7], 0);
			assertEquals(compressed[n - 8], (byte)(135));
			assertEquals(compressed[n - 9], 0);
			assertEquals(compressed[n - 10], (byte)(2));
		}
		{
			byte[] compressed = GZip.compress("sebi are mere");
			int n = compressed.length;
			assertEquals(compressed[0], 31);
			assertEquals(compressed[n - 1], 0);
			assertEquals(compressed[n - 2], 0);
			assertEquals(compressed[n - 3], 0);
			assertEquals(compressed[n - 4], 13);
			assertEquals(compressed[n - 5], 70);
			assertEquals(compressed[n - 6], (byte)(207));
			assertEquals(compressed[n - 7], (byte)(183));
			assertEquals(compressed[n - 8], 76);
			assertEquals(compressed[n - 9], 0);
		}
	}
}
