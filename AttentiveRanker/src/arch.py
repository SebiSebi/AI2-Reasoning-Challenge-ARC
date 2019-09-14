from settings import NUM_FEATURES, NUM_SOURCES

from keras.layers import Dense, Input, TimeDistributed
from keras.layers import Concatenate, Dropout, SpatialDropout1D
from keras.models import Model
from kv_attention import KVAttention


def get_model(top_n, return_attention_scores=False):
    answer_a = Input(shape=(NUM_SOURCES * top_n, NUM_FEATURES), name="answer_a")  # noqa: E501
    answer_b = Input(shape=(NUM_SOURCES * top_n, NUM_FEATURES), name="answer_b")  # noqa: E501
    answer_c = Input(shape=(NUM_SOURCES * top_n, NUM_FEATURES), name="answer_c")  # noqa: E501
    answer_d = Input(shape=(NUM_SOURCES * top_n, NUM_FEATURES), name="answer_d")  # noqa: E501

    # These layers are shared for each answer.
    encoder_layer1 = TimeDistributed(
                        Dense(32, activation='tanh', name="dense_1"),
                        name="time_distributed_1"
    )
    dropout_layer1 = SpatialDropout1D(0.25, name="spatial_dropout_1")
    to_scalar_layer = KVAttention(
                        key_size=64, value_size=8, name="att",
                        return_attention_scores=return_attention_scores
    )

    def encode_answer(answer):
        x = encoder_layer1(answer)
        x = dropout_layer1(x)
        x = to_scalar_layer(x)
        return x

    a = encode_answer(answer_a)
    b = encode_answer(answer_b)
    c = encode_answer(answer_c)
    d = encode_answer(answer_d)

    output = None
    y = Concatenate(axis=-1, name="concatenate_1")([a, b, c, d])
    if return_attention_scores:
        output = y
    else:
        y = Dense(32, activation='relu', name="dense_2")(y)
        y = Dropout(0.1, name="dropout_1")(y)
        y = Dense(32, activation='relu', name="dense_3")(y)
        y = Dropout(0.1, name="dropout_2")(y)
        y = Dense(32, activation='relu', name="dense_4")(y)
        output = Dense(4, activation='softmax', name="dense_5")(y)

    model = Model(inputs=[answer_a, answer_b, answer_c, answer_d],
                  outputs=[output])
    return model
