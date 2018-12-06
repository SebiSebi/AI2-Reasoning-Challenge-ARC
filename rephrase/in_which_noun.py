import spacy

from copy import deepcopy
from rephrase.service_loader import SLoader


# It is not guaranteed that the first token is a verb, although
# in 90% of the cases this is true.
# @return array of strings.
def _process_with_verb(question):
    # Try to remove aux verbs.
    # E.g. In which state did Jordan played the most of his games?
    if len(question) >= 1 and question[0].pos_ == "VERB":
        to_remove = set()
        to_past = set()
        insert_before = {}
        insert_at_end = []  # in this order.

        verb = question[0]
        if verb.lower_ == "does" or verb.lower_ == "do":
            # In which location do students of the School of Architecture
            #           of Notre Dame spend their 3rd year?
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
                # In which season was online voting introduced?
                insert_before[verb.head] = verb
                to_remove.add(verb)
            else:
                # In which direction is Puerto Rico from the island of
                #       Saint-Barthélemy?
                to_remove.add(verb)
                insert_at_end.append(verb)

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
        for token in insert_at_end:
            out.append(token.text)

        return deepcopy(out)

    return [str(x) for x in question]


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 4)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 2:
        return "@placeholder"

    question = question[1:]  # Remove "In"

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
        # Usually due to a syntactic error (e.g. unclosed quote).
        question = skipped + ["@placeholder", "."]
        return ' '.join(question)  # do not remove!

    # Try to remove aux verbs.
    # E.g. In which state did Jordan played the most of his games?
    if question[0].pos_ == "VERB":
        question = _process_with_verb(question)
    else:
        # Usually spaCy "incorrect" dependency tree.
        # In which ['music'] video did Beyoncé star as Jay Z's girlfriend,
        #   creating speculation about their relationship?
        # Should have been:
        # In which ['music', 'video'] did Beyoncé star as Jay Z's girlfriend,
        # creating speculation about their relationship?

        # Search for the first verb.
        index = 0
        for token in question:
            if token.pos_ == "VERB":
                break
            skipped.append(token.text)
            index += 1
        question = question[index:]
        question = _process_with_verb(question)

    # Remove "," from skipped words.
    # In which book, was the term \"computer\" first used?
    if len(skipped) >= 1 and skipped[-1].strip() == ',':
        skipped = skipped[:-1]

    question = question + ["in", "@placeholder", "("] + skipped + [")"]
    question.append(".")

    if not question[0].isupper():
        question[0] = question[0].capitalize()

    return ' '.join(question)
