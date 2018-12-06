import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 3:
        return "@placeholder"

    what = question[1]
    head = question[1].head  # What referes to ... ?
    question = question[2:]  # Remove "In what".
    if len(question) <= 2:
        return "@placeholder"

    if what.dep_.lower() != "det":
        # In what hemisphere did west Antarctica share during the Cambrian?
        # Insert "In @placeholder right at beginning.
        question = [str(x) for x in question]
        question = ["In", "@placeholder"] + question
        question.append(".")
    else:
        skipped = []
        to_remove = set()
        for token in question:
            if token == head or head.is_ancestor(token):
                skipped.append(token.text)
                to_remove.add(token)
            else:
                break
        while len(question) >= 1 and question[0] in to_remove:
            question = question[1:]

        out = None
        if len(question) >= 1 and question[0].pos_ == "VERB":
            to_remove = set()
            insert_before = {}
            if question[0].lemma_ == "do":
                to_remove.add(question[0])
            else:
                to_remove.add(question[0])
                if question[0].head and question[0].head != question[0]:
                    insert_before[question[0].head] = question[0]
                else:
                    # Look for the first verb.
                    for token in question[1:]:
                        if token.pos_ == "VERB":
                            insert_before[token] = question[0]
                            break
            out = []
            for token in question:
                if token in to_remove:
                    continue
                if token in insert_before:
                    out.append(insert_before[token].text)
                out.append(token.text)
        else:
            # In what country, besides Mexico, did the film experience
            # administrative issues with local authorities?
            while len(question) >= 1 and question[0].is_punct:
                question = question[1:]

            out = [str(x) for x in question]

        question = out + ["in", "@placeholder"]
        question = question + ["("] + skipped + [")", "."]

    if not question[0].isupper():
        question[0] = question[0].capitalize()
    question = ' '.join(question)

    return question
