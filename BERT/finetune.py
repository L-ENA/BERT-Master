# -*- coding: utf-8 -*-
"""finetune.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JOCOVooO9mIYGelrVfMeh_8-DIMS5t_d
"""

from google.colab import drive
drive.mount('/content/drive')
!pip install bert
!rm -rf bert
!pip install bert-tensorflow
import tensorflow as tf
import os
import collections
import pandas as pd

import tensorflow_hub as hub
from datetime import datetime

import bert
from bert import run_classifier
from bert import optimization
from bert import tokenization
from bert import modeling


from google.colab import drive
drive.mount('/content/drive')

!git clone https://github.com/google-research/bert
import sys
sys.path.append('bert/')
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import codecs

import json
import re

import pprint
import numpy as np
TPU_ADDRESS=''
####################set tpu adress
#assert 'COLAB_TPU_ADDR' in os.environ, 'ERROR: Not connected to a TPU runtime; please see the first cell in this notebook for instructions!'
#TPU_ADDRESS = 'grpc://' + os.environ['COLAB_TPU_ADDR']
#print('TPU address is', TPU_ADDRESS)

#from google.colab import auth
#auth.authenticate_user()
#with tf.Session(TPU_ADDRESS) as session:
#  print('TPU devices:')
#  pprint.pprint(session.list_devices())
#
#  # Upload credentials to TPU.
#  with open('/content/adc.json', 'r') as f:
#    auth_info = json.load(f)
#  tf.contrib.cloud.configure_gcs(session, credentials=auth_info)
#  # Now credentials are set for all future sessions on this TPU.

######Bert models from git
#BERT_MODEL = 'uncased_L-12_H-768_A-12'
#BERT_PRETRAINED_DIR = 'gs://cloud-tpu-checkpoints/bert/' + BERT_MODEL
#print('***** BERT pretrained directory: {} *****'.format(BERT_PRETRAINED_DIR))
#!gsutil ls $BERT_PRETRAINED_DIR

###############################################scibert further pretrained model
#Bert from drive
#BERT_MODEL = 'uncased_L-12_H-768_A-12'
BERT_PRETRAINED_DIR = '/content/drive/My Drive/scibert_scivocab_uncased'
#print('***** BERT pretrained directory: {} *****'.format(BERT_PRETRAINED_DIR))
#!gsutil ls $BERT_PRETRAINED_DIR

###############################################Finetuned on basis of normal bert
#Bert from drive
##BERT_MODEL = 'uncased_L-12_H-768_A-12'
#BERT_PRETRAINED_DIR = '/content/drive/My Drive/finetunedJinBase/output'
#print('***** BERT pretrained directory: {} *****'.format(BERT_PRETRAINED_DIR))

#BERT_MODEL = 'uncased_L-12_H-768_A-12'###when uing finetuned from base
#BERT_BASE = 'gs://cloud-tpu-checkpoints/bert/' + BERT_MODEL

#BERT_BASE='/content/drive/My Drive/scibert_scivocab_uncased'#use this when using scibert as base

#!gsutil ls $BERT_BASE

import os
import collections
import pandas as pd
import tensorflow as tf
import tensorflow_hub as hub
from datetime import datetime
import numpy as np

import sklearn.utils
import logging
from imp import reload




####################################################################PARAMS####SETUP
MAX_SEQ_LENGTH = 64#128 orig


# Compute train and warmup steps from batch size
# These hyperparameters are copied from this colab notebook (https://colab.sandbox.google.com/github/tensorflow/tpu/blob/master/tools/colab/bert_finetuning_with_cloud_tpus.ipynb)
BATCH_SIZE = 32#32
LEARNING_RATE = 2e-5#2-5
NUM_TRAIN_EPOCHS = 1.0

# Warmup is a period of time where hte learning rate 
# is small and gradually increases--usually helps training.
WARMUP_PROPORTION = 0.1
# Model configs
SAVE_CHECKPOINTS_STEPS = 1000
SAVE_SUMMARY_STEPS = 500

NUM_TPU_CORES = 8#not using tpu, but variable needs to exist and needs to be passed, then gpu is used automatically




#######Data settings
ID = 'id'##the id
DATA_COLUMN = 'comment_text'#the sent
#LABEL_COLUMNS = ['toxic','severe_toxic','obscene','threat','insult','identity_hate']#label prose
#LABEL_COLUMNS = ['P','I','O', 'A','M','R','C']
LABEL_COLUMNS = ['P','I','O', 'G']

TRAIN_VAL_RATIO = 0.9#for creating train and dev sets
LEN = train.shape[0]#get nr of rows/ shape is rows*columns

SIZE_TRAIN = int(TRAIN_VAL_RATIO*LEN)

###########################Only testing or using all data?
TRAIN_MINI=False#use unly subaset od data while developing model and testing stuff
NR_TRAIN=150
NR_TEST=50

#################MOde
#MODE = 'EVAL'
MODE='FINETUNE'
##########################
#LOAD='PRETRAINED'#where to load data from? git, pretrained or somewhere else when training different layers
LOAD='PRETRAINED'
if LOAD=='GIT':#use original vocab and config file from github when using the finetuned models
  BERT_VOCAB= BERT_BASE + '/vocab.txt'#Contains model vocabulary [ words to indexes mapping]
  BERT_CONFIG = BERT_BASE + '/bert_config.json'
  BERT_INIT_CHKPNT = BERT_PRETRAINED_DIR + '/model.ckpt-3585'
  
elif LOAD=='PRETRAINED':
  BERT_CONFIG = BERT_PRETRAINED_DIR + '/bert_config.json'
  BERT_VOCAB= BERT_PRETRAINED_DIR + '/vocab.txt'#Contains model vocabulary [ words to indexes mapping]
  BERT_INIT_CHKPNT = BERT_PRETRAINED_DIR + '/bert_model.ckpt'
  
elif LOAD=='MYBERT':
  BERT_CONFIG = BERT_PRETRAINED_DIR + '/bert_config.json'
  BERT_VOCAB= BERT_PRETRAINED_DIR + '/vocab.txt'#Contains model vocabulary [ words to indexes mapping]
  #BERT_INIT_CHKPNT = BERT_PRETRAINED_DIR + '/bert_model.ckpt'
  BERT_INIT_CHKPNT ='/content/drive/My Drive/cszgBert2/output/model.ckpt-5480'



#trainDat = '/content/drive/My Drive/dataframes/dfTRAINjin.df'##original csv files from toxic comment example
#devDat = '/content/drive/My Drive/dataframes/dfDEVjin.df'
#testDat = '/content/drive/My Drive/dataframes/dfTESTjin.df'

trainDat = '/content/drive/My Drive/dataframes/sampledCombined/TRAIN.p'
devDat = '/content/drive/My Drive/dataframes/sampledCombined/DEV.p'
testDat = '/content/drive/My Drive/dataframes/sampledCombined/TEST.p'

OUTPUT_DIR = "/content/drive/My Drive/bothBert"#new checkpoints go there

#################Logger setup
reload(logging)

LOG_FILENAME = os.path.join(OUTPUT_DIR, 'BERTlog.txt')#make sure output dir exists. otherwise this throws an error


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename=LOG_FILENAME,
                    filemode='a')
logging.info('------------------------------------------------------------------------------------------------------NEW Finetune')
logging.info('Finetuning bert')

logging.info('MAX_SEQ_LENGTH {}, BATCH_SIZE {}, LEARNING_RATE {}, NUM_TRAIN_EPOCHS {}, OUTPUT_DIR {}'.format(MAX_SEQ_LENGTH, BATCH_SIZE, LEARNING_RATE, NUM_TRAIN_EPOCHS, OUTPUT_DIR))
######################################################################################################get the data

print(BERT_INIT_CHKPNT)
print(BERT_VOCAB)
print(BERT_CONFIG)

class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, labels=None):
        """Constructs a InputExample.

        Args:
            guid: Unique id for the example.
            text_a: string. The untokenized text of the first sequence. For single
            sequence tasks, only this sequence must be specified.
            text_b: (Optional) string. The untokenized text of the second sequence.
            Only must be specified for sequence pair tasks.
            labels: (Optional) [string]. The label of the example. This should be
            specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.labels = labels


class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, segment_ids, label_ids, is_real_example=True):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_ids = label_ids,
        self.is_real_example=is_real_example
        
def create_examples(df, labels_available=True, nr_labels=4):#col
    """ Reads input df and gives examples in the right formant
    Creates examples for the training and dev sets."""
    examples = []
    for (i, row) in enumerate(df.values):
        guid = row[0]
        text_a = row[1]
        if labels_available:
            labels = row[2:]
        else:
            #labels = [0,0,0,0,0,0,0]
            labels = [0,0,0,0]
        examples.append(
            InputExample(guid=guid, text_a=text_a, labels=labels))
    return examples

###########################################
def convert_examples_to_features(examples,  max_seq_length, tokenizer):
    """Loads a data file into a list of `InputBatch`s."""

    features = []
    for (ex_index, example) in enumerate(examples):
        print(example.text_a)
        tokens_a = tokenizer.tokenize(example.text_a)

        tokens_b = None
        if example.text_b:
            tokens_b = tokenizer.tokenize(example.text_b)
            # Modifies `tokens_a` and `tokens_b` in place so that the total
            # length is less than the specified length.
            # Account for [CLS], [SEP], [SEP] with "- 3"
            _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
        else:
            # Account for [CLS] and [SEP] with "- 2"
            if len(tokens_a) > max_seq_length - 2:
                tokens_a = tokens_a[:(max_seq_length - 2)]

        # The convention in BERT is:
        # (a) For sequence pairs:
        #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
        #  type_ids: 0   0  0    0    0     0       0 0    1  1  1  1   1 1
        # (b) For single sequences:
        #  tokens:   [CLS] the dog is hairy . [SEP]
        #  type_ids: 0   0   0   0  0     0 0
        #
        # Where "type_ids" are used to indicate whether this is the first
        # sequence or the second sequence. The embedding vectors for `type=0` and
        # `type=1` were learned during pre-training and are added to the wordpiece
        # embedding vector (and position vector). This is not *strictly* necessary
        # since the [SEP] token unambigiously separates the sequences, but it makes
        # it easier for the model to learn the concept of sequences.
        #
        # For classification tasks, the first vector (corresponding to [CLS]) is
        # used as as the "sentence vector". Note that this only makes sense because
        # the entire model is fine-tuned.
        tokens = ["[CLS]"] + tokens_a + ["[SEP]"]
        segment_ids = [0] * len(tokens)

        if tokens_b:
            tokens += tokens_b + ["[SEP]"]
            segment_ids += [1] * (len(tokens_b) + 1)

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding = [0] * (max_seq_length - len(input_ids))
        input_ids += padding
        input_mask += padding
        segment_ids += padding

        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length
        
        labels_ids = []
        for label in example.labels:
            labels_ids.append(int(label))

        if ex_index < 0:
            print("*** Example ***")
            print("guid: %s" % (example.guid))
            print("tokens: %s" % " ".join(
                    [str(x) for x in tokens]))
            print("input_ids: %s" % " ".join([str(x) for x in input_ids]))
            print("input_mask: %s" % " ".join([str(x) for x in input_mask]))
            print(
                    "segment_ids: %s" % " ".join([str(x) for x in segment_ids]))
            print("label: %s (id = %s)" % (example.labels, labels_ids))

        features.append(
                InputFeatures(input_ids=input_ids,
                              input_mask=input_mask,
                              segment_ids=segment_ids,
                              label_ids=labels_ids))
    return features

def create_model(bert_config, is_training, input_ids, input_mask, segment_ids,
                 labels, num_labels, use_one_hot_embeddings):
    """Creates a classification model."""
    model = modeling.BertModel(
        config=bert_config,
        is_training=is_training,
        input_ids=input_ids,
        input_mask=input_mask,
        token_type_ids=segment_ids,
        use_one_hot_embeddings=use_one_hot_embeddings)

    # In the demo, we are doing a simple classification task on the entire
    # segment.
    #
    # If you want to use the token-level output, use model.get_sequence_output()
    # instead.
    output_layer = model.get_pooled_output()

    hidden_size = output_layer.shape[-1].value

    output_weights = tf.get_variable(
        "output_weights", [num_labels, hidden_size],
        initializer=tf.truncated_normal_initializer(stddev=0.02))

    output_bias = tf.get_variable(
        "output_bias", [num_labels], initializer=tf.zeros_initializer())

    with tf.variable_scope("loss"):
        if is_training:
            # I.e., 0.1 dropout
            output_layer = tf.nn.dropout(output_layer, keep_prob=0.9)

        logits = tf.matmul(output_layer, output_weights, transpose_b=True)
        logits = tf.nn.bias_add(logits, output_bias)
        ######################################################################################
        modePred ='x'
        if modePred =='threshold':
            # probabilities = tf.nn.softmax(logits, axis=-1) ### multiclass case
            probabilities = tf.nn.sigmoid(logits)#### multi-label case

            ####make predictions wrt threshold
            def multi_label_hot(prediction, threshold=0.2):
                print('Making predictions now ----------------------------------------------')
                #prediction = tf.cast(prediction, tf.float32)
                threshold = float(threshold)
                return tf.cast(tf.greater(prediction, threshold), tf.int64)
            probabilities= multi_label_hot(probabilities)#not actually probability anymore
            
        elif modePred =='max':
            #probabilities = tf.nn.softmax(logits, axis=-1) ### multiclass case
            probabilities = tf.nn.sigmoid(logits)#### multi-label case

            ####make predictions wrt threshold
            def single_label_hot(a):
                print(a)
                a = tf.cast(a, tf.float32)
                one_hot = tf.one_hot(
                    tf.argmax(a), 
                    4, ######number of label dimensions
                    on_value=1.0,
                    off_value=0.0)# num classes
                
                return one_hot
            probabilities= single_label_hot(probabilities)#not actually probability anymore    
            
        else:##get simply probabilities
            probabilities = tf.nn.sigmoid(logits)
            
        #######################################################################################
        labels = tf.cast(labels, tf.float32)
        tf.logging.info("num_labels:{};logits:{};labels:{}".format(num_labels, logits, labels))
        per_example_loss = tf.nn.sigmoid_cross_entropy_with_logits(labels=labels, logits=logits)
        loss = tf.reduce_mean(per_example_loss)

        # probabilities = tf.nn.softmax(logits, axis=-1)
        # log_probs = tf.nn.log_softmax(logits, axis=-1)
        #
        # one_hot_labels = tf.one_hot(labels, depth=num_labels, dtype=tf.float32)
        #
        # per_example_loss = -tf.reduce_sum(one_hot_labels * log_probs, axis=-1)
        # loss = tf.reduce_mean(per_example_loss)

        return (loss, per_example_loss, logits, probabilities)



def input_fn_builder(features, seq_length, is_training, drop_remainder):
  """Creates an `input_fn` closure to be passed to TPUEstimator."""

  all_input_ids = []
  all_input_mask = []
  all_segment_ids = []
  all_label_ids = []

  for feature in features:
    all_input_ids.append(feature.input_ids)
    all_input_mask.append(feature.input_mask)
    all_segment_ids.append(feature.segment_ids)
    all_label_ids.append(feature.label_ids)

  def input_fn(params):
    """The actual input function."""
    batch_size = params["batch_size"]

    num_examples = len(features)

    # This is for demo purposes and does NOT scale to large data sets. We do
    # not use Dataset.from_generator() because that uses tf.py_func which is
    # not TPU compatible. The right way to load data is with TFRecordReader.
    d = tf.data.Dataset.from_tensor_slices({
        "input_ids":
            tf.constant(
                all_input_ids, shape=[num_examples, seq_length],
                dtype=tf.int32),
        "input_mask":
            tf.constant(
                all_input_mask,
                shape=[num_examples, seq_length],
                dtype=tf.int32),
        "segment_ids":
            tf.constant(
                all_segment_ids,
                shape=[num_examples, seq_length],
                dtype=tf.int32),
        "label_ids":
            tf.constant(all_label_ids, shape=[num_examples, 4], dtype=tf.int32),################manually set to 6, change later!!
    })

    if is_training:
      d = d.repeat()
      d = d.shuffle(buffer_size=100)

    d = d.batch(batch_size=batch_size, drop_remainder=drop_remainder)
    return d

  return input_fn

class PaddingInputExample(object):
    """Fake example so the num input examples is a multiple of the batch size.
    When running eval/predict on the TPU, we need to pad the number of examples
    to be a multiple of the batch size, because the TPU requires a fixed batch
    size. The alternative is to drop the last batch, which is bad because it means
    the entire output data won't be generated.
    We use this class instead of `None` because treating `None` as padding
    battches could cause silent errors.
    """
    
def convert_single_example(ex_index, example, max_seq_length,
                           tokenizer):
    """Converts a single `InputExample` into a single `InputFeatures`."""

    if isinstance(example, PaddingInputExample):
        return InputFeatures(
            input_ids=[0] * max_seq_length,
            input_mask=[0] * max_seq_length,
            segment_ids=[0] * max_seq_length,
            label_ids=0,
            is_real_example=False)

    tokens_a = tokenizer.tokenize(str(example.text_a))
    tokens_b = None
    if example.text_b:
        tokens_b = tokenizer.tokenize(example.text_b)

    if tokens_b:
        # Modifies `tokens_a` and `tokens_b` in place so that the total
        # length is less than the specified length.
        # Account for [CLS], [SEP], [SEP] with "- 3"
        _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
    else:
        # Account for [CLS] and [SEP] with "- 2"
        if len(tokens_a) > max_seq_length - 2:
            tokens_a = tokens_a[0:(max_seq_length - 2)]

    # The convention in BERT is:
    # (a) For sequence pairs:
    #  tokens:   [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
    #  type_ids: 0     0  0    0    0     0       0 0     1  1  1  1   1 1
    # (b) For single sequences:
    #  tokens:   [CLS] the dog is hairy . [SEP]
    #  type_ids: 0     0   0   0  0     0 0
    #
    # Where "type_ids" are used to indicate whether this is the first
    # sequence or the second sequence. The embedding vectors for `type=0` and
    # `type=1` were learned during pre-training and are added to the wordpiece
    # embedding vector (and position vector). This is not *strictly* necessary
    # since the [SEP] token unambiguously separates the sequences, but it makes
    # it easier for the model to learn the concept of sequences.
    #
    # For classification tasks, the first vector (corresponding to [CLS]) is
    # used as the "sentence vector". Note that this only makes sense because
    # the entire model is fine-tuned.
    tokens = []
    segment_ids = []
    tokens.append("[CLS]")
    segment_ids.append(0)
    for token in tokens_a:
        tokens.append(token)
        segment_ids.append(0)
    tokens.append("[SEP]")
    segment_ids.append(0)

    if tokens_b:
        for token in tokens_b:
            tokens.append(token)
            segment_ids.append(1)
        tokens.append("[SEP]")
        segment_ids.append(1)

    input_ids = tokenizer.convert_tokens_to_ids(tokens)

    # The mask has 1 for real tokens and 0 for padding tokens. Only real
    # tokens are attended to.
    input_mask = [1] * len(input_ids)

    # Zero-pad up to the sequence length.
    while len(input_ids) < max_seq_length:
        input_ids.append(0)
        input_mask.append(0)
        segment_ids.append(0)

    assert len(input_ids) == max_seq_length
    assert len(input_mask) == max_seq_length
    assert len(segment_ids) == max_seq_length

    labels_ids = []
    for label in example.labels:
        try:
            labels_ids.append(int(label))
        except:
            print('Caught broken label: ' + str(label))
            labels_ids.append(0)


    feature = InputFeatures(
        input_ids=input_ids,
        input_mask=input_mask,
        segment_ids=segment_ids,
        label_ids=labels_ids,
        is_real_example=True)
    return feature


def file_based_convert_examples_to_features(
        examples, max_seq_length, tokenizer, output_file):
    """Convert a set of `InputExample`s to a TFRecord file."""

    writer = tf.python_io.TFRecordWriter(output_file)

    for (ex_index, example) in enumerate(examples):
        if ex_index % 10000 == 0:
            tf.logging.info("Writing example %d of %d" % (ex_index, len(examples)))
            print("Writing example %d of %d" % (ex_index, len(examples)))

        feature = convert_single_example(ex_index, example,max_seq_length, tokenizer)

        def create_int_feature(values):
            f = tf.train.Feature(int64_list=tf.train.Int64List(value=list(values)))
            return f

        features = collections.OrderedDict()
        features["input_ids"] = create_int_feature(feature.input_ids)
        features["input_mask"] = create_int_feature(feature.input_mask)
        features["segment_ids"] = create_int_feature(feature.segment_ids)
        features["is_real_example"] = create_int_feature(
            [int(feature.is_real_example)])
        ##############################################multiple ids or single label? 
        if isinstance(feature.label_ids, list):
            label_ids = feature.label_ids
        else:
            label_ids = feature.label_ids[0]
            
        features["label_ids"] = create_int_feature(label_ids)

        tf_example = tf.train.Example(features=tf.train.Features(feature=features))
        writer.write(tf_example.SerializeToString())
    writer.close()


def file_based_input_fn_builder(input_file, seq_length, is_training,
                                drop_remainder,numLabs=4):
    """Creates an `input_fn` closure to be passed to TPUEstimator."""

    name_to_features = {
        "input_ids": tf.FixedLenFeature([seq_length], tf.int64),
        "input_mask": tf.FixedLenFeature([seq_length], tf.int64),
        "segment_ids": tf.FixedLenFeature([seq_length], tf.int64),
        "label_ids": tf.FixedLenFeature([numLabs], tf.int64),
        "is_real_example": tf.FixedLenFeature([], tf.int64),
    }

    def _decode_record(record, name_to_features):
        """Decodes a record to a TensorFlow example."""
        example = tf.parse_single_example(record, name_to_features)

        # tf.Example only supports tf.int64, but the TPU only supports tf.int32.
        # So cast all int64 to int32.
        for name in list(example.keys()):
            t = example[name]
            if t.dtype == tf.int64:
                t = tf.to_int32(t)
            example[name] = t

        return example

    def input_fn(params):
        """The actual input function."""
        batch_size = params["batch_size"]

        # For training, we want a lot of parallel reading and shuffling.
        # For eval, we want no shuffling and parallel reading doesn't matter.
        d = tf.data.TFRecordDataset(input_file)
        if is_training:
            d = d.repeat()
            d = d.shuffle(buffer_size=100)

        d = d.apply(
            tf.contrib.data.map_and_batch(
                lambda record: _decode_record(record, name_to_features),
                batch_size=batch_size,
                drop_remainder=drop_remainder))

        return d

    return input_fn


def _truncate_seq_pair(tokens_a, tokens_b, max_length):
    """Truncates a sequence pair in place to the maximum length."""

    # This is a simple heuristic which will always truncate the longer sequence
    # one token at a time. This makes more sense than truncating an equal percent
    # of tokens from each, since if one sequence is very short then each token
    # that's truncated likely contains more information than a longer sequence.
    while True:
        total_length = len(tokens_a) + len(tokens_b)
        if total_length <= max_length:
            break
        if len(tokens_a) > len(tokens_b):
            tokens_a.pop()
        else:
            tokens_b.pop()    
   


def model_fn_builder(bert_config, num_labels, init_checkpoint, learning_rate,
                     num_train_steps, num_warmup_steps, use_tpu,
                     use_one_hot_embeddings):
    """Returns `model_fn` closure for TPUEstimator."""
    print('building model...')
    
    def model_fn(features, labels, mode, params):  # pylint: disable=unused-argument
        """The `model_fn` for TPUEstimator."""

        #tf.logging.info("*** Features ***")
        #for name in sorted(features.keys()):
        #    tf.logging.info("  name = %s, shape = %s" % (name, features[name].shape))
        print('in model fn')
        input_ids = features["input_ids"]
        input_mask = features["input_mask"]
        segment_ids = features["segment_ids"]
        label_ids = features["label_ids"]
        is_real_example = None
        if "is_real_example" in features:
             is_real_example = tf.cast(features["is_real_example"], dtype=tf.float32)
        else:
             is_real_example = tf.ones(tf.shape(label_ids), dtype=tf.float32)

        is_training = (mode == tf.estimator.ModeKeys.TRAIN)

        (total_loss, per_example_loss, logits, probabilities) = create_model(
            bert_config, is_training, input_ids, input_mask, segment_ids, label_ids,
            num_labels, use_one_hot_embeddings)

        tvars = tf.trainable_variables()
        ####################################################define which variables to train. This basically selects the vars by name
        #tvars = [v for v in tvars if re.search(r'^((?!(layer\_[89])).)*$',v.name)]#use negative lookarounds to exclude variable layers 8 and 9
        #tvars = [v for v in tvars if re.search(r'(layer\_[89])|embeddings|pooler',v.name)]#use layers 8 and 9 plus update pooling and embdeding
        
        ################################
        initialized_variable_names = {}
        scaffold_fn = None#tf.train.Scaffold()
        print(type(scaffold_fn))
        print(init_checkpoint)
        if init_checkpoint:
            (assignment_map, initialized_variable_names
             ) = modeling.get_assignment_map_from_checkpoint(tvars, init_checkpoint)
            if use_tpu:

                def tpu_scaffold():
                    print('using tpu')
                    tf.train.init_from_checkpoint(init_checkpoint, assignment_map)
                    return tf.train.Scaffold()

                scaffold_fn = tpu_scaffold
            else:
                tf.train.init_from_checkpoint(init_checkpoint, assignment_map)

        print("**** Trainable Variables ****")
        
       # print(len(tvars))
        for var in tvars:
            init_string = ""
            if var.name in initialized_variable_names:
                init_string = ", *INIT_FROM_CKPT*"
                #print("  name = %s, shape = %s%s", var.name, var.shape,init_string)

        output_spec = None
        if mode == tf.estimator.ModeKeys.TRAIN:

            train_op = optimization.create_optimizer(
                total_loss, learning_rate, num_train_steps, num_warmup_steps, use_tpu)

            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                loss=total_loss,
                train_op=train_op,
                scaffold=scaffold_fn)
        elif mode == tf.estimator.ModeKeys.EVAL:

            def metric_fn(per_example_loss, label_ids, probabilities, is_real_example):
                ######
                eval_dict = {}
                #predictions = tf.argmax(logits, axis=-1, output_type=tf.int32)
                accuracy = tf.metrics.accuracy(
                     labels=label_ids, predictions=probabilities, weights=is_real_example)
                
                label_ids = tf.cast(label_ids, dtype=tf.int64)
                probabilities= tf.cast(probabilities, dtype=tf.int64)
                print(label_ids)
                print(probabilities)
               # metric1 = tf.metrics.precision_at_k(label_ids, probabilities, 1, class_id=0)
                #metric2 = tf.metrics.precision_at_k(label_ids, probabilities, 1, class_id=1)
                #metric3 = tf.metrics.precision_at_k(label_ids, probabilities, 1, class_id=2)
                
                loss = tf.metrics.mean(values=per_example_loss, weights=is_real_example)
                

                return {
                    "eval_accuracy": accuracy,
                    #"prec1": metric1,
                    #"prec2": metric2,
                    #"prec3": metric3,
                    "eval_loss": loss,
                }  
                #####ORIGINAL
                #logits_split = tf.split(probabilities, num_labels, axis=-1)
                #label_ids_split = tf.split(label_ids, num_labels, axis=-1)
                # metrics change to auc of every class
                #eval_dict = {}
                #for j, logits in enumerate(logits_split):
                    #label_id_ = tf.cast(label_ids_split[j], dtype=tf.int32)
                    #current_auc, update_op_auc = tf.metrics.auc(label_id_, logits)
                    #eval_dict[str(j)] = (current_auc, update_op_auc)
                #eval_dict['eval_loss'] = tf.metrics.mean(values=per_example_loss)
                return eval_dict

                ## original eval metrics
                # predictions = tf.argmax(logits, axis=-1, output_type=tf.int32)
                # accuracy = tf.metrics.accuracy(
                #     labels=label_ids, predictions=predictions, weights=is_real_example)
                # loss = tf.metrics.mean(values=per_example_loss, weights=is_real_example)
                # return {
                #     "eval_accuracy": accuracy,
                #     "eval_loss": loss,
                # }

            eval_metrics = metric_fn(per_example_loss, label_ids, probabilities, is_real_example)
            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                loss=total_loss,
                eval_metric_ops=eval_metrics,
                scaffold=scaffold_fn)
        else:
            print("mode:", mode,"probabilities:", probabilities)
            output_spec = tf.estimator.EstimatorSpec(
                mode=mode,
                predictions={"probabilities": probabilities},
                scaffold=scaffold_fn)
        return output_spec

    return model_fn        

def create_output(predictions, columns):
    probabilities = []
    
    for (i, prediction) in enumerate(predictions):
        preds = prediction["probabilities"]
        probabilities.append(preds)
        
    dff = pd.DataFrame(probabilities)
    dff.columns = columns
    
    return dff

train = pd.read_pickle(trainDat).dropna()#yhis was necessary when getting data from csvs, but probably not needed when importing from the dataframes

##print(train.head())
dev = pd.read_pickle(devDat).dropna()
train = pd.concat([train,dev])#for convenience, and to make sure that different runs have different examples
train = sklearn.utils.shuffle(train)#optional shuffle



test = pd.read_pickle(testDat).dropna()

if TRAIN_MINI:####use this to test training with small samples (only during development)
    test = test.sample(n=NR_TEST)
    train = train.sample(n=NR_TRAIN)#optional reduction of df for testing/development
##print(train.head())





x_train = train[:SIZE_TRAIN]
x_val = train[SIZE_TRAIN:]

# Use the InputExample class from BERT's run_classifier code to create examples from the data
train_examples = create_examples(x_train)



print('all: {} -- train: {} -- val: {}'.format(train.shape, x_train.shape, x_val.shape))
logging.info('all: {} -- train: {} -- val: {}'.format(train.shape, x_train.shape, x_val.shape))

###########################################################Create the tokeniser obj and other objs
bert_config = modeling.BertConfig.from_json_file(BERT_CONFIG)#load config file

tokenization.validate_case_matches_checkpoint(True,BERT_INIT_CHKPNT)
tokenizer = tokenization.FullTokenizer(
      vocab_file=BERT_VOCAB, do_lower_case=True)

run_config = tf.estimator.RunConfig(#assign some config values like directory or amount of saved checkpoints
    model_dir=OUTPUT_DIR,
    save_summary_steps=SAVE_SUMMARY_STEPS,
    keep_checkpoint_max=1,
    save_checkpoints_steps=SAVE_CHECKPOINTS_STEPS)

# Compute # train and warmup steps from batch size
num_train_steps = int(len(train_examples) / BATCH_SIZE * NUM_TRAIN_EPOCHS)
num_warmup_steps = int(num_train_steps * WARMUP_PROPORTION)



train_file = os.path.join(OUTPUT_DIR, "train.tf_record")
#filename = Path(train_file)
if not os.path.exists(train_file):
    open(train_file, 'w').close()


###########################################################
logging.info('Converting train examples to features')   
if MODE=='FINETUNE':
  file_based_convert_examples_to_features(train_examples, MAX_SEQ_LENGTH, tokenizer, train_file)#store examples in file. here multiple/single label has to be changed
logging.info("***** Training phase *****")
logging.info("  Num examples = {}".format(len(train_examples)))
logging.info("  Batch size =  {}".format(BATCH_SIZE))
logging.info("  Num steps = {}".format(num_train_steps))



train_input_fn = file_based_input_fn_builder(
    input_file=train_file,
    seq_length=MAX_SEQ_LENGTH,
    is_training=True,
    drop_remainder=True)


RESULTS_DIR = os.path.join(OUTPUT_DIR, 'output')
## Specify outpit directory and number of checkpoint steps to save
##run_config = tf.estimator.tpu.RunConfig(
##    model_dir=RESULTS_DIR,
##    save_summary_steps=SAVE_SUMMARY_STEPS,
##    keep_checkpoint_max=1,
##    save_checkpoints_steps=SAVE_CHECKPOINTS_STEPS)

is_per_host = tf.contrib.tpu.InputPipelineConfig.PER_HOST_V2
tpu_cluster_resolver = tf.contrib.cluster_resolver.TPUClusterResolver(TPU_ADDRESS)
run_config = tf.contrib.tpu.RunConfig(
    model_dir=RESULTS_DIR,
    save_summary_steps=SAVE_SUMMARY_STEPS,
    keep_checkpoint_max=1,
    save_checkpoints_steps=SAVE_CHECKPOINTS_STEPS,
    cluster=tpu_cluster_resolver,
    tpu_config=tf.contrib.tpu.TPUConfig(
          
          num_shards=NUM_TPU_CORES,
          per_host_input_for_training=is_per_host))
print(len(LABEL_COLUMNS))
model_fn = model_fn_builder(
  bert_config=bert_config,
  num_labels= len(LABEL_COLUMNS),
  init_checkpoint=BERT_INIT_CHKPNT,
  learning_rate=LEARNING_RATE,
  num_train_steps=num_train_steps,
  num_warmup_steps=num_warmup_steps,
  use_tpu=False,
  use_one_hot_embeddings=False)

estimator = tf.estimator.Estimator(
  model_fn=model_fn,
  config=run_config,
  params={"batch_size": BATCH_SIZE})

##########################Train

if MODE=='FINETUNE':###finetune and evaluate
    print(f'Beginning Training!')
    logging.info('Running training')
    current_time = datetime.now()
    estimator.train(input_fn=train_input_fn, max_steps=num_train_steps)
    print("Training took time ", datetime.now() - current_time)
    logging.info("Training took time ", datetime.now() - current_time)

    eval_file = os.path.join(OUTPUT_DIR, "eval.tf_record")
    #filename = Path(train_file)
    if not os.path.exists(eval_file):
        open(eval_file, 'w').close()

    eval_examples = create_examples(x_val)
    file_based_convert_examples_to_features(eval_examples, MAX_SEQ_LENGTH, tokenizer, eval_file)

    eval_steps = None

    eval_drop_remainder = False
    eval_input_fn = file_based_input_fn_builder(
        input_file=eval_file,
        seq_length=MAX_SEQ_LENGTH,
        is_training=False,
        drop_remainder=False)

    result = estimator.evaluate(input_fn=eval_input_fn, steps=eval_steps)
    print(result.keys())
    output_eval_file = os.path.join(OUTPUT_DIR, "eval_results.txt")
    with tf.gfile.GFile(output_eval_file, "w") as writer:
        tf.logging.info("***** Eval results *****")###tf.logging.info("***** Eval results *****")
        logging.info("***** Eval results *****")
        for key in sorted(result.keys()):
            tf.logging.info("  %s = %s", key, str(result[key]))
            logging.info("  %s = %s", key, str(result[key]))
            writer.write("%s = %s\n" % (key, str(result[key])))
        


x_test = test #testing a small sample
x_test = x_test.reset_index(drop=True)
predict_examples = create_examples(x_test,False)#first step: get data that is to be tested



test_features = convert_examples_to_features(predict_examples, MAX_SEQ_LENGTH, tokenizer)#create bert friendlly input

print('Beginning Predictions!')
logging.info('Beginning Predictions!')
current_time = datetime.now()

predict_input_fn = input_fn_builder(features=test_features, seq_length=MAX_SEQ_LENGTH, is_training=False, drop_remainder=False)
predictions = estimator.predict(predict_input_fn)
print("Prediction took time ", datetime.now() - current_time)
#logging.info("Prediction took time ", datetime.now() - current_time)

output_df = create_output(predictions, LABEL_COLUMNS)
output_df.to_pickle(os.path.join(OUTPUT_DIR, 'predictionsCSZG.df'))#save predictions

merged_df =  pd.concat([x_test, output_df], axis=1)
#print(merged_df[['comment_text']])
#submission = merged_df.drop(['comment_text'], axis=1)#drop orig sent data
merged_df.to_csv(os.path.join(OUTPUT_DIR, "resultsCSZG.csv"), index=False)
logging.info('merged df:')
for i in range(6):
    logging.info(str(merged_df.loc[i].to_csv(header=None, index=False).strip('\n').split('\n')))
merged_df.head()

from google.colab import drive
drive.mount('/content/drive')

output_df.to_csv(os.path.join(OUTPUT_DIR, 'predCSZG.csv'))
#output_df.to_pickle(os.path.join(OUTPUT_DIR, 'predictions.df'))#save predictions
print(output_df.head())

print(len(LABEL_COLUMNS))