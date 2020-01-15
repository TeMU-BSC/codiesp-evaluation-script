#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 18 15:22:29 2019

@author: antonio
"""

# Code to calculate MAP from CodiEsp results files using trectools library
# Discarded because it uses an approximation which I do not understand

import pandas as pd
from trectools import TrecQrel, TrecRun, TrecEval
from sklearn.preprocessing import LabelEncoder
import argparse


def format_gs(filepath, output_path, gs_names = ['qid', "q0", 'docno', 'reference']):
    
    # DESCRIPTION: Load Gold Standard table.
    
    # INPUT: route to TSV file with Gold Standard.
    
    # OUTPUT: pandas dataframe with columns ["query", "q0", "docid", "rel"].
    
    # Note: Dataframe headers chosen to match library standards. 
    #       More informative headers for the INPUT would be: 
    #       ["clinical case","label","code","relevance"]
    
    
    # https://github.com/joaopalotti/trectools#file-formats
    
    gs = pd.read_csv(filepath, sep='\t', header = None, names = gs_names)

    
    # Preprocessing
    gs = gs.drop('reference', axis=1) # remove reference
    gs["q0"] = str(0) # column with all zeros (q0) # Columnn needed for the library to properly import the dataframe
    gs["rel"] = str(1) # column indicating the relevance of the code (in GS, all codes are relevant)
    gs.docno = gs.docno.str.lower() # Lowercase codes
    
    # Remove codes predicted twice in the same clinical case 
    # (they are present in GS because one code may have several references)
    gs = gs.drop_duplicates(subset=['qid','docno'],  
                            keep='first')  # Keep first of the predictions

    # Write dataframe to Qrel file
    gs.to_csv(output_path, index=False, header=None, sep=' ')
    
    return

def format_predictions(filepath, output_path, system_name = 'xx', 
                       pred_names = ['query','docid']):
    
    # DESCRIPTION: Load Predictions table and add extra columns to match 
    # trectools library standards.
        
    # INPUT: route to TSV file with Predictions.
    
    # OUTPUT: pandas dataframe with columns ['query', "q0", 'docid', 'rank', 'score', 'system']
    
    # Note: Dataframe headers chosen to match library standards.
    #       More informative INPUT headers would be: 
    #       ["clinical case","code"]

    # https://github.com/joaopalotti/trectools#file-formats
    
    pred = pd.read_csv(filepath, sep='\t', header = None, names = pred_names)
    
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
    
    # Remove codes predicted twice in the same clinical case (needed here???)
    pred = pred.drop_duplicates(subset=["query","docid"], 
                                keep='first')  # Keep first of the predictions
  
    # Write dataframe to Run file
    pred.to_csv(output_path, index=False, header=None, sep = '\t')

def parse_arguments():
    
    # DESCRIPTION: Parse command line arguments
    
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-g", "--gs_path", required = True, dest = "gs_path", 
                        help = "path to GS file")
    parser.add_argument("-p", "--pred_path", required = True, dest = "pred_path", 
                        help = "path to predictions file")
    
    args = parser.parse_args()
    gs_path = args.gs_path
    pred_path = args.pred_path
    
    return gs_path, pred_path


if __name__ == '__main__':
    
    gs_path, pred_path = parse_arguments()

    ###### 1. Format GS as TrecQrel format: ######
    format_gs(gs_path, './intermediate_gs_file.txt')
        
    
    ###### 2. Format predictions as TrecRun format: ######
    format_predictions(pred_path, './intermediate_predictions_file.txt')
    
    
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