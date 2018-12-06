'''
    Various scripts with different purposes. Mainly data processing.
'''

import include_sys_path
import qa.tokenizers as tokenizers
import tqdm

from autocorrect import spell
from qa.utils import all_sentences
from qa.utils import read_data_as_json
from qa.utils import print_data_stats
from qa.utils import num_words as get_num_words
from qa.utils import text_similaritiy, pretty_print
from qa.settings import WORD_EMBEDDINGS_PATH, WORD_EMBEDDINGS_DIM
from qa.word_embeddings_loader import WordEmbeddings

include_sys_path.void()


# Given a file with a word per each line, outputs another file, in JSON format,
# with the following structure: "<entity>": index. A word is considered an
# entity if it starts with an upper case letter and has at least 2 characters.
def _build_entity_file(input_file_path, output_file_path):
    index = {}
    cnt = 0
    with open(input_file_path, "r") as f:
        for line in f:
            word = line.rstrip()
            if len(word) < 2:
                continue
            if not word[0].isupper():
                continue
            if word not in index:
                cnt += 1
                index[word] = cnt
    print("Found {} entities.".format(len(index)))
    with open(output_file_path, "w") as g:
        g.write(pretty_print(index))
        g.flush()
    print("Index written to {}".format(output_file_path))
    print("Done.")


def _get_unknown_embeddings_list(dataset_paths):
    assert(isinstance(dataset_paths, list))

    data = []
    for path in dataset_paths:
        data += read_data_as_json(path)
    print_data_stats(data, "Combined")

    tokenizer = tokenizers.SpacyTokenizer()
    tokenizer.fit_on_texts(all_sentences(data))
    print("\nNum words: {}".format(len(tokenizer.word_counts())), flush=True)

    word_index = tokenizer.word_index()
    embedder = WordEmbeddings(WORD_EMBEDDINGS_PATH, WORD_EMBEDDINGS_DIM, True)
    dim = embedder.get_embedding_len()
    emb_found = 0
    num_processed = 0
    with open("words_not_found.txt", "w") as g:
        for word in word_index:
            if num_processed % 100 == 1:
                print("Processed {} out of {} words.".format(
                                num_processed, len(word_index)))
            num_processed += 1

            w_vector = embedder.get_vector(word)
            if w_vector is None:
                w_vector = embedder.get_vector(word.lower())
            if w_vector is None:
                corrected_word = spell(word)
                assert(isinstance(corrected_word, str))
                w_vector = embedder.get_vector(corrected_word)

            if w_vector is not None:
                emb_found += 1
                assert(w_vector.shape[0] == dim)
            else:
                g.write(word + "\n")
        g.flush()

    num_words = len(word_index)
    assert(num_words == num_processed)
    if num_words == 0:
        num_words = 1
    print("Found {0:.2f}% embeddings.".format(
                            100.0 * emb_found / num_words))


def _plot_length(dataset_path, what):
    assert(what in ["question", "answer", "context"])

    data = read_data_as_json(dataset_path)

    lengths = None
    if what == "question":
        lengths = [get_num_words(x['question']) for x in data]
    elif what == "answer":
        lengths = []
        lengths += [get_num_words(x['answers'][0]['text']) for x in data]
        lengths += [get_num_words(x['answers'][1]['text']) for x in data]
        lengths += [get_num_words(x['answers'][2]['text']) for x in data]
        lengths += [get_num_words(x['answers'][3]['text']) for x in data]
        assert(len(lengths) == 4 * len(data))
    elif what == "context":
        lengths = []
        lengths += [get_num_words(x['answers'][0]['context']) for x in data]
        lengths += [get_num_words(x['answers'][1]['context']) for x in data]
        lengths += [get_num_words(x['answers'][2]['context']) for x in data]
        lengths += [get_num_words(x['answers'][3]['context']) for x in data]
        assert(len(lengths) == 4 * len(data))

    assert(isinstance(lengths, list))

    import matplotlib.pyplot as plt
    plt.figure()
    plt.hist(lengths, bins='auto', density=False, facecolor='b', alpha=0.75)

    plt.xlabel("# words")
    plt.ylabel("Count")
    plt.title("Histogram of " + what + " length")
    plt.grid(True)
    plt.show()


def _dataset_similarity(dataset_path1, dataset_path2):
    assert(isinstance(dataset_path1, str))
    assert(isinstance(dataset_path2, str))

    data1 = read_data_as_json(dataset_path1)
    data2 = read_data_as_json(dataset_path2)

    # Check for common ids.
    ids1 = set()
    for entry in data1:
        ids1.add(entry["id"])

    ids2 = set()
    for entry in data2:
        ids2.add(entry["id"])

    assert(len(ids1) == len(data1))
    assert(len(ids2) == len(data2))

    common_ids = []
    for x in ids1:
        if x in ids2:
            common_ids.append(x)

    if len(common_ids) >= 1:
        print("********** WARNING! Common question ids! **********")
        print(sorted(common_ids[0:20]))
        # return

    # Check for question similarity.
    q_sim = []
    idx = 0
    for entry1 in tqdm.tqdm(data1):
        q1 = entry1["question"]
        assert(isinstance(q1, str))

        aux = []
        for entry2 in data2:
            sim = 0
            l1 = len(q1)
            l2 = len(entry2["question"])
            if 1.0 * min(l1, l2) / max(l1, l2) >= 0.8:
                sim = text_similaritiy(q1, entry2["question"])
            aux.append((entry2, sim))
        aux = sorted(aux, key=lambda x: x[1], reverse=True)[0]
        q_sim.append((entry1, aux[0], aux[1]))

        idx += 1

    q_sim = sorted(q_sim, key=lambda x: x[2], reverse=True)

    for q1, q2, sim in q_sim[0:20]:
        print("*********************************************************")
        print(sim)
        print(pretty_print(q1))
        print(pretty_print(q2))
        print("*********************************************************")
        print("")

    print("Done checking datasets: \n\t{}\n\t{}".format(dataset_path1,
                                                        dataset_path2))


if __name__ == "__main__":
    # _build_entity_file("words_not_found.txt", "data/entities.json")
    # _get_unknown_embeddings_list(["test.json"])
    _plot_length("data/questions/SQuAD/10_train-v1.1_with_context.json",
                 what="context")
    # import os
    # from qa.settings import KaggleAllenAI, ARC_Easy
    # _dataset_similarity(
    #         os.path.join(KaggleAllenAI, "kaggle_allen_ai_train.json"),
    #         os.path.join(ARC_Easy, "ARC-Easy-Test.json")
    # )
