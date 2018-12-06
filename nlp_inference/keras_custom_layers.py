import numpy as np

from keras import backend as K
from keras.engine.topology import Layer
from keras.initializers import RandomNormal
from keras.losses import categorical_crossentropy
from keras.layers import Input, LSTM, TimeDistributed, Add
from keras.layers import Multiply, Lambda, Dense
from keras.models import Model


class SliceSequence(Layer):
    '''
    Input: 2D tensor (timestamps, dim)
    Output: the tensor sliced between [l, r) in timestamp axis.
    '''

    def __init__(self, left, right, **kwargs):
        assert(left <= right)
        assert(left >= 0)
        self.left = left
        self.right = right
        super(SliceSequence, self).__init__(**kwargs)

    def build(self, input_shape):
        # (batch_size, timestamps, dim)
        assert(len(input_shape) == 3)
        assert(input_shape[1] >= self.right)
        super(SliceSequence, self).build(input_shape)

    def call(self, x):
        return x[:, self.left:self.right, :]

    def compute_output_shape(self, input_shape):
        return (input_shape[0], self.right - self.left, input_shape[2])


class GetSequenceElement(Layer):
    '''
    Input: 2D tensor (timestamps, dim)
    Output: the tensor element at timestamp x.
    '''

    def __init__(self, index, **kwargs):
        self.index = index
        super(GetSequenceElement, self).__init__(**kwargs)

    def build(self, input_shape):
        # (batch_size, timestamps, dim)
        assert(len(input_shape) == 3)
        super(GetSequenceElement, self).build(input_shape)

    def call(self, x):
        y = x[:, self.index, :]
        assert(len(y.shape) == 2)
        return y

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[2])


class LinkedAttention(Layer):
    '''
    As described in this paper: https://arxiv.org/pdf/1509.06664.pdf
    Initially used for natural language inference task.
    '''

    def __init__(self, dim, **kwargs):
        self.dim = dim
        super(LinkedAttention, self).__init__(**kwargs)

    def build(self, input_shape):
        # [0] => (batch_size, timestamps, dim1)
        # [1] => (batch_size, dim2)
        if not isinstance(input_shape, list):
            raise ValueError('Linked Attention layer expects a list '
                             'of tensors as inputs.')
        if len(input_shape) != 2:
            raise ValueError('Linked Attention layer expects two tensors as '
                             'input, {} were given'.format(len(input_shape)))
        if len(input_shape[0]) != 3:
            raise ValueError('First input in Linked Attention should have '
                             'shape (batch_size, timestamps, dim)')
        if len(input_shape[1]) != 2:
            raise ValueError('Second input in Linked Attention should have '
                             'shape (batch_size, dim)')
        self.Wy = self.add_weight(name='Wy',
                                  shape=(input_shape[0][2], self.dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        self.Wh = self.add_weight(name='Wh',
                                  shape=(input_shape[1][1], self.dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        self.w = self.add_weight(name='w',
                                 shape=(self.dim, 1),
                                 initializer='glorot_uniform',
                                 trainable=True)
        self.Wp = self.add_weight(name='Wp',
                                  shape=(input_shape[0][2], self.dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        self.Wx = self.add_weight(name='Wx',
                                  shape=(input_shape[1][1], self.dim),
                                  initializer='glorot_uniform',
                                  trainable=True)
        self.num_timestamps = input_shape[0][1]
        super(LinkedAttention, self).build(input_shape)

    def call(self, inputs):
        if not isinstance(inputs, list):
            raise ValueError('Linked Attention layer expects a list '
                             'of tensors as inputs.')
        if len(inputs) != 2:
            raise ValueError('Linked Attention layer expects two tensors as '
                             'input, {} were given'.format(len(inputs)))
        input_states = inputs[0]
        last_state = inputs[1]

        # Each LSTM state is a row vector in "input_states".
        # Apply a linear transformation to each hidden state.
        # The same transformation to all states.
        # hs.shape = (batch_size, timestamps, self.dim)
        hs = K.dot(input_states, self.Wy)

        # Apply a linear function to last_state and expand
        # it to each row vector.
        # aux3.shape = (batch_size, timestamps, size_LSTM_2)
        # aux4.shape = (batch_size, timestamps, self.dim)
        aux1 = K.expand_dims(last_state, -1)
        aux2 = K.dot(aux1, K.ones(shape=(1, self.num_timestamps)))
        aux3 = K.permute_dimensions(aux2, (0, 2, 1))
        aux4 = K.dot(aux3, self.Wh)
        assert(aux3.shape[1] == hs.shape[1])
        assert(aux3.shape[2] == last_state.shape[1])
        assert(aux4.shape[1] == hs.shape[1])
        assert(aux4.shape[2] == hs.shape[2])
        assert(aux4.shape[2] == self.dim)

        m = K.relu(hs + aux4)
        alpha = K.expand_dims(K.softmax(K.squeeze(K.dot(m, self.w), -1)), 1)

        # r.shape = (batch_size, 1, size_LSTM_1)
        r = K.batch_dot(alpha, input_states)

        output_1 = K.dot(r, self.Wp)
        output_2 = K.dot(K.expand_dims(last_state, 1), self.Wx)
        output_3 = K.squeeze(output_1, 1) + K.squeeze(output_2, 1)
        return K.relu(output_3)

    def compute_output_shape(self, input_shape):
        return (input_shape[0][0], self.dim)


# Layer ID must be something cast-able to a string.
# input_tensor must have shape (batch_size, steps, dim)
# input_tensor.shape[2] == dim must be true.
def TimeDistributedHighway(input_tensor, dim, layer_id, activation='relu'):
    dense_output = TimeDistributed(
                Dense(dim, activation=activation,
                      name="TD_HW_dense_{}".format(layer_id)),
                name="TD_HW_dense_TD_{}".format(layer_id))(input_tensor)

    pass_gate = TimeDistributed(
                Dense(dim, activation='sigmoid',
                      bias_initializer=RandomNormal(mean=-6.0, stddev=0.05),
                      name="TD_HW_pass_{}".format(layer_id)),
                name="TD_HW_pass_TD_{}".format(layer_id))(input_tensor)
    forget_gate = TimeDistributed(
                Lambda(lambda x: 1.0 - x, output_shape=(dim,),
                       name="TD_HW_forget_lambda_{}".format(layer_id)),
                name="TD_HW_forget_lambda_TD_{}".format(layer_id))(pass_gate)

    output1 = Multiply(name="TD_HW_o1_{}".format(layer_id))(
                                    [dense_output, pass_gate])
    output2 = Multiply(name="TD_HW_o2_{}".format(layer_id))(
                                    [input_tensor, forget_gate])

    return Add(name="TD_HW_add_{}".format(layer_id))([output1, output2])


# Should be the same as in QA (bidaff).
class Similarity(Layer):
    '''
    As described in this paper: https://arxiv.org/pdf/1611.01603.pdf
    '''

    def __init__(self, **kwargs):
        super(Similarity, self).__init__(**kwargs)

    def build(self, input_shape):
        # Input whould be a pair of 3D tensors (including the batch axis).
        # [0] => (batch_size, steps1, dim)
        # [1] => (batch_size, steps2, dim)
        if not isinstance(input_shape, list):
            raise ValueError('Similarity layer expects a list '
                             'of tensors as inputs.')
        if len(input_shape) != 2:
            raise ValueError('Similarity layer expects two tensors as '
                             'input, {} were given.'.format(len(input_shape)))
        if len(input_shape[0]) != 3:
            raise ValueError('First input in Similarity layer should have '
                             'shape (batch_size, timestamps1, dim).')
        if len(input_shape[1]) != 3:
            raise ValueError('Second input in Similarity layer should have '
                             'shape (batch_size, timestamps2, dim).')
        if input_shape[0][2] != input_shape[1][2]:
            raise ValueError('Expected 3rd dimensions to be equal in '
                             'Similarity layer.')

        self.WS = self.add_weight(name='WS',
                                  shape=(3 * input_shape[0][2],),
                                  initializer='glorot_uniform',
                                  trainable=True)

        super(Similarity, self).build(input_shape)

    def call(self, inputs):
        if not isinstance(inputs, list):
            raise ValueError('Similarity layer expects a list '
                             'of tensors as inputs.')
        if len(inputs) != 2:
            raise ValueError('Similarity layer expects two tensors as '
                             'input, {} were given.'.format(len(inputs)))

        x = inputs[0]
        y = inputs[1]

        # Each line in X should have the form: dataX,       1s,      dataX.
        # Each line in Y should have the form: 1s,       dataY,      dataY.
        #
        #                               =>     dataX,    dataY,  dataX * dataY
        #
        x = K.concatenate([x, K.ones(K.shape(x)), x], axis=-1)
        y = K.concatenate([K.ones(K.shape(y)), y, y], axis=-1)

        # Pair each lines and take elementwise product (without summation).
        # x = K.reshape(x, (-1, x.shape[1], 1, x.shape[2]))
        # y = K.reshape(y, (-1, 1, y.shape[1], y.shape[2]))
        x = K.expand_dims(x, axis=2)
        y = K.expand_dims(y, axis=1)
        rez = x * y

        # Apply dot product with a vector.
        rez = rez * self.WS

        # return K.ones((1, 93)) * self.WS
        return K.sum(rez, axis=-1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0][0], input_shape[0][1], input_shape[1][1])


def main():
    input = Input(shape=(7, 2))
    output_1, state1_h, state1_c = LSTM(4, return_sequences=True,
                                        return_state=True)(input)
    output_2 = LSTM(4)(output_1, initial_state=[state1_h, state1_c])
    output_3 = LinkedAttention(250)([output_1, output_2])

    # state_h and state_c are only for the last timestamp.
    # output_1[-1] == state_h

    model = Model(inputs=[input], outputs=[output_1, output_3])
    model.compile(loss=categorical_crossentropy,
                  optimizer='adam',
                  metrics=['accuracy'])
    model.summary()
    # y = model.predict(np.ones((3, 7, 2)), batch_size=3)

    '''
    x = K.variable(value=np.array([[[1, 4]], [[-3, 2]]]))
    y = K.variable(value=np.array([[[1, 2, 3], [-1, 5, 2]],
                                  [[3, 4, 1], [1, 6, 4]]]))
    z = K.batch_dot(x, y)
    print(x.shape)
    print(K.eval(z))
    '''


if __name__ == "__main__":
    np.random.seed(181)
    main()
