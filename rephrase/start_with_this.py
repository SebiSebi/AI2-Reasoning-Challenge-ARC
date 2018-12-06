import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return str(question) + " @placeholder ."

    wh_family = set([
        'what',
        'who',
        'why',
        'where',
        'which',
        'how',
        'when',
        'whom'
    ])

    count = 0
    for token in question:
        if token.lower_ in wh_family:
            count += 1

    if count == 0:
        # Continuation.
        # E.g. This is an example of
        question = [str(x) for x in question]
        question.append("@placeholder")
        question.append(".")
        return ' '.join(question)

    # At least one wh- word.
    # Replace the first wh- word in the question.
    # Not 100% accuracy but 95%.
    # E.g. This decision reflected a revision of what?
    wh_word = None
    for token in question:
        if token.lower_ in wh_family:
            wh_word = token
            break
    assert(wh_word is not None)

    out = []
    skip = False
    for token in question:
        if token == wh_word:
            out.append("@placeholder")
            if token.lower_ == "how":
                if token != question[-1] and token.nbor().lower_ == "many":
                    skip = True
        else:
            if not skip:
                out.append(token.text)
            skip = False

    question = out + ["."]
    return ' '.join(question)
