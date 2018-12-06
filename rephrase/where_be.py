import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 3:
        return "@placeholder"

    pos = question[-1].tag_
    if pos == "VBN" or pos == "VBD":
        question = [str(x) for x in question]
        verb = question[1]
        question = question[2:]  # Remove Where is/was/are/etc
        question = question[:-1] + [verb] + question[-1:]
        question.append("in")
        question.append("@placeholder")
        question.append(".")
    elif len(pos) >= 2 and pos[0:2] == "NN":
        question = [str(x) for x in question]
        verb = question[1]
        question = question[2:]  # Remove Where is/was/are/etc
        question.append(verb)
        question.append("in")
        question.append("@placeholder")
        question.append(".")
    elif pos[0:2] == "CD":
        question = [str(x) for x in question]
        verb = question[1]
        question = question[2:]  # Remove Where is/was/are/etc
        question.append(verb)
        question.append("in")
        question.append("@placeholder")
        question.append(".")
    elif pos == "IN":
        verb = question[1].text
        question = question[2:]
        is_verb = False
        if len(question) >= 2 and question[-2].pos_ == "VERB":
            is_verb = True

        question = [str(x) for x in question]
        if is_verb:
            question = question[:-2] + [verb] + question[-2:]
        else:
            question = question[:-1] + [verb] + question[-1:]

        question.append("@placeholder")
        question.append(".")
    elif pos[0:2] == "JJ":
        # There are two cases. Either a verb is in the sentence
        # after "BE" or not. In the latter, we must skip all the
        # tokens that are descendants of the last word in the
        # depenency tree.
        verb = question[1].text
        question = question[2:]

        index = None
        i = 0
        for token in question:
            if token.pos_ == "VERB":
                index = i
                break
            i += 1

        if index is not None:
            # Insert BE before the main verb.
            question = [str(x) for x in question]
            question = question[:index] + [verb] + question[index:]
        else:
            # Skip last word descendants.
            index = len(question) - 1
            last = question[-1]
            i = 0
            for token in question:
                if last.is_ancestor(token) and token.pos_ in ["ADV", "DET"]:
                    index = i
                    break
                i += 1
            question = [str(x) for x in question]
            question = question[:index] + [verb] + question[index:]

        question.append("in")
        question.append("@placeholder")
        question.append(".")
    else:
        question = [str(x) for x in question]
        question = question[2:]
        question.append("in")
        question.append("@placeholder")
        question.append(".")

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()

    return ' '.join(question)
