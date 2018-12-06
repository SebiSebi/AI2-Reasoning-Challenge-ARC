
from rephrase.service_loader import SLoader


def split_in_sentences(text):
    assert(isinstance(text, str))
    nlp = SLoader.get_full_spacy_nlp()
    return list(nlp(text).sents)
