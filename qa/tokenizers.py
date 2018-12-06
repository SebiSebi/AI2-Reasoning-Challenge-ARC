import json
import spacy
import tqdm

from keras.preprocessing.text import Tokenizer as KerasTok
from qa.settings import DEBUG, ENTITY_LIST_PATH

_SPACY_MODEL = "en_core_web_sm"


class Tokenizer(object):

    def __init__(self):
        pass

    def word_index(self):
        raise NotImplementedError("Implement word_index()")

    def fit_on_texts(self, texts):
        raise NotImplementedError("Implement fit_on_texts()")

    def word_counts(self):
        raise NotImplementedError("Implement word_counts()")

    def texts_to_sequences(self, texts):
        raise NotImplementedError("Implement texts_to_sequences()")

    def index_to_word(self, word):
        raise NotImplementedError("Implement index_to_word()")


class KerasTokenizer(Tokenizer):

    def __init__(self):
        self.tokenizer = KerasTok(lower=False)
        self.inverted_index = None

    def word_index(self):
        return self.tokenizer.word_index

    def fit_on_texts(self, texts):
        self.tokenizer.fit_on_texts(texts)
        word_index = self.tokenizer.word_index
        self.inverted_index = {}
        for word in word_index:
            index = word_index[word]
            self.inverted_index[index] = word

    def word_counts(self):
        return self.tokenizer.word_counts

    def texts_to_sequences(self, texts):
        return self.tokenizer.texts_to_sequences(texts)

    def index_to_word(self, index):
        assert(isinstance(index, int))
        assert(self.inverted_index is not None)
        if index == 0:
            return ""
        return self.inverted_index[index]


class SpacyTokenizer(Tokenizer):

    def __init__(self, with_lemmas=False):
        assert(isinstance(with_lemmas, bool))
        self.tokenizer = KerasTok(filters='[]{|}~', lower=False)
        self.nlp = self.__load_spacy_token_model()
        self.entity_list = self.__read_entity_list()
        self.with_lemmas = with_lemmas
        self.inverted_index = None

        assert(self.nlp is not None)
        assert(self.entity_list is not None)
        assert(isinstance(self.entity_list, dict))

    def __load_spacy_token_model(self):
        model = spacy.load(_SPACY_MODEL,
                           disable=['parser', 'textcat', 'tagger', 'ner'])
        if DEBUG:
            print("[SpacyTok] Loaded NLP model: {}".format(_SPACY_MODEL))
        return model

    def __read_entity_list(self):
        index = None
        with open(ENTITY_LIST_PATH, "r") as g:
            index = json.loads(g.read())
        ids = set()
        for word in index:
            assert(index[word] not in ids)
            ids.add(index[word])
        if DEBUG:
            print("[SpacyTok] Loaded {} entities.".format(len(index)))
        return index

    def __is_integer(self, text, positive=False):
        try:
            x = int(text)
            if positive and x <= 0:
                return False
            return True
        except Exception as e:
            pass
        return False

    def __process_num(self, token):
        return "number " + ' '.join(list(token.text))

    def __is_num(self, token):
        if token.is_alpha:  # ten
            return False
        if token.like_num:
            return True
        text = token.text
        if len(text) >= 2 and (text[0] == '-' or text[0] == "−"):
            try:
                float(text[1:])
                return True
            except Exception as e:
                pass
        return False

    def __process_interval(self, token):
        assert("–" in token.text)
        text = "interval from " + ' '.join(list(token.text))
        return text.replace("–", "to")

    def __is_interval(self, token):
        text = token.text
        if len(text) < 3:
            return False
        if text.count("–") != 1:
            return False
        idx = text.find("–")
        assert(idx >= 0)
        if idx == 0 or idx == len(text) - 1:
            return False
        if not self.__is_integer(text[0:idx]):
            return False
        if not self.__is_integer(text[idx + 1:]):
            return False
        return True

    def __process_measure(self, token):
        text = token.text
        assert(len(text) >= 2)
        fractional_part = None
        if text[-1] == "½":
            fractional_part = ".5"
        elif text[-1] == "¼":
            fractional_part = ".25"
        assert(fractional_part is not None)
        return "quantity " + ' '.join(list(text[:-1] + fractional_part))

    def __is_measure(self, token):
        text = token.text
        if len(text) < 2:
            return False
        if text[-1] == "½" or text[-1] == "¼":
            return True
        return False

    def __process_entity(self, token):
        text = token.text
        assert(text in self.entity_list)
        index = str(self.entity_list[text])
        index = ' '.join(list(index))
        return "entity <s> " + index + " </s>"

    # This method handles:
    # a) not like terms: I don't => I do not
    # b) Numbers
    # c) °C, °F, m²
    # d) Currency symbols.
    # e) Intervals: 1995–2010
    # f) Measurements: 2½
    # e) TODO(sebisebi): abbreviations
    def __process_text(self, text, return_lemmas=False):
        assert(isinstance(text, str))
        assert(isinstance(return_lemmas, bool))

        out = []
        doc = self.nlp(text)
        for token in doc:
            text = None
            if token.text == "n't":
                text = "not"
            elif token.is_digit:
                text = "number " + ' '.join(list(token.text))
            elif self.__is_num(token):
                text = self.__process_num(token)
            elif token.text == "°":
                text = "degrees"
            elif token.text == "C" and len(out) >= 1 and out[-1] == "degrees":
                text = "Celsius"
            elif token.text == "F" and len(out) >= 1 and out[-1] == "degrees":
                text = "Fahrenheit"
            elif token.is_currency:
                text = "money " + token.text
            elif token.text == "\'s":
                text = "\'s"
            elif token.text == "m²":
                text = "square meter"
            elif self.__is_interval(token):
                text = self.__process_interval(token)
            elif self.__is_measure(token):
                text = self.__process_measure(token)
            elif token.text in self.entity_list:
                text = self.__process_entity(token)
            else:
                if return_lemmas:
                    if token.lemma_ == "-PRON-":
                        text = token.text
                    else:
                        text = token.lemma_
                else:
                    text = token.text
            assert(text is not None)
            out.append(text)
        return ' '.join(out)

    def __process_texts(self, texts, return_lemmas=False, show_progress=False):
        assert(isinstance(texts, list))
        out = []
        values = texts
        if show_progress:
            values = tqdm.tqdm(texts, desc="[SpacyTok] Fit on texts")
        for text in values:
            out.append(self.__process_text(text, return_lemmas))
        return out

    def word_index(self):
        return self.tokenizer.word_index

    def fit_on_texts(self, texts):
        texts = self.__process_texts(texts, return_lemmas=self.with_lemmas,
                                     show_progress=True)
        # for text in texts:
        #     print(text)
        self.tokenizer.fit_on_texts(texts)

        # Build inverted index.
        word_index = self.tokenizer.word_index
        self.inverted_index = {}
        for word in word_index:
            index = word_index[word]
            self.inverted_index[index] = word

    def word_counts(self):
        return self.tokenizer.word_counts

    def texts_to_sequences(self, texts):
        texts = self.__process_texts(texts, return_lemmas=self.with_lemmas,
                                     show_progress=False)
        return self.tokenizer.texts_to_sequences(texts)

    def index_to_word(self, index):
        assert(isinstance(index, int))
        assert(self.inverted_index is not None)
        if index == 0:
            return ""
        return self.inverted_index[index]


'''
tok = SpacyTokenizer()
tok.fit_on_texts(["I couldn't drive 14½ km away from my -5¼ house - "
                  "in Abgeordnetenhaus, Germany.",
                  "It's like -421°F outside.",
                  "Can I buy this coat for ten $?",
                  "No, she doesn't like 141 guys!!!",
                  "It's Jamies's boat between 20–18412."])
'''
