package data;


import static org.junit.Assert.*;
import org.junit.Test;
import data.ConcretenessRatings;
import data.ConcretenessRatingsProtos.Entry;
import data.ConcretenessRatingsProtos.Ratings;


public class ConcretenessRatingsTest {

	@Test
	public void testGetRatings() {
		assertNotNull(ConcretenessRatings.getRatings());
		
		Ratings ratings = ConcretenessRatings.getRatings();
		assertSame(ratings, ConcretenessRatings.getRatings());
		
		Entry entry = ratings.getRatingsMapOrThrow("in principle");
		assertEquals(entry.getBigram(), true);
		assertEquals(entry.getRating(), 1.21, 0.000001);
		assertEquals(entry.getRatingSd(), 0.41, 0.000001);
		assertEquals(entry.getUnknown(), 4);
		assertEquals(entry.getNumPersons(), 28);
		assertEquals(entry.getKnownPercentage(), 0.86, 0.000001);
		assertEquals(entry.getFrequencyCount(), 0);
		assertEquals(entry.getType(), "#N/A");
		
		assertEquals(ratings.getRatingsMapOrThrow("dispiritedness").getUnknown(), 3);
		assertEquals(ratings.getRatingsMapOrThrow("dispiritedness").getBigram(), false);
		
		assertEquals(ratings.getRatingsMapOrThrow("unshaved").getRatingSd(), 1.04, 0.000001);
	}

	
	@Test
	public void testGetWordConcretness() {
		assertEquals(ConcretenessRatings.getWordConcretness("multicolored"), 4.11, 0.000001);
		assertEquals(ConcretenessRatings.getWordConcretness("midshipman"), 4.54, 0.000001);
		assertEquals(ConcretenessRatings.getWordConcretness("possessor"), 3.21, 0.000001);
		assertEquals(ConcretenessRatings.getWordConcretness("reconciling"), 1.68, 0.000001);
		assertEquals(ConcretenessRatings.getWordConcretness("essentialness"), 1.04, 0.000001);
	}

	@Test(expected = IllegalArgumentException.class)
	public void testGetWordConcretnessThrows() {
		assertEquals(ConcretenessRatings.getWordConcretness("does not exist"), 5.0, 0.000001);
	}
}
