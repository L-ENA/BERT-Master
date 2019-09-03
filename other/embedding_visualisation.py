# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 14:56:14 2019

This code was mostly adapted from:
    https://towardsdatascience.com/google-news-and-leo-tolstoy-visualizing-word2vec-word-embeddings-with-t-sne-11558d8bd4d
    
@author: ls612
"""




from gensim.models import Word2Vec
from gensim.models import KeyedVectors
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

import random
random.seed(222)

def tsne_plot_3d(title, label, embeddings, a=1):
    fig = plt.figure()
    ax = Axes3D(fig)
    #colors = cm.rainbow(np.linspace(0, 1, 1))
    plt.scatter(embeddings[:, 0], embeddings[:, 1], embeddings[:, 2], c='r', alpha=a, label=label)
    plt.legend(loc=4)
    plt.title(title)
    for ii in range(0,360,60):
        ax.view_init(elev=30., azim=ii)
        plt.savefig("3ds\\movie%d.png" % ii)
    plt.show()
    
def tsne_plot_similar_words(title, labels, embedding_clusters, word_clusters, a, filename=None):
    plt.figure(figsize=(16, 9))
    colors = cm.rainbow(np.linspace(0, 1, len(labels)))
    for label, embeddings, words, color in zip(labels, embedding_clusters, word_clusters, colors):
        x = embeddings[:, 0]
        y = embeddings[:, 1]
        plt.scatter(x, y, c=color, alpha=a, label=label)
        for i, word in enumerate(words):
            plt.annotate(word, alpha=0.5, xy=(x[i], y[i]), xytext=(5, 2),
                         textcoords='offset points', ha='right', va='bottom', size=8)
    plt.legend(loc=4)
    plt.title(title)
    plt.grid(True)
    if filename:
        plt.savefig(filename, format='png', dpi=150, bbox_inches='tight')
    plt.show()
    
def tsne_plot_2d(label, embeddings, words=[], a=1):
    plt.figure(figsize=(16, 9))
    colors = cm.rainbow(np.linspace(0, 1, 1))
    x = embeddings[:,0]
    y = embeddings[:,1]
    plt.scatter(x, y, c=colors, alpha=a, label=label)
    for i, word in enumerate(words):
        plt.annotate(word, alpha=0.3, xy=(x[i], y[i]), xytext=(5, 2), 
                     textcoords='offset points', ha='right', va='bottom', size=10)
    plt.legend(loc=4)
    plt.grid(True)
    plt.savefig("hhh.png", format='png', dpi=150, bbox_inches='tight')
    plt.show()


    
    
def evalModel(myModel, whichM='new emb'):
    evals=myModel.accuracy('w2vEVAL.txt')#evaluate on general purpose set
    
    sections=[domain['section'] for domain in evals] #compile results and print them
    accuracy=[]
    for domain in evals:
        try:
            accuracy.append(len(domain['correct'])/(len(domain['correct'])+ len(domain['incorrect'])))
        except:
            accuracy.append(0)  
    
    print('-------------------------------EVALUATION {} --------------------------------'.format(whichM))#print closest words for this model
    print(sorted(set(zip(accuracy,sections))))
    words=['trial' , 'schizophrenia' , 'Seroquel' , 'seroquel', 'positive-symptom' , 'quetiapine' , 'antipsychotic' , 'extrapyramidal' , 'PANSS','panss', 'PANSS' 'flu', 'linux', 'aardvark', 'dapper']
    similar_words=[]
    for search_term in words:
        try:
            similar_words.append(str({search_term: [item[0] for item in (myModel.wv.most_similar([search_term], topn=5))]}))
        except:
            similar_words.append('Word not found')
    
    print(similar_words)
    
def visualise(myModel, types='2d_similar', num=20000):
    if types=='2d_similar':
        keys = ['antipsychotic' , 'trial' , 'schizophrenia' , 'quetiapine' , 'aardvark', 'extrapyramidal' , 'PANSS', 'efficacy', 'Seroquel', 'positive-symptom',  'diabetes']
    #######################################################getting similar words and their embeddings
        embedding_clusters = []
        word_clusters = []
        for word in keys:
            embeddings = []
            words = []
            for similar_word, _ in myModel.most_similar(word, topn=15):
                words.append(similar_word)
                embeddings.append(myModel[similar_word])
                
            embedding_clusters.append(embeddings)
            word_clusters.append(words)
            ##########################dimensionality reduction
        embedding_clusters = np.array(embedding_clusters)
        n, m, k = embedding_clusters.shape
        tsne_model_en_2d = TSNE(perplexity=15, n_components=2, init='pca', n_iter=3500, random_state=32)
        embeddings_en_2d = np.array(tsne_model_en_2d.fit_transform(embedding_clusters.reshape(n * m, k))).reshape(n, m, 2)
        tsne_plot_similar_words('Similar words from my model', keys, embeddings_en_2d, word_clusters, 0.7, 'similar_words.png')
        
    elif types=='2d_all':
        words_all = []
        embeddings_all = []
        
        words= random.sample(list(myModel.wv.vocab), num)
        for word in words:
            embeddings_all.append(myModel.wv[word])
            words_all.append(word)
        print('Chose {} random vectors'.format(num))    
        tsne_ak_2d = TSNE(perplexity=30, n_components=2, init='pca', n_iter=3500, random_state=32)
        embeddings_all_2d = tsne_ak_2d.fit_transform(embeddings_all)
        print('Plotting the reduced vectors')
        tsne_plot_2d('All words in 2d embedding', embeddings_all_2d, a=0.1)
    elif types=='3d_all':
        words_all = []
        embeddings_all = []
        
        words= random.sample(list(myModel.wv.vocab), num)
        for word in words:
            embeddings_all.append(myModel.wv[word])
            words_all.append(word)
        print('Chose {} random vectors'.format(num))    
        tsne_all_3d = TSNE(perplexity=30, n_components=3, init='pca', n_iter=1000, random_state=32)
        embeddings_all_3d = tsne_all_3d.fit_transform(embeddings_all)
        print('Plotting the reduced vectors')
        tsne_plot_3d('Embedding dimensionality reduction to 3D', 'Original embedding', embeddings_all_3d, a=0.1)
    
        
#oldModelLocation= "C:\\Users\\ls612\\wikipedia-pubmed-and-PMC-w2v.bin"
#modelOld = KeyedVectors.load_word2vec_format(oldModelLocation , binary=True)
print('Visualising...')
visualise(modelOld, types='3d_all')    

#newModelLocation= "\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\LSTM-PICO-Detection-master\\other_spyder\\2019-07-18-11-29-04bigrams_norm.bin"
#modelNew = KeyedVectors.load_word2vec_format(newModelLocation , binary=True, unicode_errors='ignore')    
#evalModel(modelNew)

#visualise(modelNew)
        
#print('Loading model...')
#latestModelLocation= "\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\LSTM-PICO-Detection-master\\other_spyder\\bigrams_FINAL.bin"
#modelLatest = KeyedVectors.load_word2vec_format(latestModelLocation ,binary=True, unicode_errors='ignore')    
#print('Visualising...')
#visualise(modelLatest, types='3d_all')    