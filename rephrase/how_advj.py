import spacy

from rephrase.service_loader import SLoader


def _is_aux_verb(aux, main_verb):
    # How many editions have been launched?
    # have is aux
    # The same with could be repaired ..., etc.
    if aux.pos_ != "VERB":
        return False
    if aux.head != main_verb:
        return False
    return True


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return str(question) + " @placeholder ."

    # Skip HOW X VERB? (X)
    # How far from each other were the motors in Gramme's demonstrations?
    # => far from each other
    question = question[1:]  # Remove "How"
    advj = question[0]
    measure = []
    while len(question) >= 1:
        token = question[0]
        if token == advj or advj.is_ancestor(token):
            measure.append(token.text)
            question = question[1:]
        else:
            break
    assert(len(measure) >= 1)
    measure = ' '.join(measure)

    if len(question) <= 1:
        # How lond did the creation of Red Book CD - DA standard take?
        # long => lond => spaCy error.
        out = "@placeholder " + measure
        if len(question) > 0:
            out = out + " " + str(question)
        return out + " ."

    assert(isinstance(measure, str))
    verb = question[0]
    if verb.pos_ != "VERB":
        # Caused by a spaCy wrong dependency tree.
        # How [far] away was the plant located from the epicenter?
        # Extend @measure until the first verb.
        while len(question) >= 1:
            token = question[0]
            if token.pos_ != "VERB":
                measure += (" " + token.text)
                question = question[1:]
            else:
                break

        if len(question) <= 1:
            # How far back to San Diego's roots in the arts and theater
            #       sector go?
            out = "@placeholder " + measure
            if len(question) > 0:
                out = out + " " + str(question)
            return out + " ."

    assert(isinstance(measure, str))
    assert(len(question) > 1)
    assert(question[0].pos_ == "VERB")

    verb = question[0]
    if verb.lemma_ == "do":
        if verb.head == verb:
            # How often do temperatures on the coastal plain of NC drop below
            #       freezing at night?
            # Insert @placeholder at the end.
            question = [str(x) for x in question[1:]]
            if len(question) >= 1 and not question[0].isupper():
                question[0] = question[0].capitalize()
            question.append("@placeholder")
            question.append("(")
            question.append(measure)
            question.append(")")
            question.append(".")
            return ' '.join(question)
        else:
            # Insert @placeholder at the end.
            # How far did the Arctic tern chick travel?
            # Correct main verb tense.
            main_verb = verb.head
            out = []
            for token in question[1:]:
                if token == main_verb and verb.lower_ == "did":
                    # To past.
                    past_tense = SLoader.get_past_tense_list()
                    out.append(past_tense.get(token.lemma_, token.text))
                else:
                    out.append(token.text)
            question = out

            if len(question) >= 1 and not question[0].isupper():
                question[0] = question[0].capitalize()
            question.append("@placeholder")
            question.append("(")
            question.append(measure)
            question.append(")")
            question.append(".")
            return ' '.join(question)

    if verb.head != verb:
        # How high had cotton revenues risen by the time of the American
        #           Civil War?
        main_verb = verb.head
        index = -1
        for i in range(0, len(question)):
            if question[i] == main_verb:
                index = i
                break
        assert(index > 0 and index < len(question))
        insert_before = main_verb
        if index >= 1 and _is_aux_verb(question[index - 1], main_verb):
            insert_before = question[index - 1]

        out = []
        for token in question[1:]:
            if token == insert_before:
                out.append(verb.text)
            out.append(token.text)
            if token == main_verb:
                out.append("@placeholder")
                out.append("(")
                out.append(measure)
                out.append(")")
        out.append(".")
        question = out

        if len(question) >= 1 and not question[0].isupper():
            question[0] = question[0].capitalize()
        return ' '.join(question)

    # Look for the subject (as a child of the verb).
    # How old are most of the native language speakers in northern Catalonia?
    subj = None
    for child in verb.children:
        if child.dep_.lower() in ["nsubj", "nsubjpass"]:
            subj = child
            break

    if subj is None:
        # How large in square kilometers is Greater Hyderabad?
        # How simple is the process of transformation?
        # Insert verb and @placeholder at the end.
        question = [str(x) for x in question[1:]]
        question.append(verb.text)
        question.append("@placeholder")
        question.append("(")
        question.append(measure)
        question.append(")")
        question.append(".")

        if len(question) >= 1 and not question[0].isupper():
            question[0] = question[0].capitalize()
        return ' '.join(question)

    insert_after = subj
    for child in subj.subtree:
        if child.idx > insert_after.idx:
            insert_after = child

    out = []
    for token in question[1:]:
        out.append(token.text)
        if token == insert_after:
            out.append(verb.text)
            out.append("@placeholder")
            out.append("(")
            out.append(measure)
            out.append(")")
    out.append(".")
    question = out

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()
    return ' '.join(question)
