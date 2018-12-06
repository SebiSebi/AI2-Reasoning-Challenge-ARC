package data.processing;

import static org.junit.Assert.*;
import java.util.Random;
import org.junit.Test;
import java.util.ArrayList;
import data.processing.stages.PipelineStage;
import utils.Pair;

public class PipelineTest {
	
	static final String ALPHANUM = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
	
	@Test
	public void testSingleWorker() throws IllegalStateException, InterruptedException {
		Pipeline<String, Integer, Integer> pipeline = new Pipeline<String, Integer, Integer>();
		pipeline.setInputStage(new PipelineStage<String, Integer>() {
			public final Integer process(String input) {
				return input.length();
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input - 3;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input * input * input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input + 7;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return (input >> 1);
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input + 5;
			}
		});
		
		Random rnd = new Random();
		ArrayList<Integer> expected = new ArrayList<Integer>();
		for (int i = 0; i < 5000; i++) {
			int len = rnd.nextInt(75);
			StringBuilder sb = new StringBuilder(len);
			for (int j = 0; j < len; j++) {
				sb.append(ALPHANUM.charAt(rnd.nextInt(ALPHANUM.length())));
			}
			pipeline.addInput(sb.toString());
			expected.add(((((len - 3) * (len - 3) * (len - 3)) + 7) >> 1) + 5);
		}
		
		ArrayList<Integer> data = pipeline.runAll(1);
		assertNotNull(data);
		assertEquals(data, expected);
	}

	@Test
	public void testStressWorkers() throws IllegalStateException, InterruptedException {
		Pipeline<String, Integer, Integer> pipeline = new Pipeline<String, Integer, Integer>();
		pipeline.setInputStage(new PipelineStage<String, Integer>() {
			public final Integer process(String input) {
				return input.length();
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input - 7;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input * input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input + 17;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return (input >> 1);
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input - 35;
			}
		});
		
		Random rnd = new Random();
		ArrayList<Integer> expected = new ArrayList<Integer>();
		for (int i = 0; i < 250000; i++) {
			int len = rnd.nextInt(75);
			StringBuilder sb = new StringBuilder(len);
			for (int j = 0; j < len; j++) {
				sb.append(ALPHANUM.charAt(rnd.nextInt(ALPHANUM.length())));
			}
			pipeline.addInput(sb.toString());
			expected.add(((((len - 7) * (len - 7)) + 17) >> 1) - 35);
		}
		
		ArrayList<Integer> data = pipeline.runAll(350);
		assertNotNull(data);
		assertEquals(data, expected);
	}
	
	@Test
	public void testStressWorkersWithSleep() throws IllegalStateException, InterruptedException {
		Pipeline<String, Integer, Boolean> pipeline = new Pipeline<String, Integer, Boolean>();
		pipeline.setInputStage(new PipelineStage<String, Integer>() {
			public final Integer process(String input) {
				return input.length();
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input - 7;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				try {
					if (Math.random() < 0.01) {
						Thread.sleep((long)(Math.random() * 100)); // milliseconds to sleep.
					}
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
				return input * input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input + 17;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return (input >> 1);
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Integer, Boolean>() {
			public final Boolean process(Integer input) {
				try {
					Thread.sleep((long)(Math.random() * 15));  // milliseconds to sleep.
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
				return input % 3 == 2;
			}
		});
		
		Random rnd = new Random();
		ArrayList<Boolean> expected = new ArrayList<Boolean>();
		for (int i = 0; i < 50000; i++) {
			int len = rnd.nextInt(75);
			StringBuilder sb = new StringBuilder(len);
			for (int j = 0; j < len; j++) {
				sb.append(ALPHANUM.charAt(rnd.nextInt(ALPHANUM.length())));
			}
			pipeline.addInput(sb.toString());
			expected.add(((((len - 7) * (len - 7)) + 17) >> 1) % 3 == 2);
		}
		
		ArrayList<Boolean> data = pipeline.runAll(150);
		assertNotNull(data);
		assertEquals(data, expected);
	}
	
	@Test
	public void testPipelineTypes() throws IllegalStateException, InterruptedException {
		Pipeline<Integer, Boolean, String> pipeline = new Pipeline<Integer, Boolean, String>();
		pipeline.setInputStage(new PipelineStage<Integer, Boolean>() {
			public final Boolean process(Integer input) {
				return input % 5 == 2;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return !input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return !input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return !input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return !input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return !input;
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Boolean, String>() {
			public final String process(Boolean input) {
				if (input)
					return "a";
				return "ZZx";
			}
		});
		
		Random rnd = new Random();
		ArrayList<String> expected = new ArrayList<String>();
		for (int i = 0; i < 50; i++) {
			int x = rnd.nextInt();
			pipeline.addInput(x);
			if (x % 5 != 2)
				expected.add("a");
			else
				expected.add("ZZx");
		}
		
		ArrayList<String> data = pipeline.runAll(15);
		assertNotNull(data);
		assertEquals(data, expected);
	}
	
	@Test
	public void testEmptyPipeline() throws IllegalStateException, InterruptedException {
		Pipeline<Integer, Boolean, String> pipeline = new Pipeline<Integer, Boolean, String>();
		pipeline.setInputStage(new PipelineStage<Integer, Boolean>() {
			public final Boolean process(Integer input) {
				return input % 5 <= 2;
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Boolean, String>() {
			public final String process(Boolean input) {
				if (input)
					return "a";
				return "ZZx";
			}
		});
		
		Random rnd = new Random();
		ArrayList<String> expected = new ArrayList<String>();
		for (int i = 0; i < 50; i++) {
			int x = rnd.nextInt();
			pipeline.addInput(x);
			if (x % 5 <= 2)
				expected.add("a");
			else
				expected.add("ZZx");
		}
		
		ArrayList<String> data = pipeline.runAll(15);
		assertNotNull(data);
		assertEquals(data, expected);
	}
	
	@Test(expected = IllegalStateException.class)
	public void testNoInputStage() throws IllegalStateException, InterruptedException {
		Pipeline<Boolean, Boolean, String> pipeline = new Pipeline<Boolean, Boolean, String>();
		pipeline.setOutputStage(new PipelineStage<Boolean, String>() {
			public final String process(Boolean input) {
				if (input)
					return "a";
				return "ZZx";
			}
		});
		
		ArrayList<String> data = pipeline.runAll(15);
		assertNotNull(data);
	}
	
	@Test(expected = IllegalStateException.class)
	public void testNoOutputStage() throws IllegalStateException, InterruptedException {
		Pipeline<Boolean, Boolean, String> pipeline = new Pipeline<Boolean, Boolean, String>();
		pipeline.setInputStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return !input;
			}
		});
		
		ArrayList<String> data = pipeline.runAll(5);
		assertNotNull(data);
	}
	
	@Test
	public void testDeepPipeline() throws IllegalStateException, InterruptedException {
		Pipeline<String, Integer, Integer> pipeline = new Pipeline<String, Integer, Integer>();
		pipeline.setInputStage(new PipelineStage<String, Integer>() {
			public final Integer process(String input) {
				return input.length();
			}
		});
		
		for (int i = 1; i <= 50; i++) {
			pipeline.addStage(new PipelineStage<Integer, Integer>() {
				public final Integer process(Integer input) {
					return input + 1;
				}
			});
		}
		
		for (int i = 1; i <= 500; i++) {
			pipeline.addStage(new PipelineStage<Integer, Integer>() {
				public final Integer process(Integer input) {
					return input + 3;
				}
			});
		}

		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input * input;
			}
		});
		
		for (int i = 1; i <= 1602; i++) {
			pipeline.addStage(new PipelineStage<Integer, Integer>() {
				public final Integer process(Integer input) {
					return input - 2;
				}
			});
		}
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input - 75;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input * 7;
			}
		});
		
		pipeline.addStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input;
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Integer, Integer>() {
			public final Integer process(Integer input) {
				return input >> 3;
			}
		});
		
		Random rnd = new Random();
		ArrayList<Integer> expected = new ArrayList<Integer>();
		for (int i = 0; i < 2500; i++) {
			int len = rnd.nextInt(175);
			StringBuilder sb = new StringBuilder(len);
			for (int j = 0; j < len; j++) {
				sb.append(ALPHANUM.charAt(rnd.nextInt(ALPHANUM.length())));
			}
			pipeline.addInput(sb.toString());
			expected.add((((len + 1550) * (len + 1550) - 3279) * 7) >> 3);
		}
		
		ArrayList<Integer> data = pipeline.runAll(35);
		assertNotNull(data);
		assertEquals(data, expected);
	}
	
	@Test
	public void testNoInputData() throws IllegalStateException, InterruptedException {
		Pipeline<Integer, Boolean, Boolean> pipeline = new Pipeline<Integer, Boolean, Boolean>();
		pipeline.setInputStage(new PipelineStage<Integer, Boolean>() {
			public final Boolean process(Integer input) {
				return input % 5 == 2;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return !input;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return !input;
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				return Math.random() <= 0.5;
			}
		});
		
		ArrayList<Boolean> data = pipeline.runAll(50);
		assertNotNull(data);
		assertEquals(data.size(), 0);
	}
	
	@Test
	public void testComplexType() throws IllegalStateException, InterruptedException {
		Pipeline<String, Pair<Integer, Integer>, Pair<String, Integer>> pipeline = new Pipeline<String, Pair<Integer, Integer>, Pair<String, Integer>>();
		pipeline.setInputStage(new PipelineStage<String, Pair<Integer, Integer>>() {
			public final Pair<Integer, Integer> process(String in) {
				return Pair.makePair(in.length(), in.length() << 2);
			}
		});
		
		pipeline.addStage(new PipelineStage<Pair<Integer, Integer>, Pair<Integer, Integer>>() {
			public final Pair<Integer, Integer> process(Pair<Integer, Integer> input) {
				return Pair.makePair(input.getSecond(), input.getFirst());
			}
		});
		
		pipeline.addStage(new PipelineStage<Pair<Integer, Integer>, Pair<Integer, Integer>>() {
			public final Pair<Integer, Integer> process(Pair<Integer, Integer> input) {
				return Pair.makePair(input.getFirst() + 1, input.getSecond() * 3 - 13);
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Pair<Integer, Integer>, Pair<String, Integer>>() {
			public final Pair<String, Integer> process(Pair<Integer, Integer> input) {
				if (input.getFirst() <= 0)
					return Pair.makePair("", input.getFirst() - input.getSecond());
				StringBuilder sb = new StringBuilder(10);
				for (int i = 0; i < input.getFirst() % 25; i++)
					sb.append('s');
				return Pair.makePair(sb.toString(), input.getFirst() - input.getSecond());
			}
		});
		
		Random rnd = new Random();
		ArrayList<Pair<String, Integer>> expected = new ArrayList<Pair<String, Integer>>();
		for (int i = 0; i < 50000; i++) {
			int len = rnd.nextInt(350);
			StringBuilder sb = new StringBuilder(len);
			for (int j = 0; j < len; j++) {
				sb.append(ALPHANUM.charAt(rnd.nextInt(ALPHANUM.length())));
			}
			pipeline.addInput(sb.toString());
			StringBuilder sb2 = new StringBuilder(10);
			for (int j = 0; j < ((len << 2) + 1) % 25; j++)
				sb2.append('s');
			expected.add(Pair.makePair(sb2.toString(), (len << 2) - (len * 3 - 13) + 1));
		}
		
		ArrayList<Pair<String, Integer>> data = pipeline.runAll(8);
		assertNotNull(data);
		assertEquals(data, expected);
	}
	
	@Test
	public void testInputStageThrows() throws IllegalStateException, InterruptedException {
		Pipeline<Integer, Boolean, String> pipeline = new Pipeline<Integer, Boolean, String>();
		pipeline.setInputStage(new PipelineStage<Integer, Boolean>() {
			public final Boolean process(Integer input) {
				if (input % 2 == 0) {
					throw new IllegalArgumentException("Input is even.");
				}
				return input % 5 <= 2;
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Boolean, String>() {
			public final String process(Boolean input) {
				if (input)
					return "a";
				return "ZZx";
			}
		});
		
		for (int i = 0; i < 5; i++) {
			pipeline.addInput(i + 1);
		}
		
		ArrayList<String> data = pipeline.runAll(6);
		assertNull(data);
	}
	
	@Test
	public void testOutputStageThrows() throws IllegalStateException, InterruptedException {
		Pipeline<Integer, Boolean, String> pipeline = new Pipeline<Integer, Boolean, String>();
		pipeline.setInputStage(new PipelineStage<Integer, Boolean>() {
			public final Boolean process(Integer input) {
				return input % 2 == 1;
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Boolean, String>() {
			public final String process(Boolean input) {
				if (input)
					throw new NullPointerException("Test exception.");
				return "ZZx";
			}
		});
		
		for (int i = 0; i < 5; i++) {
			pipeline.addInput(i);
		}
		
		ArrayList<String> data = pipeline.runAll(8);
		assertNull(data);
	}
	
	@Test
	public void testInternalStageThrows() throws IllegalStateException, InterruptedException {
		Pipeline<Integer, Boolean, String> pipeline = new Pipeline<Integer, Boolean, String>();
		pipeline.setInputStage(new PipelineStage<Integer, Boolean>() {
			public final Boolean process(Integer input) {
				return input % 2 == 1;
			}
		});
		
		pipeline.addStage(new PipelineStage<Boolean, Boolean>() {
			public final Boolean process(Boolean input) {
				if (!input)
					throw new SecurityException("Test exception2.");
				return !input;
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<Boolean, String>() {
			public final String process(Boolean input) {
				return "sebisebi";
			}
		});
		
		for (int i = 0; i < 5; i++) {
			pipeline.addInput(i + 1);
		}
		
		ArrayList<String> data = pipeline.runAll(2);
		assertNull(data);
	}
	
	@Test
	public void testStageReturnsNull() throws IllegalStateException, InterruptedException {
		Pipeline<Integer, String, String> pipeline = new Pipeline<Integer, String, String>();
		pipeline.setInputStage(new PipelineStage<Integer, String>() {
			public final String process(Integer input) {
				if (input % 2 == 0)
					return "";
				return "sebisebi";
			}
		});
		
		pipeline.addStage(new PipelineStage<String, String>() {
			public final String process(String input) {
				if (input.length() == 8)
					return null;
				return input;
			}
		});
		
		pipeline.setOutputStage(new PipelineStage<String, String>() {
			public final String process(String input) {
				return "sebisebi";
			}
		});
		
		for (int i = 0; i < 5; i++) {
			pipeline.addInput(i);
		}
		
		ArrayList<String> data = pipeline.runAll(100);
		assertNull(data);
	}
}
