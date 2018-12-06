import spacy


# @return string (joined by ' ')
def _to_capitalize(question):
    assert(isinstance(question, list))

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()

    return ' '.join(question)


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return str(question) + " @placeholder ."

    PREP = {
        'describe': 'as',
        'identify': 'as',
        'view': 'as',
        'define': 'as',
        'rate': 'as',
        'compare': 'as',
        'credit': 'as',  # Was credited as ...
        'see': 'as',
        'classify': 'as',
    }

    question = question[1:]  # Remove "How".
    verb = question[0]
    if verb.head and verb.head != verb:
        main_verb = verb.head

        out = []
        for token in question[1:]:
            if token == main_verb:
                out.append(verb.text)  # is/was/were/etc
            out.append(token.text)

        out.append(PREP.get(main_verb.lemma_, "by"))
        out.append("@placeholder")
        out.append(".")

        return _to_capitalize(out)

    # Mostly spaCy "wrong" dependency trees.
    # Search for the first verb.
    # How is thermal mass used to keep buildings cool?
    main_verb = None
    for token in question[1:]:
        if token.pos_ == "VERB":
            main_verb = token
            break

    if main_verb is not None:
        out = []
        for token in question[1:]:
            if token == main_verb:
                out.append(verb.text)  # is/was/were/etc
            out.append(token.text)

        out.append(PREP.get(main_verb.lemma_, "by"))
        out.append("@placeholder")
        out.append(".")

        return _to_capitalize(out)

    # No verb was found. Search for the subject and for the first adjective "
    # after the subject. If no ADJ then insert verb at the end.
    #
    # How is the retail market of Mexico City?
    # How were these stores different than most during that time?
    subj = None
    for token in question[1:]:
        if token.dep_.lower() in ["nsubj", "nsubjpass"]:
            subj = token
            break
    
    if subj is not None and subj != question[-1]:
        subj = subj.nbor()  # Next token.
        while subj != question[-1]:
            if subj.pos_ == "ADJ":
                break
            subj = subj.nbor()

        if subj.pos_ == "ADJ":
            out = []
            for token in question[1:]:
                if token == subj:
                    out.append(verb.text)  # is/was/were/etc
                out.append(token.text)
            out.append("by")
            out.append("@placeholder")
            out.append(".")

            return _to_capitalize(out)

    # Insert aux verb at the end.
    # How is the retail market of Mexico City?
    question = [str(x) for x in question[1:]]
    question.append(verb.text)
    question.append("@placeholder")
    question.append(".")

    return _to_capitalize(question)
