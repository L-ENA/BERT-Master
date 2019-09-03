# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:23:40 2019

For making O annotations in abstracts

@author: ls612
"""

if __name__ ==  '__main__':
    import pickle
    import codecs
    import os
    import re
    ###############################functions
    def writeOut(sents, counts,tag, destination='annotated.txt', mode='single'):
        OUTPUT_DIR=os.getcwd()
        
        written=False#check if annotation was already made
        
        myOutput=[]
        if(mode=='single'):#add tag exclusively to top counting sentence
            for i, sent in enumerate(sents):
                if counts[i]==max(counts) and written==False and i>0:
                    #print('{}{}'.format(tag,sent))
                    written=True
                    myOutput.append('{}{}'.format(tag,sent))#write intervention tag
                else:
                    #print('wrote other sent')
                    myOutput.append(sent)
            
        else:####makes multiple annotations for this tag
            #print('writing out')
            
            for i, sent in enumerate(sents):  
                print(i)
                if counts[i]>1 and counts[i]>=max(counts)-1:
                    #print('{}{}'.format(tag,sent))
                    myOutput.append('{}{}'.format(tag,sent))#write intervention tag
                else:
                    #print(sent)
                    myOutput.append(sent)
                
        f = codecs.open(os.path.join(OUTPUT_DIR, destination), encoding='utf-8', mode='a')#write new file to current work directory   
        f.writelines(myOutput)    
        f.close()
        
        
      
    #####################################################OUTCOMES
    def matching_regex(myAb): 
        print(myAb)
        sents=[]
        counts=[]
        for x in myAb:
            x=str(x)
            
            if('###' in x):
                #writeOut(sents, counts, oTag, '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\O_abs.txt', mode='double')
                sents=[]
                counts=[]
                    
            sents.append(x)
            counts.append(0)
            for reg in O_regexes:
                #print(reg)
                if re.search(reg, x, re.IGNORECASE):
                    print(reg)
                    counts[-1]= counts[-1]+1#found intervention
            for reg in O_case:
                    
                if re.search(reg, x):#case sensitive because scale abbreviations like has will match wrong strings in lower case
                    print(reg)
                    counts[-1]= counts[-1]+1#found intervention    
        writeOut(sents, counts, oTag, '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\O_abs.txt' , mode='double')  
        print('{}{}'.format('Done ', oTag)) 
    ############################getting regexes
    ########participants, they contain some outcome info as well, these are potential adverse events as well as P tags
    e_events=['Akathisia',
     'Movement Disorders',
     'Parkinsonism',
     'Tardive Dyskinesia',
     'Amenorrhea',
     'Hypersalivation',
     'Abnormal Electrocardiogram',
     'Constipation',
     'Urinary Incontinence',
     'Extrapyramidal Symptoms',
     'Tremor',
     'Adverse Events',
     'Hepatic Dysfunction',
     'Bed Ulcer',
     'Polydipsia-Hyponatremia',
     'Hyperlipidemia',
     'Erectile Dysfunction',
     'Hyperprolactinemia',
     'Hyperhomocysteinemia',
     'Polydipsia',
     'Hyperglycemia',
     'Hyperprolinemia',
     'Dyskinesia',
     'Headache',
     'Deficit Syndrome',
     'Leucopenia',
     'Neutropenia',
     'Dyslipidemia',
     'Gastrointestinal Adverse Events']
    
    ############################################outcome data
    outc_ID = pickle.load(open("\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\pickles\\dict_tblOutcome.p", "rb"))
    raw= outc_ID.values()
    #print(len(raw))
    other=[i for i in raw if not re.search('\(|\)', i)]
    abbrev=[re.sub('(.+)(\()(.*)(\))(.*)?', r'\3', i).strip() for i in raw if re.search('(.+)(\(.*\))(.*)?', i)]#abbreviations in separate list
    long=[re.sub('(.+)(\()(.*)(\))(.*)?', r'\1\5', i).strip().lower() for i in raw if re.search('(.+)(\(.*\))(.*)?', i)]#written out part of the scales and abbreviations
    
    long=[re.sub(r'\s?\+\s?', '', i).strip() for i in long]#clean the + away
    abbrev=[re.sub(r'\s?\+\s?', '', i).strip() for i in abbrev]#clean the + away
    other=[re.sub(r'\s?\+\s?', '', i).strip() for i in other]#clean the + away
    
    newLists=[long, other, e_events]#add adverse event from participants section
    exclusionList= ['', 'work', 'study', 'schizophrenia', 'who', 'times']
    O_master=[]
    abbreviations=[]
    for new in newLists:
        for interv in new:
            #print(interv)
            if ('(' in interv and not ')'in interv):#replace lonely brackets
                interv=interv.replace('(', '')
            if (')'in interv and not '('in interv):
                interv=interv.replace(')', '')
            if ('[' in interv and not ']'in interv):#replace lonely brackets
                interv=interv.replace('[', '')
            if (']'in interv and not '['in interv):
                interv=interv.replace(']', '')
                
            interv= interv.strip().lower()    
            if interv not in O_master and interv not in exclusionList and len(interv) >2:
                O_master.append(interv)
                
    
    for interv in abbrev:
         #print(interv)
        if ('(' in interv and not ')'in interv):#replace lonely brackets
            
            interv=interv.replace('(', '')
        if (')'in interv and not '('in interv):
            
            interv=interv.replace(')', '')
        if ('[' in interv and not ']'in interv):#replace lonely brackets
            
            interv=interv.replace('[', '')
        if (']'in interv and not '['in interv):
            print(interv)
            interv=interv.replace(']', '')
                
        interv= interv.strip()    
        if interv not in abbreviations and interv not in exclusionList:
            abbreviations.append(interv)  
              
    #print(len(O_master)) 
    #print(len(abbreviations)) 
    
    wbound='\\b'
    O_regexes=['{}{}{}'.format(wbound, i, wbound) for i in O_master]
    O_case=['{}{}{}'.format(wbound, i, wbound) for i in abbreviations if len(i)>1]
    print(len(O_regexes))
    print(len(O_case))
    
#    oTag='MAIN OUTCOME MEASURES|O|'
#    pTag='SUBJECTS|P|'
#    iTag='INTERVENTION|I|'
#    #########################################get source file
#    fh=codecs.open('\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\abstractsO.txt','r',encoding='utf8')
#    lines=[line for line in fh]
#    #####################################
#    abstracts=[]
#    abstr=[]
#    
#    class abstract():
#        def __init__(self):
#            self.lines=[]
#            
#        def addline(self, line):
#            self.lines.append(line)
#        def deleteAll(self):
#            self.lines=[]
#            
#            
#    ab_filler= abstract()
#            
#    for line in lines:
#        #line=str(line)
#        if '###' in line:
#           abstracts.append(ab_filler.lines)#append previous abstract
#           ab_filler= abstract()#reset 
#           ab_filler.addline(line)#add first line of new abstract
#        else:
#           ab_filler.addline(line)#add some line
#    print(len(abstracts))
#         
#       
#    for ab in abstracts:
#        matching_regex(ab)
#     
#    print('finished')
    
#for ab in tester:
   # matching_regex(ab)
    #d=0   
