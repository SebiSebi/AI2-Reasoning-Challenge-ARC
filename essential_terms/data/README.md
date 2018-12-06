About: essential_terms_dataset.tsv
----
It contains about 180 duplicates (as questions). It is not recommended
to be used when splitting data because there will be some questions
both in the train and in validation / test sets.


About: essential_terms_dataset2.tsv
----
Same as *essential_terms_dataset.tsv* but with duplicates removed.
180 - 200 questions have been dropped.


About: ARC Corpus
----

The ARC Corpus contains 14M unordered, science-related sentences including
knowledge relevant to ARC, and is provided to as a starting point for
addressing the challenge. This dataset was built from documents publicly
available through the major search engines, from dictionary definitions from
Wiktionary, and from articles from Simple Wikipedia that were tagged as science.
For further details of its construction, see (Clark et al., 2018).

Downloaded from: http://data.allenai.org/arc/arc-corpus/


About: science_term_list.txt
----

A file with about 9000 terms commonly used in scientific disciplines.


About: SmartStopList.txt
----

A stop-word list from SMART (Salton, 1971). Available [here](http://www.lextek.com/manuals/onix/stopwords2.html).


About: NER_to_ID.json
----

Bijection between spaCy [named entities](https://spacy.io/api/annotation#named-entities) and ids (0, 1, ...).
It can be used, for example, to generate NER's on hot encoding.
