import argparse
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast, DataCollatorForSeq2Seq, Seq2SeqTrainingArguments, Seq2SeqTrainer
from sklearn.model_selection import train_test_split
import random

# Define the model and the tokenizer
model = MBartForConditionalGeneration.from_pretrained("facebook/mbart-large-50-many-to-many-mmt")
tokenizer = MBart50TokenizerFast.from_pretrained("facebook/mbart-large-50-many-to-many-mmt", src_lang="pt_XX")

# Reads the file from the command line
parser = argparse.ArgumentParser()
parser.add_argument('FileToFineTune', help='File with PT-LGP pairs')
argss = parser.parse_args()
file_pairs = argss.FileToFineTune

# Creates lists of all PT and LGP sentences
pt_sentences = []
lgp_sentences = []
with open(file_pairs, 'r') as pairs:
	pairs_lines = pairs.readlines()
	for pair in pairs_lines:
		split_line = pair.strip().split("\t")
		pt_sentences.append(split_line[0])
		lgp_sentences.append(split_line[1])
		
# Creates the vocabulary (glosses from LGP)
all_strings = ' '.join(lgp_sentences)
words = all_strings.split()
vocabulary_set = set(words)
vocabulary = list(vocabulary_set)

print("len tokenizer before: ", len(tokenizer))
print("size input embeddings before: ", model.get_input_embeddings())

# Adds the new tokens from LGP (glosses)
added_tokens = tokenizer.add_tokens(vocabulary)
model._resize_token_embeddings(len(tokenizer))

print("added_tokens: ", added_tokens)
print("len tokenizer after: ", len(tokenizer))

print("size input embeddings after: ", model.get_input_embeddings())



""" # Defines the sentence to be translated
sentence_to_translate = "Olá, como estás?"

# translate Portuguese to Portuguese
encoded_ar = tokenizer(sentence_to_translate, return_tensors="pt")
generated_tokens = model.generate(
    **encoded_ar,
    forced_bos_token_id=tokenizer.lang_code_to_id["pt_XX"]
)
print(tokenizer.batch_decode(generated_tokens, skip_special_tokens=True))
 """