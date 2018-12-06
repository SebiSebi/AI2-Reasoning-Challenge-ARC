import spacy

import rephrase.which_of as which_of
import rephrase.in_which_of as in_which_of
import rephrase.which_noun as which_noun
import rephrase.which_be as which_be
import rephrase.in_which_noun as in_which_noun
import rephrase.which_verb as which_verb

from rephrase.service_loader import SLoader
from rephrase.utils import QType, get_question_type


# Calls another WHICH_ module (but not this one).
def _process_internal(question):
    assert(isinstance(question, spacy.tokens.span.Span))

    if len(question) < 2:
        return str(question) + "@placeholder"

    question = "Which " + str(question) + " ?"
    nlp = SLoader.get_full_spacy_nlp()
    question = list(nlp(question).sents)[0]
    qtype = get_question_type(question)

    if qtype == QType.WHICH_OF:
        return which_of.process(question)

    if qtype == QType.IN_WHICH_OF:
        # No examples in the entire SQuAD dataset.
        return in_which_of.process(question)

    if qtype == QType.WHICH_NOUN:
        return which_noun.process(question)

    if qtype == QType.WHICH_BE:
        return which_be.process(question)

    if qtype == QType.IN_WHICH_NOUN:
        # No examples in the entire SQuAD dataset.
        return in_which_noun.process(question)

    if qtype == QType.WHICH_VERB:
        return which_verb.process(question)

    question = question[1:]  # Remove "Which"
    question = ["@placeholder"] + [str(x) for x in question]
    question[-1] = '.'  # Replace "?" with "."
    return ' '.join(question)


# A "Which ...?" question that cannot be resolved by a specific which category.
# Which single from B'Day was only released in the U.K.?
# Which 1909 ballet used Chopin's music?
# Very similar to WHAT_GENERAL.
def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    which_token = question[0]
    question = question[1:]  # Remove "Which"
    if len(question) < 2:
        return str(question) + " @placeholder ."

    if which_token.dep_ == "det" and which_token.head.dep_ == "nsubj":
        # Most common case.
        # Which three Western European countries have a lower Social
        #           Progress ranking than Portugal?
        # Skip subject and make it a description to @placeholder.
        skipped = []
        subj = which_token.head
        while len(question) >= 1:
            token = question[0]
            if token == subj or subj.is_ancestor(token):
                skipped.append(token.text)
                question = question[1:]
            else:
                break
        question = _process_internal(question)
        skipped = '( ' + ' '.join(skipped) + ' )'
        placeholder = "@placeholder"
        return question.replace(placeholder, placeholder + " " + skipped)
    elif which_token.dep_ in ["det", "dobj"]:
        # E.g. Which Arab Caliphate defeated Iran first?
        # Do the same as above.
        skipped = []
        subj = which_token.head
        while len(question) >= 1:
            token = question[0]
            if token == subj or subj.is_ancestor(token):
                skipped.append(token.text)
                question = question[1:]
            else:
                break
        if len(question) == 0:
            return "@placeholder " + ' '.join(skipped) + " ."
        question = _process_internal(question)
        skipped = '( ' + ' '.join(skipped) + ' )'
        placeholder = "@placeholder"
        return question.replace(placeholder, placeholder + " " + skipped)
    else:
        # Search for the first verb, then do the same as above.
        # Which typically has thicker skin, dogs or wolves?
        skipped = []
        while len(question) >= 1:
            token = question[0]
            if token.pos_ == "VERB":
                break
            skipped.append(token.text)
            question = question[1:]
        if len(question) == 0:
            # No examples in the entire SQuAD dataset.
            return "@placeholder " + ' '.join(skipped) + " ."
        else:
            question = _process_internal(question)
            skipped = '( ' + ' '.join(skipped) + ' )'
            placeholder = "@placeholder"
            return question.replace(placeholder, placeholder + " " + skipped)

    assert(False)
    return None
