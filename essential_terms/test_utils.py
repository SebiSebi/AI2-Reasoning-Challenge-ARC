import unittest
import utils

from settings import DEBUG, FULL_DATASET_PATH


class TestReadAsArray(unittest.TestCase):
    def setUp(self):
        self.data = utils.read_as_array(FULL_DATASET_PATH)

    def tearDown(self):
        self.data = None

    def test_shuffle(self):
        self.assertFalse(DEBUG)
        question_1 = self.data[0]["question"]
        question_2 = self.data[1]["question"]
        question_n = self.data[-1]["question"]
        not_shuffled = True
        if "If an object is attracted to a magnet" not in question_1:
            not_shuffled = False
        if "Animals get energy for growth and repair from" not in question_2:
            not_shuffled = False
        if "can remove the salt that is in seawater" not in question_n:
            not_shuffled = False
        self.assertFalse(not_shuffled)

    def test_data_structure(self):
        self.assertFalse(DEBUG)
        self.assertEqual(len(self.data), 2191)
        for entry in self.data:
            self.assertIn('question', entry)
            self.assertIn('answers', entry)
            self.assertIn('terms', entry)
            self.assertEqual(len(entry['answers']), 4)
            self.assertIsInstance(entry['terms'], dict)
            self.assertIsInstance(entry['answers'], list)

    def test_data_content(self):
        self.assertFalse(DEBUG)

        question = "A shoe manufacturer randomly selects 10% of the production"
        entry = None
        for x in self.data:
            if question not in x["question"]:
                continue
            assert(entry is None)
            entry = x
        self.assertIsNotNone(entry)
        self.assertEqual(entry['answers'][0], 'quality control')
        self.assertEqual(entry['answers'][1], 'product distribution')
        self.assertEqual(entry['answers'][2], 'production selection')
        self.assertEqual(entry['answers'][3], 'research and development')
        self.assertIn("What is this process called?", entry["question"])
        self.assertDictEqual(entry['terms'], {
            'A': 0,
            'shoe': 2,
            'manufacturer': 1,
            'randomly': 2,
            'selects': 3,
            '10': 5,
            'percent': 5,
            'of': 0,
            'the': 0,
            'production': 2,
            'from': 0,
            'each': 0,
            'shift': 1,
            'Each': 0,
            'these': 0,
            'shoes': 2,
            'is': 0,
            'checked': 3,
            'to': 0,
            'ensure': 1,
            'that': 0,
            'it': 0,
            'correctly': 2,
            'made': 2,
            'What': 0,
            'this': 0,
            'process': 4,
            'called': 2
        })

    def test_celsius_degree(self):
        self.assertFalse(DEBUG)

        question = "Freezing of any substance occurs ___."
        entry = None
        for x in self.data:
            if question != x["question"]:
                continue
            assert(entry is None)
            entry = x
        self.assertIsNotNone(entry)
        self.assertEqual(entry['answers'][0], 'when the particles of the '
                                              'substance are able to slide '
                                              'past one another')
        self.assertEqual(entry['answers'][1], 'at 0°C')
        self.assertEqual(entry['answers'][2], 'when a liquid changes to a '
                                              'solid, regardless of '
                                              'temperature')
        self.assertEqual(entry['answers'][3], 'when energy is added to '
                                              'a substance')
        self.assertIn("occurs ___.", entry["question"])
        self.assertDictEqual(entry['terms'], {
            'Freezing': 5,
            'of': 0,
            'any': 0,
            'substance': 1,
            'occurs': 4
        })

    def test_fahrenheit_degree(self):
        self.assertFalse(DEBUG)

        question = "When the temperature of water rises from 0°F to 100°F,"
        entry = None
        for x in self.data:
            if question not in x["question"]:
                continue
            assert(entry is None)
            entry = x
        self.assertIsNotNone(entry)
        self.assertEqual(entry['answers'][0], 'From solid to gas to liquid')
        self.assertEqual(entry['answers'][1], 'From gas to solid')
        self.assertEqual(entry['answers'][2], 'From liquid to solid')
        self.assertEqual(entry['answers'][3], 'From solid to liquid to gas')
        self.assertIn("what changes of state occur?", entry["question"])
        self.assertDictEqual(entry['terms'], {
            'When': 0,
            'the': 0,
            'temperature': 5,
            'of': 0,
            'water': 5,
            'rises': 3,
            'from': 0,
            '0': 4,
            '100': 4,
            'what': 0,
            'changes': 3,
            'state': 2,
            'occur': 2,
            'to': 0,
            'fahrenheit': 4,
            'degrees': 4
        })


if __name__ == "__main__":
    unittest.main()
