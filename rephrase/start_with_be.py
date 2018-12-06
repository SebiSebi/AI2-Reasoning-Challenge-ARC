import spacy


def _find_ors(question):
    # Be aware that 'conj' can also mean 'and'.
    first = None
    last = None
    for token in question:
        if token.dep_.lower() == "conj":
            head = token.head
            is_and = False
            for child in head.children:
                if child.dep_.lower() == "cc" and child.lower_ == "and":
                    is_and = True
                    break
            if not is_and:
                if first is None:
                    first = token.head
                    last = token
                else:
                    last = token
    if first is None:
        assert(last is None)
        return None

    assert(last is not None)

    # Move last as far as possible.
    # E.g. Are British and American English regarded as distinct languages,
    # or dialects of a single language?
    last_children = last.children
    for child in last_children:
        if child.idx > last.idx and child.lower_ != "?":
            last = child

    # first should not be a VERB.
    while first != question[-1] and first.nbor().pos_ in ["VERB", "ADP"]:
        first = first.nbor()

    return first, last


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) < 2:
        return str(question) + " @placeholder ."

    ors = _find_ors(question)  # Used after parsing.

    nsubj = None
    for token in question:
        if token.dep_.lower() in ["nsubj", "nsubjpass"]:
            nsubj = token
            break
    if nsubj is not None:
        # Is the Apple SDK available to third-party game publishers?
        # subj =  "SDK"
        aux = sorted(list(nsubj.subtree) + [nsubj], key=lambda x: x.idx)
        nsubj = aux[-1]
        for i in range(1, len(aux)):
            if aux[i].pos_ == "VERB":
                nsubj = aux[i - 1]
                break

        out = []
        verb = question[0].lower_
        for token in question[1:]:
            out.append(token.text)
            if token == nsubj:
                out.append(verb)
        question = out
    else:
        # Find first verb.
        main_verb = None
        for token in question[1:]:
            if token.pos_ == "VERB":
                main_verb = token
                break

        if main_verb is not None:
            out = []
            verb = question[0].lower_
            for token in question[1:]:
                if token == main_verb:
                    out.append(verb)
                out.append(token.text)
            question = out
        else:
            main = None
            for child in question[0].children:
                if child.dep_.lower() == "expl":
                    main = child
                    break

            if main is not None:
                # Is there a single standard for HDTV color support?
                out = []
                verb = question[0].lower_
                for token in question[1:]:
                    out.append(token.text)
                    if token == main:
                        out.append(verb)
                question = out
            else:
                main = question[0]
                for child in question[0].children:
                    if child.dep_ == "attr" and child.idx > main.idx:
                        main = child
                out = []
                verb = question[0].lower_
                for token in question[1:]:
                    if token == main:
                        out.append(verb)
                    out.append(token.text)
                question = out

    assert(isinstance(question, list))

    if ors is None:
        question.append("-")
        question.append("@placeholder")
        question = question + ["(", "true", "or", "false", ")"]
    else:
        assert(len(ors) == 2)
        first = ors[0]
        last = ors[1]

        try:
            first = question.index(first.text)
            last = question.index(last.text, first)  # Starting at first.
            before = question[:first]
            middle = question[first:last + 1]
            after = question[last + 1:]
            question = before + ["@placeholder", "("] + middle + [")"] + after
        except ValueError:
            question.append("-")
            question.append("@placeholder")

    question.append(".")
    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()
    return ' '.join(question)
