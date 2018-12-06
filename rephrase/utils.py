import spacy

from enum import Enum


class QType(Enum):
    UNKNOWN = 0
    WHICH_OF = 1  # Which of the following ... ? Which of these items ... ?
    IN_WHICH_OF = 2  # In which of the following ... does ... ?
    REPLACE_UNDERSCORES = 3  # The atoms in a can of soda are __________.
    WHAT_BE = 4  # What is an example of a natural satellite?
    WHAT_DO = 5  # What does vastenavond mean?
    WHERE_BE = 6  # Where is the biggest city in the world located?
    WHERE_DO = 7  # Where did Sheptycki study police cooperation?
    WHO = 8  # Who was the founder of the Kirata dynasty?
    HOW_MANY = 9  # How many seats are in the Provincial Assembly?
    IN_WHAT = 10  # In what leaf structure is photosynthetic tissue found?
    WHEN_DO = 11  # When did Greece adopt the Euro as its currency?
    WHEN_BE = 12  # When is the genitive case used?
    WHAT_NOUN = 13  # What type of galaxy is the Milky Way?
    WHICH_NOUN = 14  # Which stadium is in the South Bronx?
    WHICH_BE = 15  # Which is Melbourne's largest dam?
    IN_WHICH_NOUN = 16  # In which structure is the Sun located?
    WHY = 17  # Why did the CEO of Google think the new software was necessary?
    WHAT_VERB = 18  # What caused the loss to Steaua Bucuresti in Seville?
    WHAT_GENERAL = 19  # What in tobacco can hurt dogs?
    HOW_MUCH = 20  # How much land did Bronck eventually own?
    HOW_LONG = 21  # How long is Suez canal?
    HOW_DO = 22  # How do producers get energy?
    HOW_BE = 23  # How is adolescence defined socially?
    THE = 24  # The Permian is an example of what?
    ALONG_WITH = 25  # Along with Charles, who was the son of Pippin?
    ACCORD_TO = 26  # According to Avicenna, what always exists?
    ON_WHAT = 27  # On what date was the Aviation School founded?
    IN_SMTH_QUESTION = 28  # In 1995, who decided to manage the girls group?
    START_WITH_NOUN = 29  # Methodism is part of what movement?
    START_WITH_PROPER_NOUN = 30  # Mrigavyadha means what?
    START_WITH_A = 31  # A natural camo pattern is known as what?
    HOW_ADVJ = 32  # How large is Notre Dame in acres?
    WHICH_VERB = 33  # Which can be regarded as the most interesting project?
    WHICH_GENERAL = 34  # Which famous landmark did Beyonce see in China?
    START_WITH_BE = 35  # Is balsa a softwood or a hardwood?
    START_WITH_THIS = 36  # This is an example of


def get_question_type(q):
    assert(isinstance(q, spacy.tokens.span.Span))

    # Which
    if len(q) >= 3 and q[0].lower_ == "which" and q[1].lower_ == "of":
        return QType.WHICH_OF

    if len(q) >= 4 and q[0].lower_ == "in" and (
                    q[1].lower_ == "which" and q[2].lower_ == "of"):
        return QType.IN_WHICH_OF

    if len(q) >= 4 and q[0].lower_ == "which" and q[1].pos_ == "NOUN":
        return QType.WHICH_NOUN

    if len(q) >= 3 and q[0].lower_ == "which" and q[1].lemma_ == "be":
        return QType.WHICH_BE

    if len(q) >= 4 and q[0].lower_ == "in" and (
                    q[1].lower_ == "which" and q[2].pos_ == "NOUN"):
        return QType.IN_WHICH_NOUN

    # verb is not "be" or "do".
    if len(q) >= 4 and q[0].lower_ == "which" and q[1].pos_ == "VERB":
        return QType.WHICH_VERB

    if len(q) >= 3 and q[0].lower_ == "which":
        return QType.WHICH_GENERAL

    # Special case
    if "___" in str(q):
        return QType.REPLACE_UNDERSCORES

    # What
    if len(q) >= 3 and q[0].lower_ == "what" and q[1].lemma_ == "be":
        return QType.WHAT_BE

    if len(q) >= 3 and q[0].lower_ == "what" and q[1].lemma_ == "do":
        return QType.WHAT_DO

    if len(q) >= 4 and q[0].lower_ == "in" and q[1].lower_ == "what":
        return QType.IN_WHAT

    if len(q) >= 4 and q[0].lower_ == "what" and q[1].pos_ == "NOUN":
        return QType.WHAT_NOUN

    # verb is not "be" or "do".
    if len(q) >= 4 and q[0].lower_ == "what" and q[1].pos_ == "VERB":
        return QType.WHAT_VERB

    if len(q) >= 3 and q[0].lower_ == "what":
        return QType.WHAT_GENERAL

    if len(q) >= 4 and q[0].lower_ == "on" and q[1].lower_ == "what":
        return QType.ON_WHAT

    # Where
    if len(q) >= 4 and q[0].lower_ == "where" and q[1].lemma_ == "be":
        return QType.WHERE_BE

    if len(q) >= 4 and q[0].lower_ == "where" and q[1].lemma_ == "do":
        return QType.WHERE_DO

    # Who
    if len(q) >= 3 and q[0].lower_ == "who":
        return QType.WHO

    # How
    if len(q) >= 3 and q[0].lower_ == "how" and q[1].lower_ == "many":
        return QType.HOW_MANY

    if len(q) >= 3 and q[0].lower_ == "how" and q[1].lower_ == "much":
        return QType.HOW_MUCH

    if len(q) >= 3 and q[0].lower_ == "how" and q[1].lower_ == "long":
        return QType.HOW_LONG

    if len(q) >= 3 and q[0].lower_ == "how" and q[1].lemma_ == "do":
        return QType.HOW_DO

    if len(q) >= 3 and q[0].lower_ == "how" and q[1].lemma_ == "be":
        return QType.HOW_BE

    if len(q) >= 3 and q[0].lower_ == "how" and q[1].pos_ in ["ADV", "ADJ"]:
        return QType.HOW_ADVJ

    # When
    if len(q) >= 3 and q[0].lower_ == "when" and q[1].lemma_ == "do":
        return QType.WHEN_DO

    if len(q) >= 3 and q[0].lower_ == "when" and q[1].lemma_ == "be":
        return QType.WHEN_BE

    # Why
    if len(q) >= 3 and q[0].lower_ == "why":
        return QType.WHY

    # The
    if len(q) >= 3 and q[0].lower_ == "the":
        return QType.THE

    # Along with
    if len(q) >= 3 and q[0].lower_ == "along" and q[1].lower_ == "with":
        return QType.ALONG_WITH

    # According
    if len(q) >= 3 and q[0].lemma_ == "accord" and q[1].lower_ == "to":
        return QType.ACCORD_TO

    # General types (must be the latest ones).
    if len(q) >= 3 and q[0].pos_ == "NOUN":
        return QType.START_WITH_NOUN

    if len(q) >= 3 and q[0].pos_ == "PROPN":
        return QType.START_WITH_PROPER_NOUN

    if len(q) >= 3 and q[0].lower_ == "a":  # article
        return QType.START_WITH_A

    if len(q) >= 3 and q[0].lemma_ == "be":
        return QType.START_WITH_BE

    if len(q) >= 3 and q[0].lower_ == "this":
        return QType.START_WITH_THIS

    if _is_in_something_question(q):
        return QType.IN_SMTH_QUESTION

    if _is_in_something_question_wrong_comma(q):
        return QType.IN_SMTH_QUESTION

    return QType.UNKNOWN


# In 2010, Beyonce released Dereon to what country?
# In areas of strict enforcement, what happened to Christians?
def _is_in_something_question(q):
    assert(isinstance(q, spacy.tokens.span.Span))

    if len(q) <= 3:
        return False
    if q[0].lower_ != "in":
        return False

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
        return False

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
        return False
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
        # Does not happen in the entire SQuAD dataset.
        return False

    question = q[index + 1:]
    if len(question) >= 1 and question[0].text == ",":
        question = question[1:]

    if get_question_type(question) == QType.UNKNOWN:
        return False

    return True


# In some cases a comma is missing and this confuses spaCy.
# In 2001 which Japanese Prime <Minister apologized for the brothels?
def _is_in_something_question_wrong_comma(q):
    assert(isinstance(q, spacy.tokens.span.Span))

    if len(q) <= 3:
        return False
    if q[0].lower_ != "in":
        return False

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
        return False

    question = q[index + 1:]
    if len(question) >= 1 and question[0].text == ",":
        question = question[1:]

    if len(question) <= 1:
        # In Victorian times a popular social activity was?
        return False

    if get_question_type(question) == QType.UNKNOWN:
        # Depends on the coverage status :)
        # In hard rock, an electric guitar can also be used for what?
        return False

    # In order for a gene to encode multiple proteins, how must its
    #           mRNAs be arranged?
    # In 1835 where did Chopin and his parents visit?
    # In addition to the police who did the BDF often have conflicts with?
    return True
