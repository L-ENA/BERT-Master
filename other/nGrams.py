import tqdm
import pickle
import math
from gensim.models import Word2Vec
from gensim.models import KeyedVectors

path='\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\LSTM-PICO-Detection-master\\other_spyder\\2-grams\\2-grams-2013.tsv'

f = open(path, 'r')
lines= f.readlines()#get all the lines. these lines are tab-separated, first entry is the bigram and third is the count 
f.close()

print('Number of unique bigrams: {}'.format(len(lines)))#how many bigrams are included
print(lines[7700000])#some exaple

oldModelLocation= "C:\\Users\\ls612\\wikipedia-pubmed-and-PMC-w2v.bin"
modelOld = KeyedVectors.load_word2vec_format(oldModelLocation , binary=True)        
additionalKeys=list(modelOld.wv.vocab.keys())

splitted = [line.split('\t') for line in lines]#get bigram data into list, to make it easy to select just the bigram and its count
sentDict={entry[0]: entry[2] for entry in tqdm.tqdm(splitted)}

###we want to recreate vocabulary for the old model, so we only need frequency counts for those vocab. 
lookup={word:0 for word in additionalKeys}#make dict to look up if a word is in the keyed vectors: this works thousands time faster (373647 vs. 41 iterations per second) than looking it up in multi-million length list

print(len(sentDict.items()))
wordlist=[]
for key, value in tqdm.tqdm(sentDict.items()):
    content= key.split(' ')#thats how bigrams were separated
    try:#this list will simulate the corpus, so we only add words that actually have a trained vector already... otherwise my extended embedding will have lots of vectors with random initialisation that can't be trained with the new training data because they don't appear
        
        a= lookup[content[0]]#just a quick unelegant way to ckeck if the words have a valid embedding. if lookup for any content part fails, error is caught and word is not added 
        b= lookup[content[1]]
        for i in range(math.ceil(int(value)/2)):#make wordlists that represent bigram frequency, but takes  care that list does not get too long by dividing through 2. would divide through 3 if it were trigrams since each word in bigram appears in one other bigram in a sentence, but not twice in a sentence ('i' 'am' 'at')
            wordlist.append(content)#eg if bigram count for ['hello' , 'world'] is 4, this adds the sentence ['hello','world'] twice to sent list.
            
    except:
        a=0#not pretty or useful, but fast switching to next key
               
#        
print('Number of valid sentence lists containing bigrams: {}'.format(len(wordlist)))  
print(wordlist[115986615])

with open('bigramFrequencies.p', 'wb') as f:#save the sent list. 
    pickle.dump(wordlist, f)
