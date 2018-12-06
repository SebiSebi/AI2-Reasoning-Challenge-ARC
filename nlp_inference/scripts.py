'''
    Various scripts with different purposes. Mainly data processing.
'''

import include_sys_path
import tqdm

from nlp_inference.texts import num_words as get_num_words
from nlp_inference.utils import read_data_as_json

include_sys_path.void()


def _plot_length(dataset_path, what):
    assert(what in ["premise", "hypothesis"])

    data = read_data_as_json(dataset_path)
    assert(isinstance(data, list))

    field = None
    if what == "premise":
        field = "sentence1"
    elif what == "hypothesis":
        field = "sentence2"
    assert(field is not None)

    lengths = []
    for x in tqdm.tqdm(data):
        lengths.append(get_num_words(x[field]))
    assert(len(lengths) == len(data))

    import matplotlib.pyplot as plt
    plt.figure()
    plt.hist(lengths, bins='auto', density=False, facecolor='b', alpha=0.75)

    plt.xlabel("# words")
    plt.ylabel("Count")
    plt.title("Histogram of " + what + " length")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    from nlp_inference.settings import TRAIN_DATA_PATH
    _plot_length(TRAIN_DATA_PATH, what="hypothesis")
