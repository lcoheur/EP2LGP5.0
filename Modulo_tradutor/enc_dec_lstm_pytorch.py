from __future__ import unicode_literals, print_function, division
from io import open
import unicodedata
import string
import re
import random
import time
import math

import spacy
import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import matplotlib.ticker as ticker
import numpy as np

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class Encoder(nn.Module):
    def __init__(self, vocab_len, embedding_dim, hidden_dim, n_layers, dropout_prob):
        super().__init__()
 
        self.embedding = nn.Embedding(vocab_len, embedding_dim)
        self.rnn = nn.LSTM(embedding_dim, hidden_dim, n_layers, dropout=dropout_prob)
 
        self.dropout = nn.Dropout(dropout_prob)
 
    def forward(self, input_batch):
        embed = self.dropout(self.embedding(input_batch))
        outputs, (hidden, cell) = self.rnn(embed)
 
        return hidden, cell
    
class OneStepDecoder(nn.Module):
    def __init__(self, input_output_dim, embedding_dim, hidden_dim, n_layers, dropout_prob):
        super().__init__()
        # self.input_output_dim will be used later
        self.input_output_dim = input_output_dim
 
        self.embedding = nn.Embedding(input_output_dim, embedding_dim)
        self.rnn = nn.LSTM(embedding_dim, hidden_dim, n_layers, dropout=dropout_prob)
        self.fc = nn.Linear(hidden_dim, input_output_dim)
        self.dropout = nn.Dropout(dropout_prob)
 
    def forward(self, target_token, hidden, cell):
        target_token = target_token.unsqueeze(0)
        embedding_layer = self.dropout(self.embedding(target_token))
        output, (hidden, cell) = self.rnn(embedding_layer, (hidden, cell))
 
        linear = self.fc(output.squeeze(0))
 
        return linear, hidden, cell
    
class Decoder(nn.Module):
    def __init__(self, one_step_decoder, device):
        super().__init__()
        self.one_step_decoder = one_step_decoder
        self.device=device
 
    def forward(self, target, hidden, cell):
        target_len, batch_size = target.shape[0], target.shape[1]
        target_vocab_size = self.one_step_decoder.input_output_dim
        # Store the predictions in an array for loss calculations
        predictions = torch.zeros(target_len, batch_size, target_vocab_size).to(self.device)
        # Take the very first word token, which will be sos
        input = target[0, :]
        
        # Loop through all the time steps
        for t in range(target_len):
            predict, hidden, cell = self.one_step_decoder(input, hidden, cell)
 
            predictions[t] = predict
            input= predict.argmax(1)        
        
        return predictions
    
class EncoderDecoder(nn.Module):
    def __init__(self, encoder, decoder):
        super().__init__()
 
        self.encoder = encoder
        self.decoder = decoder        
 
    def forward(self, source, target):
        
        hidden, cell = self.encoder(source)
        outputs= self.encoder(target, hidden, cell)
                    
        return outputs
    
def get_datasets():
	# Download the language files
	spacy_de = spacy.load('pt')
	spacy_en = spacy.load('pt')
 
	# define the tokenizers
	def tokenize_de(text):
		return [token.text for token in spacy_de.tokenizer(text)][::-1]

	def tokenize_en(text):
		return [token.text for token in spacy_en.tokenizer(text)]
 
	# Create the pytext's Field
	Source = Field(tokenize=tokenize_de, init_token='<sos>', eos_token='<eos>', lower=True)
	Target = Field(tokenize=tokenize_en, init_token='<sos>', eos_token='<eos>', lower=True)
 
	# Splits the data in Train, Test and Validation data
	train_data, valid_data, test_data = Multi30k.splits(exts=('.de', '.en'), fields=(Source, Target))
 
	# Build the vocabulary for both the language
	Source.build_vocab(train_data, min_freq=3)
	Target.build_vocab(train_data, min_freq=3)
 
	# Set the batch size
	BATCH_SIZE = 128
 
	# Create the Iterator using builtin Bucketing
	train_iterator, valid_iterator, test_iterator = BucketIterator.splits((train_data, valid_data, test_data), 
	                                                                      batch_size=BATCH_SIZE, 
	                                                                      sort_within_batch=True,
	                                                                      sort_key=lambda x: len(x.src),
	                                                                      device=device)
	return train_iterator,valid_iterator,test_iterator,Source,Target
