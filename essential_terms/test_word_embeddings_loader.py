import numpy as np
import os
import unittest

from settings import DEBUG
from word_embeddings_loader import WordEmbeddings


class TestWordEmbeddings(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_glove_6B_50d(self):
        self.assertFalse(DEBUG)
        w1 = WordEmbeddings(os.path.join("data", "glove.6B.50d.txt"), 50)
        w2 = WordEmbeddings(None, 50, True, "glove_6B_50d")
        required_words = [
            "the", "a", ",", "car", "bucharest", "nice", "science",
            "10", "degrees", "tie", "coffee", "banana", "number",
            "celsius", "fahrenheit", "love", "math", "˚c", "%",
            "london", "murder", "beautiful", "physics"
        ]
        should_not_be_found = [
            "bannnannas", "more that one word", "1ii12mimmi"
        ]

        for word in required_words:
            w_vector1 = w1.get_vector(word)
            w_vector2 = w2.get_vector(word)
            self.assertIsNotNone(w_vector1)
            self.assertIsNotNone(w_vector2)
            self.assertEqual(w_vector1.shape, w_vector2.shape)
            self.assertTrue(np.allclose(w_vector1, w_vector2))
            self.assertEqual(w_vector1.shape[0], 50)
            self.assertEqual(w_vector2.shape[0], 50)

        for word in should_not_be_found:
            w_vector1 = w1.get_vector(word)
            w_vector2 = w2.get_vector(word)
            self.assertIsNone(w_vector1)
            self.assertIsNone(w_vector2)

    def test_glove_6B_300d(self):
        self.assertFalse(DEBUG)
        w1 = WordEmbeddings(os.path.join("data", "glove.6B.300d.txt"), 300)
        w2 = WordEmbeddings(None, 300, True, "glove_6B_300d")
        required_words = [
            "the", "a", ",", "car", "bucharest", "nice", "science",
            "10", "degrees", "tie", "coffee", "banana", "number",
            "celsius", "fahrenheit", "love", "math", "˚c", "%",
            "apple", "rock", "romania", "iowa"
        ]
        should_not_be_found = [
            "bannnannas", "more that one word", "1ii12mimmi"
        ]

        for word in required_words:
            w_vector1 = w1.get_vector(word)
            w_vector2 = w2.get_vector(word)
            self.assertIsNotNone(w_vector1)
            self.assertIsNotNone(w_vector2)
            self.assertEqual(w_vector1.shape, w_vector2.shape)
            self.assertTrue(np.allclose(w_vector1, w_vector2))
            self.assertEqual(w_vector1.shape[0], 300)
            self.assertEqual(w_vector2.shape[0], 300)

        for word in should_not_be_found:
            w_vector1 = w1.get_vector(word)
            w_vector2 = w2.get_vector(word)
            self.assertIsNone(w_vector1)
            self.assertIsNone(w_vector2)


if __name__ == "__main__":
    unittest.main()
