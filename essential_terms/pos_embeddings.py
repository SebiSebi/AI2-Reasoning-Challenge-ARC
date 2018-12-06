'''
    This module is used to build word vectors for POS tags.
    For info regarding POS meaning see [1]. For spaCy full
    tag list see [2].

    [1] https://www.clips.uantwerpen.be/pages/mbsp-tags
    [2] https://github.com/explosion/spaCy/blob/master/spacy/lang/en/tag_map.py
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
            print("Loading {} model ...".format(_SPACY_MODEL))
        self.nlp = spacy.load(_SPACY_MODEL, disable=['parser', 'textcat'])
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
                    assert(isinstance(token.tag_, str))
                    assert(token.tag_ is not None)
                    parsed.append(token.tag_)
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
    for pos in ["VB", "POS", "WRB", "JJ", "NN", "."]:
        predicted = model.wv.most_similar(positive=[pos])
        print("Predictions for {}:".format(spacy.explain(pos)))
        for (w, sim) in predicted:
            print("\t", spacy.explain(w), round(sim, 3))
        print("")


def _train(save_model=True, output_path=None, show_plot=False):
    # Warning: ARC Corpus is very large! (14621856 sentences)
    sentence_iterator = _SentenceIterator(os.path.join("data",
                                                       "ARC_Corpus.txt"),
                                          limit=100000)

    # sg = 1 => use skip-grams instead of CBOW.
    # size = word vector size
    # window is the maximum distance between the target word and words around.
    model = Word2Vec(sentence_iterator,
                     size=10, sg=1, window=5,
                     min_count=100, workers=6, iter=10)
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
    # _train(save_model=True, output_path="data/model.bin", show_plot=False)
    model = Word2Vec.load("data/model2.bin")
    # _show_pca_plot(model)
    _test(model)
