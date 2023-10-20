import sys
import nltk
import spacy
from collections import Counter
from spacy import displacy
import pandas as pd
import matplotlib.pyplot as plt
import string

def characterize_corpus(sentences):
    # Split each sentence into a list of words using whitespace as the delimiter

    print("--------------------")
    print("Number of sentences in the test corpus: ", len(sentences))

    word_counts = [len(sentence.split()) for sentence in sentences]

    # Calculate the average, maximum, and minimum number of words
    average_words = sum(word_counts) / len(word_counts)
    max_words = max(word_counts)
    min_words = min(word_counts)

    max_index = word_counts.index(max_words)

    print("--------------------")
    print("Average of words in the sentences: ", average_words)

    # Print the maximum number of words and the corresponding sentence
    print("--------------------")
    print("Maximum words in a sentence:", max_words)
    print("Sentences with the maximum number of words:")
    for i, sentence in enumerate(sentences):
        if i == max_index:
            print(sentence.strip())
        elif len(sentence.split()) == max_words:
            print(sentence.strip())
    
    min_index = word_counts.index(min_words)

    # Print the minimum number of words and the corresponding sentence
    print("--------------------")
    print("Minimum words in a sentence:", min_words)
    """ print("Sentences with the minimum number of words:")
    for i, sentence in enumerate(sentences):
        if i == min_index:
            print(sentence.strip())
        elif len(sentence.split()) == min_words:
            print(sentence.strip()) """
    
    # Tokenize the text into words
    words = []
    for sentence in sentences:
        words += nltk.word_tokenize(sentence)
    
    new_list = [item for item in words if item not in string.punctuation]
    new_list = [item for item in new_list if item not in ["IX", "CL", "NG", "N"]]

    # Calculate the vocabulary size
    vocab_set = set(new_list)
    vocab_size = len(vocab_set)
    
    # Calculate the word frequency distribution
    word_freq = Counter(new_list)
    top_words = word_freq.most_common(10)  # Get the top 10 most common words


    # Print the results
    print("Vocabulary size:", vocab_size)
    print("Top 10 most common words:", top_words)


filename = sys.argv[1]
nltk.download('averaged_perceptron_tagger')
nlp = spacy.load('pt_core_news_md')

port_sentences = []
lgp_sentences = []
with open(filename, 'r') as f:
    lines = f.readlines()
    for line in lines:
        port_sentences.append(line)
        #split_line = line.strip().split("\t")
        #print(split_line)
        #port_sentences.append(split_line[0])
        # lgp_sentences.append(split_line[1])

print("----------------Portuguese sentences---------------------")
characterize_corpus(port_sentences)
print("-----------------LGP sentences-------------------------")
# characterize_corpus(lgp_sentences)

document = nlp(open(filename, encoding="utf-8").read())
sents = []
pos_tags = []

for line in document.text.split('\n'):
    if line.strip():
        first_element = line.split('\t')[0]
        sents.append(nlp(first_element))

#Extract part of speech tags
for sent in sents:
    for token in sent:
        pos_tags.append(token.pos_ )
        if token.pos_ == "PART":
            print("PARTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT")
            print(token)

##Count the occurrences of each tag
tag_counts = Counter(pos_tags)

#Calculate the total number of tags
total_tags = sum(tag_counts.values())

#Calculate the percentage of each tag
tag_percentages = {tag: count/total_tags*100 for tag, count in tag_counts.items()}

for tag in tag_percentages:
    print(tag)
    print(tag_percentages.get(tag))

""" #Create bar chart of the tag counts
tags = tag_percentages.keys()
percentages = tag_percentages.values()



plt.bar(tags, percentages)
plt.title('Part of speech tag distribution')
plt.xlabel('Tag')
plt.ylabel('Percentage')
plt.show()
 """