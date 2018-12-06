import numpy as np


class CharEmbeddings(object):
    def __init__(self, path, wl):
        self.embeddings = None
        self.wl = wl
        self.embeddings = {}
        self.all_words = [""]
        self.word_index = {}
        index = 1
        with open(path) as f:
            for line in f:
                data = line.split()
                word, data = self.__extract_word(data, wl)
                w_vector = np.asarray(data, dtype='float32')
                self.embeddings[word] = w_vector
                assert(wl == w_vector.shape[0])
                self.all_words.append(word)
                self.word_index[word] = index
                index += 1

        assert(len(self.all_words) == len(self.word_index) + 1)
        for word in self.word_index:
            pos = self.word_index[word]
            assert(self.all_words[pos] == word)

        # Build embdeddings matrix.
        self.embeddings_matrix = np.zeros((len(self.word_index) + 1, wl),
                                          dtype=np.float32)
        for word in self.all_words[1:]:
            index = self.word_index[word]
            w_vector = self.get_vector(word)
            assert(self.all_words[index] == word)

            if w_vector is None:
                w_vector = np.zeros((wl,))
            assert(w_vector.shape[0] == wl)
            self.embeddings_matrix[index] = w_vector

        print("Finished loading word vectors at {}".format(path))
        print("Known embeddings: {}".format(len(self.embeddings)))
        print("Word vector length: {}\n".format(wl))

    def get_embeddings_matrix(self):
        return self.embeddings_matrix

    def get_num_words(self):
        return len(self.word_index)

    def get_index(self, word):
        return self.word_index.get(word, 0)

    def __extract_word(self, line, wl):
        assert(len(line) >= wl)
        if len(line) == wl:
            return '', line
        w_vector = None
        word = line[0]
        line = line[1:]
        for i in range(0, len(line)):
            x = line[i]
            try:
                x = float(x)
                w_vector = line[i:]
                break
            except Exception as e:
                print(e)
                word += line[i]
        return word, w_vector

    def get_vector(self, word):
        return self.embeddings.get(word, None)

    def get_embedding_len(self):
        return self.wl
