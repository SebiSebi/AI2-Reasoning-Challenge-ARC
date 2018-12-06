import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    out = []
    which = question[0]
    for token in question[1:]:
        if not which.is_ancestor(token):
            out.append(token.text)

    out.append(".")

    return "@placeholder " + ' '.join(out)
