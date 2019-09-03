from gensim.models.keyedvectors import KeyedVectors




def makeTxt():
    """Procedure to build text file from binary embedding data


    Args:
        none

    """
    print('start')
    model = KeyedVectors.load_word2vec_format('\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\LSTM-PICO-Detection-master\\other_spyder\\Extended embeddings\\2019-07-19-09-34-51-bigrams_FINAL.bin', binary=True)#, limit = 20 for tests
    model.save_word2vec_format('\\\\smbhome.uscs.susx.ac.uk\\ls612\\Documents\\Dissertation\\Data\\extended.txt', binary=False)
    print('done creating text files')


#file = open('testfile.txt', 'w')
#file.write('Why? Because we can.')

#file.close()

makeTxt()



#if __name__ == "__makeTxt__":
    #main()
