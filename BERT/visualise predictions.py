# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 10:14:33 2019

Simple script, to filter the predictions file and save results to csv - this was used to quickly obtain examples described in the dissertation results.
@author: ls612
"""
import pandas as pd

pathLabels='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\dataframes\\dfTESTjin.df'

pathSchizLabels='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\dataframes\\dfTESTcszg.df'
pathSchizBase = '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\Results\\JinBaseCSZGtest\\predictionsCSZG.df'#just used cszg for evaluation()
pathSchizSci = '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\Results\\JinScibertCSZGtest\\predictionsCSZG.df'

pathCszgSci = '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\Results\\cszgScibertCSZGtest\\predictionsCSZG.df'#trained 2 layers on cszg data
pathBothSci = '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\Results\\bothScibert\\predictionsCSZG.df'#trained 2 layers on cszg data

pathBase='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\Results\\JinBase\\predictions.df'
pathSci='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\Results\\JinScibert\\predictions.df'

pathSchizPure='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\Results\\cszgScibert\\predictionsCSZG.df'#scibert trained and testedonly on schiz data
pathSchizPureLabels ='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\dataframes\\combined\\sampled\\df\\TESTcszg.p'

pathBothPred='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\Results\\mixScibert\\predictionsCSZG.df'
pathBothLabels='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\BERT\\dataframes\\combined\\sampled\\df\\TEST.p'

###chose preds and labels to compare
pred = pd.read_pickle(pathSci)
pred= pred.rename(columns={"P": "p_pred", "I": "i_pred", "O": "o_pred", "A": "a_pred", "M": "m_pred", "R": "r_pred", "C": "c_pred"})#rename before concat, since columns are the same
lab = pd.read_pickle(pathLabels) 

combi = pd.concat([pred, lab], axis=1)

print(pred.head())
print(lab.head())
print(combi.head())

#examples = combi.loc[(combi['P']==1)& (combi['p_pred']>=0.2) & (combi['i_pred']>=0.2)]#examples where P was labelled, and P plus I was predicted
#PI_bert=examples.to_csv('PI_bert.csv')

#examples = combi.loc[(combi['R']==1)& (combi['o_pred']>=0.3)]#where r was labelled but O predicted
#PI_bert=examples.to_csv('OnotR_bert.csv')

#examples = combi.loc[(combi['M']==1)& (combi['m_pred']<=0.3)]#where m was labelled but not predicted 
#PI_bert=examples.to_csv('notM_bert.csv')

examples = combi.loc[(combi['I']==1)& (combi['i_pred']<=0.2)]#where i was labelled but not predicted confidently
PI_bert=examples.to_csv('labInotPred_bert.csv')

print(examples.head())