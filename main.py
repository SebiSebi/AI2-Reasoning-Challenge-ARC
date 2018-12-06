import include_sys_path  # This must be the first imported module.


from answer.models import Cerebro
from answer.settings import TRAIN_PATH, VAL_PATH, TEST_PATH
from answer.utils import read_dataset

include_sys_path.void()  # To remove unused module warning.


def predict_and_save_to_file():
    from answer.settings import KAGGLE_CONTEST_PATH

    data = read_dataset(KAGGLE_CONTEST_PATH)
    model = Cerebro()
    rez = model.predict(data)

    with open("submission.csv", "w") as g:
        g.write("id,correctAnswer\n")
        for q_id, ans in rez:
            g.write(q_id)
            g.write(",")
            g.write(chr(65 + int(ans)))
            g.write("\n")
        g.flush()


def main():
    train_data = []
    for path in TRAIN_PATH:
        train_data += read_dataset(path)

    val_data = []
    for path in VAL_PATH:
        val_data += read_dataset(path)

    test_data = []
    for path in TEST_PATH:
        test_data += read_dataset(path)

    model = Cerebro()
    # model.train(train_data, val_data, test_data)
    # model.binary_test(test_data)
    # model.test_4way(test_data)
    model.output_cvs_predictions(test_data)
    # model.predict_batch(val_data[:5])
    # model.print_diff(test_data)
    # predict_and_save_to_file()
    '''
    with open("models.txt", "r") as f:
        for line in f:
            line = line.split(' ')
            assert(len(line) == 2)
            model.test_4way(test_data, line[0])
    '''


if __name__ == "__main__":
    main()
