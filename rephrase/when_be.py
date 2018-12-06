import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return "@placeholder"

    verb = question[1]
    if verb.head and verb.head != verb and verb.head.pos_ == "VERB":
        out = []
        for token in question[2:]:
            if token == verb.head:
                out.append(verb.text)
            out.append(token.text)
        question = out
    elif verb.head and verb.head != verb:
        insert_before = {}
        if verb.dep_.lower() == "auxpass":
            # When was the new Gateway Community College open?
            insert_before[verb.head] = verb.text
        else:
            # When was Arsenal's match the first to be televised live?
            # Insert verb after descendants.
            min_idx = None
            child = None
            found = False
            for token in question[2:]:
                if verb.is_ancestor(token):
                    found = True
                    continue
                if child is None or token.idx < min_idx:
                    min_idx = token.idx
                    child = token
            if child and found:
                insert_before[child] = verb.text
            elif verb.head.nbor():
                # Insert after head.
                insert_before[verb.head.nbor()] = verb.text
        out = []
        for token in question[2:]:
            if token in insert_before:
                out.append(insert_before[token])
            out.append(token.text)
        question = out
    else:
        # First look for a VBN.
        # Last apparition is preferred.
        # When was the fictionalized "Chopin" produced.
        child = None
        for token in question[2:]:
            if token.tag_[:2] == "VB":
                child = token
        if child:
            out = []
            for token in question[2:]:
                if token == child:
                    out.append(verb.text)
                out.append(token.text)
            question = out
        else:
            # Find the subject between between children.
            child = None
            for x in verb.children:
                if x.dep_ == "nsubj":
                    child = x
                    break
            if child is None:
                out = [str(x) for x in question[2:]]
                out.append(verb.text)
                question = out
            else:
                max_idx = child.idx
                last = child
                for token in question[2:]:
                    if not child.is_ancestor(token):
                        continue
                    if token.idx > max_idx:
                        max_idx = token.idx
                        last = token
                out = []
                for token in question[2:]:
                    out.append(token.text)
                    if token == last:
                        out.append(verb.text)
                question = out

    question.append("on")
    question.append("@placeholder")
    question.append(".")

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()
    question = ' '.join(question)

    return question
