'''
    This module contains different architectures for solving QA instances.
'''

from keras import backend as K
from keras.losses import categorical_crossentropy
from keras.layers import Embedding, Input, Dense, LSTM, concatenate
from keras.layers import Dropout, Bidirectional, TimeDistributed
from keras.layers import RepeatVector, Add, Activation, Reshape
from keras.layers import Permute, Lambda, Concatenate, Multiply
from keras.models import Model
from keras.utils import plot_model
from qa.keras_custom_layers import CharCNN, TimeDistributedHighway, Similarity
from qa.settings import QUESTION_LEN, ANSWER_LEN, CONTEXT_LEN, MAX_WORD_LEN
from qa.settings import CHAR_EMBEDDINGS_DIM


# Achieves a binary accuracy of about 73.5%.
def simple_LSTM(num_words, embeddings_matrix, ce_loader,
                scope, embedding_dim=64):
    # (batch, input_len) => (batch, input_len, embedding_dim)
    q_input = Input(shape=(QUESTION_LEN,), name="q_input")
    a_input = Input(shape=(ANSWER_LEN,), name="a_input")
    c_input = Input(shape=(CONTEXT_LEN,), name="c_input")

    q_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=QUESTION_LEN,
                      name="embedding_q_" + scope,
                      mask_zero=False,
                      trainable=False)
    a_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=ANSWER_LEN,
                      name="embedding_a_" + scope,
                      mask_zero=False,
                      trainable=False)
    c_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=CONTEXT_LEN,
                      name="embedding_c_" + scope,
                      mask_zero=False,
                      trainable=False)

    q = q_emb(q_input)
    a = a_emb(a_input)
    c = c_emb(c_input)

    q_lstm = LSTM(150, recurrent_dropout=0.15)(q)
    a_lstm = LSTM(150, recurrent_dropout=0.15)(a)
    c_lstm = LSTM(150, recurrent_dropout=0.15)(c)

    cqa = concatenate([c_lstm, q_lstm, a_lstm], axis=1)
    cqa = Dropout(0.25)(cqa)

    output_1 = Dense(250, activation='relu')(cqa)
    output_1 = Dropout(0.25)(output_1)
    output_2 = Dense(350, activation='relu')(output_1)

    output = Dense(2, activation='softmax')(output_2)
    model = Model(inputs=[q_input,
                          a_input, c_input], outputs=[output])
    model.compile(loss=categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    plot_model(model, to_file='2way_model.png', show_shapes=True)
    return model


def attentive_reader(num_words, embeddings_matrix, ce_loader, scope,
                     embedding_dim=64):
    # (batch, input_len) => (batch, input_len, embedding_dim)
    q_input = Input(shape=(QUESTION_LEN,), name="q_input")
    a_input = Input(shape=(ANSWER_LEN,), name="a_input")
    c_input = Input(shape=(CONTEXT_LEN,), name="c_input")

    q_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=QUESTION_LEN,
                      name="embedding_q_" + scope,
                      mask_zero=False,
                      trainable=False)
    a_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=ANSWER_LEN,
                      name="embedding_a_" + scope,
                      mask_zero=False,
                      trainable=False)
    c_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=CONTEXT_LEN,
                      name="embedding_c_" + scope,
                      mask_zero=False,
                      trainable=False)

    q = q_emb(q_input)
    a = a_emb(a_input)
    c = c_emb(c_input)

    q = TimeDistributed(Dense(300, activation='tanh'))(q)
    a = TimeDistributed(Dense(300, activation='tanh'))(a)
    c = TimeDistributed(Dense(300, activation='tanh'))(c)

    # q = Dropout(0.25)(q)
    # a = Dropout(0.25)(a)
    # c = Dropout(0.25)(c)

    q_lstm = Bidirectional(LSTM(50, recurrent_dropout=0.35))(q)
    c_lstm = Bidirectional(LSTM(50, recurrent_dropout=0.35,
                                return_sequences=True))(c)

    aux1 = TimeDistributed(Dense(200, activation=None,
                                 use_bias=False))(c_lstm)

    aux2 = Dense(200, activation=None, use_bias=False)(q_lstm)
    aux2 = RepeatVector(CONTEXT_LEN)(aux2)

    mt = Add()([aux1, aux2])
    mt = TimeDistributed(Activation('tanh'))(mt)

    st = TimeDistributed(Dense(1, activation=None, use_bias=False))(mt)
    st = Reshape((CONTEXT_LEN,))(st)
    st = Activation('softmax')(st)
    st = Reshape((CONTEXT_LEN, 1))(st)

    c_lstm = Permute((2, 1))(c_lstm)
    r = Lambda(lambda x: K.batch_dot(x[0], x[1]))([c_lstm, st])
    r = Reshape((-1,))(r)

    # Combine document attention and query (question).
    aux1 = Dense(450, activation=None, use_bias=False)(q_lstm)
    r = Dense(450, activation=None, use_bias=False)(r)

    gAS = Add()([r, aux1])
    gAS = Activation('tanh')(gAS)

    a_lstm = Bidirectional(LSTM(50, recurrent_dropout=0.25))(a)
    cqa = concatenate([gAS, a_lstm], axis=1)

    cqa = Dense(250, activation='relu')(cqa)

    cqa = Dropout(0.40)(cqa)

    cqa = Dense(250, activation='relu')(cqa)

    cqa = Dropout(0.15)(cqa)

    output = Dense(2, activation='softmax')(cqa)
    model = Model(inputs=[q_input,
                          a_input, c_input], outputs=[output])
    model.compile(loss=categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    plot_model(model, to_file='2way_model.png', show_shapes=True)
    return model


def attentive_reader_cqa(num_words, embeddings_matrix, scope,
                         embedding_dim=64):
    # (batch, input_len) => (batch, input_len, embedding_dim)
    q_input = Input(shape=(QUESTION_LEN,), name="q_input")
    a_input = Input(shape=(ANSWER_LEN,), name="a_input")
    c_input = Input(shape=(CONTEXT_LEN,), name="c_input")

    q_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=QUESTION_LEN,
                      name="embedding_q_" + scope,
                      mask_zero=False,
                      trainable=False)
    a_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=ANSWER_LEN,
                      name="embedding_a_" + scope,
                      mask_zero=False,
                      trainable=False)
    c_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=CONTEXT_LEN,
                      name="embedding_c_" + scope,
                      mask_zero=False,
                      trainable=False)

    q = q_emb(q_input)
    a = a_emb(a_input)
    c = c_emb(c_input)

    q = TimeDistributed(Dense(300, activation='tanh'))(q)
    a = TimeDistributed(Dense(300, activation='tanh'))(a)
    c = TimeDistributed(Dense(300, activation='tanh'))(c)

    q = Dropout(0.25)(q)
    a = Dropout(0.25)(a)
    c = Dropout(0.25)(c)

    q_lstm = Bidirectional(LSTM(35, recurrent_dropout=0.1))(q)
    c_lstm = Bidirectional(LSTM(35, recurrent_dropout=0.1,
                                return_sequences=True))(c)
    a_lstm = Bidirectional(LSTM(35, recurrent_dropout=0.1))(a)

    aux1 = TimeDistributed(Dense(125, activation=None,
                                 use_bias=False))(c_lstm)

    # Question attention
    aux2 = Dense(125, activation=None, use_bias=False)(q_lstm)
    aux2 = RepeatVector(CONTEXT_LEN)(aux2)

    # Answer attention
    aux3 = Dense(125, activation=None, use_bias=False)(a_lstm)
    aux3 = RepeatVector(CONTEXT_LEN)(aux3)

    mt = Add()([aux1, aux2, aux3])
    mt = TimeDistributed(Activation('tanh'))(mt)

    st = TimeDistributed(Dense(1, activation=None, use_bias=False))(mt)
    st = Reshape((CONTEXT_LEN,))(st)
    st = Activation('softmax')(st)
    st = Reshape((CONTEXT_LEN, 1))(st)

    c_lstm = Permute((2, 1))(c_lstm)
    r = Lambda(lambda x: K.batch_dot(x[0], x[1]))([c_lstm, st])
    r = Reshape((-1,))(r)

    # Combine document attention and query (question).
    aux1 = Dense(450, activation=None, use_bias=False)(q_lstm)
    r = Dense(450, activation=None, use_bias=False)(r)

    gAS = Add()([r, aux1])
    gAS = Activation('tanh')(gAS)

    cqa = concatenate([gAS, a_lstm, q_lstm], axis=1)

    cqa = Dense(250, activation='relu')(cqa)

    cqa = Dropout(0.25)(cqa)

    cqa = Dense(250, activation='relu')(cqa)

    cqa = Dropout(0.15)(cqa)

    output = Dense(2, activation='softmax')(cqa)
    model = Model(inputs=[q_input,
                          a_input, c_input], outputs=[output])
    model.compile(loss=categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def attention_heatmap(num_words, embeddings_matrix, scope, embedding_dim=64):
    # (batch, input_len) => (batch, input_len, embedding_dim)
    q_input = Input(shape=(QUESTION_LEN,), name="q_input")
    a_input = Input(shape=(ANSWER_LEN,), name="a_input")
    c_input = Input(shape=(CONTEXT_LEN,), name="c_input")

    q_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=QUESTION_LEN,
                      name="embedding_q_" + scope,
                      mask_zero=False,
                      trainable=False)
    a_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=ANSWER_LEN,
                      name="embedding_a_" + scope,
                      mask_zero=False,
                      trainable=False)
    c_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=CONTEXT_LEN,
                      name="embedding_c_" + scope,
                      mask_zero=False,
                      trainable=False)

    q = q_emb(q_input)
    a = a_emb(a_input)
    c = c_emb(c_input)

    q = TimeDistributed(Dense(300, activation='tanh'))(q)
    a = TimeDistributed(Dense(300, activation='tanh'))(a)
    c = TimeDistributed(Dense(300, activation='tanh'))(c)

    q_lstm = Bidirectional(LSTM(50, recurrent_dropout=0.35))(q)
    c_lstm = Bidirectional(LSTM(50, recurrent_dropout=0.35,
                                return_sequences=True))(c)

    aux1 = TimeDistributed(Dense(200, activation=None,
                                 use_bias=False))(c_lstm)

    aux2 = Dense(200, activation=None, use_bias=False)(q_lstm)
    aux2 = RepeatVector(CONTEXT_LEN)(aux2)

    mt = Add()([aux1, aux2])
    mt = TimeDistributed(Activation('tanh'))(mt)

    st = TimeDistributed(Dense(1, activation=None, use_bias=False))(mt)
    st = Reshape((CONTEXT_LEN,))(st)
    st = Activation('softmax')(st)
    st = Reshape((CONTEXT_LEN, 1))(st)

    model = Model(inputs=[q_input, a_input, c_input], outputs=[st])
    model.compile(loss=categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


def bidaff(num_words, embeddings_matrix, ce_loader, scope, embedding_dim=64):
    # (batch, input_len) => (batch, input_len, embedding_dim)
    q_input = Input(shape=(QUESTION_LEN,), name="q_input")
    a_input = Input(shape=(ANSWER_LEN,), name="a_input")
    c_input = Input(shape=(CONTEXT_LEN,), name="c_input")

    q_char_input = Input(shape=(QUESTION_LEN * MAX_WORD_LEN,),
                         name="q_char_input")
    a_char_input = Input(shape=(ANSWER_LEN * MAX_WORD_LEN,),
                         name="a_char_input")
    c_char_input = Input(shape=(CONTEXT_LEN * MAX_WORD_LEN,),
                         name="c_char_input")

    # Word embedders.
    q_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=QUESTION_LEN,
                      name="embedding_q2_" + scope,
                      mask_zero=False,
                      trainable=False)
    a_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=ANSWER_LEN,
                      name="embedding_a2_" + scope,
                      mask_zero=False,
                      trainable=False)
    c_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                      output_dim=embedding_dim,
                      weights=[embeddings_matrix],
                      input_length=CONTEXT_LEN,
                      name="embedding_c2_" + scope,
                      mask_zero=False,
                      trainable=False)

    # Char embedders.
    q_char_emb = Embedding(input_dim=ce_loader.get_num_words() + 1,
                           output_dim=ce_loader.get_embedding_len(),
                           weights=[ce_loader.get_embeddings_matrix()],
                           input_length=MAX_WORD_LEN * QUESTION_LEN,
                           name="char_embedding_q2_" + scope,
                           mask_zero=False,
                           trainable=False)

    a_char_emb = Embedding(input_dim=ce_loader.get_num_words() + 1,
                           output_dim=ce_loader.get_embedding_len(),
                           weights=[ce_loader.get_embeddings_matrix()],
                           input_length=MAX_WORD_LEN * ANSWER_LEN,
                           name="char_embedding_a2_" + scope,
                           mask_zero=False,
                           trainable=False)

    c_char_emb = Embedding(input_dim=ce_loader.get_num_words() + 1,
                           output_dim=ce_loader.get_embedding_len(),
                           weights=[ce_loader.get_embeddings_matrix()],
                           input_length=MAX_WORD_LEN * CONTEXT_LEN,
                           name="char_embedding_c2_" + scope,
                           mask_zero=False,
                           trainable=False)

    q = q_emb(q_input)
    a = a_emb(a_input)
    c = c_emb(c_input)

    q_char = q_char_emb(q_char_input)
    a_char = a_char_emb(a_char_input)
    c_char = c_char_emb(c_char_input)

    assert(CHAR_EMBEDDINGS_DIM == ce_loader.get_embedding_len())
    q_char = Reshape((QUESTION_LEN, MAX_WORD_LEN, CHAR_EMBEDDINGS_DIM))(q_char)
    a_char = Reshape((ANSWER_LEN, MAX_WORD_LEN, CHAR_EMBEDDINGS_DIM))(a_char)
    c_char = Reshape((CONTEXT_LEN, MAX_WORD_LEN, CHAR_EMBEDDINGS_DIM))(c_char)

    # CharCNNs for char level embeddings.
    q_char = CharCNN(q_char, name="q_charcnn")
    a_char = CharCNN(a_char, name="a_charcnn")
    c_char = CharCNN(c_char, name="c_charcnn")

    # Concatenate GloVe word embeddings with char-level embeddings.
    q = Concatenate(axis=-1)([q, q_char])
    a = Concatenate(axis=-1)([a, a_char])
    c = Concatenate(axis=-1)([c, c_char])

    q = Dropout(0.2)(q)
    c = Dropout(0.2)(c)
    a = Dropout(0.2)(a)

    # Pass them through a 2 layer highway network.
    for highway_index in range(1, 2):
        q = TimeDistributedHighway(q, 92,
                                   "highway_q_bidaff_{}".format(highway_index))
        a = TimeDistributedHighway(a, 92,
                                   "highway_a_bidaff_{}".format(highway_index))
        c = TimeDistributedHighway(c, 92,
                                   "highway_c_bidaff_{}".format(highway_index))

    # Contextual Embed Layer
    q_lstm = Bidirectional(LSTM(30, recurrent_dropout=0.15,
                                return_sequences=True))(q)
    c_lstm = Bidirectional(LSTM(30, recurrent_dropout=0.15,
                                return_sequences=True))(c)

    sim = Similarity()([c_lstm, q_lstm])

    # *************   Context-to-query attention. ***********************

    # Softmax on each line.
    col_softmax = Lambda(lambda x: K.softmax(x, axis=-1))(sim)

    # Product between sofmax prob and each query vector.
    UT = Lambda(lambda x: K.batch_dot(x[0], x[1], axes=(2, 1)),
                output_shape=lambda x: x[0][:2] + x[1][2:])(
                        [col_softmax, q_lstm])

    # *************   Query-to-context attention. ***********************

    # Max per line then softmax.
    line_softmax = Lambda(lambda x: K.max(x, axis=-1),
                          output_shape=lambda x: (x[0], x[1]))(sim)
    line_softmax = Lambda(lambda x: K.softmax(x, axis=-1))(line_softmax)

    # Make @line_softmax a matrix with 1 row.
    line_softmax = Lambda(lambda x: K.expand_dims(x, axis=1),
                          output_shape=lambda x: (x[0], 1, x[1]))(line_softmax)

    # Matrix multiplication.
    HT = Lambda(lambda x: K.batch_dot(x[0], x[1], axes=(2, 1)),
                output_shape=lambda x: x[0][:2] + x[1][2:])(
                        [line_softmax, c_lstm])

    # Remove one extra row.
    HT = Lambda(lambda x: K.squeeze(x, axis=1),
                output_shape=lambda x: (x[0], x[2]))(HT)

    HT = RepeatVector(CONTEXT_LEN)(HT)

    # ************    Combine attention vectors. ***********************

    G = Concatenate(axis=-1)([
        c_lstm,
        UT,
        Multiply()([c_lstm, UT]),
        Multiply()([c_lstm, HT])
    ])

    a_lstm = Bidirectional(LSTM(20, recurrent_dropout=0.15))(a)
    a_lstm = RepeatVector(CONTEXT_LEN)(a_lstm)

    cqa = Concatenate(axis=-1)([G, a_lstm])
    cqa = Dropout(0.2)(cqa)
    cqa = Bidirectional(LSTM(30, recurrent_dropout=0.15))(cqa)

    cqa = Dropout(0.25)(cqa)

    cqa = Dense(100, activation='relu')(cqa)

    cqa = Dropout(0.25)(cqa)

    output = Dense(2, activation='softmax')(cqa)
    model = Model(inputs=[
                    q_input, a_input, c_input,
                    q_char_input, a_char_input, c_char_input,
                  ], outputs=[output])
    model.compile(loss=categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    plot_model(model, to_file='2way_model.png', show_shapes=True)
    return model


# Simple entry point for other modules. This can be called by default,
# multiple times and the same model will be returned. It is useful for testing
# models because you need to change only one line of code and the change gets
# propagated to all the places where @define_mode is called.
def define_model(*args, **kwargs):
    return bidaff(*args, **kwargs)


if __name__ == "__main__":
    import numpy as np

    num_words = 50
    dim = 32
    embeddings_matrix = np.zeros((num_words + 1, dim), dtype=np.float32)
    model = define_model(num_words, embeddings_matrix, "sebi",
                         embedding_dim=dim)
    model.summary()
