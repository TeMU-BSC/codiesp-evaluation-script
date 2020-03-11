# CodiEsp: Evaluation Scripts

## Introduction
These scripts are distributed as part of the Clinical Cases Coding in Spanish language Track (CodiEsp). They are intended to be run via command line:

```
$> python codiespD_P_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv -c /path/to/codes.tsv
$> python codiespX_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv -cD /path/to/codes-D.tsv -cP path/to/codes-P.tsv
```

They compute the evaluation metrics for the corresponding tasks (Mean Average Precision for CodiEsp-D and CodiEsp-P and F-score for CodiEsp-X).

Mean Average Precision (MAP) is computed using the Python implementation of TREC evaluation tool, [trectools](https://github.com/joaopalotti/trectools), by Palotti et al. (2019) [1].

+ gold_standard.tsv must be the gold standard files distributed in the [CodiEsp Track webpage](http://temu.bsc.es/codiesp/index.php/datasets/). 

+ predictions.tsv must be the predictions file. 
    + For CodiEsp-D and CodiEsp-P, it is a tab-separated file with two columns: clinical case and code. Codes must be ordered by rank. For example:```S1889-836X2016000100006-1	DIAGNOSTICO	n20.0	litiasis renal```

    + For CodiEsp-X, the file predictions.tsv is also a tab-separated file. In this case, with four columns: clinical case, reference position, code label, code. For example: ```S1889-836X2016000100006-1	100 200	DIAGNOSTICO	n20.0```

## Prerequisites
This software requires to have Python 3 installed on your system with the libraries Pandas, NumPy, SciPy, Matplotlib and [trectools](https://pypi.python.org/pypi/trectools). For a detailed description, see requirements.txt.


## Directory structure
The directory structure of this repo is not required to run the Python scripts. 

##### gold/
This directory contains the gold standard files for each of the sub-tasks, in separated
directories. Each sub-directory may contain different sub-directories for each data set: 
sample, train, development, test, etc. Sample gold standard files and toy data are in this GitHub repository. For more gold standard files, please, visit the [CodiEsp Track webpabe](http://temu.bsc.es/codiesp/index.php/datasets/). 
Gold standard files must be in the appropriate format (such as the files distributed in the [CodiEsp Track webpage](http://temu.bsc.es/codiesp/index.php/datasets/)).

##### system/
This directory contains the submission files for each of the sub-tasks, in separated
directories. Each sub-directory may contain different sub-directories for each data set: 
sample, train, development, test, etc. A toy data directory is provided. Files in the latter directories must be in the appropriate format (explained in the [Introduction section](#introduction)).

##### codiesp_codes/
This directory contains the TSV files with the lists of valid codes for the subtasks (with their descriptions in Spanish and English).

## Usage
Both scripts require the same two parameters:
+ The --gs_path (-g) option specifies the path to the Gold Standard file.
+ The --pred_path (-p) option specifies the path to the predictions file.

In addition, codiespD_P_evaluate.py requires an extra parameter:
+ The --valid_codes_path (-c) option specifies the path to the list of valid codes for the CodiEsp subtask we are evaluating.

Finally, codiespX_evaluate.py requires two extra parameters:
+ The --valid_codes_D_path (-cD) option specifies the path to the list of valid codes for the CodiEsp-D subtask.
+ The --valid_codes_P_path (-cP) option specifies the path to the list of valid codes for the CodiEsp-P subtask.

```
$> python codiespD_P_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv -c /path/to/codes.tsv
$> python codiespX_evaluate.py -g /path/to/gold_standard.tsv -p /path/to/predictions.tsv -cD /path/to/codes-D.tsv -cP path/to/codes-P.tsv
```

## Examples
#### Example 1:
Evaluate the system output pred_D.tsv against the gold standard gs_D.tsv (both inside toy_data subfolders).

```
$> python3 codiespD_P_evaluation.py -g gold/toy_data/gs_D.tsv -p system/toy_data/pred_D.tsv -c codiesp_codes/codiesp-D_codes.tsv

MAP estimate: 0.444
```

#### Example 2:
Evaluate the system output pred_X.tsv against the gold standard gs_X.tsv (both inside toy_data subfolders). Evaluation measures are Precision, Recall and F-score. A True Positive is considered when the correct code is predicted and the right reference position is also given (with 10 characters of error tolerance).

```
$>  python3 codiespX_evaluation.py -g gold/toy_data/gs_X.tsv -p system/toy_data/pred_X.tsv -cD codiesp_codes/codiesp-D_codes.tsv -cP codiesp_codes/codiesp-P_codes.tsv 

-----------------------------------------------------
Clinical case name			Precision
-----------------------------------------------------
S0000-000S0000000000000-00		nan
-----------------------------------------------------
S1889-836X2016000100006-1		0.7
-----------------------------------------------------
codiespX_evaluation.py:248: UserWarning: Some documents do not have predicted codes, document-wise Precision not computed for them.

Micro-average precision = 0.636


-----------------------------------------------------
Clinical case name			Recall
-----------------------------------------------------
S0000-000S0000000000000-00		nan
-----------------------------------------------------
S1889-836X2016000100006-1		0.636
-----------------------------------------------------
codiespX_evaluation.py:260: UserWarning: Some documents do not have Gold Standard codes, document-wise Recall not computed for them.

Micro-average recall = 0.538


-----------------------------------------------------
Clinical case name			F-score
-----------------------------------------------------
S0000-000S0000000000000-00		nan
-----------------------------------------------------
S1889-836X2016000100006-1		0.667
-----------------------------------------------------
codiespX_evaluation.py:271: UserWarning: Some documents do not have predicted codes, document-wise F-score not computed for them.
codiespX_evaluation.py:274: UserWarning: Some documents do not have Gold Standard codes, document-wise F-score not computed for them.

Micro-average F-score = 0.583


__________________________________________________________

MICRO-AVERAGE STATISTICS:

Micro-average precision = 0.636

Micro-average recall = 0.538

Micro-average F-score = 0.583
```

## Contact
Antonio Miranda-Escalada (antonio.miranda@bsc.es)


## References
[1] Palotti, Joao and Scells, Harrisen and Zuccon, Guido: TrecTools: an open-source Python library for Information Retrieval practitioners involved in TREC-like campaigns, SIGIR'19, 2019, ACM.


## License


