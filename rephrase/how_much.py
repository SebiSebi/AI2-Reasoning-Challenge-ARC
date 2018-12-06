import spacy

from rephrase.service_loader import SLoader


def _has_aux_pass(token):
    # How many editions have been launched?
    # have is aux
    # been is auxpass
    for child in token.children:
        if child.dep_.lower() == "auxpass":
            return True
    return False


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return "@placeholder"

    insert_before = {}
    skip = set()
    to_past = set()
    for token in question:
        if token.pos_ == "VERB" and token.dep_.lower() == "aux":
            if token.lemma_ == "do":
                if token.lower_ == "did":
                    to_past.add(token.head)
                skip.add(token)
            else:
                if token.lemma_ == "have" and token.head:
                    if not _has_aux_pass(token.head):
                        insert_before[token.head] = token
                        skip.add(token)
                elif token.lemma_ == "be":
                    pass  # Seems ok to let it as it is.

    question = question[2:]  # Skip "How much"
    out = []
    for token in question:
        if token in insert_before:
            out.append(insert_before[token].text)
        if token in skip:
            continue
        if token in to_past:
            past_tense = SLoader.get_past_tense_list()
            out.append(past_tense.get(token.lower_, token.text))
        else:
            out.append(token.text)

    question = ["@placeholder"] + out + ["."]
    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()

    return ' '.join(question)
