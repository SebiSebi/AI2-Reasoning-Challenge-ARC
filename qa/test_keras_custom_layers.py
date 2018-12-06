import include_sys_path
import numpy as np
import unittest


from keras.layers import Input
from keras.losses import categorical_crossentropy
from keras.models import Model
from qa.keras_custom_layers import Similarity

include_sys_path.void()


class TestKerasCustomLayers(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _do_brute_force(self, x, y, WS):
        self.assertEqual(len(x.shape), 3)
        self.assertEqual(len(y.shape), 3)

        self.assertEqual(x.shape[0], y.shape[0])
        self.assertEqual(x.shape[2], y.shape[2])

        self.assertEqual(len(WS.shape), 1)
        self.assertEqual(WS.shape[0], 3 * x.shape[2])

        nr_batches = x.shape[0]
        nr_lines = x.shape[1]
        nr_cols = y.shape[1]
        dim = x.shape[2]

        out = np.zeros((nr_batches, nr_lines, nr_cols))

        for batch in range(0, nr_batches):
            for i in range(0, nr_lines):
                for j in range(0, nr_cols):
                    input1 = x[batch][i]
                    input2 = y[batch][j]
                    assert(len(input1.shape) == 1)
                    assert(len(input2.shape) == 1)
                    assert(input1.shape[0] == dim)
                    assert(input2.shape[0] == dim)

                    rez = np.concatenate((input1, input2,
                                          np.multiply(input1, input2)))
                    out[batch][i][j] = sum(np.multiply(rez, WS).tolist())

        return out

    def test_similarity_layer1(self):
        np.random.seed(181)

        input1 = Input(shape=(2, 3), name="input1")
        input2 = Input(shape=(4, 3), name="input2")

        output = Similarity()([input1, input2])

        model = Model(inputs=[input1, input2], outputs=[output])
        model.compile(loss=categorical_crossentropy,
                      optimizer='adam',
                      metrics=['accuracy'])

        x = np.array([
                [[1, 2, 3], [4, 5, 6]],
                [[-0.5, -1, -1.5], [-2, -2.5, -3]]
        ])
        y = np.array([
                [[7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18]],
                [[-13, -14, -15], [-7, -8, -9], [-10, -11, 0], [-16, -17, -18]]
        ])

        rez = model.predict({
            'input1': x,
            'input2': y
        }, batch_size=2)
        assert(rez.shape == (2, 2, 4))

        WS = np.array([0.4666319, 0.7074857, -0.14512873, 0.00937462,
                      -0.225935, -0.02118444, 0.31465364, -0.75302243,
                       0.5018892])

        correct = self._do_brute_force(x, y, WS)
        self.assertTrue(np.allclose(rez, correct))

    def test_similarity_layer2(self):
        np.random.seed(181)

        input1 = Input(shape=(20, 3), name="input1")
        input2 = Input(shape=(55, 3), name="input2")

        output = Similarity()([input1, input2])

        model = Model(inputs=[input1, input2], outputs=[output])
        model.compile(loss=categorical_crossentropy,
                      optimizer='adam',
                      metrics=['accuracy'])

        x = np.random.rand(2, 20, 3)
        y = np.random.rand(2, 55, 3)

        rez = model.predict({
            'input1': x,
            'input2': y
        }, batch_size=2)
        assert(rez.shape == (2, 20, 55))

        WS = np.array([0.4666319, 0.7074857, -0.14512873, 0.00937462,
                      -0.225935, -0.02118444, 0.31465364, -0.75302243,
                       0.5018892])

        correct = self._do_brute_force(x, y, WS)
        self.assertTrue(np.allclose(rez, correct, rtol=1e-03, atol=1e-04))

    def test_similarity_layer3(self):
        np.random.seed(181)

        input1 = Input(shape=(20, 3), name="input1")
        input2 = Input(shape=(55, 3), name="input2")

        output = Similarity()([input1, input2])

        model = Model(inputs=[input1, input2], outputs=[output])
        model.compile(loss=categorical_crossentropy,
                      optimizer='adam',
                      metrics=['accuracy'])

        x = np.random.rand(2, 20, 3)
        y = np.random.rand(2, 55, 3)

        rez = model.predict({
            'input1': x,
            'input2': y
        }, batch_size=1)
        assert(rez.shape == (2, 20, 55))

        WS = np.array([0.4666319, 0.7074857, -0.14512873, 0.00937462,
                      -0.225935, -0.02118444, 0.31465364, -0.75302243,
                       0.5018892])

        correct = self._do_brute_force(x, y, WS)
        self.assertTrue(np.allclose(rez, correct, rtol=1e-03, atol=1e-04))

    def test_similarity_layer4(self):
        np.random.seed(1)

        input1 = Input(shape=(21, 31), name="input1")
        input2 = Input(shape=(33, 31), name="input2")

        output = Similarity()([input1, input2])

        model = Model(inputs=[input1, input2], outputs=[output])
        model.compile(loss=categorical_crossentropy,
                      optimizer='adam',
                      metrics=['accuracy'])

        for bs in range(1, 46):
            x = np.random.rand(45, 21, 31)
            y = np.random.rand(45, 33, 31)

            rez = model.predict({
                'input1': x,
                'input2': y
            }, batch_size=bs)
            assert(rez.shape == (45, 21, 33))

            WS = np.array([
                0.33329689502716064,
                0.05604761838912964,
                0.28802502155303955,
                0.28234565258026123,
                0.523222029209137,
                0.41031163930892944,
                -0.14249956607818604,
                -0.43279412388801575,
                -0.497104287147522,
                0.22764116525650024,
                0.39735716581344604,
                0.13601726293563843,
                0.4671897292137146,
                -0.3082568347454071,
                -0.04944866895675659,
                -0.28589922189712524,
                -0.037893831729888916,
                -0.28463542461395264,
                -0.36206069588661194,
                0.0668899416923523,
                -0.4948527216911316,
                0.22906696796417236,
                -0.052874982357025146,
                -0.29423588514328003,
                0.26233619451522827,
                -0.33587318658828735,
                -0.43152204155921936,
                0.4593856930732727,
                -0.4741814136505127,
                0.1333429217338562,
                -0.1887567639350891,
                -0.34228259325027466,
                -0.3107457756996155,
                0.43063706159591675,
                -0.21224215626716614,
                -0.09071975946426392,
                0.4439937472343445,
                0.0844951868057251,
                0.09965360164642334,
                -0.2116629183292389,
                -0.5062006711959839,
                0.3017547130584717,
                -0.27608251571655273,
                -0.009411394596099854,
                0.28634870052337646,
                -0.00047725439071655273,
                0.05995291471481323,
                0.42113804817199707,
                0.3448009490966797,
                0.21367967128753662,
                -0.13090252876281738,
                -0.012765467166900635,
                -0.257916122674942,
                0.2814415693283081,
                0.4709520936012268,
                0.4020163416862488,
                0.5528196692466736,
                0.380185067653656,
                -0.03504306077957153,
                -0.49870190024375916,
                0.012332916259765625,
                0.5224936604499817,
                0.4435167908668518,
                0.027802109718322754,
                0.45893603563308716,
                0.48115283250808716,
                -0.15582382678985596,
                0.5021577477455139,
                0.47930294275283813,
                -0.49089330434799194,
                0.10558325052261353,
                -0.12305817008018494,
                -0.04828047752380371,
                0.5058884024620056,
                0.4346519708633423,
                0.28631651401519775,
                0.4973401427268982,
                -0.13449999690055847,
                -0.4491456151008606,
                0.4879600405693054,
                -0.40190011262893677,
                0.29989027976989746,
                -0.3853851556777954,
                0.4409407377243042,
                0.14880752563476562,
                -0.3423907160758972,
                -0.04245656728744507,
                -0.21889811754226685,
                -0.23796716332435608,
                -0.11448028683662415,
                0.4302811026573181,
                0.18658721446990967,
                0.4150739908218384,
            ])

            correct = self._do_brute_force(x, y, WS)
            self.assertTrue(np.allclose(rez, correct, rtol=0.001, atol=0.0001))
