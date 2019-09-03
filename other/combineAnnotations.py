# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 16:31:40 2019

@author: ls612
"""
import codecs
import re
import random 
allAbs={}

###combine all tags
#sent=([], string) each abs consists of a list of tuples, where the first entry are tags of the sent, and second entry is the sent

pFile='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\Annotated full\\P_abstracts.txt'

f = codecs.open(pFile,encoding='utf-8', mode='r')
lines= f.readlines()#get all the lines. these lines are tab-separated, first entry is the bigram and third is the count 
f.close()

key=''

print(len(lines))
################################################have only one annotation

############################multiple:
###add P sents and create dict
for line in lines:
    if '###' in line:
        key=line.strip()
        allAbs[key]= []#make empty dict entry for this annotated abstract
    
    else:
    
        if key != '':
            allAbs[key].append(line)
            
            
            
print('Example abstract, only P annotation in abs ###148:')
for line in allAbs['###148:']:
    print(line)

             
############add O tAGS
oFile='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\Annotated full\\O_abs.txt'

f = codecs.open(oFile,encoding='utf-8', mode='r')#####GET THE LINES
lines= f.readlines()#get all the lines. these lines are tab-separated, first entry is the bigram and third is the count 
f.close()            

key='' 
for line in lines:
    if '###' in line:#recognise header
        key=line.strip().replace('\ufeff', '')
        counter=0
    else:
        if key != '':
            if 'MAIN OUTCOME MEASURES|O|' in line:
                try:
                    new = 'MAIN OUTCOME MEASURES|O|'+ allAbs[key][counter]#add tag to old sent
                    allAbs[key][counter]= new#set the updated line
                except:
                    print('Clash in abs {} line {} >> {}: \n {}'.format(key,counter, line,  allAbs[key]))
            counter += 1#keep count 


             
 ##################################################################Add I tags            
iFile='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\Annotated full\\Inew.txt'

f = codecs.open(iFile,encoding='utf-8', mode='r')#####GET THE LINES
lines= f.readlines()#get all the lines. these lines are tab-separated, first entry is the bigram and third is the count 
f.close()            

key='' 
for line in lines:
    if '###' in line:#recognise header
        key=line.strip().replace('\ufeff', '')
        counter=0
        
    else:
        if key != '':
            if 'INTERVENTION|I|' in line:
                try: 
                    new = 'INTERVENTION|I|'+ allAbs[key][counter]#add tag to old sent (append to the front)
                    allAbs[key][counter]= new#set the updated line
                except:
                    print('Clash in abs {} line {} >>({}): \n {}'.format(key,counter, line,  allAbs[key]))
            counter += 1#keep count 
            
print('Example abstract, all annotation in abs ###148:')
for line in allAbs['###148:']:
    print(line)        
####################simplify labels ###HEURISTICS     
 #Labels:                       
 #         
 
#labels=[#combining for pure tags
#        
#        ['MAIN OUTCOME MEASURES|O|INTERVENTION|I|SUBJECTS|P|','SUBJECTS|P|'],
#        ['INTERVENTION|I|MAIN OUTCOME MEASURES|O|SUBJECTS|P|','SUBJECTS|P|'],
#        
#        ['INTERVENTION|I|SUBJECTS|P|','SUBJECTS|P|'],
#        ['MAIN OUTCOME MEASURES|O|SUBJECTS|P|','SUBJECTS|P|'],
#        ['MAIN OUTCOME MEASURES|O|INTERVENTION|I|','INTERVENTION|I|'],
#        ['INTERVENTION|I|MAIN OUTCOME MEASURES|O|','INTERVENTION|I|'],
#        ['SUBJECTS|P|','SUBJECTS|P|'], 
#        ['INTERVENTION|I|','INTERVENTION|I|'],
#        ['MAIN OUTCOME MEASURES|O|','MAIN OUTCOME MEASURES|O|']
#        ]

labels=[#combining to yield pio combination tags
        
        ['MAIN OUTCOME MEASURES|O|INTERVENTION|I|SUBJECTS|P|','MAIN OUTCOME MEASURES+INTERVENTION+SUBJECTS|OIP|'],
        ['INTERVENTION|I|MAIN OUTCOME MEASURES|O|SUBJECTS|P|','MAIN OUTCOME MEASURES+INTERVENTION+SUBJECTS|OIP|'],
        
        ['INTERVENTION|I|SUBJECTS|P|','INTERVENTION+SUBJECTS|IP|'],
        ['MAIN OUTCOME MEASURES|O|SUBJECTS|P|','MAIN OUTCOME MEASURES+SUBJECTS|OP|'],
        ['MAIN OUTCOME MEASURES|O|INTERVENTION|I|','MAIN OUTCOME MEASURES+INTERVENTION|OI|'],
        ['INTERVENTION|I|MAIN OUTCOME MEASURES|O|','MAIN OUTCOME MEASURES+INTERVENTION|OI|'],
        ['SUBJECTS|P|','SUBJECTS|P|'], 
        ['INTERVENTION|I|','INTERVENTION|I|'],
        ['MAIN OUTCOME MEASURES|O|','MAIN OUTCOME MEASURES|O|']
        ]

#####9205:
###27742
for key, value in allAbs.items():#for each abstract
    for i, sent in enumerate(value):#for each sent in the abstract
        foundLabel=False#to check if label is assigned or if the NA label should be applied
        for lab in labels:#for each labelling possibility
            
            labKey, labVal = lab[0],lab[1]
            if labKey in sent:#check if label is there
                foundLabel=True
                sent = sent.replace(labKey, labVal)#replace combined label with shorter label
                allAbs[key][i]=sent#set new value
        
            
        if foundLabel==False and re.search('\w|[.]', sent):#no p i o tag, therefore a generic tag is applied to any line that contains words, since every sent needs to have a label
            sent = 'General|G|' + sent#label sent####make orig model compatible, otherwise use 'GENERAL|G|'
            allAbs[key][i]=sent#set new sent
            
            
                
print('Example abstract, combined all annotation in abs ###148:')###get examples
for line in allAbs['###148:']:
    print(line)         
    
print('Nr of abstracts before selection' + str(len(allAbs.keys())))

selectedAbs= {}
unqualifiedAbs={}
chineseAbs={}
for key, value in allAbs.items():
    p=False
    i=False
    o=False
    whites=0
    chinese=False
    
    for sent in value:
        if re.search(u'[\u4e00-\u9fff]', sent):
            chinese=True
            sent = ' '#no permanent change, just for identification purposes (only want to count picos in english text so I need to make sure that it finds nothing in following lines)
            ##print(sent)
            
        if re.search('(\|P\|)|(\|IP\|)|(\|OIP\|)|(\|OP\|)', sent):
            p=True
            
        if re.search('(\|I\|)|(\|IP\|)|(\|OIP\|)|(\|OI\|)', sent):
            i=True
            
        if re.search('(\|O\|)|(\|OI\|)|(\|OIP\|)|(\|OP\|)', sent):
            o=True
        
        if re.search('^\s$', sent):
            whites += 1
            
    if len(value)-whites >=3 and o ==True and p==True and i==True and chinese==False:#states inclusion criteria: abstract needs to have all picos and be longer than 1 (some meerkat abstracts seem to be 1 line summaries, maybe translated from chinese)
        selectedAbs[key]=value#transfer the qualified abstract
    
    elif chinese==True:
        chineseAbs[key]=value#save chinese abstracts
        if len(value)-whites >=2 and p==True and i==True and o ==True:#if remaining english text is pico complete
            val = [se for se in value if not re.search(u'[\u4e00-\u9fff]', se)]#select non-chinese sents
            selectedAbs[key]=val#use non-chinese sents
            #print(val)
    else:
        unqualifiedAbs[key]=value#can manually add tags if required, or analyse why those are excluded (mostly chinese text that had annotations here and there but not pico complete)
 
keyList = list(selectedAbs.keys())
num = len(keyList) 
frac = int(num/10)      
print('Nr of abstracts after selection' + str(num))    

    
        
random.shuffle(keyList)#shuffle, does not return anything

dev=keyList[:frac]#split key lists 
test=keyList[frac:frac*2]
train=keyList[frac*2:]

print(len(dev))
print(len(test))
print(len(train))
##############################################################################################write out to text files
tr = codecs.open('\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\TrainMeerkat.txt',encoding='utf-8', mode='w')

for key in train:
    tr.write(key+'\n')###write abstract to training file
    tr.writelines(selectedAbs[key])
tr.close()

tes = codecs.open('\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\TestMeerkat.txt',encoding='utf-8', mode='w')

for key in test:
    tes.write(key+'\n')###write abstract to training file
    tes.writelines(selectedAbs[key])
tes.close()

dv = codecs.open('\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\Dev.txt',encoding='utf-8', mode='w')

for key in dev:
    dv.write(key+'\n')###write abstract to training file
    dv.writelines(selectedAbs[key])
dv.close()

exclude = codecs.open('\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\ExcludedMeerkat.txt',encoding='utf-8', mode='w')

for key in unqualifiedAbs.keys():
    exclude.write(key+'\n')###write abstract to training file
    exclude.writelines(unqualifiedAbs[key])
exclude.close()

chinese = codecs.open('\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\splitted\\meerkatFinalAlltags\\ChineseMeerkat.txt',encoding='utf-8', mode='w')

for key in chineseAbs.keys():
    chinese.write(key+'\n')###write abstract to training file
    chinese.writelines(chineseAbs[key])
chinese.close()
    
#lines= f.readlines()#get all the lines. these lines are tab-separated, first entry is the bigram and third is the count 
#f.close()         