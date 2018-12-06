from keras import backend as K
from keras.losses import categorical_crossentropy
from keras.layers import Embedding, Input, LSTM, Dense, Lambda
from keras.layers import Dropout, Multiply
from keras.layers import Bidirectional, RepeatVector, Concatenate
from keras.models import Model
from multinli.keras_custom_layers import TimeDistributedHighway, Similarity
from multinli.settings import PREMISE_LEN, HYPOTHESIS_LEN


def bidaff(num_words, embeddings_matrix, scope, embedding_dim=64):
    # (batch, input_len) => (batch, input_len, embedding_dim)
    premise_input = Input(shape=(PREMISE_LEN,), name="p_input")
    premise_emb = Embedding(input_dim=num_words + 1,  # word 0 used for padding
                            output_dim=embedding_dim,
                            weights=[embeddings_matrix],
                            input_length=PREMISE_LEN,
                            name="embedding_prem_" + scope,
                            mask_zero=False,
                            trainable=False)(premise_input)
    hypothesis_input = Input(shape=(HYPOTHESIS_LEN,), name="h_input")
    hypothesis_emb = Embedding(input_dim=num_words + 1,
                               output_dim=embedding_dim,
                               weights=[embeddings_matrix],
                               input_length=HYPOTHESIS_LEN,
                               name="embeding_hypo_" + scope,
                               mask_zero=False,
                               trainable=False)(hypothesis_input)

    premise_emb = Dropout(0.2, name="dropout_1")(premise_emb)
    hypothesis_emb = Dropout(0.2, name="dropout_2")(hypothesis_emb)

    # Pass them through a 1 layer highway network.
    for highway_index in range(1, 2):
        premise_emb = TimeDistributedHighway(
                            premise_emb, embedding_dim,
                            "highway_p_bidaff_{}".format(highway_index))
        hypothesis_emb = TimeDistributedHighway(
                            hypothesis_emb, embedding_dim,
                            "highway_h_bidaff_{}".format(highway_index))

    # Contextual Embed Layer
    prem = Bidirectional(LSTM(75, recurrent_dropout=0.15,
                         return_sequences=True, name="lstm_1"),
                         name="bidirectional_1")(premise_emb)
    hypo = Bidirectional(LSTM(75, recurrent_dropout=0.15,
                         return_sequences=True, name="lstm_2"),
                         name="bidirectional_2")(hypothesis_emb)

    sim = Similarity(name="similarity_1")([prem, hypo])

    # *************   Context-to-query attention. ***********************

    # Softmax on each line.
    col_softmax = Lambda(lambda x: K.softmax(x, axis=-1),
                         name="lambda_1")(sim)

    # Product between sofmax prob and each query vector.
    UT = Lambda(lambda x: K.batch_dot(x[0], x[1], axes=(2, 1)),
                output_shape=lambda x: x[0][:2] + x[1][2:],
                name="lambda_2")([col_softmax, hypo])

    # *************   Query-to-context attention. ***********************

    # Max per line then softmax.
    line_softmax = Lambda(lambda x: K.max(x, axis=-1),
                          output_shape=lambda x: (x[0], x[1]),
                          name="lambda_3")(sim)
    line_softmax = Lambda(lambda x: K.softmax(x, axis=-1),
                          name="lambda_4")(line_softmax)

    # Make @line_softmax a matrix with 1 row.
    line_softmax = Lambda(lambda x: K.expand_dims(x, axis=1),
                          output_shape=lambda x: (x[0], 1, x[1]),
                          name="lambda_5")(line_softmax)

    # Matrix multiplication.
    HT = Lambda(lambda x: K.batch_dot(x[0], x[1], axes=(2, 1)),
                output_shape=lambda x: x[0][:2] + x[1][2:],
                name="lambda_6")([line_softmax, prem])

    # Remove one extra row.
    HT = Lambda(lambda x: K.squeeze(x, axis=1),
                output_shape=lambda x: (x[0], x[2]),
                name="lambda_7")(HT)

    HT = RepeatVector(PREMISE_LEN, name="repeat_vector_1")(HT)

    # ************    Combine attention vectors. ***********************

    G = Concatenate(axis=-1, name="concatenate_1")([
        prem,
        UT,
        Multiply(name="multiply_1")([prem, UT]),
        Multiply(name="multiply_2")([prem, HT])
    ])

    G = Bidirectional(LSTM(75, recurrent_dropout=0.1, name="lstm_3"),
                      name="bidirectional_3")(G)

    output_1 = Dense(200, activation='relu', name="dense_1")(G)
    output_1 = Dropout(0.2, name="dropout_3")(output_1)

    output_2 = Dense(200, activation='relu', name="dense_2")(output_1)
    output_2 = Dropout(0.2, name="dropout_4")(output_2)

    output_3 = Dense(200, activation='relu', name="dense_3")(output_2)

    output = Dense(3, activation='softmax', name="dense_4")(output_3)

    model = Model(inputs=[premise_input, hypothesis_input], outputs=[output])
    model.compile(loss=categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    return model


# Simple entry point for other modules. This can be called by default,
# multiple times and the same model will be returned. It is useful for testing
# models because you need to change only one line of code and the change gets
# propagated to all the places where @define_mode is called.
def define_model(*args, **kwargs):
    return bidaff(*args, **kwargs)
