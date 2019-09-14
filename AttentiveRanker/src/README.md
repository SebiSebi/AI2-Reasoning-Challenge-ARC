# Attentive Ranker Code


Prerequisites
-------------

1. `python >= 3.6.4`;
2. Install the required packages specified in `requirements.txt` (if using `pip` you can run `pip install -r requirements.txt`);
3. Download this [archive](https://drive.google.com/file/d/1QK9rWNGF-7iKIolIykhcJrWZDqjWyC3i/view?usp=sharing)
and unzip it in the root directory. It includes the trained models and the data annotated with
the discriminator scores.


Evaluation
----------

Run: `python eval.py -d easy_test` (for evaluation on the ARC Easy Test dataset).
Run: `python eval.py --help` to get the flag information.


Re-training
-----------

Run: `python train.py`. Trained models will be saved into `models/` directory.
The dataset split should be specified in the `settings.py`. By default, the training
is done on the ARC Easy dataset.
