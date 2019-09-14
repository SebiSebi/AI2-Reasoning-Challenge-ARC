import tensorflow as tf

from keras import backend as K
from keras.engine import Layer


# This attention is similar to the Key-Value-Query self-attention but
# only uses the Key and the Value since we don't need the third component
# for this use case. The main application of the KV attention is to
# select the most important timestamps from a time-series using self
# information: that is, there is no other tensor to compute attention to.
# KV attention works as follow:
#  * Let x be the input with shape (batch_size, timestamps, size).
#  * Let xt be the component of x at timestamp t (shape = (size,))
#  * Each xt is projected onto the key vector space and onto the
#    value vector space using independent matrices.
#  * Furthermore, each element from the key space is projected
#    into a single scalar using a dot product. These values are then
#    normalized using the softmax function;
#  * The vectors in the Value space are summed according to the probabilities
#    and the weighted sum is the final output of the layer.
# A quick draw with the graph can be found:
#  * here: http://bit.do/eL7kf and
#  * here: https://tinyurl.com/y5ncha3b (same image).
# @key_size = the dimention of the key vector space.
# @value_size = the dimention of the value vector space.
# Both are required.
class KVAttention(Layer):

    # @attention_size is the variable @k from the paper.
    def __init__(self, key_size, value_size,
                 return_attention_scores=False, **kwargs):
        if K.backend() != 'tensorflow':
            raise RuntimeError('KVAttention is only available with '
                               'the TensorFlow backend.')
        assert(isinstance(key_size, int) and key_size >= 1)
        assert(isinstance(value_size, int) and value_size >= 1)
        assert(isinstance(return_attention_scores, bool))

        self.key_size = key_size
        self.value_size = value_size
        self.return_attention_scores = return_attention_scores
        self.imput_dim = None
        self.timestamps = None

        super(KVAttention, self).__init__(**kwargs)

    # The model receives an input with shape (batch_size, timestamp, input_dim)
    def build(self, input_shape):
        assert(len(input_shape) == 3)

        self.timestamps = input_shape[1]
        self.input_dim = input_shape[2]

        self.key_embed_w = self.add_weight(
                        shape=(self.input_dim, self.key_size),
                        name='key_embed_w',
                        initializer='glorot_uniform',
                        trainable=True
        )
        self.key_embed_b = self.add_weight(
                        shape=(self.key_size,),
                        name='key_embed_b',
                        initializer='zeros',
                        trainable=True
        )
        self.key_to_scalar_w = self.add_weight(
                        shape=(self.key_size, 1),
                        name='key_to_scalar_w',
                        initializer='glorot_uniform',
                        trainable=True
        )
        self.key_to_scalar_b = self.add_weight(
                        shape=(1,),
                        name='key_to_scalar_b',
                        initializer='zeros',
                        trainable=True
        )
        self.value_embed_w = self.add_weight(
                        shape=(self.input_dim, self.value_size),
                        name='value_embed_w',
                        initializer='glorot_uniform',
                        trainable=True
        )
        self.value_embed_b = self.add_weight(
                        shape=(self.value_size,),
                        name='value_embed_b',
                        initializer='zeros',
                        trainable=True
        )

        super(KVAttention, self).build(input_shape)

    def call(self, inputs, mask=None):
        input_tensor = inputs  # (batch_size, timestamp, input_dim)
        assert(len(input_tensor.shape) == 3)
        assert(input_tensor.shape[1] == self.timestamps)
        assert(input_tensor.shape[2] == self.input_dim)

        # K = tanh(W_emb * input_tensor + b_emb).
        K = tf.reshape(input_tensor, [-1, self.input_dim])
        K = tf.nn.xw_plus_b(K, self.key_embed_w, self.key_embed_b)
        K = tf.tanh(K)  # K.shape = (batch * timestamp, key_size)

        # Further encode the key into a single scalar for each timestamp.
        K = tf.nn.xw_plus_b(K, self.key_to_scalar_w, self.key_to_scalar_b)
        K = tf.tanh(K)  # K.shape = (batch * timestamp, 1)
        K = tf.reshape(K, [-1, self.timestamps])
        # K.shape = (batch_size, timestamp)

        # Apply softmax to the Key tensor.
        assert(len(K.shape) == 2)
        assert(K.shape[1] == self.timestamps)
        P = tf.nn.softmax(K)  # P.shape (batch_size, timestamps)
        assert(P.shape[1:] == K.shape[1:])
        if self.return_attention_scores:
            return P

        # Build the Value vector (key part is completed, we have P).
        # V = tanh(W_emb2 * input_tensor + b_emb2).
        V = tf.reshape(input_tensor, [-1, self.input_dim])
        V = tf.nn.xw_plus_b(V, self.value_embed_w, self.value_embed_b)
        V = tf.nn.relu(V)  # V.shape = (batch * timestamp, value_size)
        V = tf.reshape(V, [-1, self.timestamps, self.value_size])
        # V.shape = (batch_size, timestamp, value_size)

        # Perform the weighted sum.
        P = tf.expand_dims(P, 1)
        # P.shape = (batch_size, 1, timestamps)
        # V.shape = (batch_size, timestamps, value_size)

        out = tf.matmul(P, V)
        assert(len(out.shape) == 3)
        assert(out.shape[1] == 1)
        out = tf.squeeze(out, axis=1)
        assert(out.shape[1] == self.value_size)

        return out

    def compute_output_shape(self, input_shape):
        assert(isinstance(input_shape, tuple))
        assert(len(input_shape) == 3)
        if self.return_attention_scores:
            return (input_shape[0], self.timestamps)
        return (input_shape[0], self.value_size)
