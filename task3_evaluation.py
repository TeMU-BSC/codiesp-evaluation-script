#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 16:11:51 2020

@author: antonio
"""

import pandas as pd
import argparse



def read_gs(filepath, gs_headers=["clinical_case","label_gs", "code", "ref", "pos_gs"]):
    
    # DESCRIPTION: Load Gold Standard table
    
    # INPUT: route to TSV file with Gold Standard.
    
    # OUTPUT: pandas dataframe with columns:
    #       ['clinical_case','label_gs','code','ref','pos_gs','start_pos_gs','end_pos_gs']
    
    gs_data = pd.read_csv(filepath, sep="\t", names=gs_headers)
    
    gs_data['start_pos_gs'], gs_data['aux_end_gs'] = gs_data['pos_gs'].str.split(' ', 1).str
    
    # In case there are discontinuous annotations, just keep the first and 
    # last offset and consider everything in between as part of the reference.
    gs_data["end_pos_gs"] = gs_data['aux_end_gs'].apply(lambda x: x.split(' ')[-1]) 
    gs_data = gs_data.drop(["aux_end_gs"], axis=1)
    
    gs_data['start_pos_gs'] = gs_data['start_pos_gs'].astype("int")
    gs_data['end_pos_gs'] = gs_data['end_pos_gs'].astype("int")
    
    return gs_data

def read_run(filepath, run_headers=["clinical_case","pos_pred","label_pred", "code"]):
    
    # DESCRIPTION: Load Predictions table
        
    # INPUT: route to TSV file with Predictions.
    
    # OUTPUT: pandas dataframe with columns:
    #        [clinical_case, label_pred, code, start_pos_pred, end_pos_pred]
        
    run_data = pd.read_csv(filepath, sep="\t", names=run_headers)
    
    # Split position into starting and end positions
    run_data['start_pos_pred'], run_data['end_pos_pred'] = run_data['pos_pred'].str.split(' ', 1).str
    run_data['start_pos_pred'] = run_data['start_pos_pred'].astype("int")
    run_data['end_pos_pred'] = run_data['end_pos_pred'].astype("int")
    run_data = run_data.drop("pos_pred", axis=1)
    
    return run_data

def parse_arguments():
    
    # DESCRIPTION: Parse command line arguments
    
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-g", "--gs_path", required = True, dest = "gs_path", 
                        help = "path to GS file")
    parser.add_argument("-p", "--pred_path", required = True, dest = "pred_path",
                        help = "path to predictions file")
    
    args = parser.parse_args()
    gs_filepath = args.gs_path
    pred_filepath = args.pred_path
    
    return gs_filepath, pred_filepath

def calculate_score(df_gs, df_pred, tol = 10):
           
    # DESCRIPTION: Calculate task 3 score:
    # 
    #           number of correctly found references
    # score = ---------------------------------------
    #                 total number of codes
    #
    # Two scores are calculated: per document and micro-average.
    # In case a code has several references, just acknowledging one is enough.
    # In case of discontinuous references, the reference is considered to 
    # start and the start position of the first part of the reference and to 
    # end at the final position of the last part of the reference.
    
    # INPUT: pandas dataframes with the Gold Standard (df_gs) and with the
    #       predictions (df_pred). Dataframes columns are those output by the
    #       functions read_gs and read_run.
    
    # OUTPUT: pandas series with one entry per clinical case score (index 
    #       column contains clinical case names) and float with the 
    #       micro-average score.

    # Predicted Positives:
    PredP_per_cc = df_run.drop_duplicates(subset=['clinical_case', 
                                                  "code"]).groupby("clinical_case")["code"].count()
    PredP = df_run.drop_duplicates(subset=['clinical_case', "code"]).shape[0]
    
    # Gold Standard Positives:
    GSP_per_cc = df_gs.drop_duplicates(subset=['clinical_case', 
                                               "code"]).groupby("clinical_case")["code"].count()
    GSP = df_gs.drop_duplicates(subset=['clinical_case', "code"]).shape[0]
    
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
        
    # Calculate weights proportional to the amount of useless text wrongly selected
    # weight = 1 - (useless space / reference length)
    '''df_sel["weight"] = 1 - ((df_sel["start_space"] + df_sel["end_space"]) /
                            (df_sel["end_pos_gs"] - df_sel["start_pos_gs"]))'''
    
    # Remove duplicates that appear in case there are codes with several references in GS
    # In case just one of the references is predicted, mark the code as True
    df_final = df_sel.sort_values(by="is_valid",
                                  ascending=True).drop_duplicates(
                                      subset=["clinical_case", "code"],
                                      keep="last")

    # True Positives:
    TP_per_cc = df_final[df_final["is_valid"] == True].groupby("clinical_case")["is_valid"].count()
    TP = df_final[df_final["is_valid"] == True].shape[0]
    
    # Calculate Final Metrics:
    P_per_cc =  TP_per_cc / PredP_per_cc
    P = TP / PredP
    R_per_cc = TP_per_cc / GSP_per_cc
    R = TP / GSP
    F1_per_cc = (2 * P_per_cc * R_per_cc) / (P_per_cc + R_per_cc)
    F1 = (2 * P * R) / (P + R)
                                            
    return P_per_cc, P, R_per_cc, R, F1_per_cc, F1
    

if __name__ == '__main__':
    
    gs_path, pred_path = parse_arguments()
    
    ###### 1. Load GS and Predictions ######
    df_gs = read_gs(gs_path)
    df_run = read_run(pred_path)
    
    ###### 2. Calculate score ######
    P_per_cc, P, R_per_cc, R, F1_per_cc, F1 = calculate_score(df_gs, df_run)
    
    ###### 3. Show results ######  
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tPrecision')
    print('-----------------------------------------------------')
    for index, val in P_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
        
    print('\nMicro-average precision = {}\n'.format(round(P, 3)))
    
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tRecall')
    print('-----------------------------------------------------')
    for index, val in R_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
        
    print('\nMicro-average recall = {}\n'.format(round(R, 3)))
    
    print('\n-----------------------------------------------------')
    print('Clinical case name\t\t\tF-score')
    print('-----------------------------------------------------')
    for index, val in F1_per_cc.items():
        print(str(index) + '\t\t' + str(round(val, 3)))
        print('-----------------------------------------------------')
        
    print('\nMicro-average F-score = {}\n'.format(round(F1, 3)))
    print('\nMicro-average precision = {}\n'.format(round(P, 3)))
    print('\nMicro-average recall = {}\n'.format(round(R, 3)))
