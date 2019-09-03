from model.data_utils import Dataset, getWeights
from model.models import HANNModel
from model.config import Config
import argparse
import re
#########################graph for using ORIGINAL model architecture (pure p i o tags)!!!!!!!!

parser = argparse.ArgumentParser()

def main():
    # create instance of config
    print('x')
    
    config = Config(parser)
    #config.lossParam = 'weights'##not using weights for now
    
    # build model
    model = HANNModel(config)
    model.build()
    print('x')
    ###############################################comment this if model is trained from scratch
    config.restore = True
    if config.restore:
        model.restore_session("\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\newEmbedding\\model.weights") # optional, restore weights
   # model.reinitialize_weights("proj")#reinitialise for this scope
    #####################################################################
    print('x')
    # create datasets
    dev   = Dataset(config.filename_dev, config.processing_word,
                         config.processing_tag, config.max_iter)
    train = Dataset(config.filename_train, config.processing_word,
                         config.processing_tag, config.max_iter)
    test  = Dataset(config.filename_test, config.processing_word,
                         config.processing_tag, config.max_iter)

    
#    if config.lossParam == 'weights':
#        weights=getWeights(train)
#        wList=[[w] for w in weights ]
#        
#        model.class_weight = wList
#        print(model.class_weight)
#        print('Using balanced class weights')
        ##gives self.loss as Tensor("add_5:0", shape=(), dtype=float32)
    
    #train model
    #model.train(train, dev)

    # evaluate model
    #model.evaluate(test)
    testNewData(test, config, model)
    
################################################################schiz data evaluation and visualisation    
#    
#    parser = argparse.ArgumentParser()
#
#def main():
#    # create instance of config
#    print('x')
#    
#    config = Config(parser)
#
#    # build model
#    model = HANNModel(config)
#    model.build()
#    print('x')
#    ###############################################comment this if model is trained from scratch
#    config.restore = True
#    if config.restore:
#        model.restore_session("\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\output\\model.weights") # optional, restore weights
#   # model.reinitialize_weights("proj")#reinitialise for this scope
#    #####################################################################
#    print('x')
#    # create datasets
#    dev   = Dataset(config.filename_dev, config.processing_word,
#                         config.processing_tag, config.max_iter)
#    train = Dataset(config.filename_train, config.processing_word,
#                         config.processing_tag, config.max_iter)
#    test  = Dataset(config.filename_test, config.processing_word,
#                         config.processing_tag, config.max_iter)
#    
#    
#    schizData = Dataset(config.filename_schiz, config.processing_word,
#                         config.processing_tag, config.max_iter)
#    testNewData(schizData, config, model)
#    
def testNewData(test, config, model):###method to visualise model predictions
    from model.data_utils import minibatches
    sentences = []
    picos=[]
    labs = []
    labs_pred = []
    for words, labels in minibatches(test, config.batch_size):
        labels_pred, document_lengths = model.predict_batch(words)
        for lList in labels:
            for l in lList:
                labs.append(config.tag_decode[l])#decode label
        
        for abstract in words:
            for sentence in abstract:
                prose= ' '.join(config.vocab_decode[w] for w in sentence)#decode from embedding indexes and join back as sentence
                sentences.append(prose)
                 
        for absTags in labels_pred:
            for tag in absTags:
                picos.append(config.tag_decode[tag])    #decode tag    
    
    truePreds=[]
    falsePreds=[]            
    for i, pico in enumerate(picos):    
        if labs[i] == pico and re.search('P|I|O', pico):#a correctly predicted pico
            
            truePreds.append('Predicted {} (True label is {}){}{}'.format(pico,labs[i],'-->' , sentences[i]))
        elif labs[i] != pico and re.search('P|I|O', labs[i]):  #an incorrectly predicted pico
            falsePreds.append('Predicted {} (True label is {}){}{}'.format(pico,labs[i],'-->' , sentences[i]))
            
#    maxi=100
#    count=0 
#    print('-----------False--------------')       
#    for pred in falsePreds:
#        if count<maxi:
#            print(pred)
#            count += 1
#            count = 0   
#            
#    count=0         
#    print('-----------TRUE--------------')
#    for pred in truePreds:
#        if count<maxi:
#            print(pred)
#            count += 1    
            
    #selection= falsePreds[200:]
    for sel in falsePreds:
        if re.search('Predicted I',sel):
            print(sel)
            
        
            
               
    
    #print(schizData)                    
   # for x in test:
       # print(x)
    # train model
    #model.train(train, dev)

    # evaluate model
    #model.evaluate(schizData)

    ###################################prediction
    #a,b = model.predict_batch([[3, 76,890,2334,567,6534,8765,2345], [689,45,27998,43,568,36],[45788,35,864,954,86],[247857,398,43,27,86,47],[85479,543,5,26,8,21],[4675, 543,87,1,67]])
    #['To test the efficacy of a pregnancy adapted version of an existing @ ICBT-program for depression as well as assessing acceptability and adherence DESIGN : Randomised controlled trial .','Online and telephone .','Self-referred pregnant women ( gestational week @ at intake ) currently suffering from major depressive disorder .','@ pregnant women ( gestational week @ ) with major depression were randomised to either treatment as usual ( TAU ) provided at their antenatal clinic or to ICBT as an add-on to usual care .', 'The primary outcome was depressive symptoms measured with the Montgomery-sberg depression rating scale-self report ( MADRS-S ) .', 'The Edinburgh Postnatal Depression Scale and measures of anxiety and sleep were used .', 'The ICBT group had significantly lower levels of depressive symptoms', 'post treatment ( p < @ , Hedges g = @ ) and were more likely to be responders ( i.e. achieve a statistically reliable improvement ) ( RR = @ ; p = @ ) .', 'Measures of treatment credibility , satisfaction , utilization , and adherence were comparable to implemented ICBT for depression .', 'Pregnancy adapted ICBT for antenatal depression is feasible , acceptable and efficacious .', 'These results need to be replicated in larger trials to validate these promising findings .'])
    #a= model.predict(['Schizophrenic', 'patients','were','randomized','to','either','chlorpromazine','or','CBT'])
    #(['@ hospitalised patients with acute exacerbations of chronic and subchronic schizophrenia were randomized to receive chlorpromazine or \' Seroquel \' titrated from an initial dose of @ mg/day to a maximum of @ mg/day in a @-week , multicentre , double-blind study .',
#'Efficacy data showed \' Seroquel \' to be comparable to chlorpromazine .',
#'Patients tolerated \' Seroquel \' well ; there were no acute dystonic reactions or agranulocytosis and the incidence of extrapyramidal effects was low .',
#'( \' Seroquel \' Trial @ / @ ) .',
#'This work has been published elsewhere - see AN : @ .'])
    
    #print(a)
    #print(b)
if __name__ == "__main__":
    main()
