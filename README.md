# CodiEsp: Evaluation Scripts

## Introduction
These scripts is distributed as part of the Clinical Cases Coding in Spanish language Track (CodiEsp). They are intended to be run via command line:

```
$> python task1_2_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv
$> python task3_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv
```

They produce the evaluation metrics for the corresponding tasks (Mean Average Precision for the tasks 1 and 2 and the evaluation score of task 3).

gold_standard.tsv must be the gold standard files distributed in the CodiEsp Track webpage (http://temu.bsc.es/codiesp/index.php/2019/09/19/datasets/). 
predictions.tsv must be the predictions file. For task 1 and 2 it is a tab-separated file with two columns: clinical case and code. Codes must be ordered by rank. For example:
INSERT EXAMPLE OF PREDICTIONS.TSV FOR TASK 1 or 2

For task 3, the file predictions.tsv is also a tab-separated file. In this case, with four columns: clinical case, reference position, code label, code. For example:
INSERT EXAMPLE OF PREDICTIONS.TSV FOR TASK 3


## Prerequisites
This software requires to have Python 3 installed on your system with the libraries Pandas, NumPy, SciPy, Matplotlib and trectools (https://pypi.python.org/pypi/trectools).


## Directory structure
##### gold/
This directory contains the gold standard files for each of the sub-tasks, in separated
directories. Each sub-directory may contain different sub-directories for each data set: 
sample, train, development, test, etc. Sample gold standard files and toy data are in this GitHub repository. For more gold standard files, please, visit the CodiEsp Track webpabe (http://temu.bsc.es/codiesp/index.php/2019/09/19/datasets/). 
Gold standard files must be in the appropriate format (such as the files distributed in the CodiEsp Track webpage, http://temu.bsc.es/codiesp/index.php/2019/09/19/datasets/).

##### system/
This directory contains the submission files for each of the sub-tasks, in separated
directories. Each sub-directory may contain different sub-directories for each data set: 
sample, train, development, test, etc. A toy data directory is provided. Files in the latter directories must be in the appropriate format (explained in the Introduction section).

The directory structure of this GitHub repository is not mandatory to run the Python scripts.


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
Evaluate the system output pred_task1_2.tsv (inside toy_data subfolder) against the gold standard gs_task1_2.tsv (inside toy_data subfolder).

```
$> python3 task1_2_evaluation.py -g gold/toy_data/gs_task1_2.txt -p system/toy_data/pred_task1_2.txt

MAP estimate: 0.652
```

#### Example 2:
Evaluate the system output pred_task3.tsv (inside toy_data subfolder) against the gold standard gs_task3.tsv (inside toy_data subfolder).

```
$> python3 task3_evaluation.py -g gold/toy_data/gs_task3.tsv -p system/toy_data/pred_task3.tsv

-----------------------------------------------------
Clinical case name                      Precision
-----------------------------------------------------
S0000-000S0000000000000-00              0.333
-----------------------------------------------------
S1889-836X2016000100006-1               0.636
-----------------------------------------------------

Micro-average precision = 0.571


-----------------------------------------------------
Clinical case name                      Recall
-----------------------------------------------------
S0000-000S0000000000000-00              0.5
-----------------------------------------------------
S1889-836X2016000100006-1               0.636
-----------------------------------------------------

Micro-average precision = 0.615


-----------------------------------------------------
Clinical case name                      F-score
-----------------------------------------------------
S0000-000S0000000000000-00              0.4
-----------------------------------------------------
S1889-836X2016000100006-1               0.636
-----------------------------------------------------

Micro-average F-score = 0.615
```

## Contact
Antonio Miranda-Escalada (antonio.miranda@bsc.es)


## License


