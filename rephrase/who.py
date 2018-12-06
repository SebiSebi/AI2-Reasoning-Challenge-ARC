import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    question = question[1:]
    if len(question) <= 1:
        return "@placeholder"

    if question[0].lemma_ == "do":
        if question[-1].pos_ == "ADP":
            # Who did Sonam Gyatso send gifts to?
            question = [str(x) for x in question]
            question = question[1:]
            question.append("@placeholder")
            question.append(".")
            if len(question) >= 1 and not question[0].isupper():
                question[0] = question[0].capitalize()
            return ' '.join(question)
        elif question[0].head and question[0].head.pos_ == "VERB":
            verb = question[0].head
            children = verb.children
            child = None
            min_idx = None
            for x in children:
                if x.dep_.lower() in ["prep", "prt"]:
                    if child is None or x.idx < min_idx:
                        child = x
                        min_idx = x.idx
            if child:
                # for, with, to, under, upon, "from" => after prep or prt.
                out = []
                for token in question[1:]:
                    if token == child:
                        if token.lower_ in ["for", "with", "to",
                                            "under", "upon", "from"]:
                            out.append(token.text)
                            out.append("@placeholder")
                        else:
                            out.append("@placeholder")
                            out.append(token.text)
                    else:
                        out.append(token.text)
                question = out + ["."]
            elif verb != question[0]:  # No preposition. Insert after verb.
                out = []
                for token in question[1:]:
                    if token == verb:
                        out.append(token.text)
                        out.append("@placeholder")
                    else:
                        out.append(token.text)
                question = out + ["."]
            else:  # No main verb. Insert at beginning.
                question = [str(x) for x in question]
                question = ["@placeholder"] + question + ["."]

            assert(isinstance(question, list))
            if len(question) >= 1 and not question[0].isupper():
                question[0] = question[0].capitalize()

            return ' '.join(question)
        elif question[0].head and question[0].head != question[0]:
            # Some verb do have head but their are falsely
            # tagged as NOUNS or anything != VERB.
            # E.g. Who did Bob Ewell attack during the story?
            #      "attack" is clearly a VERB but Spacy
            #      says it is a NOUN.
            # E.g. Who did Stratford Canning convince to turn
            #      down the treaty proposal?
            #      "convince" should be a VERB
            verb = question[0].head
            out = []
            for token in question[1:]:
                if token == verb:
                    out.append(token.text)
                    out.append("@placeholder")
                else:
                    out.append(token.text)
            question = out + ["."]

            if len(question) >= 1 and not question[0].isupper():
                question[0] = question[0].capitalize()

            return ' '.join(question)
        else:
            question = [str(x) for x in question]
            question = question[1:]
            if question[0].strip() == "else":  # Who else ... ?
                question[0] = "also"
            question = ["@placeholder"] + question + ["."]
            question = ' '.join(question)
    else:
        question = [str(x) for x in question]
        if question[0].strip() == "else":  # Who else ... ?
            question[0] = "also"
        question = ["@placeholder"] + question + ["."]
        question = ' '.join(question)

    return question
