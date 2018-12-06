import string

from scitail.service_loader import SLoader


# Basic tokenizing (not to be used for advanced stuff).
def tokenize(sentence):
    aux = sentence
    for x in list(string.punctuation):
        aux = aux.replace(x, ' ')
    # Hack to remove multiple consecutive spaces.
    return [x.strip() for x in ' '.join(aux.split()).strip().split(' ')]


# Basic tokenizing (not to be used for advanced stuff).
def num_words(sentence):
    return len(tokenize(sentence))


def split_in_sentences(text):
    assert(isinstance(text, str))
    nlp = SLoader.get_token_spacy_nlp()
    return list(nlp(text).sents)
