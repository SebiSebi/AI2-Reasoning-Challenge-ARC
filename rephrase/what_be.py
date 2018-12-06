import spacy


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    question = [str(x) for x in question]
    question = question[1:]  # Remove "What" token.
    question.append(question[0])  # Add "be" to the end.
    question = question[1:]  # Remove "Be" from beginning.
    if not question[0].isupper():
        question[0] = question[0].capitalize()
    question = ' '.join(question)

    return question + " @placeholder ."
