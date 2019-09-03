

# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:23:40 2019
###annotate I tags
@author: ls612
"""
if __name__ ==  '__main__':
    import pickle
    import codecs
    import os
    import re
    import numpy as np
    import matplotlib.pyplot as plt
    
    ############################getting regexes
    class Study:
        def __init__(self, col):
            self.CENTRALStudyID = col[1]
            self.CRGStudyID = col[2]
            self.ShortName = col[3]
            self.StatusofStudy = col[4]
            self.TrialistContactDetails = col[5]
            self.CENTRALSubmissionStatus = col[6]
            self.Notes = col[7]
            self.DateEntered = col[8]
            self.DateToCENTRAL = col[9]
            self.DateEdited = col[10]
            self.Search_Tagged = col[11]
            self.UDef1 = col[12]
            self.UDef2 = col[13]###the country
            self.UDef3 = col[14]
            self.UDef4 = col[15]
            self.UDef5 = col[16]#the comparisons raw string
            self.interventions = self.cleanI(col[16])
            self.ISRCTN = col[17]
            self.UDef6 = col[18]
            self.UDef7 = col[19]
            self.UDef8 = col[20]
            self.UDef10 = col[21]
            self.UDef9 = col[22]
    ############################################intervention data
    study_vals= pickle.load(open("\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\pickles\\dict_tblStudy.p", "rb"))#load study data
    interventionFrequency={}
    #print(study_vals)   
    for key in study_vals.keys():#get most frequent interventions
        for intervention in study_vals[key][0].interventions:
            interventionFrequency[intervention] = interventionFrequency.get(intervention, 0) + 1
         
    print(study_vals[142][0].UDef5)#some name
    #sorted(interventionFrequency.values(), reverse=True)
    # Create a list of tuples sorted by index 1 i.e. value field     
    listofTuples = sorted(interventionFrequency.items() , reverse=True, key=lambda x: x[1])
    y=[] 
    names=[]
    # Iterate over the sorted sequence
    for elem in listofTuples :
        #print(elem[0] , " -->" , elem[1] ) 
        y.append(elem[1])
        names.append(elem[0])
    print(len(y))  
    x= np.arange(len(y))
    
    nr=150
    plt.bar(names[:nr], y[:nr])
    plt.xticks(x[:nr], names[:nr], rotation='vertical')
    plt.text(0.72, 0.9, "Mean = 4 \nMedian = 1 \nTotal= 8533", size=12,transform=plt.gca().transAxes,
             ha="left", va="top",
             bbox=dict(boxstyle="square",
                       ec=(.6, 0.5, 0.5),
                       fc=(.6, 0.8, 0.8),
                       )
             
             )
    plt.text(0.97, 0.33, "- 19 studies", size=10, rotation=70., transform=plt.gca().transAxes,
             ha="right", va="top",
             bbox=dict(boxstyle="larrow",alpha=0.4,
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )
    plt.text(0.58, 0.33, "- 33 studies", size=10, rotation=70., transform=plt.gca().transAxes,
             ha="right", va="top",
             bbox=dict(boxstyle="larrow",alpha=0.4, 
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )
    
    plt.ylabel('Number of studies')
    plt.title('Sparsity of Interventions - free text - most common 150')
    
    xticks = plt.gca().xaxis.get_major_ticks()
    
    for i in range(len(xticks)):
        if i % 10 != 0:
            xticks[i].set_visible(False)
    plt.show()
    
    mean = np.mean(y)###info nrs
    print(mean)
    print(np.median(y))
    print(y[:nr])
    
    #######################cleaned intervention names, to be used in tagging regex
    I_freeText= names
    int_ID = pickle.load(open("\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\pickles\\dict_tblIntervention.p", "rb"))#load intervention name dict
    intervention_vals = pickle.load(open("\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\pickles\\dict_tblStudyIntervention.p", "rb"))#lode intervention names in study
    intDict={}
    for key in intervention_vals.keys():#get most frequent interventions
        for intervention in intervention_vals[key]:
            intDict[intervention] = intDict.get(intervention, 0) + 1
         
    ##################################################################################plot most common interventions to reveal sparsity
    listofTuples = sorted(intDict.items() , reverse=True, key=lambda x: x[1])
    y=[] 
    codes=[]
    # Iterate over the sorted sequence
    for elem in listofTuples :
        #print(elem[0] , " -->" , elem[1] ) 
        y.append(elem[1])
        codes.append(elem[0])
    print(len(y))  
    x= np.arange(len(y))
    
    ############cleaning
    names2 = [re.sub('{.+}','',int_ID[key]).strip() for key in codes]#get intervention names from dict, but clean tags away
    ##############
    nr=150
    plt.bar(names2[:nr], y[:nr])
    plt.xticks(x[:nr], names2[:nr], rotation='vertical')
    plt.text(0.72, 0.9, "Mean = 17 \nMedian = 2 \nTotal= 2673", size=12,transform=plt.gca().transAxes,
             ha="left", va="top",
             bbox=dict(boxstyle="square",
                       ec=(.6, 0.5, 0.5),
                       fc=(.6, 0.8, 0.8),
                       )
             
             )
    plt.text(0.97, 0.33, "- 35 studies", size=10, rotation=70., transform=plt.gca().transAxes,
             ha="right", va="top",
             bbox=dict(boxstyle="larrow",alpha=0.4,
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )
    plt.text(0.58, 0.33, "- 71 studies", size=10, rotation=70., transform=plt.gca().transAxes,
             ha="right", va="top",
             bbox=dict(boxstyle="larrow",alpha=0.4, 
                       ec=(1., 0.5, 0.5),
                       fc=(1., 0.8, 0.8),
                       )
             )
    
    plt.ylabel('Number of studies')
    plt.title('Sparsity of Interventions - catalogued - most common 150')
    
    xticks = plt.gca().xaxis.get_major_ticks()
    mean = np.mean(y)
    print(mean)
    print(np.median(y))
    for i in range(len(xticks)):
        if i % 10 != 0:
            xticks[i].set_visible(False)
    plt.show()
    print(y[:75])
    print(names2[:75])
    
    print(len(names2))#batch of clean names
    allInterventions= names2.copy()
    for I in I_freeText:#add them all together to get biggest database on schizophrenia intervention names
        if I not in allInterventions:
            allInterventions.append(I)
    print(len(allInterventions))  
    
    allInterventions= [re.sub('\*', "", inter) for inter in allInterventions]
    allInterventions= [re.sub('}', "", inter) for inter in allInterventions]
    allInterventions= [re.sub('{', "", inter) for inter in allInterventions]
    print(len(allInterventions)) 
    print(allInterventions)
    
    chineseIntEng=[re.sub('(\[.+\])', '', i).strip() for i in allInterventions if re.search('(\[.+\])', i)]
    chinesePure= [re.sub('(.*)(\[)(.+)(\])', r'\3', i) for i in allInterventions if re.search('(\[.+\])', i)]
    
    noAddon=[re.sub('(.*)(\()(.+)(\))(.*)$', r'\1\5', i) if re.search('(\(.+\))', i) else i for i in allInterventions]#clean text in brackets
    Addons=[re.sub('(.*)(\()(.+)(\))', r'\3', i) for i in allInterventions if re.search('(\(.+\))', i)]
    print(len(noAddon))
    noAddon=[re.sub('(.*)(\()(.+)(\))(.*)$', r'\1\5', i) if re.search('(\(.+\))', i) else i for i in noAddon ]#clean text in brackets
    Addons2=[re.sub('(.*)(\()(.+)(\))', r'\3', i) for i in noAddon if re.search('(\(.+\))', i)]
    print(len(noAddon))
    noAddon=[re.sub('(.*)(\()(.+)(\))(.*)$', r'\1\5', i) if re.search('(\(.+\))', i) else i for i in noAddon]#clean text in brackets
    Addons3=[re.sub('(.*)(\()(.+)(\))', r'\3', i) for i in noAddon if re.search('(\(.+\))', i)]
    print(len(noAddon))#no terms in brackets anymore
    
    for interv in noAddon:
        for i in re.split('\s\+\s', interv):
            if i.strip() not in noAddon:
                print('added ' + i)
                noAddon.append(i.strip())
    print(len(noAddon))  
    
    newLists=[chineseIntEng, chinesePure, noAddon, ['(randomi[sz]ed|allocated) to']]
    exclusionList= ['study', 'chronic', 'intervention', '+', '', 'drugs', 'se', 'be', 'work', 'follow-up']
    
    I_master=[]
    for new in newLists:
        for interv in new:
            if ('(' in interv and not ')'in interv):#replace lonely brackets
                
                interv=interv.replace('(', '')
                
            if (')'in interv and not '('in interv):
                interv=interv.replace(')', '')
            interv= interv.strip().lower()    
            if interv not in I_master and interv not in exclusionList:
                I_master.append(interv)
    print(len(I_master)) 
    
    I_regexes=[]
    for i in I_master:
        if re.search('\+', i):
            
            i=(re.sub(r'\+', r'(\+|plus|and|added to|with)', i))##to allow for variations in expressing combined treatments
            
        if re.search(r'[Aa]nti(psychotic|depressant)\b', i):   
            i=(re.sub(r'([Aa]nti)(psychotic|depressant)', r'\1\2s?', i))#allow for common plurals
            
        if re.search(r'[Aa]nti(psychotics\?|depressants\?)( medications?|[Dd]rugs?)', i): #allow to omit additional info on drug
            i=(re.sub(r'([Aa]nti)(psychotics\?|depressants\?)( medications?|[Dd]rugs?)', r'\1\2(\3)?', i))
            
            
        if re.search(r'(tau)\b', i, re.IGNORECASE): #allow TAU
            i=(re.sub(r'(TAU|tau)(\b)', r'(\1|treatment as usual)', i))
            
        elif re.search(r'(treatment as usual)', i, re.IGNORECASE): #allow TAU
            i=(re.sub(r'([Tt]reatment [Aa]s [Uu]sual)', r'(\1|TAU)', i))
            print(i)       
            
        I_regexes.append(r'\b'+i+r'\b')
    print(len(I_regexes))    
        
    
