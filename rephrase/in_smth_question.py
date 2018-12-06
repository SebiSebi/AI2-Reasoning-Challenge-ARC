import rephrase.utils as utils
import spacy

from rephrase.service_loader import SLoader


def _process_internal(question):
    import rephrase.question_dispatcher as question_dispatcher

    assert(isinstance(question, spacy.tokens.span.Span))
    qtype = utils.get_question_type(question)
    if qtype != utils.QType.UNKNOWN:
        return question_dispatcher.get_options()[qtype](question)

    # Unknown question.
    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    question = [str(x) for x in question]
    question.append(".")
    return "@placeholder " + ' '.join(question)


# In areas of strict enforcement, what happened to Christians?
def _split_without_autocorrect(q):
    assert(isinstance(q, spacy.tokens.span.Span))

    wh_family = set([
        'what',
        'who',
        'where',
        'which',
        'how',
        'when',
        'why'
    ])

    # Take a look at a dependency tree in order to understand the following
    # part of the code.
    children = []
    for child in q[0].children:  # This is a generator (has no @len).
        if child.lemma_ not in wh_family:
            children.append(child)
        else:
            # In terms of Swaziland, what does SNL refer to?
            pass

    if len(children) == 0:
        # In how many geographic regions does UNFPA operate?
        return None, None

    # pobj  => 95%
    # amod  => In general, what does immunology study?
    # pcomp => In enforcing a charge of genocide, what loophole do many
    #                   of the signatories possess?
    good_children = []
    for child in children:
        if child.dep_.lower() in ["pobj", "amod", "pcomp"]:
            good_children.append(child)

    if len(good_children) == 0:
        # Does not happen in the entire SQuAD.
        return None, None
    if len(good_children) >= 2:
        # In the build-up to genocide, what have other authors focused on?
        # In terms of Swaziland, what does SNL refer to?
        pass

    # Choose the farthest child to "In".
    good_children = sorted(good_children, key=lambda x: x.idx, reverse=True)
    main = good_children[0]
    assert(main.head == q[0])

    # Skip over main token's syntactic descendents.
    skipped = ["In"]
    index = 0
    for token in q[1:]:  # Without "In".
        if token.text == ",":
            # In Portugal, where can you find the giant European catfish?
            break

        if token == main or main.is_ancestor(token):
            skipped.append(token.text)
            index += 1
        else:
            break
    if len(skipped) <= 1:
        return None, None

    question = q[index + 1:]
    if len(question) >= 1 and question[0].text == ",":
        question = question[1:]

    if utils.get_question_type(question) == utils.QType.UNKNOWN:
        return None, None

    return skipped, question


# In some cases a comma is missing and this confuses spaCy.
# In 2001 which Japanese Prime <Minister apologized for the brothels?
def _split_with_autocorrect(q):
    assert(isinstance(q, spacy.tokens.span.Span))

    wh_family = set([
        'what',
        'who',
        'why',
        'where',
        'which',
        'how',
        'when',
        'whom',
        'whose'
    ])

    skipped = ["In"]
    index = 0
    for token in q[1:]:  # Without "In".
        if token.text == ",":  # Stop at first comma.
            break
        if token.lemma_ in wh_family:
            break

        skipped.append(token.text)
        index += 1

    if len(skipped) <= 1:
        # In how many colors is the current iPod Touch available?
        # In which previous catastrophe not live up to international
        #           standards?
        return None, None

    question = q[index + 1:]
    if len(question) >= 1 and question[0].text == ",":
        question = question[1:]

    if len(question) <= 1:
        # In Victorian times a popular social activity was?
        return None, None

    # At this point we are sure that we can answer the second part.
    # Otherwise, there is a bug in utils.py (where the question type is
    # checked).
    return skipped, question


# Returns a pair (skipped, rem).
def _split_question(question):
    assert(isinstance(question, spacy.tokens.span.Span))

    p1, p2 = _split_without_autocorrect(question)
    if p1 is not None:
        return p1, p2

    return _split_with_autocorrect(question)


def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    skipped, question = _split_question(question)
    assert(isinstance(skipped, list))
    assert(isinstance(question, spacy.tokens.span.Span))

    if len(skipped) >= 1:
        skipped[0] = "in"  # Not "In".
    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    question = [str(x) for x in question]
    if not question[0].isupper():
        question[0] = question[0].capitalize()

    skipped = ' '.join(skipped)
    question = ' '.join(question)

    # Swap main question and "In ...".
    question = question + ", " + skipped + " ?"
    nlp = SLoader.get_full_spacy_nlp()
    doc = nlp(question)
    question = doc[0:len(doc)]  # Convert to spaCy Span (not Doc).

    return _process_internal(question)
