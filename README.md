# Multiple-choice question answering for ARC Challenge

- [Structure](#structure)
- [Stats](#stats)
- [Results](#results)
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

Stats
-----

```
--------------------------------------------------------------------------------
 Language             Files        Lines        Blank      Comment         Code
--------------------------------------------------------------------------------
 Java                    63        19577         1807         2480        15290
 Python                 141        21601         2983         4881        13737
 XML                      1          197            5            0          192
 Protobuf                 4          118           25            2           91
 Markdown                 2           72           23            0           49
 Bourne Shell             2           50            9            6           35
 Makefile                 2           47           17            0           30
--------------------------------------------------------------------------------
 Total                  215        41662         4869         7369        29424
--------------------------------------------------------------------------------
```

Collected using [cgag/loc](https://github.com/cgag/loc)

Results
-------

|Dataset             | Accuracy |
|:------------------:|:--------:|
|ARC-Easy Test       |60.943%   |
|ARC-Challenge Test  |26.706%   |


Running the model
-----------------

Please contact `gpirtoaca@gmail.com` if you want to build and run the model. There are a lot of dependencies (both software and data sources) that need to be installed.

Paper
--------------------------

TODO
