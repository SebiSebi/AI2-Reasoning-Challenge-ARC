import spacy

from copy import deepcopy
from rephrase.service_loader import SLoader


# It is guaranteed that the first token is a verb.
# @return array of strings.
def _process_with_verb(question):
    to_remove = set()
    to_past = set()
    insert_before = {}

    verb = question[0]
    if verb.lower_ == "does" or verb.lower_ == "do":
        to_remove.add(verb)
    elif verb.lower_ == "did":
        # Put main verb to past tense.
        to_remove.add(verb)
        to_past.add(verb.head)
    elif verb.lemma_ == "be":
        insert_before[verb.head] = verb
        to_remove.add(verb)

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

    return deepcopy(out)


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    question = question[1:]  # Remove "Why"
    if len(question) < 2:
        return str(question) + " because @placeholder ."

    verb = question[0]
    if verb.pos_ == "VERB":
        if verb.head and verb.head != verb:
            # verb.dep_ in ["auxpass", "aux"] in 99.9% of the cases.
            question = _process_with_verb(question)
        else:
            if verb.lemma_ == "do":
                # Should have been tagged differently by spaCy (seems a bug).
                # Why did the train catch fire?
                question = [str(x) for x in question[1:]]
            else:
                # Search for a VBD or a VBN.
                main_verb = None
                for token in question[1:]:
                    if token.tag_ in ["VBD", "VBN"]:
                        main_verb = token
                        break

                if main_verb is not None:
                    out = []
                    for token in question[1:]:
                        if token == main_verb:
                            out.append(verb.text)
                        out.append(token.text)
                    question = out
                else:
                    # Insert verb after the subject.
                    # Why were television ratings down across the board "
                    #   during American Idols seventh season?
                    subj = None
                    for token in question[1:]:
                        if token.dep_.lower() == "nsubj":
                            subj = token
                            break

                    if subj is not None:
                        out = []
                        for token in question[1:]:
                            out.append(token.text)
                            if token == subj:
                                out.append(verb.text)
                        question = out
                    else:
                        # Insert verb after first word.
                        # Why was there concerns in 2010?
                        # Why is there difficulty in defining process theology?
                        insert_after = question[1]
                        out = []
                        for token in question[1:]:
                            out.append(token.text)
                            if token == insert_after:
                                out.append(verb.text)
                        question = out
    else:
        # Wrong question format:
        # Why type of conflict is sociocultural anthropology interested in?
        question = [str(x) for x in question]

    question.append("because")
    question.append("@placeholder")
    question.append(".")

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()

    return ' '.join(question)
