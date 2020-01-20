# CodiEsp: Evaluation Scripts

## Introduction
These scripts are distributed as part of the Clinical Cases Coding in Spanish language Track (CodiEsp). They are intended to be run via command line:

```
$> python task1_2_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv
$> python task3_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv
```

They compute the evaluation metrics for the corresponding tasks (Mean Average Precision for the tasks 1 and 2 and F-score for task 3).

Mean Average Precision (MAP) is computed using the Python implementation of TREC evaluation tool, [trectools](https://github.com/joaopalotti/trectools), by Palotti et al. (2019) [1].

+ gold_standard.tsv must be the gold standard files distributed in the [CodiEsp Track webpage](http://temu.bsc.es/codiesp/index.php/2019/09/19/datasets/). 

+ predictions.tsv must be the predictions file. 
    + For task 1 and 2, it is a tab-separated file with two columns: clinical case and code. Codes must be ordered by rank. For example:```S1889-836X2016000100006-1	DIAGNOSTICO	n20.0	litiasis renal```

    + For task 3, the file predictions.tsv is also a tab-separated file. In this case, with four columns: clinical case, reference position, code label, code. For example: ```S1889-836X2016000100006-1	DIAGNOSTICO	n20.0	litiasis renal```

## Prerequisites
This software requires to have Python 3 installed on your system with the libraries Pandas, NumPy, SciPy, Matplotlib and [trectools](https://pypi.python.org/pypi/trectools).


## Directory structure
The directory structure of this repo is not required to run the Python scripts. 

##### gold/
This directory contains the gold standard files for each of the sub-tasks, in separated
directories. Each sub-directory may contain different sub-directories for each data set: 
sample, train, development, test, etc. Sample gold standard files and toy data are in this GitHub repository. For more gold standard files, please, visit the [CodiEsp Track webpabe](http://temu.bsc.es/codiesp/index.php/2019/09/19/datasets/). 
Gold standard files must be in the appropriate format (such as the files distributed in the [CodiEsp Track webpage](http://temu.bsc.es/codiesp/index.php/2019/09/19/datasets/)).

##### system/
This directory contains the submission files for each of the sub-tasks, in separated
directories. Each sub-directory may contain different sub-directories for each data set: 
sample, train, development, test, etc. A toy data directory is provided. Files in the latter directories must be in the appropriate format (explained in the [Introduction section](#introduction)).


## Usage
Both scripts accept the same two parameters:
+ The --gs_path (-g) option specifies the path to the Gold Standard file.
+ The --pred_path (-p) option specifies the path to the predictions file.

```
$> python task1_2_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv
$> python task3_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv
```

## Examples
#### Example 1:
Evaluate the system output pred_task1_2.tsv against the gold standard gs_task1_2.tsv (both inside toy_data subfolders).

```
$> python3 task1_2_evaluation.py -g gold/toy_data/gs_task1_2.txt -p system/toy_data/pred_task1_2.txt

MAP estimate: 0.652
```

#### Example 2:
Evaluate the system output pred_task3.tsv against the gold standard gs_task3.tsv (both inside toy_data subfolders). Evaluation measures are Precision, Recall and F-score. A True Positive is considered when the correct code is predicted and the right reference position is also given (with 10 characters of error tolerance).

```
$> python3 task3_evaluation.py -g gold/toy_data/gs_task3.tsv -p system/toy_data/pred_task3.tsv

-----------------------------------------------------
Clinical case name			Precision
-----------------------------------------------------
S0000-000S0000000000000-00		0.333
-----------------------------------------------------
S1889-836X2016000100006-1		0.636
-----------------------------------------------------

Micro-average precision = 0.571


-----------------------------------------------------
Clinical case name			Recall
-----------------------------------------------------
S0000-000S0000000000000-00		0.5
-----------------------------------------------------
S1889-836X2016000100006-1		0.636
-----------------------------------------------------

Micro-average recall = 0.615


-----------------------------------------------------
Clinical case name			F-score
-----------------------------------------------------
S0000-000S0000000000000-00		0.4
-----------------------------------------------------
S1889-836X2016000100006-1		0.636
-----------------------------------------------------

Micro-average F-score = 0.593


__________________________________________________________

MICRO-AVERAGE STATISTICS:

Micro-average precision = 0.571

Micro-average recall = 0.615

Micro-average F-score = 0.593
```

## Contact
Antonio Miranda-Escalada (antonio.miranda@bsc.es)


## References
[1] Palotti, Joao and Scells, Harrisen and Zuccon, Guido: TrecTools: an open-source Python library for Information Retrieval practitioners involved in TREC-like campaigns, SIGIR'19, 2019, ACM.


## License


