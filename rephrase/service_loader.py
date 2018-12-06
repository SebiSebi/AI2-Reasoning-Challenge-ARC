import json
import spacy

from rephrase.settings import PAST_TENSE_VERB_LIST, VERB_LIST
from rephrase.settings import PAST_PARTICIPLE_VERB_LIST
from spacy.symbols import ORTH, LEMMA, POS


class SLoader(object):
    __nlp = None
    __past_tense_list = None
    __verb_list = None
    __past_participle_list = None

    @staticmethod
    def get_full_spacy_nlp():
        if SLoader.__nlp is None:
            SLoader.__nlp = spacy.load('en_core_web_sm')

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

    @staticmethod
    def get_past_tense_list():
        if SLoader.__past_tense_list is None:
            obj = None
            with open(PAST_TENSE_VERB_LIST, "r") as f:
                obj = json.loads(f.read())
            SLoader.__past_tense_list = obj

        return SLoader.__past_tense_list

    @staticmethod
    def get_past_participle_list():
        if SLoader.__past_participle_list is None:
            obj = None
            with open(PAST_PARTICIPLE_VERB_LIST, "r") as f:
                obj = json.loads(f.read())
            SLoader.__past_participle_list = obj

        return SLoader.__past_participle_list

    @staticmethod
    def get_verb_list():
        if SLoader.__verb_list is None:
            obj = set()
            with open(VERB_LIST, "r") as f:
                for line in f:
                    obj.add(line.strip())
            SLoader.__verb_list = obj

        return SLoader.__verb_list
