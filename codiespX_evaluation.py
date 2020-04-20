#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:11:51 2020

@author: antonio
"""

import pandas as pd
import argparse
import warnings

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)
warnings.formatwarning = warning_on_one_line

def read_gs(filepath, gs_headers=["clinical_case","label_gs", "code", "ref", "pos_gs"]):
    '''
    DESCRIPTION: Load Gold Standard table
    
    INPUT: 
        filepath: str
            route to TSV file with Gold Standard.
    
    OUTPUT: 
        gs_data: pandas dataframe
            with columns:['clinical_case','label_gs','code','ref','pos_gs','start_pos_gs','end_pos_gs']
    '''
    # Check GS format:
    check = pd.read_csv(filepath, sep='\t', header = None, nrows=1)
    if check.shape[1] != 5:
        raise ImportError('The GS file does not have 4 columns. Then, it was not imported')
    
    gs_data = pd.read_csv(filepath, sep="\t", names=gs_headers)
    
    gs_data['start_pos_gs'], gs_data['aux_end_gs'] = gs_data['pos_gs'].str.split(' ', 1).str
    
    # In case there are discontinuous annotations, just keep the first and 
    # last offset and consider everything in between as part of the reference.
    gs_data["end_pos_gs"] = gs_data['aux_end_gs'].apply(lambda x: x.split(' ')[-1]) 
    gs_data = gs_data.drop(["aux_end_gs"], axis=1)
    
    gs_data['start_pos_gs'] = gs_data['start_pos_gs'].astype("int")
    gs_data['end_pos_gs'] = gs_data['end_pos_gs'].astype("int")
    
    return gs_data

def read_run(filepath, valid_codes, 
             run_headers=["clinical_case","pos_pred","label_pred", "code"]):
    '''
    DESCRIPTION: Load Predictions table
        
    INPUT: 
        filepath: str
            route to TSV file with Predictions.
        valid_codes: set
            set of valid codes of this subtask
    
    OUTPUT: 
        run_data: pandas dataframe
            with columns:[clinical_case, label_pred, code, start_pos_pred, end_pos_pred]
    '''
    # Check predictions format
    check = pd.read_csv(filepath, sep='\t', header = None, nrows=1)
    if check.shape[1] != 4:
        raise ImportError('The predictions file does not have 4 columns. Then, it was not imported')
        
    run_data = pd.read_csv(filepath, sep="\t", names=run_headers)
    
    # Check predictions types
    if all(run_data.dtypes == pd.Series({'clinical_case': object,
                                         'pos_pred': object,
                                         'label_pred': object,
                                         'code': object})) == False:
        warnings.warn('The predictions file has wrong types')
        
    # Check if predictions file is empty
    if run_data.shape[0] == 0:
        is_empty = 1
        warnings.warn('The predictions file is empty')
    else:
        is_empty = 0
        
    # Remove codes predicted but not in list of valid codes
    run_data = run_data[run_data['code'].isin(valid_codes)]
    if (run_data.shape[0] == 0) & (is_empty == 0):
        warnings.warn('None of the predicted codes are considered valid codes')
        
    # Split position into starting and end positions
    run_data['start_pos_pred'], run_data['end_pos_pred'] = run_data['pos_pred'].str.split(' ', 1).str
    run_data['start_pos_pred'] = run_data['start_pos_pred'].astype("int")
    run_data['end_pos_pred'] = run_data['end_pos_pred'].astype("int")
    run_data = run_data.drop("pos_pred", axis=1)
    
    return run_data

def parse_arguments():
    '''
    DESCRIPTION: Parse command line arguments
    '''
    
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-g", "--gs_path", required = True, dest = "gs_path", 
                        help = "path to GS file")
    parser.add_argument("-p", "--pred_path", required = True, dest = "pred_path",
                        help = "path to predictions file")
    parser.add_argument("-cD", "--valid_codes_D_path", required = True, 
                    dest = "codes_D_path", help = "path to valid CIE10 Diagnostico codes TSV")
    parser.add_argument("-cP", "--valid_codes_P_path", required = True, 
                dest = "codes_P_path", help = "path to valid CIE10 Procedimiento codes TSV")
    
    args = parser.parse_args()
    gs_path = args.gs_path
    pred_path = args.pred_path
    codes_d_path = args.codes_D_path
    codes_p_path = args.codes_P_path
    
    return gs_path, pred_path, codes_d_path, codes_p_path

def calculate_metrics(df_gs, df_pred, tol = 10):
    '''       
    DESCRIPTION: Calculate task X metrics:
    
    Two type of metrics are calculated: per document and micro-average.
    In case a code has several references, just acknowledging one is enough.
    In case of discontinuous references, the reference is considered to 
    start and the start position of the first part of the reference and to 
    end at the final position of the last part of the reference.
    
    INPUT: 
        df_gs: pandas dataframe
            with the Gold Standard. Columns are those output by the function read_gs.
        dfg_pred: pandas dataframe
            with the predictions. Columns are those output by the function read_run.
    
    OUTPUT: 
        P_per_cc: pandas series
            Precision per clinical case (index contains clinical case names)
        P: float
            Micro-average precision
        R_per_cc: pandas series
            Recall per clinical case (index contains clinical case names)
        R: float
            Micro-average recall
        F1_per_cc: pandas series
            F-score per clinical case (index contains clinical case names)
        F1: float
            Micro-average F-score
    '''
    
    # Predicted Positives:
    Pred_Pos_per_cc = df_run.drop_duplicates(subset=['clinical_case', 
                                                  "code"]).groupby("clinical_case")["code"].count()
    Pred_Pos = df_run.drop_duplicates(subset=['clinical_case', "code"]).shape[0]
    
    # Gold Standard Positives:
    GS_Pos_per_cc = df_gs.drop_duplicates(subset=['clinical_case', 
                                               "code"]).groupby("clinical_case")["code"].count()
    GS_Pos = df_gs.drop_duplicates(subset=['clinical_case', "code"]).shape[0]
    
    # Eliminate predictions not in GS
    df_sel = pd.merge(df_run, df_gs, 
                      how="right",
                      on=["clinical_case", "code"])
    
    # Check if GS reference is inside predicted interval
    df_sel["start_space"] = (df_sel["start_pos_gs"] - df_sel["start_pos_pred"])
    df_sel["end_space"] = (df_sel["end_pos_pred"] - df_sel["end_pos_gs"])
    df_sel["is_valid"] = df_sel.apply(lambda x: ((x["start_space"] <= tol) & 
                                                 (x["start_space"] >= 0) &
                                                 (x["end_space"] <= tol) &
                                                 (x["end_space"] >= 0)), axis=1)
    
    # Remove duplicates that appear in case there are codes with several references in GS
    # In case just one of the references is predicted, mark the code as True
    df_final = df_sel.sort_values(by="is_valid",
                                  ascending=True).drop_duplicates(
                                      subset=["clinical_case", "code"],
                                      keep="last")

    # True Positives:
    TP_per_cc = (df_final[df_final["is_valid"] == True]
                 .groupby("clinical_case")["is_valid"].count())
    TP = df_final[df_final["is_valid"] == True].shape[0]
    
    # Add entries for clinical cases that are not in predictions but are present
    # in the GS
    cc_not_predicted = (df_run.drop_duplicates(subset=["clinical_case"])
                        .merge(df_gs.drop_duplicates(subset=["clinical_case"]), 
                              on='clinical_case',
                              how='right', indicator=True)
                        .query('_merge == "right_only"')
                        .drop('_merge', 1))['clinical_case'].to_list()
    for cc in cc_not_predicted:
        TP_per_cc[cc] = 0
    
    # Remove entries for clinical cases that are not in GS but are present
    # in the predictions
    cc_not_GS = (df_gs.drop_duplicates(subset=["clinical_case"])
                .merge(df_run.drop_duplicates(subset=["clinical_case"]), 
                      on='clinical_case',
                      how='right', indicator=True)
                .query('_merge == "right_only"')
                .drop('_merge', 1))['clinical_case'].to_list()
    Pred_Pos_per_cc = Pred_Pos_per_cc.drop(cc_not_GS)

    # Calculate Final Metrics:
    P_per_cc =  TP_per_cc / Pred_Pos_per_cc
    P = TP / Pred_Pos
    R_per_cc = TP_per_cc / GS_Pos_per_cc
    R = TP / GS_Pos
    F1_per_cc = (2 * P_per_cc * R_per_cc) / (P_per_cc + R_per_cc)
    if (P+R) == 0:
        F1 = 0
        warnings.warn('Global F1 score automatically set to zero to avoid division by zero')
        return P_per_cc, P, R_per_cc, R, F1_per_cc, F1
    F1 = (2 * P * R) / (P + R)
                                            
    return P_per_cc, P, R_per_cc, R, F1_per_cc, F1
    

if __name__ == '__main__':
    
    gs_path, pred_path,codes_d_path, codes_p_path = parse_arguments()
    
    ###### 0. Load valid codes lists: ######
    valid_codes_D = set(pd.read_csv(codes_d_path, sep='\t', header=None, 
                                  usecols=[0])[0].tolist())
    valid_codes_D = set([x.lower() for x in valid_codes_D])
    
    valid_codes_P = set(pd.read_csv(codes_p_path, sep='\t', header=None, 
                                  usecols=[0])[0].tolist())
    valid_codes_P = set([x.lower() for x in valid_codes_P])
    
    valid_codes = valid_codes_D.union(valid_codes_P)
    
    ###### 1. Load GS and Predictions ######
    df_gs = read_gs(gs_path)
    df_run = read_run(pred_path, valid_codes)
    
    ###### 2. Calculate score ######
    P_per_cc, P, R_per_cc, R, F1_per_cc, F1 = calculate_metrics(df_gs, df_run)
    
    ###### 3. Show results ######  
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tPrecision')
    print('-----------------------------------------------------')
    for index, val in P_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
    if any(P_per_cc.isna()):
        warnings.warn('Some documents do not have predicted codes, ' + 
                      'document-wise Precision not computed for them.')
        
    print('\nMicro-average precision = {}\n'.format(round(P, 3)))
    
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tRecall')
    print('-----------------------------------------------------')
    for index, val in R_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
    if any(R_per_cc.isna()):
        warnings.warn('Some documents do not have Gold Standard codes, ' + 
                      'document-wise Recall not computed for them.')
    print('\nMicro-average recall = {}\n'.format(round(R, 3)))
    
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tF-score')
    print('-----------------------------------------------------')
    for index, val in F1_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
    if any(P_per_cc.isna()):
        warnings.warn('Some documents do not have predicted codes, ' + 
                      'document-wise F-score not computed for them.')
    if any(R_per_cc.isna()):
        warnings.warn('Some documents do not have Gold Standard codes, ' + 
                      'document-wise F-score not computed for them.')
    print('\nMicro-average F-score = {}\n'.format(round(F1, 3)))
    
    print('\n__________________________________________________________')
    print('\nMICRO-AVERAGE STATISTICS:')
    print('\nMicro-average precision = {}'.format(round(P, 3)))
    print('\nMicro-average recall = {}'.format(round(R, 3)))
    print('\nMicro-average F-score = {}\n'.format(round(F1, 3)))
