import include_sys_path
import os

from qa.two_way import main

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
include_sys_path.void()


if __name__ == "__main__":
    main()
