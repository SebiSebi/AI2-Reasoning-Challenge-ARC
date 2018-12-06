import spacy

from rephrase.service_loader import SLoader


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return "@placeholder"

    verb = question[1]  # Do/does/did ...
    question = question[2:]  # Remove "When do/does/did" tokens.
    to_replace = {}
    if verb.head and verb.head != verb and verb.head.pos_ == "VERB":
        if verb.lower_ == "did":
            verb_text = verb.head.lower_
            past_tense = SLoader.get_past_tense_list()
            verb_text = past_tense.get(verb_text, verb_text)
            to_replace[verb.head] = verb_text
        else:
            # Present tense. Do nothing.
            pass

    out = []
    for token in question:
        if token in to_replace:
            out.append(to_replace[token])
        else:
            out.append(token.text)
    question = out
    question.append("in")
    question.append("@placeholder")
    question.append(".")

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()
    question = ' '.join(question)

    return question
