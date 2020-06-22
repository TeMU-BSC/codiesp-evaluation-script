#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 09:45:01 2020

@author: antonio
"""
import pandas as pd
import argparse
import warnings

###### 0. Load valid codes lists: ######

def read_gs(gs_path):
    gs_data = pd.read_csv(gs_path, sep="\t", names=['clinical_case', 'code'])
    gs_data.code = gs_data.code.str.lower()
    return gs_data

def read_run(pred_path, valid_codes):
    run_data = pd.read_csv(pred_path, sep="\t", names=['clinical_case', 'code'])
    run_data.code = run_data.code.str.lower()
    run_data = run_data[run_data['code'].isin(valid_codes)]
    if (run_data.shape[0] == 0):
        warnings.warn('None of the predicted codes are considered valid codes')
    return run_data



def calculate_metrics(df_gs, df_pred):
    Pred_Pos_per_cc = df_pred.drop_duplicates(subset=['clinical_case', 
                                                  "code"]).groupby("clinical_case")["code"].count()
    Pred_Pos = df_pred.drop_duplicates(subset=['clinical_case', "code"]).shape[0]
    
    # Gold Standard Positives:
    GS_Pos_per_cc = df_gs.drop_duplicates(subset=['clinical_case', 
                                               "code"]).groupby("clinical_case")["code"].count()
    GS_Pos = df_gs.drop_duplicates(subset=['clinical_case', "code"]).shape[0]
    cc = set(df_gs.clinical_case.tolist())
    TP_per_cc = pd.Series(dtype=float)
    for c in cc:
        pred = set(df_pred.loc[df_pred['clinical_case']==c,'code'].values)
        gs = set(df_gs.loc[df_gs['clinical_case']==c,'code'].values)
        TP_per_cc[c] = len(pred.intersection(gs))
        
    TP = sum(TP_per_cc.values)
        
    
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
    print('\n{}|{}|{}'.format(round(P, 3), round(R, 3), round(F1, 3)))