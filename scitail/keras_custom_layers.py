
from keras import backend as K
from keras.engine.topology import Layer
from keras.initializers import RandomNormal
from keras.layers import TimeDistributed, Add, Multiply, Lambda, Dense


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
