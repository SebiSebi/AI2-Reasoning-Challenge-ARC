import include_sys_path
import spacy

from spacy import displacy

include_sys_path.void()


# is a second meter usually unnecessary to monitor electricity use

nlp = spacy.load('en_core_web_sm')
doc = nlp("Is sapwood the younger or older wood in a tree?")
doc = nlp("Is the color difference between heartwood and sapwood usually very subtle or conspicuous?")
doc = nlp("Were the szlachta obscure and mysterious or obvious and proud?")
doc = nlp("Is the Premier League the most watched football league in the world?")
doc = nlp("At different times of the year, Venus appears as a different shape because?")
doc = nlp("In a tug-of-war game, balanced forces are best represented when both teams cause the flag to?")
displacy.serve(doc, style='dep')

# Who did the Carthaginians hire to lead their army after several losses against the Romans?
# Who did Osama bin Laden volunteer to help fight in the 80s

'''
1) ________ questions:
        An image that can be ... it is called a _________
2) How does <something> <action> in order to <purpose>?
        How does a parachute sufficiently increase air resistance to allow the parachutist to land safely.
3) Which <multime> is <something>?
        Which of these is a greenhouse gas?
        Which of the following cars is a greenhouse gas?
'''
