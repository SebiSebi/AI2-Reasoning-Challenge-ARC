import numpy as np
import spacy
import unittest

from settings import DEBUG
from dep_graph_utils import build_degree_centrality
from dep_graph_utils import build_closeness_centrality
from dep_graph_utils import build_eigenvector_centrality


class TestWordEmbeddings(unittest.TestCase):
    nlp = spacy.load("en_core_web_sm")

    def setUp(self):
        self.assertIsInstance(self.nlp, spacy.lang.en.English)

    def tearDown(self):
        pass

    def __to_softmax(self, x):
        assert(isinstance(x, dict))
        softmax_sum = 0.0
        for word in x:
            softmax_sum += np.exp(x[word])
        for word in x:
            x[word] = 1.0 * np.exp(x[word]) / softmax_sum
        return x

    def test_degree_centrality_single_sentence(self):
        self.assertFalse(DEBUG)
        doc = self.nlp("U.S.A economy has grown up by over 10% in the "
                       "last year.")
        deg = build_degree_centrality(doc)
        correct = {
            'u.s.a': 1.0,
            'grown': 6.0,
            'has': 1.0,
            'economy': 2.0,
            'up': 1.0,
            'by': 2.0,
            '%': 2.0,
            '10': 2.0,
            'over': 1.0,
            'in': 2.0,
            'year': 3.0,
            'last': 1.0,
            'the': 1.0,
            '.': 1.0
        }
        correct = self.__to_softmax(correct)
        self.assertEqual(len(deg), len(correct))
        for word in correct:
            self.assertAlmostEqual(correct[word], deg[word])

    def test_degree_centrality_multiple_sentences(self):
        self.assertFalse(DEBUG)
        doc = self.nlp("U.S.A economy has grown up by over 10% in the "
                       "last year. It is one of the most powerful countries "
                       "in the world.")
        deg = build_degree_centrality(doc)
        correct = {
            'it': 1.0,
            'u.s.a': 1.0,
            'grown': 6.0,
            'has': 1.0,
            'economy': 2.0,
            'up': 1.0,
            'by': 2.0,
            '%': 2.0,
            '10': 2.0,
            'over': 1.0,
            'in': 2.0,
            'year': 3.0,
            'last': 1.0,
            'the': 1.0,
            '.': 1.0,
            'is': 3.0,
            'one': 2.00,
            'of': 2.0,
            'countries': 4,
            'powerful': 2.0,
            'most': 1.0,
            'world': 2.0
        }
        correct = self.__to_softmax(correct)
        self.assertEqual(len(deg), len(correct))
        for word in correct:
            self.assertAlmostEqual(correct[word], deg[word])

    def test_degree_centrality_multiple_sentences_2(self):
        self.assertFalse(DEBUG)
        doc = self.nlp("I love apples and pizza and water. "
                       "She is my girlfriend. "
                       "Apples are very tasty. Wow! "
                       "She and I are walking")
        deg = build_degree_centrality(doc)
        correct = {
            'is': 3.0,
            'she': 2.0,
            '.': 1.0,
            'girlfriend': 2.0,
            'my': 1.0,
            'love': 3.0,
            'i': 1.0,
            'apples': 2.0,
            'and': 1.0,
            'pizza': 3.0,
            'water': 1.0,
            'are': 2.0,
            'tasty': 2.0,
            'very': 1.0,
            'walking': 2.0,
            '!': 1.0,
            'wow': 1.0
        }
        correct = self.__to_softmax(correct)
        self.assertEqual(len(deg), len(correct))
        for word in correct:
            self.assertAlmostEqual(correct[word], deg[word])

    def test_closeness_centrality_single_sentence(self):
        self.assertFalse(DEBUG)
        doc = self.nlp("the dog and the woman love the dog")
        res = build_closeness_centrality(doc)
        correct = {
            'the': 0.3498152884342143,
            'dog': 0.5240641711229946,
            'and': 0.4117647058823529,
            'woman': 0.4666666666666667,
            'love': 0.5384615384615384
        }
        self.assertEqual(len(res), len(correct))
        for word in correct:
            self.assertAlmostEqual(correct[word], res[word])

    def test_closeness_centrality_single_sentence_2(self):
        self.assertFalse(DEBUG)
        doc = self.nlp("One way animals usually respond to a sudden "
                       "drop in temperature is by ...")
        res = build_closeness_centrality(doc)
        correct = {
            'one': 0.2765957446808511,
            'way': 0.37142857142857144,
            'animals': 0.35135135135135137,
            'usually': 0.35135135135135137,
            'temperature': 0.24528301886792453,
            'respond': 0.52,
            'to': 0.48148148148148145,
            'a': 0.3023255813953488,
            'sudden': 0.3023255813953488,
            'drop': 0.41935483870967744,
            'in': 0.3170731707317073,
            '...': 0.35135135135135137,
            'is': 0.37142857142857144,
            'by': 0.2765957446808511
        }
        self.assertEqual(len(res), len(correct))
        for word in correct:
            self.assertAlmostEqual(correct[word], res[word])

    def test_closeness_centrality_multiple_sentences(self):
        self.assertFalse(DEBUG)
        doc = self.nlp("She likes flowers. Flowers are beautiful."
                       "Me and she, flowers.")
        res = build_closeness_centrality(doc)
        correct = {
            'are': 1.0,
            'me': 0.8333333333333334,
            'she': 0.6125,
            'likes': 1.0,
            'flowers': 0.5666666666666668,
            '.': 0.5666666666666668,
            'and': 0.5,
            ',': 0.4166666666666667,
            'beautiful': 0.6
        }
        self.assertEqual(len(res), len(correct))
        for word in correct:
            self.assertAlmostEqual(correct[word], res[word])

    def test_eigenvector_centrality_single_sentence(self):
        self.assertFalse(DEBUG)
        doc = self.nlp("the dog and the woman love the dog")
        res = build_eigenvector_centrality(doc)
        correct = {
            'the': 0.29717276965249706,
            'dog': 0.6408944972532619,
            'and': 0.29717276965249717,
            'woman': 0.37856558445287347,
            'love': 0.4092671864884675
        }
        self.assertEqual(len(res), len(correct))
        for word in correct:
            self.assertAlmostEqual(correct[word], res[word])

    def test_eigenvector_centrality_multiple_sentences(self):
        self.assertFalse(DEBUG)
        doc = self.nlp("She likes flowers. Flowers are beautiful. "
                       "Me and she, flowers.")
        res = build_eigenvector_centrality(doc)
        correct = {
            'beautiful': 0.4082482904638628,
            'she': 0.4250440865037962,
            '.': 0.40824829046386296,
            'likes': 0.7071067811865477,
            'flowers': 0.40824829046386313,
            'are': 0.7071067811865477,
            ',': 0.20490833661795926,
            'me': 0.6767662621499844,
            'and': 0.3262603891209974,
        }
        self.assertEqual(len(res), len(correct))
        for word in correct:
            self.assertAlmostEqual(correct[word], res[word])


if __name__ == "__main__":
    unittest.main()
