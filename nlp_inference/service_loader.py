import spacy

from spacy.symbols import ORTH, LEMMA, POS


class SLoader(object):
    __nlp = None

    @staticmethod
    def get_token_spacy_nlp():
        if SLoader.__nlp is None:
            SLoader.__nlp = spacy.load('en_core_web_sm',
                                       disable=['parser',
                                                'textcat',
                                                'tagger',
                                                'ner'])
            SLoader.__nlp.add_pipe(SLoader.__nlp.create_pipe('sentencizer'))
            for i in range(2, 15):
                x = '_' * i
                SLoader.__nlp.tokenizer.add_special_case(x, [
                    {
                        ORTH: x,
                        LEMMA: x,
                        POS: 'NOUN'
                    }
                ])
        return SLoader.__nlp
