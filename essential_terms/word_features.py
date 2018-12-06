import json
import numpy as np
import spacy

from dep_graph_utils import build_degree_centrality
from dep_graph_utils import build_closeness_centrality
from dep_graph_utils import build_eigenvector_centrality
from gensim.models import Word2Vec
from pmi_utils import PMIData
from pmi_utils import reduce_max_and_avg
from settings import DEBUG
from settings import SCIENCE_TERMS_LIST_PATH
from settings import CONCRETNESS_RATINGS_PATH
from settings import POS_EMBEDDINGS_PATH, POS_EMBEDDINGS_DIM
from settings import DEP_EMBEDDINGS_PATH, DEP_EMBEDDINGS_DIM
from settings import SMART_STOP_LIST_PATH
from settings import NER_LIST_PATH
from settings import NER_COUNT

_SPACY_MODEL = "en_core_web_sm"

# Entry fields used:
#   -> question
#   -> answers
#   -> terms
#   -> q_doc
#   -> deg_centrality
#   -> closeness_centrality
#   -> eigen_centrality
#   -> tok_answer0
#   -> tok_answer1
#   -> tok_answer2
#   -> tok_answer3
#   -> tok_question


class WordFeatures(object):
    def __init__(self):
        if DEBUG:
            print("[WF] Setting up word features ...")

        self.science_terms_list = self.__read_science_terms_list()
        self.concretness_ratings = self.__read_concretness_ratings()
        self.pos_embedding_model = self.__read_pos_embeddings()
        self.dep_embedding_model = self.__read_dep_embeddings()
        self.nlp = self.__load_spacy_model()
        self.token_nlp = self.__load_spacy_token_model()
        self.stop_words = self.__load_smart_stop_words()
        self.NER_ids = self.__load_NER_bijection()
        self.pmi_values = None

        assert(isinstance(self.science_terms_list, set))
        assert(isinstance(self.concretness_ratings, dict))
        assert(isinstance(self.pos_embedding_model, Word2Vec))
        assert(isinstance(self.dep_embedding_model, Word2Vec))
        assert(isinstance(self.nlp, spacy.lang.en.English))
        assert(isinstance(self.token_nlp, spacy.lang.en.English))
        assert(self.nlp is not self.token_nlp)
        assert(isinstance(self.stop_words, set))
        assert(isinstance(self.NER_ids, dict))

        if DEBUG:
            print("[WF] All data loaded (spaCy, POS embeddings, s.a.).\n")

    def __read_science_terms_list(self):
        # Read the list of science terms (about 9010).
        data = set()
        with open(SCIENCE_TERMS_LIST_PATH, "r") as g:
            for line in g:
                data.add(line.strip())
        if DEBUG:
            print("[WF] Read {} science terms.".format(len(data)))
        return data

    def __read_concretness_ratings(self):
        data = None
        with open(CONCRETNESS_RATINGS_PATH, "r") as g:
            data = json.loads(g.read())
            assert("ratingsMap" in data)
            data = data["ratingsMap"]
            for word in data:
                assert("rating" in data[word])
            if DEBUG:
                print("[WF] Read {} concretness ratings.".format(len(data)))
        return data

    def __read_pos_embeddings(self):
        model = Word2Vec.load(POS_EMBEDDINGS_PATH)
        if DEBUG:
            print("[WF] Loaded POS embeddings from {}.".format(
                                                    POS_EMBEDDINGS_PATH))
        return model

    def __read_dep_embeddings(self):
        model = Word2Vec.load(DEP_EMBEDDINGS_PATH)
        if DEBUG:
            print("[WF] Loaded DEP embeddings from {}.".format(
                                                    DEP_EMBEDDINGS_PATH))
        return model

    def __load_spacy_model(self):
        model = spacy.load(_SPACY_MODEL)
        if DEBUG:
            print("[WF] Loaded {} model.".format(_SPACY_MODEL))
        return model

    def __load_spacy_token_model(self):
        model = spacy.load(_SPACY_MODEL,
                           disable=['parser', 'textcat', 'tagger', 'ner'])
        if DEBUG:
            print("[WF] Loaded {} model for tokenization only.".format(
                                                    _SPACY_MODEL))
        return model

    def __load_smart_stop_words(self):
        stop_words = set()
        with open(SMART_STOP_LIST_PATH, "r") as f:
            for line in f:
                word = line.rstrip()
                stop_words.add(word.lower())
                stop_words.add(word.capitalize())
        if DEBUG:
            print("[WF] Loaded {} SMART stop words.".format(
                                                    len(stop_words) >> 1))
        return stop_words

    def __load_NER_bijection(self):
        ids = None
        with open(NER_LIST_PATH, "r") as g:
            ids = json.loads(g.read())
        if ids is None:
            return None
        if len(ids) != NER_COUNT:
            return None
        for ner in ids:
            assert(isinstance(ner, str))
            assert(isinstance(ids[ner], int))
        if DEBUG:
            print("[WF] Loaded {} NER ids.".format(len(ids)))
        return ids

    def __maybe_parse_question(self, entry):
        # Should we parse the question using spaCy?
        if "q_doc" not in entry or entry["q_doc"] is None:
            entry["q_doc"] = self.nlp(entry["question"])
        assert(entry["q_doc"].is_parsed)

    def __maybe_build_degree_centrality(self, entry):
        assert(entry["q_doc"].is_parsed)
        if "deg_centrality" not in entry or entry["deg_centrality"] is None:
            entry["deg_centrality"] = build_degree_centrality(entry["q_doc"])
        assert("deg_centrality" in entry)

    def __maybe_build_closeness_centrality(self, entry):
        assert(entry["q_doc"].is_parsed)
        name = "closeness_centrality"
        if name not in entry or entry[name] is None:
            entry[name] = build_closeness_centrality(entry["q_doc"])
        assert("closeness_centrality" in entry)

    def __maybe_build_eigenvector_centrality(self, entry):
        assert(entry["q_doc"].is_parsed)
        name = "eigen_centrality"
        if name not in entry or entry[name] is None:
            entry[name] = build_eigenvector_centrality(entry["q_doc"])
        assert("eigen_centrality" in entry)

    def is_science_term(self, word):
        assert(isinstance(word, str))
        if word in self.science_terms_list:
            return True
        return False

    def get_concretness_rating(self, word):
        assert(isinstance(word, str))
        if word in self.concretness_ratings:
            return self.concretness_ratings[word]["rating"]
        else:
            return 2.5

    def get_POS_embedding(self, word, entry):
        # Entry is a reference to the tuple (question, answers, terms).
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))

        self.__maybe_parse_question(entry)
        doc = entry["q_doc"]
        assert(isinstance(doc, spacy.tokens.doc.Doc))

        tag = None
        for token in doc:
            if token.text == word or token.lower_ == word:
                tag = token.tag_
                break

        emb = None
        try:
            emb = self.pos_embedding_model.wv[tag]
        except:
            emb = np.zeros((POS_EMBEDDINGS_DIM,))
        assert(emb is not None)
        assert(len(emb.shape) == 1)
        assert(emb.shape[0] == POS_EMBEDDINGS_DIM)
        return emb

    def get_DEP_embedding(self, word, entry):
        # Entry is a reference to the tuple (question, answers, terms).
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))

        self.__maybe_parse_question(entry)
        doc = entry["q_doc"]
        assert(isinstance(doc, spacy.tokens.doc.Doc))

        dep = None
        for token in doc:
            if token.text == word or token.lower_ == word:
                dep = token.dep_
                break

        emb = None
        try:
            emb = self.dep_embedding_model.wv[dep]
        except:
            emb = np.zeros((DEP_EMBEDDINGS_DIM,))
        assert(emb is not None)
        assert(len(emb.shape) == 1)
        assert(emb.shape[0] == DEP_EMBEDDINGS_DIM)
        return emb

    def is_stop_word(self, word, entry):
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))

        self.__maybe_parse_question(entry)
        doc = entry["q_doc"]
        assert(isinstance(doc, spacy.tokens.doc.Doc))

        for token in doc:
            if token.text == word or token.lower_ == word:
                return token.is_stop or token.is_punct or token.is_quote
        return False

    def get_degree_centrality(self, word, entry):
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))

        self.__maybe_parse_question(entry)
        self.__maybe_build_degree_centrality(entry)
        assert("deg_centrality" in entry)
        deg_centrality = entry["deg_centrality"]
        if word in deg_centrality:
            return deg_centrality[word]
        if word.lower() in deg_centrality:
            return deg_centrality[word.lower()]
        return 0.0

    def get_closeness_centrality(self, word, entry):
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))

        self.__maybe_parse_question(entry)
        self.__maybe_build_closeness_centrality(entry)
        closeness_centrality = entry["closeness_centrality"]
        if word in closeness_centrality:
            return closeness_centrality[word]
        if word.lower() in closeness_centrality:
            return closeness_centrality[word.lower()]
        return 0.0

    def get_eigen_centrality(self, word, entry):
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))

        self.__maybe_parse_question(entry)
        self.__maybe_build_eigenvector_centrality(entry)
        eigen_centrality = entry["eigen_centrality"]
        if word in eigen_centrality:
            return eigen_centrality[word]
        if word.lower() in eigen_centrality:
            return eigen_centrality[word.lower()]
        return 0.0

    def get_one_hot_NER(self, word, entry):
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))

        self.__maybe_parse_question(entry)
        doc = entry["q_doc"]
        assert(isinstance(doc, spacy.tokens.doc.Doc))

        ners = set()
        for token in doc:
            if token.text == word or token.lower_ == word:
                if token.ent_type_ != "":
                    ners.add(token.ent_type_)
        # There can be more that one NER per token. Example:
        #       50 {'CARDINAL', 'QUANTITY'}
        one_hot = np.zeros((NER_COUNT,), dtype=np.float32)
        for ner in ners:
            assert(ner in self.NER_ids)
            one_hot[self.NER_ids[ner]] = 1.0
        return one_hot

    def get_bool_features(self, word, entry):
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))

        self.__maybe_parse_question(entry)
        doc = entry["q_doc"]
        assert(isinstance(doc, spacy.tokens.doc.Doc))

        features = np.zeros((3,), dtype=np.float32)
        for token in doc:
            if token.text == word or token.lower_ == word:
                if token.is_upper and token.is_stop is False:
                    if word.lower() in self.stop_words:
                        continue
                    features[0] = 1.0
                if token.is_currency:
                    features[1] = 1.0
                if token.like_num:
                    features[2] = 1.0
                break
        return features

    # To be used for PMI usage only.
    def __maybe_tokenize(self, name, text, entry):
        if name not in entry or entry[name] is None:
            entry[name] = self.__tokenize_and_remove_stopwords(text)
        return entry[name]

    def get_PMI(self, word, entry, use_question=True,
                reduce_f=reduce_max_and_avg):
        assert(isinstance(word, str))
        assert(isinstance(entry, dict))
        assert(isinstance(use_question, bool))

        term = word.lower()
        unigram_pmi = []  # (term, unigram)
        bigram_pmi = []  # (term, bigram)
        trigram_pmi = []  # (term, trigram)
        docs = [
            self.__maybe_tokenize("tok_answer0", entry["answers"][0], entry),
            self.__maybe_tokenize("tok_answer1", entry["answers"][1], entry),
            self.__maybe_tokenize("tok_answer2", entry["answers"][2], entry),
            self.__maybe_tokenize("tok_answer3", entry["answers"][3], entry)
        ]
        if use_question:
            docs = docs + [
                self.__maybe_tokenize("tok_question", entry["question"], entry)
            ]
        assert(len(docs) in [4, 5])

        # Build ngrams from answers and [question].
        ngrams = set()
        for doc in docs:
            ngrams.update(set([(x.lower(),) for x in doc]))
            ngrams.update(PMIData.build_bigrams(doc))
            ngrams.update(PMIData.build_trigrams(doc))
        for ngram in ngrams:
            assert(len(ngram) >= 1 and len(ngram) <= 3)
            if term in ngram or term.lower() in ngram:
                continue
            pair = ((term.lower(),), ngram)
            assert(pair in self.pmi_values)
            value = self.pmi_values[pair]
            if len(ngram) == 1:
                unigram_pmi.append(value)
            elif len(ngram) == 2:
                bigram_pmi.append(value)
            else:
                trigram_pmi.append(value)

        unigram_pmi = reduce_f(unigram_pmi)
        bigram_pmi = reduce_f(bigram_pmi)
        trigram_pmi = reduce_f(trigram_pmi)

        return np.array([unigram_pmi, bigram_pmi, trigram_pmi])

    def __tokenize_and_remove_stopwords(self, text):
        assert(isinstance(text, str))
        doc = self.token_nlp(text)
        tokens = []
        for token in doc:
            if token.is_stop or token.is_punct or token.is_space:
                continue
            if token.is_bracket or token.is_quote:
                continue
            if token.lower_ in self.stop_words:
                continue
            tokens.append(token.lower_)  # This *must* be lower.
        return tokens

    def train_PMI(self, dataset):
        assert(isinstance(dataset, list))
        if DEBUG:
            print("[WF][train_PMI] Dataset length: {}".format(len(dataset)))
        pairs = []
        for entry in dataset:
            assert("question" in entry)
            assert("answers" in entry)
            assert("terms" in entry)

            # Include both the questions and anwers.
            docs = [
                self.__tokenize_and_remove_stopwords(entry["question"]),
                self.__tokenize_and_remove_stopwords(entry["answers"][0]),
                self.__tokenize_and_remove_stopwords(entry["answers"][1]),
                self.__tokenize_and_remove_stopwords(entry["answers"][2]),
                self.__tokenize_and_remove_stopwords(entry["answers"][3])
            ]
            assert(len(docs) == 5)
            ngrams = set()
            for doc in docs:
                ngrams.update(set([(x.lower(),) for x in doc]))
                ngrams.update(PMIData.build_bigrams(doc))
                ngrams.update(PMIData.build_trigrams(doc))
            for term in entry["terms"]:
                for ngram in ngrams:
                    if term in ngram or term.lower() in ngram:
                        continue
                    pairs.append(([term.lower()], list(ngram)))
        if DEBUG:
            print("[WF][train_PMI] Need to compute {} PMI values "
                  "(with duplicates).\n".format(len(pairs)))
            print("", end='', flush=True)

        pmi = PMIData(use_ARC_corpus=True, use_wikipedia=True)
        pmi_values = pmi.fetch_PMI_values(pairs)
        assert(len(pairs) == len(pmi_values))

        self.pmi_values = {}
        for i in range(0, len(pairs)):
            assert(isinstance(pairs[i][0], list))
            assert(isinstance(pairs[i][1], list))
            pair = (tuple(pairs[i][0]), tuple(pairs[i][1]))
            if pair not in self.pmi_values:
                self.pmi_values[pair] = pmi_values[i]
            else:
                assert(np.allclose(pmi_values[i], self.pmi_values[pair]))
        assert(len(self.pmi_values) <= len(pairs))
        assert(len(self.pmi_values) <= len(pmi_values))
        for pair in self.pmi_values:
            new_pair = (pair[1], pair[0])
            if new_pair in self.pmi_values:
                value1 = self.pmi_values[pair]
                value2 = self.pmi_values[new_pair]
                if not np.allclose(value1, value2):
                    print("[WF][train_PMI] WARNING! Swapped pair expected to "
                          "have the same value: {}:{} \t {}:{}".format(
                              pair, value1, new_pair, value2), flush=True)

        if DEBUG:
            print("[WF][train_PMI] Computed {} unique PMI values.".format(
                                                    len(self.pmi_values)))
            show_pmi = []
            for pair in self.pmi_values:
                if self.pmi_values[pair] > 0:
                    show_pmi.append((pair, self.pmi_values[pair]))
            show_pmi.sort(key=lambda x: x[1], reverse=True)
            num_positive = len(show_pmi)
            print("[WF][train_PMI] Found {} ({}%) positive NPMI values".format(
                num_positive,
                round(100.0 * num_positive / max(len(self.pmi_values), 1), 2)))
            out = '\n'.join(["\t * " + str(x) for x in show_pmi[:20]])
            print("[WF][train_PMI] Top correlated pairs:\n{}\n".format(out))

        assert(self.pmi_values is not None)
        assert(isinstance(self.pmi_values, dict))

# TODO(sebisebi):
# answers like:  'owl', '→', 'mole', '→', 'bugs', '→', 'grass',
# maybe replace -> with a word
