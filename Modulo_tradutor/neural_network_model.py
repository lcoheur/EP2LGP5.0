import string
import numpy as np

from keras.preprocessing.text import Tokenizer
from keras_preprocessing.sequence import pad_sequences
from keras.models import Model
from keras.layers import LSTM, Input, TimeDistributed, Dense, Activation, RepeatVector, Embedding
from keras.optimizers import Adam
from keras.losses import sparse_categorical_crossentropy
from keras.callbacks import EarlyStopping
from keras.callbacks import ModelCheckpoint

# Path to translation file
path_to_data = 'new_training_file.txt'

# Read file
translation_file = open(path_to_data,"r", encoding='utf-8') 
raw_data = translation_file.read()
translation_file.close()

# Parse data
raw_data = raw_data.split('\n')
pairs = [sentence.split('\t') for sentence in raw_data]
pairs = pairs[1000:20000]

def clean_sentence(sentence):
    # Lower case the sentence
    lower_case_sent = sentence.lower()
    # Strip punctuation
    string_punctuation = string.punctuation + "¡" + '¿'
    clean_sentence = lower_case_sent.translate(str.maketrans('', '', string_punctuation))
   
    return clean_sentence


def tokenize(sentences):
    # Create tokenizer
    text_tokenizer = Tokenizer()
    # Fit texts
    text_tokenizer.fit_on_texts(sentences)
    return text_tokenizer.texts_to_sequences(sentences), text_tokenizer

# Clean sentences
pt_sentences = [pair[0] for pair in pairs]
lgp_sentences = [pair[1] for pair in pairs]

# Tokenize words
pt_text_tokenized, pt_text_tokenizer = tokenize(pt_sentences)
lgp_text_tokenized, lgp_text_tokenizer = tokenize(lgp_sentences)

print('Maximum length pt sentence: {}'.format(len(max(pt_text_tokenized,key=len))))
print('Maximum length lgp sentence: {}'.format(len(max(lgp_text_tokenized,key=len))))

# Check language length
pt_vocab = len(pt_text_tokenizer.word_index) + 1
lgp_vocab = len(lgp_text_tokenizer.word_index) + 1

print("PT vocabulary is of {} unique words".format(pt_vocab))
print("LGP vocabulary is of {} unique words".format(lgp_vocab))

max_pt_len = int(len(max(pt_text_tokenized,key=len)))
max_lgp_len = int(len(max(lgp_text_tokenized,key=len)))

pt_pad_sentence = pad_sequences(pt_text_tokenized, max_pt_len, padding = "post")
lgp_pad_sentence = pad_sequences(lgp_text_tokenized, max_lgp_len, padding = "post")

# Reshape data
pt_pad_sentence = pt_pad_sentence.reshape(*pt_pad_sentence.shape, 1)
lgp_pad_sentence = lgp_pad_sentence.reshape(*lgp_pad_sentence.shape, 1)

# Create the Encoder
input_sequence = Input(shape=(max_pt_len,))
embedding = Embedding(input_dim=pt_vocab, output_dim=128,)(input_sequence)
encoder = LSTM(64, return_sequences=False)(embedding)
r_vec = RepeatVector(max_lgp_len)(encoder)

# Create the Decoder
decoder = LSTM(64, return_sequences=True, dropout=0.2)(r_vec)
logits = TimeDistributed(Dense(lgp_vocab))(decoder)

# Create the Encoder Decoder
enc_dec_model = Model(input_sequence, Activation('softmax')(logits))
enc_dec_model.compile(loss=sparse_categorical_crossentropy,
              optimizer=Adam(1e-3),
              metrics=['accuracy'])

enc_dec_model.summary()

checkpoint_filepath = 'saved_model/checkpoint'
model_checkpoint_callback = ModelCheckpoint(
    filepath=checkpoint_filepath,
    save_weights_only=False,
    verbose=1,
    monitor='loss',
    mode='min',
    save_best_only=False)


model_results = enc_dec_model.fit(pt_pad_sentence, lgp_pad_sentence, batch_size=16, epochs=50, callbacks=[model_checkpoint_callback])

enc_dec_model.save("saved_model/new_model")

def logits_to_sentence(logits, tokenizer):

    index_to_words = {idx: word for word, idx in tokenizer.word_index.items()}
    index_to_words[0] = '<empty>' 

    return ' '.join([index_to_words[prediction] for prediction in np.argmax(logits, 1)])

index = 14
print("The lgp sentence is: {}".format(lgp_sentences[index]))
print("The pt sentence is: {}".format(pt_sentences[index]))
print('The predicted sentence is :')
print(logits_to_sentence(enc_dec_model.predict(pt_pad_sentence[index:index+1])[0], lgp_text_tokenizer))
