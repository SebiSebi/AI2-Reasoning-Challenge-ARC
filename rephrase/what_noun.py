import spacy

from rephrase.service_loader import SLoader


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 4)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return "@placeholder"

    noun = question[1]
    skipped = [noun.text]
    index = 1
    for token in question[2:]:
        if noun.is_ancestor(token):
            skipped.append(token.text)
            index += 1
        else:
            break
    question = question[index + 1:]

    if len(question) == 0:
        # Usually a format problem that confuses
        # spaCy (e.g. unmatched closing ")
        # What reviewer called Twilight Princess " One of the greatest
        #   games ever created?
        question = ["@placeholder"] + skipped
        question.append(".")
        return ' '.join(question)
    else:
        # Try to remove aux verbs.
        # E.g. What type of shoes did Michael Jordan buy?
        if len(question) >= 1 and question[0].pos_ == "VERB":
            to_remove = set()
            to_past = set()
            insert_before = {}

            verb = question[0]
            if verb.lower_ == "does" or verb.lower_ == "do":
                # What does Portugal have to offer tourists?
                # Do not bother with 1st/3rd person.
                # Leave it as it is.
                to_remove.add(verb)
            elif verb.lower_ == "did":
                # Put main verb to past tense.
                to_remove.add(verb)
                if verb != verb.head:
                    to_past.add(verb.head)
            elif verb.lemma_ == "be":
                if verb.head and verb.dep_ in ["aux", "auxpass"] and (
                        verb.head != verb and verb.head.pos_ == "VERB"):
                    # What company was Kanye presenting for when he spoke "
                    # negatively about President Bush?
                    insert_before[verb.head] = verb
                    to_remove.add(verb)
                else:
                    # What function is an M.Div?
                    # What type was Beyonce's early music?
                    # Do nothing.
                    pass

            out = []
            for token in question:
                if token in insert_before:
                    out.append(insert_before[token].text)
                if token in to_remove:
                    continue
                if token in to_past:
                    past_tenses = SLoader.get_past_tense_list()
                    out.append(past_tenses.get(token.text, token.text))
                else:
                    out.append(token.text)
            question = out
        else:
            question = [str(x) for x in question]

    question = ["@placeholder", "("] + skipped + [")"] + question
    question.append(".")

    if not question[0].isupper():
        question[0] = question[0].capitalize()
    question = ' '.join(question)

    return question
