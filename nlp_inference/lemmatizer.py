import spacy


class Lemmatizer(object):
    ''' Wrapper for lazy loading and lemmatization over SpaCy. '''

    def __init__(self, nlp=None, model='en_core_web_sm'):
        self.nlp = None
        if nlp is not None:
            self.nlp = nlp
        else:
            self.nlp = spacy.load(model)

    # Tokenize -> lemmatize -> join a sequence or text
    def sequence_lemmas(self, seq):
        doc = self.nlp(seq, disable=['parser', 'tagger', 'textcat', 'ner'])
        lemmas = []
        for token in doc:
            if token.is_punct:
                continue
            lemma = token.lemma_
            if lemma == '-PRON-':
                lemma = token.lower_
            lemmas.append(lemma)
        return ' '.join(lemmas)
