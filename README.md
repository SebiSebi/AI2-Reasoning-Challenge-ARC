# Multiple-choice question answering for ARC Challenge

- [Structure](#structure)
- [Running the model](#running-the-model)
- [Paper](#paper)


Structure
---------

* `answer/` - the neural network that combines all the solvers;
* `essential_terms/` - the model that assigns essential scores for each term in a question;
* `multinli/` - the neural network trained on the MultiNLI dataset;
* `nlp_inference/` - the neural network trained on the SNLI dataset;
* `scitail/` - the neural network trained on the SciTail dataset;
* `rephrase/` - the module that transforms questions into affirmative sentences;
* `qa/` - pre-trained neural networks on the SQuAD v1 dataset;
* `protos/` - protocol buffer definitions (for passing data around);
* `wikipedia_indexer/` - code for indexing Wikipedia dumps and science book collection. It also includes the IR solvers and candidate context extraction tool.

Running the model
-----------------

Please contact `gpirtoaca@gmail.com` if you want to build and run the model. There are a lot of dependencies (both software and data sources) that need to be installed.

Paper
--------------------------

TODO
