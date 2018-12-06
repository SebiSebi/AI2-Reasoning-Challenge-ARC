import spacy


def _process_with_modal_verb(question, what_token):
    assert(len(question) >= 2)

    verb = question[0]
    is_negated = False
    if question[1].lower_ in ["not", "n't"]:
        is_negated = True
        question = question[2:]
    else:
        question = question[1:]

    if len(question) == 0:
        if is_negated:
            return [str(verb), "not", "@placeholder", "."]
        return [str(verb), "@placeholder", "."]

    if question[0].pos_ == "VERB":
        # What could happen when antibiotics are used with other drugs?
        out = []
        out.append("@placeholder")
        out.append(verb.text)
        if is_negated:
            out.append("not")
        out = out + [str(x) for x in question]
        return out

    # Insert modal verb after subject and @placeholder after what_token head.
    head = what_token.head
    if head.pos_ == "VERB":
        # What could we monitor electronically that could help inform new
        #       methods of wood protection?  => ADV
        # What can small mutations be caused by?  => ADP
        while head != question[-1] and head.nbor().pos_ in ["ADV", "ADP"]:
            if head.nbor().lower_ == "if":
                break
            head = head.nbor()

    subj = None
    for token in question:
        if token.dep_.lower() in ["nsubj", "nsubjpass"]:
            subj = token
            break

    if subj is None:
        # What can each forwarding operation location provide?
        # Insert before last verb.
        for token in question:
            if token == question[-1]:  # no neighbour.
                continue
            nbor = token.nbor()
            if nbor == token:
                continue
            if nbor.pos_ == "VERB":
                subj = token

    if subj is None:
        # No subject an no verb. Probably wrong tagging.
        # What can the displacement of ice cause?
        if len(question) == 1:
            subj = question[-1]
        else:
            subj = question[-2]

    if subj.pos_ == "NOUN":
        # What can the scent of vanilla be used for?
        word = subj
        for token in question:
            if subj.is_ancestor(token) and token.idx > word.idx:
                word = token
        subj = word

    if subj.idx >= head.idx:
        # What should the government of China be responsible for providing
        #       to earthquake survivors?
        # Move head to last VERB.
        last_verb = question[-1]
        for token in question:
            if token.pos_ == "VERB":
                last_verb = token
        head = last_verb

    out = []
    for token in question:
        out.append(token.text)
        if token == subj:
            out.append(verb.text)
        if token == head:
            out.append("@placeholder")

    return out


# The verb is not "do" or "be".
def process(question):
    assert(isinstance(question, spacy.tokens.span.Span))
    assert(len(question) >= 3)

    while len(question) >= 1 and question[-1].is_punct:
        question = question[:-1]

    what_token = question[0]
    question = question[1:]  # Remove "What"
    if len(question) < 2:
        return str(question) + " @placeholder ."

    verb = question[0]
    if verb.lemma_ in ["can", "could", "may", "might", "should", "must"]:
        question = _process_with_modal_verb(question, what_token)
    elif verb.lemma_ in ["will", "would"]:
        # Although not modal verbs, it works fine.
        question = _process_with_modal_verb(question, what_token)
    elif verb.lemma_ == "have":
        if what_token.dep_.lower() == "nsubj" and what_token.head == verb.head:
            question = ["@placeholder"] + [str(x) for x in question]
        else:
            # Treat "have" as a modal verb.
            # What has the ASA identified as being ethically dangerous?
            question = _process_with_modal_verb(question, what_token)
    else:
        question = ["@placeholder"] + [str(x) for x in question]

    if len(question) >= 1 and not question[0].isupper():
        question[0] = question[0].capitalize()
    question.append(".")

    return ' '.join(question)
