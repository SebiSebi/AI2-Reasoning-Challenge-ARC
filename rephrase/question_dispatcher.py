import rephrase.which_of as which_of
import rephrase.in_which_of as in_which_of
import rephrase.replace_underscores as replace_underscores
import rephrase.what_be as what_be
import rephrase.what_do as what_do
import rephrase.where_be as where_be
import rephrase.where_do as where_do
import rephrase.who as who
import rephrase.how_many as how_many
import rephrase.in_what as in_what
import rephrase.when_do as when_do
import rephrase.when_be as when_be
import rephrase.what_noun as what_noun
import rephrase.which_noun as which_noun
import rephrase.which_be as which_be
import rephrase.in_which_noun as in_which_noun
import rephrase.why as why
import rephrase.what_verb as what_verb
import rephrase.what_general as what_general
import rephrase.how_much as how_much
import rephrase.how_long as how_long
import rephrase.how_do as how_do
import rephrase.how_be as how_be
import rephrase.the as the
import rephrase.along_with as along_with
import rephrase.accord_to as accord_to
import rephrase.on_what as on_what
import rephrase.start_with_noun as start_with_noun
import rephrase.start_with_proper_noun as start_with_proper_noun
import rephrase.start_with_a as start_with_a
import rephrase.how_advj as how_advj
import rephrase.which_verb as which_verb
import rephrase.which_general as which_general
import rephrase.in_smth_question as in_smth_question
import rephrase.start_with_be as start_with_be
import rephrase.start_with_this as start_with_this

import rephrase.utils as utils


_options = {
    utils.QType.WHICH_OF: which_of.process,
    utils.QType.IN_WHICH_OF: in_which_of.process,
    utils.QType.REPLACE_UNDERSCORES: replace_underscores.process,
    utils.QType.WHAT_BE: what_be.process,
    utils.QType.WHAT_DO: what_do.process,
    utils.QType.WHERE_BE: where_be.process,
    utils.QType.WHERE_DO: where_do.process,
    utils.QType.WHO: who.process,
    utils.QType.HOW_MANY: how_many.process,
    utils.QType.IN_WHAT: in_what.process,
    utils.QType.WHEN_DO: when_do.process,
    utils.QType.WHEN_BE: when_be.process,
    utils.QType.WHAT_NOUN: what_noun.process,
    utils.QType.WHICH_NOUN: which_noun.process,
    utils.QType.WHICH_BE: which_be.process,
    utils.QType.IN_WHICH_NOUN: in_which_noun.process,
    utils.QType.WHY: why.process,
    utils.QType.WHAT_VERB: what_verb.process,
    utils.QType.WHAT_GENERAL: what_general.process,
    utils.QType.HOW_MUCH: how_much.process,
    utils.QType.HOW_LONG: how_long.process,
    utils.QType.HOW_DO: how_do.process,
    utils.QType.HOW_BE: how_be.process,
    utils.QType.THE: the.process,
    utils.QType.ALONG_WITH: along_with.process,
    utils.QType.ACCORD_TO: accord_to.process,
    utils.QType.ON_WHAT: on_what.process,
    utils.QType.START_WITH_NOUN: start_with_noun.process,
    utils.QType.START_WITH_PROPER_NOUN: start_with_proper_noun.process,
    utils.QType.START_WITH_A: start_with_a.process,
    utils.QType.HOW_ADVJ: how_advj.process,
    utils.QType.WHICH_VERB: which_verb.process,
    utils.QType.WHICH_GENERAL: which_general.process,
    utils.QType.IN_SMTH_QUESTION: in_smth_question.process,
    utils.QType.START_WITH_BE: start_with_be.process,
    utils.QType.START_WITH_THIS: start_with_this.process
}


def get_options():
    return _options
