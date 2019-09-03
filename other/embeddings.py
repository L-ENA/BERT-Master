# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 14:56:14 2019

@author: ls612
"""
from gensim.models import Word2Vec
from gensim.models import KeyedVectors
import pickle
import logging
from imp import reload


####################################LOGGER setup
reload(logging)
LOG_FILENAME = r'0608.txt'


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=LOG_FILENAME,
                    filemode='a')
logging.info('------------------------------------------------------------------------------------------------------NEW RUN')
logging.info('Creating new embedding')
###########################################################################functions
class SentIterator(object):#a memory friendlier iterator (compared with loading all split sents at once)
    def __init__(self, location, adKeys):
        
        #self.sentList= [[word.lower() for word in sent] for sent in pickle.load(open(location, 'rb'))]#original embeddings have no lowercasing
        #self.bigSentList= [[word.lower() for word in sent] for sent in pickle.load(open(location, 'rb'))]
        self.sentList= pickle.load(open(location, 'rb'))#original embeddings have no lowercasing
        self.bigSentList= pickle.load(open(location, 'rb'))
        self.bigrams= pickle.load(open('bigramFrequencies.p', 'rb'))
        print(self.sentList[12])
        self.additionalKeys=adKeys
        self.useAdditional= False
        self.stop_words = ['I','(',')','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','what','which','who','whom','this','that','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','only','own','same','so','than','too','very','can','will','just','should','now',',']
        self.n=5
        self.ret=[]#final list of sentences
        
        for sent in self.additionalKeys:
            self.bigSentList.append(sent)
            
            
        for sent in self.bigSentList:
            #keys= [word for word in sent if word not in self.stop_words]
            self.ret.append(sent)#add sentence from input file
            
        for sent in self.bigrams:   #give bigrams to simulate frequncies for huffman tree
            self.ret.append(sent)
        
    def __iter__(self):
        #for fname in os.listdir(self.dirname):
            #for line in open(os.path.join(self.dirname, fname)):
                #yield line.split()
        if self.useAdditional == True:#to build vocab with pretrained keys, needs to return lists representing a sentnce
            for sent in self.ret:    
                yield sent
            
        else:       
            for sent in self.sentList:#give training data sentences, without stopwords
                y= [word for word in sent if word not in self.stop_words]
                yield y
#             

def evalModel(myModel):
    evals=myModel.accuracy('w2vEVAL.txt')#evaluate on general purpose set
    
    sections=[domain['section'] for domain in evals] #compile results and print them
    accuracy=[]
    for domain in evals:
        try:
            accuracy.append(len(domain['correct'])/(len(domain['correct'])+ len(domain['incorrect'])))
        except:
            accuracy.append(0)  
    logging.info('General evaluation task:')
    logging.info(sorted(set(zip(accuracy,sections))))#####evaluate this model
    print('-------------------------------EVALUATION--------------------------------')
    print(sorted(set(zip(accuracy,sections))))
    words=['trial' , 'schizophrenia' , 'Seroquel' , 'seroquel', 'positive-symptom' , 'quetiapine' , 'antipsychotic' , 'extrapyramidal' , 'PANSS','panss', 'PANSS' 'flu', 'linux', 'aardvark', 'dapper']
    similar_words=[]
    for search_term in words:
        try:
            similar_words.append(str({search_term: [item[0] for item in (myModel.wv.most_similar([search_term], topn=5))]}))
        except:
            similar_words.append('Word not found')
    logging.info('Word similarity task:')
    logging.info(similar_words)
    print(similar_words)
    
########################################################################################################Recreate and train    
modelList=[]


sentLocation= '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\abstractsTokenized.p'
oldModelLocation= "\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\wikipedia-pubmed-and-PMC-w2v.bin"
modelOld = KeyedVectors.load_word2vec_format(oldModelLocation , binary=True)
additionalKeys=list(modelOld.wv.vocab.keys())
print('Nr of unique vocab in old model: {}'.format(len(additionalKeys)))
l = [additionalKeys[i:i + 15] for i in range(0, len(additionalKeys), 15)]#split into even lists 
data = SentIterator(sentLocation, l)

   
####################################PART 0: LOAD EXISTING MODEL and evaluate it


logging.info('Evaluation of original model:')
evalModel(modelOld)
#
#
###########################PART 1: GET THE ADDITIONAL VOCABULARY
######### a list of lists, where each sublist consists of a tokenised sentence: [['this', 'is', 'the', 'first', 'sentence', 'for', 'word2vec'], [.., .. , .. , .. , ..]]
sentLocation= '\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Code\\abstractsTokenized.p'
   

logging.info('Adding keys: ' + str(len(additionalKeys)))

data.useAdditional= True
#############################PART 2: Param description of original model
##word2vec was run using the skip-gram model with a window size of 5, 
##hierarchical softmax training, 
##and a frequent word subsampling threshold of 0.001 to create 200-dimensional vectors.
#
softmax=1#use hierarchical softmax
skipgram=1#use skipgram
win=5#window size
dims=200#dimensions
subsamples= 0.001#downsampling param
minc= 0 #ignore words with lesser counts
parallelise=4#amount of workers
total_iters= 6
batchSize= 150
lock=1.0
lr_init=0.005#0.025 is default, make smaller because we are only fine tuning
min_alpha=0.0001#unchanged default value

logging.info('>>>>>>>>>PARAMS  (without stopw., with extra bigrams, normal cases) <<<<<<< minc: {}, iters: {}, batchsize: {}, lock: {}, alpha: {}'.format(minc, total_iters, batchSize, lock, lr_init))
##################################PART3: create, train and evaluate new model
NewModel = Word2Vec(window=win, size=dims,sample= subsamples, min_count=minc, workers=parallelise, hs=softmax, sg=skipgram, batch_words=batchSize, alpha=lr_init)
#
NewModel.build_vocab(data)
total_examples = NewModel.corpus_count
logging.info('Nr of words in new corpus : {}'.format(total_examples))
#
NewModel.intersect_word2vec_format(oldModelLocation, binary=True, lockf=lock)#combine vocabs. Unlock them by parameter, so that they can be changed: lockf
#
#
totalKeys=list(NewModel.wv.vocab.keys())
print('Nr of unique vocab in old model: {}'.format(len(totalKeys)))
####################TRAIN and EVALUATE
data.useAdditional= False
NewModel.train(data, total_examples=total_examples, epochs=total_iters)
total_examples = NewModel.corpus_count
logging.info('Nr of words in new corpus after training : {}'.format(total_examples))
name='bigrams_FINAL.txt'
##
##modelList.append(NewModel)   
##############################################################################save model
#try:
    
    #NewModel.wv.save_word2vec_format(name, binary=False)
#except:
   # print('not enough space on disk')
    
logging.info('Evaluating model after {} epochs'.format(total_iters))
evalModel(NewModel)
logging.info('Finished training and evaluating')