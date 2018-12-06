import MySQLdb
import itertools
import numpy as np
import os
import spacy

from settings import DEBUG
from settings import SMART_STOP_LIST_PATH

_SPACY_MODEL = "en_core_web_sm"
_ARC_CORPUS_PATH = os.path.join("data", "ARC_Corpus.txt")
_WIKIPEDIA_PATH = os.path.join("data", "wiki_text2.txt")
_ARC_CORPUS_LIMIT = 10000000
_WIKIPEDIA_CORPUS_LIMIT = 20000000
_TOTAL_SENTENCES = 30000000


# A list of reducers to be used when computing PMI over questions.
def reduce_max_or_default(array):
    if len(array) == 0:
        return 0
    return max(array)


def reduce_avg_or_default(array):
    if len(array) == 0:
        return 0
    return 1.0 * sum(array) / len(array)


def reduce_positive_avg(array):
    array = [x for x in array if x > 0]
    if len(array) == 0:
        return 0
    return 1.0 * sum(array) / len(array)


def reduce_max_and_avg(array):
    return [reduce_max_or_default(array), reduce_positive_avg(array)]


# Iteratator over the lines in a file. Split by '\n'.
# spaCy is used to remove stop words and tokenize each sentence.
class _LineIterator(object):
    def __init__(self, path, nlp, limit=None):
        self.path = path
        self.nlp = nlp
        self.limit = limit
        self.stop_words = set()

        # Add custom list of stop words.
        if DEBUG:
            print("[PMI] Adding SMART stop words for {} ...".format(path))
        with open(SMART_STOP_LIST_PATH, "r") as f:
            for line in f:
                word = line.rstrip()
                self.stop_words.add(word.lower())
                self.stop_words.add(word.capitalize())
        assert(self.nlp is not None)
        assert(self.limit is not None)

    def __iter__(self):
        if DEBUG:
            print("[PMI] Started to iterate over {}".format(self.path),
                  flush=True)
        processed = 0
        with open(self.path, "r") as g:
            for line in g:
                doc = self.nlp(line.strip())
                parsed = []
                for token in doc:
                    if token.is_stop or token.is_punct or token.is_space:
                        continue
                    if token.is_bracket or token.is_quote:
                        continue
                    if token.lower_ in self.stop_words:
                        continue
                    parsed.append(token.lower_)  # This *must* be lower.
                processed += 1
                if DEBUG and processed % 10000 == 0:
                    print("[PMI] Processed {} from {}".format(processed,
                                                              self.path))
                    print("", end='', flush=True)
                if self.limit is not None and processed > self.limit:
                    break
                yield parsed
        # StopIteration is automatically raised by Python.

    def __str__(self):
        return "LineIterator at {} (limit={})".format(self.path, self.limit)


class PMIData(object):
    '''
        Interact with PMI data from SQL. Build and query PMI(x, y).
    '''
    def __init__(self, use_ARC_corpus=False, use_wikipedia=False):
        if DEBUG:
            print("[PMI] Loading {} model ...".format(_SPACY_MODEL))
        self.nlp = spacy.load(_SPACY_MODEL,
                              disable=['parser', 'textcat', 'tagger', 'ner'])
        from settings import MYSQL_USER, MYSQL_PASSWORD, PMI_DB
        self.db = MySQLdb.connect(user=MYSQL_USER,
                                  passwd=MYSQL_PASSWORD,
                                  db=PMI_DB,
                                  use_unicode=True, charset='utf8',
                                  init_command='SET NAMES UTF8')
        if DEBUG:
            print("[PMI] Using MySQL DB for log(P).\n")

        self.datasets = []
        if use_ARC_corpus:
            self.datasets.append(_LineIterator(_ARC_CORPUS_PATH, self.nlp,
                                               _ARC_CORPUS_LIMIT))
        if use_wikipedia:
            self.datasets.append(_LineIterator(_WIKIPEDIA_PATH, self.nlp,
                                               _WIKIPEDIA_CORPUS_LIMIT))
        if DEBUG:
            aux = ["\t-> " + str(x) for x in self.datasets]
            print("[PMI] Using [\n{}\n[PMI] ] datasets.\n".format(
                                                '\n'.join(aux)))

    @staticmethod
    def build_bigrams(l):
        assert(isinstance(l, list))
        l = [x.lower() for x in l]
        bigrams = set()
        for i in range(0, len(l) - 1):
            bigrams.add((l[i], l[i + 1]))
        return bigrams

    @staticmethod
    def build_trigrams(l):
        assert(isinstance(l, list))
        l = [x.lower() for x in l]
        trigrams = set()
        for i in range(0, len(l) - 2):
            trigrams.add((l[i], l[i + 1], l[i + 2]))
        return trigrams

    def __remove_known_ngrams(self, ngrams):
        assert(isinstance(ngrams, set))
        known = {}
        rem = {}
        for ngram in ngrams:
            logp = self.fetch_logp_or_none(ngram)
            if logp is None:
                rem[ngram] = 0
            else:
                known[ngram] = logp
        assert(isinstance(known, dict))
        assert(isinstance(rem, dict))
        return known, rem

    # Returns float or None. ngram should be a tuple of words or
    # a single word (a string).
    def fetch_logp_or_none(self, ngram):
        assert(self.db is not None)
        assert(isinstance(ngram, tuple) or isinstance(ngram, str))
        words = None
        if isinstance(ngram, tuple):
            words = [x.lower() for x in ngram]
            assert(len(words) in [2, 3])
        else:
            words = [ngram.lower()]
        assert(len(words) >= 1 and len(words) <= 3)
        table = None
        word = None
        if len(words) == 1:
            word = words[0].lower()
            table = "unigrams"
        elif len(words) == 2:
            word = "|".join(words)
            table = "bigrams"
        elif len(words) == 3:
            word = "|".join(words)
            table = "trigrams"

        # Query MySQL db with the right word and table.
        word = MySQLdb.escape_string(word).decode()
        session = self.db.cursor()
        session.execute("""SELECT logp FROM {}
                           WHERE word = '{}'""".format(table, word))
        logp = session.fetchone()
        if logp is None:
            return None
        logp = float(logp[0])
        return logp

    def save_ngram(self, ngram, logp):
        assert(self.db is not None)
        assert(isinstance(ngram, tuple) or isinstance(ngram, str))

        words = None
        if isinstance(ngram, tuple):
            words = [x.lower() for x in ngram]
        else:
            words = [ngram]
        assert(len(words) >= 1 and len(words) <= 3)
        table = None
        word = None
        if len(words) == 1:
            word = words[0].lower()
            table = "unigrams"
        elif len(words) == 2:
            word = "|".join(words)
            table = "bigrams"
        elif len(words) == 3:
            word = "|".join(words)
            table = "trigrams"
        else:
            assert(False)
        try:
            word = MySQLdb.escape_string(word).decode()
            session = self.db.cursor()
            session.execute("""INSERT INTO {}(word, logp)
                               VALUES('{}', {})""".format(table, word, logp))
        except Exception as e:
            print("[PMI] WARNING! " + str(e))

    def __save_all_ngrams(self, ngrams, num_sentences):
        assert(isinstance(ngrams, dict))
        if num_sentences == 0:
            num_sentences = 1
        out = {}
        for word in ngrams:
            assert(ngrams[word] <= num_sentences)
            logp = np.log2(1.0 / num_sentences) * 2.0
            if ngrams[word] > 0:
                logp = np.log2(1.0 * ngrams[word] / num_sentences)
            self.save_ngram(word, logp)
            out[word] = logp
        self.db.commit()
        return out

    def fetch_coo_or_none(self, pair):
        assert(isinstance(pair, tuple))
        assert(len(pair) == 2)

        w1 = [x.lower() for x in pair[0]]
        w2 = [x.lower() for x in pair[1]]
        word = "%[({})]% AND %[({})]%".format("|".join(w1),
                                              "|".join(w2))
        word = MySQLdb.escape_string(word).decode()
        table = "cooccurrences"
        session = self.db.cursor()
        session.execute("""SELECT logp FROM {}
                           WHERE word = '{}'""".format(table, word))
        logp = session.fetchone()
        if logp is None:
            return None
        logp = float(logp[0])
        return logp

    def save_cooccurrence(self, pair, logp):
        assert(isinstance(pair, tuple))
        assert(len(pair) == 2)

        w1 = [x.lower() for x in pair[0]]
        w2 = [x.lower() for x in pair[1]]
        word = "%[({})]% AND %[({})]%".format("|".join(w1),
                                              "|".join(w2))
        try:
            word = MySQLdb.escape_string(word).decode()
            table = "cooccurrences"
            session = self.db.cursor()
            session.execute("""INSERT INTO {}(word, logp)
                               VALUES('{}', {})""".format(table, word, logp))
        except Exception as e:
            print("[PMI] WARNING! " + str(e))

    def __save_all_coos(self, coos, num_sentences):
        assert(isinstance(coos, dict))
        if num_sentences == 0:
            num_sentences = 1
        out = {}
        for pair in coos:
            assert(coos[pair] <= num_sentences)
            logp = np.log2(1.0 / num_sentences) * 2.0
            if coos[pair] > 0:
                logp = np.log2(1.0 * coos[pair] / num_sentences)
            self.save_cooccurrence(pair, logp)
            out[pair] = logp
        self.db.commit()
        return out

    def __remove_known_coos(self, cooccurrences):
        assert(isinstance(cooccurrences, set))
        known = {}
        rem = {}
        for pair in cooccurrences:
            assert(isinstance(pair, tuple))
            assert(len(pair) == 2)
            logp = self.fetch_coo_or_none(pair)
            if logp is None:
                rem[pair] = 0
            else:
                known[pair] = logp
        assert(isinstance(known, dict))
        assert(isinstance(rem, dict))
        return known, rem

    def __compute_cooccurrences(self, pairs):
        assert(isinstance(pairs, list))
        cooccurrences = set()
        for x, y in pairs:
            w1 = tuple([z.lower() for z in x])
            w2 = tuple([z.lower() for z in y])
            assert(len(w1) >= 1 and len(w1) <= 3)
            assert(len(w2) >= 1 and len(w2) <= 3)
            cooccurrences.add((w1, w2))
        known_coo, coo = self.__remove_known_coos(cooccurrences)
        assert(len(known_coo) + len(coo) == len(cooccurrences))
        if DEBUG:
            print("[PMI] Found {} cooccurrences.".format(len(cooccurrences)))
            print("", end='', flush=True)

        if len(coo) >= 1:
            num_sentences = 0
            for dataset in self.datasets:
                for sentence in dataset:
                    num_sentences += 1
                    unigrams = set([(x,) for x in sentence])
                    bigrams = PMIData.build_bigrams(sentence)
                    trigrams = PMIData.build_trigrams(sentence)

                    for x in set(itertools.product(unigrams, unigrams)):
                        if x[0] == x[1]:
                            continue
                        if x in coo:
                            coo[x] = coo[x] + 1
                    for x in set(itertools.product(bigrams, bigrams)):
                        if x[0] == x[1]:
                            continue
                        if x in coo:
                            coo[x] = coo[x] + 1
                    for x in set(itertools.product(trigrams, trigrams)):
                        if x[0] == x[1]:
                            continue
                        if x in coo:
                            coo[x] = coo[x] + 1

                    for x in set(itertools.product(unigrams, bigrams)):
                        if x in coo:
                            coo[x] = coo[x] + 1
                    for x in set(itertools.product(unigrams, trigrams)):
                        if x in coo:
                            coo[x] = coo[x] + 1
                    for x in set(itertools.product(bigrams, trigrams)):
                        if x in coo:
                            coo[x] = coo[x] + 1

                    for x in set(itertools.product(bigrams, unigrams)):
                        if x in coo:
                            coo[x] = coo[x] + 1
                    for x in set(itertools.product(trigrams, unigrams)):
                        if x in coo:
                            coo[x] = coo[x] + 1
                    for x in set(itertools.product(trigrams, bigrams)):
                        if x in coo:
                            coo[x] = coo[x] + 1
            assert(num_sentences == _TOTAL_SENTENCES)

            # Save ngrams logP to MySQL.
            coo = self.__save_all_coos(coo, num_sentences)
            for x in coo:
                assert(x not in known_coo)
                known_coo[x] = coo[x]

            if DEBUG:
                print("[PMI] Parsed {} sentences.".format(num_sentences))
        elif DEBUG:
            print("[PMI] All cooccurrences are known :)")

        assert(isinstance(known_coo, dict))
        assert(len(known_coo) == len(cooccurrences))

        if DEBUG:
            lb = np.log2(1.0 / _TOTAL_SENTENCES)
            aux = sum(1 for x in known_coo if known_coo[x] >= lb)
            print("[PMI] Known cooccurrences probabilities: {} ({}%)".format(
                        aux,
                        round(100.0 * aux / max(len(known_coo), 1), 2)))

        return known_coo

    # pairs is a list of (x, y) values where x and y are also list of words.
    # Example:
    #       [(["I"], ["am"]),
    #        (["New"], ["York", "is"]),
    #        (["protons", "and", "neutrons"], ["atom"])]
    # Everything is converted to lower.
    def fetch_PMI_values(self, pairs):
        all_words = set()
        bigrams = set()
        trigrams = set()
        for x, y in pairs:
            assert(len(x) >= 1 and len(x) <= 3)
            assert(len(y) >= 1 and len(y) <= 3)

            if len(x) == 1:
                all_words.add(x[0].lower())
            elif len(x) == 2:
                bigrams.add(tuple([z.lower() for z in x]))
            else:
                trigrams.add(tuple([z.lower() for z in x]))

            if len(y) == 1:
                all_words.add(y[0].lower())
            elif len(y) == 2:
                bigrams.add(tuple([z.lower() for z in y]))
            else:
                trigrams.add(tuple([z.lower() for z in y]))

        for x in all_words:
            assert(isinstance(x, str))
        for x in bigrams:
            assert(isinstance(x, tuple))
            assert(len(x) == 2)
        for x in trigrams:
            assert(isinstance(x, tuple))
            assert(len(x) == 3)

        const_num_words = len(all_words)
        const_num_bigrams = len(bigrams)
        const_num_trigrams = len(trigrams)
        if DEBUG:
            print("[PMI] Found {} unigrams, {} bigrams, {} trigrams.".format(
                    const_num_words, const_num_bigrams, const_num_trigrams))

        # Already known ngram probabilities should not be re-computed.
        known_unigrams, unigrams = self.__remove_known_ngrams(all_words)
        known_bigrams, bigrams = self.__remove_known_ngrams(bigrams)
        known_trigrams, trigrams = self.__remove_known_ngrams(trigrams)
        assert(const_num_words == len(known_unigrams) + len(unigrams))
        assert(const_num_bigrams == len(known_bigrams) + len(bigrams))
        assert(const_num_trigrams == len(known_trigrams) + len(trigrams))

        if len(unigrams) + len(bigrams) + len(trigrams) >= 1:
            # Start iterating and counting.
            num_sentences = 0
            for dataset in self.datasets:
                for sentence in dataset:
                    assert(isinstance(sentence, list))
                    num_sentences += 1

                    # Count unigrams.
                    for x in set(sentence):
                        assert(isinstance(x, str))
                        if x in unigrams:
                            unigrams[x] = unigrams[x] + 1

                    # Count bigrams.
                    for x in PMIData.build_bigrams(sentence):
                        assert(isinstance(x, tuple))
                        if x in bigrams:
                            bigrams[x] = bigrams[x] + 1

                    # Count trigrams.
                    for x in PMIData.build_trigrams(sentence):
                        assert(isinstance(x, tuple))
                        if x in trigrams:
                            trigrams[x] = trigrams[x] + 1
            if DEBUG:
                print("[PMI] Parsed {} sentences.".format(num_sentences))
            assert(num_sentences == _TOTAL_SENTENCES)

            # Save ngrams logP to MySQL.
            unigram = self.__save_all_ngrams(unigrams, num_sentences)
            bigram = self.__save_all_ngrams(bigrams, num_sentences)
            trigram = self.__save_all_ngrams(trigrams, num_sentences)

            for x in unigram:
                assert(x not in known_unigrams)
                known_unigrams[x] = unigram[x]
            for x in bigram:
                assert(x not in known_bigrams)
                known_bigrams[x] = bigram[x]
            for x in trigram:
                assert(x not in known_trigrams)
                known_trigrams[x] = trigram[x]
        elif DEBUG:
            print("[PMI] All ngrams are known :)")
        assert(isinstance(known_unigrams, dict))
        assert(isinstance(known_bigrams, dict))
        assert(isinstance(known_trigrams, dict))
        assert(len(known_unigrams) == const_num_words)
        assert(len(known_bigrams) == const_num_bigrams)
        assert(len(known_trigrams) == const_num_trigrams)

        if DEBUG:
            lb = np.log2(1.0 / _TOTAL_SENTENCES)
            aux = sum(1 for x in known_unigrams if known_unigrams[x] >= lb)
            print("[PMI] Known unigrams probabilities: {} ({}%)".format(
                        aux,
                        round(100.0 * aux / max(len(known_unigrams), 1), 2)))
            aux = sum(1 for x in known_bigrams if known_bigrams[x] >= lb)
            print("[PMI] Known bigrams probabilities: {} ({}%)".format(
                        aux,
                        round(100.0 * aux / max(len(known_bigrams), 1), 2)))
            aux = sum(1 for x in known_trigrams if known_trigrams[x] >= lb)
            print("[PMI] Known trigrams probabilities: {} ({}%)".format(
                        aux,
                        round(100.0 * aux / max(len(known_trigrams), 1), 2)))
            print("", flush=True)

        cooccurrences = self.__compute_cooccurrences(pairs)

        # ngrams will be a dictionary with keys being pairs such
        # as ("am",), ("united", "states"), etc. and values are
        # logarithms base 2 of probabilities.
        ngrams = {}
        for x in known_unigrams:
            ngrams[(x.lower(),)] = known_unigrams[x]
        for x in known_bigrams:
            assert(x not in ngrams)
            ngrams[x] = known_bigrams[x]
        for x in known_trigrams:
            assert(x not in ngrams)
            ngrams[x] = known_trigrams[x]
        assert(len(ngrams) == (len(known_unigrams) +
                               len(known_bigrams) +
                               len(known_trigrams)))

        out = []
        lower_bound = np.log2(1.0 / _TOTAL_SENTENCES)
        pmis_found = 0
        bigram_pmis_found = 0
        trigram_pmis_found = 0
        total_bigrams = 0
        total_trigrams = 0
        for pair in pairs:
            x = tuple([z.lower() for z in pair[0]])
            y = tuple([z.lower() for z in pair[1]])
            assert(len(x) >= 1 and len(x) <= 3)
            assert(len(y) >= 1 and len(y) <= 3)
            if len(x) == 2 or len(y) == 2:
                total_bigrams += 1
            if len(x) == 3 or len(y) == 3:
                total_trigrams += 1
            assert(x in ngrams)
            assert(y in ngrams)
            assert((x, y) in cooccurrences)
            px = ngrams[x]
            py = ngrams[y]
            pxy = cooccurrences[(x, y)]
            if px < lower_bound or py < lower_bound or pxy < lower_bound:
                out.append(-0.75)
            else:
                pmis_found += 1
                out.append((pxy - px - py) / (-pxy))
                if len(x) == 2 or len(y) == 2:
                    bigram_pmis_found += 1
                if len(x) == 3 or len(y) == 3:
                    trigram_pmis_found += 1

        assert(len(pairs) == len(out))
        if DEBUG:
            print("", flush=True)
            print("[PMI] Valid PMI values computed: {} ({}%).".format(
                    pmis_found,
                    round(100.0 * pmis_found / max(len(pairs), 1), 2)))
            total_bigrams = max(total_bigrams, 1)
            total_trigrams = max(total_trigrams, 1)
            print("[PMI] Valid bigram PMI values computed: {} ({}%).".format(
                    bigram_pmis_found,
                    round(100.0 * bigram_pmis_found / total_bigrams, 2)))
            print("[PMI] Valid trigram PMI values computed: {} ({}%).".format(
                    trigram_pmis_found,
                    round(100.0 * trigram_pmis_found / total_trigrams, 2)))
            print("", flush=True)
        assert(isinstance(out, list))
        return out


# pmi = PMIData(use_ARC_corpus=True, use_wikipedia=True)
# pmi.fetch_PMI_values([(["erectus"], ["fossils"]),
#                       (["produced", "Sergo"], ["Sergo"]),
#                       (["protons", "and", "neUtrons"], ["10"]),
#                       (["me", "and", "she"], ["this", "bigram"])])
# print(pmi.fetch_PMI_values([(["air"], ["clean"]), (["jump"], ["soil"])]))
