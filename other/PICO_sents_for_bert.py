# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 15:40:20 2019

@author: ls612
"""
import pickle
from random import sample
import codecs
path = '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\ORIGINAL_PICO_test.txt'#get pubmed sents
cszg = '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\TrainMeerkat.txt'#meerkat sents
mode='cszg'

if mode=='jin':
    f = open(path, 'r')#read all info
    lines = f.readlines()
    f.close()
    
    p=[]
    i=[]
    o=[]
    
    for line in lines:#get just sent and not tag. save sent in its respective list. expand this for M or other tags if interested
        if '|P|' in line:
            p.append(line.split('|P|')[1].strip())
            
        elif '|O|' in line:
            o.append(line.split('|O|')[1].strip())
        elif '|I|' in line:
            i.append(line.split('|I|')[1].strip())
            
    for sent in o:####to see sents
        print(sent)   
        
        
    print(len(p))    #see how many sents of each category were found
    print(len(i)) 
    print(len(o)) 
    
    sents={'p':sample(p, 2000) ,'i':sample(i, 2000) ,'o':sample(o, 2000)}#get random samples to create lists of equal length. these are the examples that will be embedded and visualised
    
    with open('pico_examples.p', 'wb') as f:#to save them
        pickle.dump(sents, f)
        
else:
    f = codecs.open(cszg, encoding='utf-8',  mode='r')#same for schizophrenia sents
    lines = f.readlines()
    f.close()
    
    p=[]
    i=[]
    o=[]
    ip=[]
    oip=[]
    op=[]
    oi=[]
    
    
    for line in lines:#get just sent and not tag
        if '|P|' in line:
            p.append(line.split('|P|')[1].strip())
            
        elif '|O|' in line:
            o.append(line.split('|O|')[1].strip())
        elif '|I|' in line:
            i.append(line.split('|I|')[1].strip())
            
        if '|IP|' in line:
            ip.append(line.split('|IP|')[1].strip())
            
        elif '|OIP|' in line:
            oip.append(line.split('|OIP|')[1].strip())
        elif '|OI|' in line:
            oi.append(line.split('|OI|')[1].strip())   
        elif '|OP|' in line:
            op.append(line.split('|OP|')[1].strip())    
            
    for sent in o:####to see sents
        print(sent)   
        
        
    print(len(p))    
    print(len(i)) 
    print(len(o)) 
    
    ALLsents={'p':p ,'i':i,'o':o,'ip':ip,'oip':oip,'oi':oi,'op':op}#get random samples to create lists of equal length    
    with open('ALLpico_examplesCSZG.dict', 'wb') as f:
        pickle.dump(ALLsents, f)     