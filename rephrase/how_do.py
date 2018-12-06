import spacy

from rephrase.service_loader import SLoader


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
        'credit': 'as'  # Was credited as ...
    }

    question = question[1:]  # Remove "How".
    verb = question[0]
    if verb.lower_ in ["do", "does"]:
        question = [str(x) for x in question[1:]]
        question.append(PREP.get(verb.head.lemma_, "by"))
        question.append("@placeholder")
        question.append(".")

        return _to_capitalize(question)

    # assert(verb.lower_ == "did")
    if verb.head and verb.head != verb:
        main_verb = verb.head

        out = []
        for token in question[1:]:
            if token == main_verb:
                past_tense = SLoader.get_past_tense_list()
                out.append(past_tense.get(token.lower_, token.text))
            else:
                out.append(token.text)

        out.append(PREP.get(main_verb.lemma_, "by"))
        out.append("@placeholder")
        out.append(".")

        return _to_capitalize(out)

    # Mostly spaCy "wrong" dependency trees.
    # Search for the first verb.
    # No examples found.
    main_verb = None
    for token in question[1:]:
        if token.pos_ == "VERB":
            main_verb = token
            break

    if main_verb is not None:
        out = []
        for token in question[1:]:
            if token == main_verb:
                past_tense = SLoader.get_past_tense_list()
                out.append(past_tense.get(token.lower_, token.text))
            else:
                out.append(token.text)

        out.append(PREP.get(main_verb.lemma_, "by"))
        out.append("@placeholder")
        out.append(".")

        return _to_capitalize(out)

    # No verb is found. Do nothing (but remove "did").
    # How did Descartes' distinguish types of existence?
    # How did Top 40 radio what ifmusic change during this era?
    # How did the actual sales of the G4's compare to the sales expectations?
    question = [str(x) for x in question[1:]]
    question.append(PREP.get(verb.head.lemma_, "by"))
    question.append("@placeholder")
    question.append(".")

    return _to_capitalize(question)
