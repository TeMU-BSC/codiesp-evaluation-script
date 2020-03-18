#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 15:22:29 2019

@author: antonio
"""

import warnings
import pandas as pd
from trectools import TrecQrel, TrecRun, TrecEval
import argparse


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line


def format_gs(filepath, output_path, gs_names = ['qid', 'docno']):
    '''
    DESCRIPTION: Load Gold Standard table.
    
    INPUT: 
        filepath: str
            route to TSV file with Gold Standard.
        output_path: str
            route to TSV where intermediate file is stored
    
    OUTPUT: 
        stores TSV files with columns ["query", "q0", "docid", "rel"].
    
    Note: Dataframe headers chosen to match library standards. 
          More informative headers for the INPUT would be: 
          ["clinical case","label","code","relevance"]
    
    # https://github.com/joaopalotti/trectools#file-formats
    '''
    # Check GS format:
    check = pd.read_csv(filepath, sep='\t', header = None, nrows=1)
    if check.shape[1] != 2:
        raise ImportError('The GS file does not have 2 columns. Then, it was not imported')
    
    # Import GS
    gs = pd.read_csv(filepath, sep='\t', header = None, names = gs_names)  
        
    # Preprocessing
    gs["q0"] = str(0) # column with all zeros (q0) # Columnn needed for the library to properly import the dataframe
    gs["rel"] = str(1) # column indicating the relevance of the code (in GS, all codes are relevant)
    gs.docno = gs.docno.str.lower() # Lowercase codes
    gs = gs[['qid', 'q0', 'docno', 'rel']]
    
    # Remove codes predicted twice in the same clinical case 
    # (they are present in GS because one code may have several references)
    gs = gs.drop_duplicates(subset=['qid','docno'],  
                            keep='first')  # Keep first of the predictions

    # Write dataframe to Qrel file
    gs.to_csv(output_path, index=False, header=None, sep=' ')
    
def format_predictions(filepath, output_path, valid_codes, 
                       system_name = 'xx', pred_names = ['query','docid']):
    '''
    DESCRIPTION: Load Predictions table and add extra columns to match 
    trectools library standards.
        
    INPUT: 
        filepath: str
                route to TSV file with Predictions.
        output_path: str
            route to TSV where intermediate file is stored
        valid_codes: set
            set of valid codes of this subtask

    OUTPUT: 
        stores TSV files with columns  with columns ['query', "q0", 'docid', 'rank', 'score', 'system']
    
    Note: Dataframe headers chosen to match library standards.
          More informative INPUT headers would be: 
          ["clinical case","code"]

    https://github.com/joaopalotti/trectools#file-formats
    '''
    # Check predictions format
    check = pd.read_csv(filepath, sep='\t', header = None, nrows=1)
    if check.shape[1] != 2:
        raise ImportError('The predictions file does not have 2 columns. Then, it was not imported')

    # Import predictions
    pred = pd.read_csv(filepath, sep='\t', header = None, names = pred_names)
    
    # Check predictions types
    if all(pred.dtypes == pd.Series({'query': object,'docid': object})) == False:
        warnings.warn('The predictions file has wrong types')
        
    # Check if predictions file is empty
    if pred.shape[0] == 0:
        is_empty = 1
        warnings.warn('The predictions file is empty')
    else:
        is_empty = 0
        
    # Add columns needed for the library to properly import the dataframe
    pred['rank'] = 1
    pred['rank'] = pred.groupby('query')['rank'].cumsum()
    pred['q0'] = 'Q0'
    pred['score'] = float(10) 
    pred['system'] = system_name 
    
    # Reorder and rename columns
    pred = pred[['query', "q0", 'docid', 'rank', 'score', 'system']]
    
    # Lowercase codes
    pred["docid"] = pred["docid"].str.lower() 
    
    # Remove codes predicted twice in the same clinical case
    pred = pred.drop_duplicates(subset=["query","docid"], 
                                keep='first')  # Keep first of the predictions
    
    # Remove codes predicted but not in list of valid codes
    pred = pred[pred['docid'].isin(valid_codes)]
    if (pred.shape[0] == 0) & (is_empty == 0):
        warnings.warn('None of the predicted codes are considered valid codes')
  
    # Write dataframe to Run file
    pred.to_csv(output_path, index=False, header=None, sep = '\t')

def parse_arguments():
    '''
    DESCRIPTION: Parse command line arguments
    '''
    
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-g", "--gs_path", required = True, dest = "gs_path", 
                        help = "path to GS file")
    parser.add_argument("-p", "--pred_path", required = True, dest = "pred_path", 
                        help = "path to predictions file")
    parser.add_argument("-c", "--valid_codes_path", required = True, 
                        dest = "codes_path", help = "path to valid codes TSV")
    
    args = parser.parse_args()
    gs_path = args.gs_path
    pred_path = args.pred_path
    codes_path = args.codes_path
    
    return gs_path, pred_path, codes_path


if __name__ == '__main__':
    
    gs_path, pred_path, codes_path = parse_arguments()
    
    ###### 0. Load valid codes lists: ######
    valid_codes = set(pd.read_csv(codes_path, sep='\t', header=None, 
                                  usecols=[0])[0].tolist())
    valid_codes = set([x.lower() for x in valid_codes])
    
    ###### 1. Format GS as TrecQrel format: ######
    format_gs(gs_path, './intermediate_gs_file.txt')
    
    ###### 2. Format predictions as TrecRun format: ######
    format_predictions(pred_path, './intermediate_predictions_file.txt', 
                       valid_codes)
    
    
    ###### 3. Calculate MAP ######
    # Load GS from qrel file
    qrels = TrecQrel('./intermediate_gs_file.txt')

    # Load pred from run file
    run = TrecRun('./intermediate_predictions_file.txt')

    # Calculate MAP
    te = TrecEval(run, qrels)
    MAP = te.get_map(trec_eval=False) # With this option False, rank order is taken from the given document order
    
    ###### 4. Show results ######
    print('\nMAP estimate: {}\n'.format(round(MAP, 3)))