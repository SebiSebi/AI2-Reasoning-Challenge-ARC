# Documents ranked by the Attentive Ranker

Download
--------

The ranked documents for the ARC Easy and ARC Challenge questions can be downloaded from
the following sources:
* Google Drive ZIP archive [here](https://drive.google.com/file/d/1dnmhjptSIBi-N_y4qemF_F_ycqrtCqqq/view?usp=sharing).


Paper
-----

The paper describing the methods of extracting those documents can be found [here](https://arxiv.org/abs/1909.00596).


JSON structure
--------------

The `JSON` files store arrays where each entry represents a question and has the following keys:
* `question_id` (string): the question ID as in the ARC dataset;
* `question_text` (string): the text of the question;
* `correct_answer` (int): number between 0 and 3;
* `answers_text` (array[string]): an array of candidate answers. `correct_answer` is an index in this array;
* `documents` (array[array[Doc]]): for each answer, we extracted the top 60 most relevant documents. The order
of this array respects the order of `answers_text` (e.g. `documents[0]` are the relevant documents for
`answers_text[0]` and so on).

A `doc` entry has 2 keys:
* `score` (float): a number between 0 and 1: the relevance of the document;
* `doc` (string): the supporting document text.

Observations:
* For a given answer, the sum of the scores of the documents supporting that answer is `1.0`.
* For a given answer, the supporting documents are sorted by the `score` in decreasing order
(e.g. the first one is the most relevant).


Example
-------

```json
    {
    	"question_id": "ACTAAP_2007_7_19",
        "question_text": "Which instrument measures atmospheric pressure?",
	"answers_text": [
            "barometer",
            "hygrometer",
            "thermometer",
            "magnetometer"
        ],
	"correct_answer": 0,
        "documents": [
            [
                {
                    "score": 0.028740137815475464,
                    "doc": "A manometer is an apparatus used to measure the pressure of a sample of a gas. KEY TAKEAWAY \u2022 Pressure is defined as the force exerted per unit area; it can be measured using a barometer or manometer. 1: P = F A Chapter 10 Gases 10. If the applied force is constant, how does the pressure exerted by an object change as the area on which the force is exerted decreases. In the real world, how does this relationship apply to the ease of driving a small nail versus a With this in mind, would you expect a heavy person to need smaller or larger snowshoes than a lighter person. Which has the highest atmospheric pressure\u2014a cave in the Himalayas, a mine 6. Mars has an average atmospheric pressure of 0. "
                }
            ],
            [
                {
                    "score": 0.029741210862994194,
                    "doc": "Several major types of hygrometers are used to measure humidity. "
                }
            ],
            [
                {
                    "score": 0.027530180290341377,
                    "doc": "Temperature is measured by using thermometers. "
		}
            ],
            [
                {
                    "score": 0.034215666353702545,
                    "doc": "This insight was made possible not only due to scientific magnetometer measurements of the era but also as a result of a significant portion of the 125,000\u00a0miles (201,000\u00a0km) of telegraph lines then in service being significantly disrupted for many hours throughout the storm. "
                }
	    ]
        ]
    }
```

**Note**: In this example, we only display the most relevant document (`top 1`) for each answer.
In the files we provide, there are another 59 documents for each answer, with relevance scores
smaller than the top one (shown here).

Notice that in the case of answer `A` (`barometer`), the system is smart enough to know that
manometers are related to barometers. More exactly, barometers are a type of closed-tube
manometer. As a result, the document is placed at the top since it can be directly used to
deduce that answer `A` is the correct answer.
