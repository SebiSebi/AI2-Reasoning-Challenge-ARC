import base64
import numpy as np

from qa.settings import DEBUG


class WordEmbeddings(object):

    def __init__(self, path, wl, use_DB=False):
        self.embeddings = None
        self.db = None
        self.wl = wl
        self.use_DB = use_DB
        if not use_DB:
            self.embeddings = {}
            with open(path) as f:
                for line in f:
                    data = line.split()
                    word, data = self.__extract_word(data, wl)
                    w_vector = np.asarray(data, dtype='float32')
                    self.embeddings[word] = w_vector
                    assert(wl == w_vector.shape[0])
            if DEBUG:
                print("Finished loading word vectors at {}".format(path))
                print("Known embeddings: {}".format(len(self.embeddings)))
                print("Word vector length: {}\n".format(wl))
        else:
            import MySQLdb
            from qa.settings import MYSQL_USER, MYSQL_PASSWORD, WE_DB
            self.db = MySQLdb.connect(user=MYSQL_USER,
                                      passwd=MYSQL_PASSWORD,
                                      db=WE_DB,
                                      use_unicode=True, charset='utf8',
                                      init_command='SET NAMES UTF8')
            if DEBUG:
                print("Using MySQL DB for word embeddings\n")

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
                word += line[i]
        return word, w_vector

    def __get_vector_count_from_db(self):
        assert(self.db)
        try:
            session = self.db.cursor()
            session.execute("SELECT COUNT(*) FROM Embeddings")
            x = int(session.fetchone()[0])
            return x
        except Exception as e:
            return -1
        return -1

    def __insert_into_db(self, word, vector):
        word = word.decode('utf8')
        try:
            session = self.db.cursor()
            session.execute("""INSERT INTO Embeddings(word, vector)
                           VALUES('{}', "{}")""".format(word, vector))
            return 0
        except Exception as e:
            print(str(e))
            if isinstance(e.args, tuple) and e.args[0] == 1062:
                # This is a duplicate word caused by UTF-8 bug.
                pass
            elif isinstance(e.args, tuple) and e.args[0] == 1406:
                # This is a too long word exception.
                pass
            return 1
        return 0

    def insert_all(self, path):
        if self.__get_vector_count_from_db() != 0:
            raise ValueError("Trying to insert embeddings in an non empty DB")
        else:
            with open(path) as f:
                count = 0
                duplicates = 0
                skipped = 0
                for line in f:
                    data = line.split()
                    word, data = self.__extract_word(data, self.wl)
                    w_vector = np.asarray(data, dtype='float32')
                    assert(self.wl == w_vector.shape[0])
                    w_vector = ' '.join(map(str, w_vector))
                    original_word = word
                    word = base64.b64encode(word.encode('utf-8'))
                    if len(word) > 250:
                        skipped += 1
                        continue
                    if self.__insert_into_db(word, w_vector) != 0:
                        duplicates += 1
                        print("\t -> duplicate: {}".format(original_word))
                    count += 1
                    if DEBUG and count % 25000 == 0:
                        print("Processed {} word embeddings".format(count))
                    if count % 100000 == 0:
                        self.db.commit()
            self.db.commit()
            count = self.__get_vector_count_from_db()
            if DEBUG:
                print("Known embeddings: {}".format(count))
                print("Word vector length: {}".format(self.wl))
                print("Duplicates found: {}".format(duplicates))
                print("Skipped words: {}\n".format(skipped))

    def to_tsv(self, input_path, output_path):
        with open(output_path, 'w') as g:
            with open(input_path) as f:
                count = 0
                for line in f:
                    data = line.split()
                    word, data = self.__extract_word(data, self.wl)
                    w_vector = np.asarray(data, dtype='float32')
                    assert(self.wl == w_vector.shape[0])
                    w_vector = ' '.join(map(str, w_vector))
                    count += 1
                    if DEBUG and count % 25000 == 0:
                        print("Processed {} word embeddings".format(count))
                    if len(word) <= 50 and len(w_vector) <= 3500:
                        g.write(word + '\t' + w_vector + '\n')

    def get_vector(self, word):
        if not self.use_DB:
            return self.embeddings.get(word, None)
        else:
            word = base64.b64encode(word.encode('utf-8')).decode('utf8')
            session = self.db.cursor()
            session.execute("""SELECT vector FROM Embeddings
                               WHERE word = '{}'""".format(word))
            w_vector = session.fetchone()
            if w_vector is not None:
                w_vector = np.asarray(w_vector[0].split(), dtype='float32')
            return w_vector
        return None

    def get_embedding_len(self):
        return self.wl


if __name__ == "__main__":
    from qa.settings import WORD_EMBEDDINGS_PATH
    w = WordEmbeddings(WORD_EMBEDDINGS_PATH, 50, True)
    w.insert_all(WORD_EMBEDDINGS_PATH)
    # w.to_tsv(WORD_EMBEDDINGS_PATH, "/var/lib/mysql-files/processed.tsv")
