import include_sys_path

from qa.deepmind_translate import deepmind_translate
from qa.squad_translate import squad_translate

include_sys_path.void()


if __name__ == "__main__":
    pass
    # squad_translate("data/questions/SQuAD/dev-v1.1.json", "test.json", 0.35)
    # deepmind_translate("test/cnn/questions/test/", "test.json", "TEST")
