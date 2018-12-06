import spacy

from rephrase.service_loader import SLoader


# The subject of the sentence is a child of the token.
# On what day was the funeral of Donda West?
# "the funeral" = subj and child of "was"
def _has_subj_child(token):
    for child in token.children:
        if child.dep_.lower() in ["nsubj", "nsubjpass"]:
            return True
    return False


def _is_past_participle_verb(verb):
    main_form = verb.lemma_
    if main_form not in SLoader.get_verb_list():
        return False
    if main_form not in SLoader.get_past_participle_list():
        return False

    past_tense = SLoader.get_past_participle_list()[main_form]
    if past_tense == verb.lower_:
        return True
    return False


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 4)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    if len(question) <= 3:
        return "@placeholder"

    on = question[0]
    head = on.head
    question = question[2:]

    skipped = None
    if head != on:
        # On what magazine was she the cover model?
        skipped = []
        while len(question) >= 1:
            if question[0].pos_ == "VERB":
                break
            if head.is_ancestor(question[0]) or head == question[0]:
                skipped.append(question[0].text)
                question = question[1:]
            else:
                break
    else:
        # Stop at the first verb.
        # On what devices can video games be used?
        # On what was the Philip Glass opera based?
        # On what occasions are š and ž replaced with sh and zh?
        # On what film was videoconferencing widely used?
        # On what was the mitrailleuse mounted?
        # On what do plants depend in their environment?
        index = 0
        for token in question:
            if token.pos_ == "VERB":
                break
            index += 1

        if index < len(question):
            skipped = [str(x) for x in question[0:index]]
            question = question[index:]
        else:
            # No verb found.
            # Does not happen in the entire SQuAD.
            skipped = []

    assert(isinstance(skipped, list))

    if len(question) == 0:
        # Does not happen in the entire SQuAD.
        question = [str(x) for x in question]
        question = ["On", "@placeholder"] + question
        question.append(".")
        question = ' '.join(question)
        return question

    to_remove = set()
    insert_before = {}
    to_past = set()
    insert_at_end = []  # In this order.

    verb = question[0]
    if verb.pos_ == "VERB":
        # 99.99% of the cases.
        if verb.lower_ in ["do", "does"]:
            # Just remove.
            to_remove.add(verb)
        elif verb.lower_ == "did":
            to_remove.add(verb)
            if verb.head != verb and verb.head.pos_ == "VERB":
                # Normal case.
                to_past.add(verb.head)
            else:
                # 99% a spaCy tagging error.
                # Search for the first verb.
                main_verb = None
                for token in question[1:]:
                    if token.pos_ == "VERB":
                        # Very unlikely since it seems like
                        # a spaCy tagging problem.
                        main_verb = token
                        break
                    if token.lemma_ in SLoader.get_verb_list() and (
                            token in verb.children or token == verb.head):
                        # Some verbs are tagged as nouns.
                        # On what did a rescue helicopter crash with no "
                        #       survivors?
                        main_verb = token
                        break

                if main_verb is not None:
                    to_past.add(main_verb)
                else:
                    # Do nothing.
                    pass
        elif verb.lemma_ == "be":
            # On what date were the Belavezha Accords signed?
            # On what year was the USSR dissolved?
            to_remove.add(verb)
            if verb.head != verb and verb.head.pos_ == "VERB":
                insert_before[verb.head] = verb
            else:
                # Search for the first verb.
                main_verb = None
                for token in question[1:]:
                    if _is_past_participle_verb(token):
                        main_verb = token
                        break
                    if token.pos_ == "VERB":
                        # Another verb entry. <VERB1> <VERB2>
                        break

                if main_verb is not None:
                    # On what day and month was Spectre released to the
                    #   Chinese market released?
                    # On what date is Twilight Princess HD scheduled
                    #   for Australian release?
                    insert_before[main_verb] = verb
                else:
                    # No main verb linked to "be" was found.
                    # On what magazine was she the cover model?
                    # On what day was the funeral of Donda West?
                    # On what season was Kristy Lee Cook a contestant on
                    #       American Idol?
                    insert_at_end.append(verb)
        else:
            # On what part of newer iPods can you find the buttons?
            # On what devices can video games be used?
            # On what day would most of the games televised on the ESPN
            #       networks be played?
            # On what day would AFL games be shown on NFL Network?
            # Search for the first verb.
            to_remove.add(verb)
            main_verb = None
            for token in question[1:]:
                if token.pos_ == "VERB":
                    main_verb = token
                    break

            if main_verb is not None:
                insert_before[main_verb] = verb
            else:
                insert_at_end.append(verb)

    out = []
    for token in question:
        if token in insert_before:
            out.append(insert_before[token].text)
        if token in to_remove:
            continue
        if token in to_past:
            past_tense = SLoader.get_past_tense_list()
            out.append(past_tense.get(token.lower_, token.text))
        else:
            out.append(token.text)
    for token in insert_at_end:
        out.append(token.text)

    question = out + ["on", "@placeholder"]
    if len(skipped) >= 1:
        question.append("(")
        question.append(' '.join(skipped))
        question.append(")")
    question.append(".")

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()

    return ' '.join(question)
