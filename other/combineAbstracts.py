# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 18:15:38 2019
Methods to:
    1. combine original and schiz abstracts
        -to assimilate their tags ('A' becomes 'G') to create balanced number of G tags and concentrate on pico tagging
        - to sample and randomly delete G tags
@author: ls612
"""

import codecs
import random
import re
import pandas as pd 
pathSchizDev='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\Dev.txt'
pathSchizTest='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\TestMeerkat.txt'
pathSchizTrain='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\TrainMeerkat.txt'


pathOrigTrain='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\PICO_train.txt'
pathOrigDev='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\PICO_dev.txt'
pathOrigTest='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\PICO_test.txt'
#PICO_train.txt PICO_dev.txt PICO_test.txt

def combine(doc1, doc2, destination):##combine documents specified in paths as parameters, output as text file
    d1 = codecs.open(doc1,encoding='utf-8', mode='r')
    linesd1= d1.readlines()#get all the lines. these lines are tab-separated, first entry is the bigram and third is the count 
    d1.close()
    
    d2 = codecs.open(doc2,encoding='utf-8', mode='r')
    linesd2= d2.readlines()#get all the lines. these lines are tab-separated, first entry is the bigram and third is the count 
    d2.close()
    
    key=''
    allAbs={}
    p=False
    i=False
    o=False
    
    for line in linesd1:
        if '###' in line:
            if key != '':
                
                if p==False or i == False or o == False:#to sort out the previous abstract if it is not complete are not complete
                    print(key) ##see the ones that were excluded
                    #print('---')
                    del allAbs[key]
                    
                
            key=line.strip() +'ORIG\n'#to prevent overlaps if id in new and original dataset are identical###create new key
            p=False
            i=False
            o=False
           
                
            allAbs[key]= [key]#make empty dict entry for this new annotated abstract
        
    
        else:
            
            if key != '':
                ######################OPTIONAL: change uninteresting tags to G tag
#                if re.search(r'\|(A|M|R|C)\|', line):#finds tags to change
#                    line = re.sub(r'(\.+)(\|.\|)', r'\1|G|', line)
#                    if random.random() <=0.33:
#                        allAbs[key].append(line)
                #else:    #append anywaz
                #print(line)
                if re.search(r'\|[P]\|', line):
                    p=True
                elif re.search(r'\|[I]\|', line):
                    i=True
                elif re.search(r'\|[O]\|', line):
                    o=True
                        
                allAbs[key].append(line)
            
    key=''
    for line in linesd2:
        if '###' in line:
            key=line.strip() +'SCHIZ\n'#to prevent overlaps if id in new and original dataset are identical
            allAbs[key]= [key]#make empty dict entry for this annotated abstract
        
        else:
        
            if key != '':
#                if re.search(r'\|[G]\|', line):##deletes some ration oof random G samples
#                     if random.random() <=0.33:
#                        allAbs[key].append(line)
#                else:    
                allAbs[key].append(line)
            
    allKeys = list(allAbs.keys())#to get each abstract only once
    
    random.shuffle(allKeys)#shuffle to make order random
    
    finalLines=[]#var that will be written to file
    
    for key in allKeys:
        for sent in allAbs[key]:
            finalLines.append(sent)
    
    out = codecs.open(destination, encoding='utf-8', mode='w')
    out.writelines(finalLines)
    out.close()       
    print('Created file ' + destination)    
    
def originalDF(doc1,  ids,path,checkCompleteness=False):#gets the original tagged abstract sentences and outputs them as df that can be used for BERT fine tuning
    d1 = codecs.open(doc1,encoding='utf-8', mode='r')
    linesd1= d1.readlines()#get all the lines. these lines are tab-separated, first entry is the bigram and third is the count 
    d1.close()#orig
    
      #schiz
    #######################################original data: filter out the abstracts that are pico complete
    key=''
    allAbs={}
    p=False
    i=False
    o=False
    
    delCount = 0
    delAbs = []
    for line in linesd1:
        if '###' in line:
            if key != '' and checkCompleteness:
                
                if p==False or i == False or o == False:#to sort out the previous abstract if it is not complete are not complete
                    #print(key) ##see the ones that were excluded
                    #print('---')
                    delAbs.append(allAbs[key])
                    del allAbs[key]
                    delCount+=1
                
            key=line.strip()#to prevent overlaps if id in new and original dataset are identical###create new key
            p=False
            i=False
            o=False
           
                
            allAbs[key]= []#make empty dict entry for this new annotated abstract
        
    
        else:
            
            if key != '':
                ######################OPTIONAL: change uninteresting tags to G tag
#                if re.search(r'\|(A|M|R|C)\|', line):#finds tags to change
#                    line = re.sub(r'(\w+)(\|.\|)', r'\1|G|', line)
#                    if random.random() <=0.33:
#                        allAbs[key].append(line)
                #else:    #append anywaz
                #print(line)
                if checkCompleteness:
                    if re.search(r'\|[P]\|', line):
                        p=True
                    elif re.search(r'\|[I]\|', line):
                        i=True
                    elif re.search(r'\|[O]\|', line):
                        o=True
                        
                allAbs[key].append(line)
                
    rows=[]
    oip=0
    ip=0
    op=0
    oi=0
    empties=0
    MODE='else'
    ########################################################make one hot label vectors
    print('Assigning tags...')
    if MODE=='allTags':############make files that contain all possible tags, including methods, results etc
        for key, item in allAbs.items():
            counter=0#to add nr to ID
            
            for line in item:
                line = re.sub(r'\n', '', line)#get rid of unncecessary linebreaks
                if re.search(r'\|[P]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    #df.loc[len(df)] = [key+str(counter)+ids,line,1,0,1,0,0,0,0]####performance of loc is horrible here, takes wa to long for train dataframe. write to csv instead
                    rows.append([key+str(counter)+ids,line,1,0,0,0,0,0,0])#add p entry
                elif re.search(r'\|[I]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,1,0,0,0,0,0])
                elif re.search(r'\|[O]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,0,1,0,0,0,0])
                    
                elif re.search(r'\|OIP\|', line):
                    line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,1,1,1,0,0,0,0])
                    oip += 1#count how many occurrences we have for the schiz special multitags
                elif re.search(r'\|OI\|', line):
                    line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,1,1,0,0,0,0])
                    oi += 1
                elif re.search(r'\|IP\|', line):
                    line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,1,1,0,0,0,0,0]) 
                    ip += 1
                elif re.search(r'\|OP\|', line):
                    line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,1,0,1,0,0,0,0])
                    op += 1
                    
                elif re.search(r'\|[A]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,0,0,1,0,0,0]) 
                elif re.search(r'\|[M]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,0,0,0,1,0,0]) 
                elif re.search(r'\|[R]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,0,0,0,0,1,0])
                elif re.search(r'\|[C]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,0,0,0,0,0,1])
                
                else:
                    if line.strip() != '':#if line has content
                        #print(line)
                        line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                        rows.append([key+str(counter)+ids,line,0,0,0,0,0,0,0])#all zeros, for schiz abstracts that did not end up with an annotation anywhere
                        empties += 1
                counter += 1   
        df = pd.DataFrame(rows, columns=['id', 'comment_text','P','I','O', 'A','M','R','C'])#list of tagging options
            
    else:####make just PIO annotations, and optionally sample the unannotated
        for key, item in allAbs.items():
            counter=0#to add nr to ID
            
            for line in item:
                line = re.sub(r'\n', '', line)#get rid of unncecessary linebreaks
                if re.search(r'\|[P]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    #df.loc[len(df)] = [key+str(counter)+ids,line,1,0,1,0,0,0,0]####performance of loc is horrible here, takes wa to long for train dataframe. write to csv instead
                    rows.append([key+str(counter)+ids,line,1,0,0,0])#add p entry
                elif re.search(r'\|[I]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,1,0,0])
                elif re.search(r'\|[O]\|', line):
                    line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,0,1,0])
                elif re.search(r'\|OIP\|', line):
                    line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,1,1,1,0])
                    oip += 1
                elif re.search(r'\|OI\|', line):
                    line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,0,1,1,0])
                    oi += 1
                elif re.search(r'\|IP\|', line):
                    line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,1,1,0,0]) 
                    ip += 1
                elif re.search(r'\|OP\|', line):
                    line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                    rows.append([key+str(counter)+ids,line,1,0,1,0])
                    op += 1
                elif random.random() > 0.5:     
                    if re.search(r'\|[A]\|', line):
                        line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                        rows.append([key+str(counter)+ids,line,0,0,0,1]) 
                    elif re.search(r'\|[M]\|', line):
                        line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                        rows.append([key+str(counter)+ids,line,0,0,0,1]) 
                    elif re.search(r'\|[R]\|', line):
                        line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                        rows.append([key+str(counter)+ids,line,0,0,0,1])
                    elif re.search(r'\|[C]\|', line):
                        line = re.sub(r'(.+)(\|.\|)', '', line)#delete the tag
                        rows.append([key+str(counter)+ids,line,0,0,0,1])
                    
                    else:
                        if line.strip() != '':#if line has content
                            #print(line)
                            line = re.sub(r'(.+)(\|.+\|)', '', line)#delete the tag
                            rows.append([key+str(counter)+ids,line,0,0,0,1])#all zeros
                            empties += 1
                    counter += 1   
            
            df = pd.DataFrame(rows, columns=['id', 'comment_text','P','I','O', 'G'])#list of tagging options             
    #df.to_pickle(path+'.df')#save as df
    print(df.head())
    print(len(rows))
    print('Special tags added: {}  {}  {}  {}. empties: {}'.format(oip,ip,op,oi, empties))
    df.to_csv(path+'.csv', index=False)
    print(delCount)
    print(len(allAbs.items()))
    return df
    #############################print excluded abstract, if checking function was active
#    for i in range(10):
#        print()
#        for sent in delAbs[i]:
#            print(sent)
            
#use checkCompleteness param for jin sentences, because they contain some irrelevant abstracts    
#print('dev')            
dfDEVcszg=originalDF(pathSchizDev,'cszg','dfDEVcszg')
dfTESTcszg=originalDF(pathSchizTest,'cszg','dfTESTcszg')    

dfTRAINcszg=originalDF(pathSchizTrain,'cszg','dfTRAINcszg')



dfTESTjin=originalDF(pathOrigTest,'org','csvTESTjin', True)
dfTRAINjin=originalDF(pathOrigTrain,'org','csvTRAINjin', True)
dfDEVjin=originalDF(pathOrigDev,'org','csvDEVjin', True)

DEV = pd.concat([dfDEVcszg, dfDEVjin])
TEST = pd.concat([dfTESTcszg, dfTESTjin])
TRAIN = pd.concat([dfTRAINcszg, dfTRAINjin])

DEV.to_csv('DEV.csv', index=False)
TEST.to_csv('TEST.csv', index=False)
TRAIN.to_csv('TRAIN.csv', index=False)

DEV.to_pickle('DEV.p')
TEST.to_pickle('TEST.p')
TRAIN.to_pickle('TRAIN.p')

#combine(pathOrigDev,pathSchizDev, 'DEV.txt')
#combine(pathOrigTest,pathSchizTest, 'TEST.txt')
#combine(pathOrigTrain,pathSchizTrain, 'TRAIN.txt')