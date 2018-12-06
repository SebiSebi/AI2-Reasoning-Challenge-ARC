import unittest

from settings import DEBUG
from word_features import WordFeatures


class TestWordEmbeddings(unittest.TestCase):
    wf = WordFeatures()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_science_term(self):
        self.assertFalse(DEBUG)
        science_terms = [
            "aardvarks",
            "ab initio",
            "center of curvature",
            "force",
            "gravity",
            "geo-science",
            "origins of the solar system",
            "atom",
            "protons",
            "seahorses",
            "newton's law of universal gravitation",
            "nucleus",
            "zwitterion",
            "zygomorphic",
            "zygomycetes",
            "zygospore",
        ]
        for word in science_terms:
            self.assertTrue(self.wf.is_science_term(word))

        not_science_terms = [
            "love",
            "beauty",
            "nice",
            "language",
            "glasses"
        ]
        for word in not_science_terms:
            self.assertFalse(self.wf.is_science_term(word))

    def test_concreteness_ratings(self):
        self.assertFalse(DEBUG)
        to_check = {
            "roadsweeper": 4.85,
            "treeless": 4.24,
            "divisional": 2.04,
            "hopeful": 1.7,
            "essentialness": 1.04,
            "interpretively": 1.21,
            "traindriver": 4.54,
            "chocolaty": 3.45,
            "mathematical": 2.9,
            "baking soda": 5.0,
            "beach ball": 5.0,
            "birth certificate": 5.0,
            "adaptive": 1.97,
            "bucharest": 2.5,
            "soccer": 4.76,
            "sebi": 2.5,
            "fasole": 2.5
        }
        for word in to_check:
            r = to_check[word]
            self.assertAlmostEqual(self.wf.get_concretness_rating(word), r)


if __name__ == "__main__":
    unittest.main()
