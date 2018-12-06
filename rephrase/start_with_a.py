import spacy


# The same as START WITH NOUN but with other examples.
def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) < 2:
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
        # A New Hope' said to be similar to?
        question = [str(x) for x in question]
        question.append("@placeholder")
        question.append(".")
        return ' '.join(question)
    elif count == 1:
        out = []
        skip = False
        for token in question:
            if token.lower_ in wh_family:
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

    # More than 1 wh- word.
    # Replace the last wh- word in the question.
    # A detached knot will probably drop out of the wood when someone saws
    #           it into what?
    # A wildlife management unit is a place where what may be restricted to?
    wh_word = None
    for token in question:
        if token.lower_ in wh_family:
            wh_word = token
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
