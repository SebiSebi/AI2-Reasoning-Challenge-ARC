import spacy

import rephrase.what_be as what_be
import rephrase.what_do as what_do
import rephrase.in_what as in_what
import rephrase.what_noun as what_noun
import rephrase.what_verb as what_verb

from rephrase.service_loader import SLoader
from rephrase.utils import QType, get_question_type


# Calls another WHAT_ module (but not this one).
def _process_internal(question):
    assert(isinstance(question, spacy.tokens.span.Span))

    if len(question) < 2:
        return str(question) + "@placeholder"

    question = "What " + str(question) + " ?"
    nlp = SLoader.get_full_spacy_nlp()
    question = list(nlp(question).sents)[0]
    qtype = get_question_type(question)

    if qtype == QType.WHAT_BE:
        return what_be.process(question)

    if qtype == QType.WHAT_DO:
        return what_do.process(question)

    if qtype == QType.IN_WHAT:
        return in_what.process(question)

    if qtype == QType.WHAT_NOUN:
        return what_noun.process(question)

    if qtype == QType.WHAT_VERB:
        return what_verb.process(question)

    question = question[1:]  # Remove "What"
    question = ["@placeholder"] + [str(x) for x in question]
    question[-1] = '.'  # Replace "?" with "."
    return ' '.join(question)


# A "What ... ?" question that cannot be resolved by a specific what category.
# What in tobacco can hurt dogs?
# What New York radio personalty was hired as a judge for American Idol in
#               season two but declined?
def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    what_token = question[0]
    question = question[1:]  # Remove "What"
    if len(question) < 2:
        return str(question) + " @placeholder ."

    if what_token.dep_ == "det" and what_token.head.dep_ == "nsubj":
        # Most common case.
        # E.g. What two reptiles kill dogs and consume them?
        # Skip subject and make it a description to @placeholder.
        skipped = []
        subj = what_token.head
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
    elif what_token.dep_ in ["det", "dobj"]:
        # Seems that it does not matter if head is subject or not.
        # E.g. What musical concept did Chopin exploit?
        # E.g. What French Magazine cover did the media criticize? (dobj)
        # Do the same as above.
        skipped = []
        subj = what_token.head
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
    else:
        # Search for the first verb, then do the same as above.
        # E.g. What about Beyonce has influenced many entertainers?
        skipped = []
        while len(question) >= 1:
            token = question[0]
            if token.pos_ == "VERB":
                break
            skipped.append(token.text)
            question = question[1:]
        if len(question) == 0:
            # What new genre di John Field invent?
            return "@placeholder " + ' '.join(skipped) + " ."
        else:
            question = _process_internal(question)
            skipped = '( ' + ' '.join(skipped) + ' )'
            placeholder = "@placeholder"
            return question.replace(placeholder, placeholder + " " + skipped)

    assert(False)
    return None
