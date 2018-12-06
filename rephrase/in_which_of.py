import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 4)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    out = []
    which = question[0]
    first = True
    for token in question[1:]:
        if not which.is_ancestor(token):
            if first:
                if token.pos_ != "VERB":
                    out.append(token.text)
                first = False
            else:
                out.append(token.text)

    return ' '.join(out) + " in @placeholder ."
