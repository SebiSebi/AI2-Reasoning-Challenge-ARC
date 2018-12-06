import spacy


# TODO(sebisebi): Licenta/issues/7
def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return "@placeholder"

    prop_end = False
    if question[-1].pos_ == "ADP":
        # Where did Destiny 's Child get their name from?
        prop_end = True

    question = [str(x) for x in question]
    question = question[2:]  # Remove Where do/does/did/etc.
    if not prop_end:
        question.append("in")
    question.append("@placeholder")
    question.append(".")

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()

    return ' '.join(question)
