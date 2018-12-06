import rephrase.utils as utils
import spacy


def _process_internal(question):
    import rephrase.question_dispatcher as question_dispatcher

    assert(isinstance(question, spacy.tokens.span.Span))
    qtype = utils.get_question_type(question)
    if qtype != utils.QType.UNKNOWN and qtype != utils.QType.ALONG_WITH:
        return question_dispatcher.get_options()[qtype](question)

    # Either recursive question or unknown.
    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    question = [str(x) for x in question]
    question.append(".")
    return "@placeholder " + ' '.join(question)


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    if len(question) <= 3:
        return str(question) + " @placeholder ."

    wh_family = set([
        'what',
        'who',
        'where',
        'which',
        'how',
        'when',
        'why'
    ])

    # Skip over the Along with X, question?
    # Save Along With X.
    skipped = ["along", "with"]
    art = question[0]
    index = 2
    for token in question[2:]:
        if token.lower_ in wh_family:
            break
        if token == art or art.is_ancestor(token):
            skipped.append(token.text)
            index += 1
        else:
            break
    if len(skipped) >= 1 and skipped[-1] == ",":
        skipped = skipped[:-1]

    question = question[index:]

    if len(question) >= 1 and question[0].is_punct:
        # Along with X and Y, who ... ?
        question = question[1:]

    if len(question) == 0:
        # No examples in the entire SQuAD.
        question = [str(x) for x in skipped]
        question = ["@placeholder"] + question + ["."]
        return ' '.join(question)

    # Solve internally (another question type).
    question = _process_internal(question)
    skipped = '( ' + ' '.join(skipped) + ' )'
    placeholder = "@placeholder"
    return question.replace(placeholder, placeholder + " " + skipped)
