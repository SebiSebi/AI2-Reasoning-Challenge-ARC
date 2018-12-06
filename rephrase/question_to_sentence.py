'''
    Given a question, this rephraser transforms it into an affirmative sentence
    by replacing the corresponding question span with @placeholder token.

    Which of these is a greenhouse gas?
        => @placeholder is a greenhouse gas .

    How does a parachute increase air resistance to allow parachutist to land?
        => a parachute increase air resistance to allow
                parachutist to land [by] @placeholder .

    The atoms in a can of soda are __________.
        => The atoms in a can of soda are @placeholder .
'''

import include_sys_path
import rephrase.question_dispatcher as question_dispatcher
import rephrase.rephraser as rephraser
import rephrase.texts as texts
import spacy

from rephrase.decorators import with_caching
from rephrase.utils import get_question_type, QType

include_sys_path.void()


class QTS(rephraser.Rephraser):
    options = question_dispatcher.get_options()

    @staticmethod
    def __translate(question):
        assert(isinstance(question, spacy.tokens.span.Span))

        qtype = get_question_type(question)
        if qtype == QType.UNKNOWN:
            # Seems more natural to deal with unknown question types here
            # since qtype.process() is recursive and we kind of don't want
            # to have unknown recursive question calls mixed with known ones.
            while len(question) >= 1 and question[-1].is_punct:
                question = question[:-1]
            return str(question) + " @placeholder ."
        return QTS.options[qtype](question)

    @staticmethod
    @with_caching
    def process(question):
        sents = texts.split_in_sentences(question)
        assert(len(sents) >= 1)
        question = QTS.__translate(sents[-1])
        sents = ' '.join([str(x) for x in sents[:-1]])
        if len(sents) >= 1:
            return sents + " " + question
        return question

    @staticmethod
    @with_caching
    def get_qtype_as_int(question):
        sents = texts.split_in_sentences(question)
        assert(len(sents) >= 1)
        question = sents[-1]
        qtype = get_question_type(question)
        idx = 0
        for x in QType:
            if x == qtype:
                return idx
            idx += 1
        assert(False)


def proc():
    with open("kaggle_unknown.txt", "r") as f:
        for line in f:
            question = line.strip()
            text = question
            sents = texts.split_in_sentences(question)
            assert(len(sents) == 1)
            question = sents[0]
            qtype = get_question_type(question)
            if qtype == QType.UNKNOWN:
                print(QTS.process(text))


if __name__ == "__main__":
    proc()
    # QTS.process("In degrees Fahrenheit, what is Plymouth's annual mean temperature?")
    '''
    sents = [
        "In 2007, which airlines made deals to include iPod connections on their planes?",
        "In 2014, what did the census estimate the population of New York City to be?",
        "In the early 1920s, what was the second most highly populated city in the world?",
        "In the first half of 2010, what percentage of shooting victims were African-American or Hispanic?",
        "In areas of strict enforcement, what happened to Christians?",
        "In the waning years of the Malla dynasty, what fortified cities existed in the Kathmandu Valley?",
        "In the 5th century what was the capital of the Western Roman Empire?"
    ]
    print(QTS.process("On what devices can video games be used?"))
    '''

# Split issues:
# For what film was Paltrow studying Beyonce ?
