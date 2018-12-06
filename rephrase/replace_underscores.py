import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    question = list(str(question))

    out = []
    n = len(question)
    i = 0
    while i < n:
        if question[i] == '_':
            j = i
            while j + 1 < n and question[j + 1] == '_':
                j += 1
            if j - i + 1 < 3:
                out.append(question[i])
            else:
                out = out + list("@placeholder")
                i = j
        else:
            out.append(question[i])
        i += 1

    return ''.join(out)
