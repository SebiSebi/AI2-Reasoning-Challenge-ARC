'''
    This module is used to build word vectors for DEP tags.
    For info regarding dep meaning see [1] and [4]. For spaCy full
    dep list see [2] and [3]. The English dependency labels
    use the CLEAR Style by ClearNLP [4].

    [1] http://universaldependencies.org/u/dep/
    [2] https://github.com/explosion/spaCy/issues/233
    [3] https://spacy.io/api/annotation#section-dependency-parsing
    [4] http://www.mathcs.emory.edu/~choi/doc/cu-2012-choi.pdf
'''
import datetime
import dateutil.relativedelta
import numpy as np
import os
import spacy
import time

from gensim.models import Word2Vec
from settings import DEBUG

_SPACY_MODEL = "en_core_web_lg"


class _SentenceIterator(object):
    def __init__(self, path, limit=None):
        self.path = path
        if DEBUG:
            print("Loading {} model ...".format(_SPACY_MODEL), flush=True)
        self.nlp = spacy.load(_SPACY_MODEL, disable=['textcat', 'ner'])
        self.limit = limit

    def __iter__(self):
        if DEBUG:
            print("Started to iterate over sentences ", end='', flush=True)
        start_time = time.time()
        processed = 0
        with open(self.path, "r") as g:
            for line in g:
                doc = self.nlp(line.strip())
                parsed = []
                for token in doc:
                    assert(isinstance(token.dep_, str))
                    assert(token.dep_ is not None)
                    if token.dep_ == "":
                        continue
                    parsed.append(token.dep_)
                processed += 1
                if self.limit is not None and processed > self.limit:
                    break
                yield parsed
        # StopIteration is automatically raised by Python.

        if DEBUG:
            end_time = time.time()
            start_time = datetime.datetime.fromtimestamp(start_time)
            end_time = datetime.datetime.fromtimestamp(end_time)
            delta = dateutil.relativedelta.relativedelta(end_time, start_time)
            if delta.minutes > 0:
                print("(took {} min, {} sec and {} ms).".format(
                            delta.minutes, delta.seconds,
                            delta.microseconds / 1000.0),
                      flush=True)
            else:
                print("(took {} sec and {} ms).".format(
                            delta.seconds, delta.microseconds / 1000.0),
                      flush=True)


def _show_pca_plot(model):
    import matplotlib.pyplot as plt
    from sklearn.decomposition import PCA

    num_words = len(model.wv.vocab)
    # Lines are words in ND space => a matrix of num_words x size
    # Fit the model and apply the dimensionality reduction.
    data = PCA(n_components=2).fit_transform(model[model.wv.vocab])
    assert(isinstance(data, np.ndarray))
    assert(data.shape[0] == num_words)
    assert(data.shape[1] == 2)

    plt.scatter(data[:, 0], data[:, 1], s=50, c='r', marker='x', linewidth=1)
    words = list(model.wv.vocab)
    for i in range(0, len(words)):
        plt.annotate(' ' + words[i], xy=(data[i, 0], data[i, 1]))
    plt.show()


def _test(model):
    for dep in ["nsubj", "attr", "prep", "pobj", "punct", "det"]:
        predicted = model.wv.most_similar(positive=[dep])
        print("Predictions for {}:".format(spacy.explain(dep)))
        for (w, sim) in predicted:
            print("\t", spacy.explain(w), round(sim, 3))
        print("")


def _train(save_model=True, output_path=None, show_plot=False):
    # Warning: ARC Corpus is very large! (14621856 sentences)
    sentence_iterator = _SentenceIterator(os.path.join("data",
                                                       "ARC_Corpus.txt"),
                                          limit=400000)

    # sg = 1 => use skip-grams instead of CBOW.
    # size = word vector size
    # window is the maximum distance between the target word and words around.
    # iter = number of epochs (iterations over the entire dataset).
    model = Word2Vec(sentence_iterator,
                     size=9, sg=1, window=4,
                     min_count=100, workers=8, iter=5)
    num_words = len(model.wv.vocab)
    if DEBUG:
        print("Done training model. {} words found.".format(num_words))
    if save_model:
        model.save(output_path)
        if DEBUG:
            print("Model saved at {}".format(output_path))

    if show_plot:
        _show_pca_plot(model)


if __name__ == "__main__":
    _train(save_model=True, show_plot=False,
           output_path="data/dep_embeddings.bin")
    # model = Word2Vec.load("data/model.bin")
    # _show_pca_plot(model)
    # _test(model)
