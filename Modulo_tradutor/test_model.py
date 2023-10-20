#from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
from transformers import pipeline
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('FileWithSentences', help='Ficheiro com as frases originais')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()
pt_sentences = argss.FileWithSentences
to_write = argss.FileToWrite

translator = pipeline("translation", model="m2m-418", src_lang= "pt", tgt_lang = "pt")
#translator = pipeline("translation", model="mbart-finetuned-pt-lgp-35000", src_lang= "ept", tgt_lang = "lgp")

sentences = []
with open(pt_sentences, 'r') as file_sentences:
	lines = file_sentences.readlines()
	for line in lines:
		split_line = line.strip().split("\t")
		sentences.append(split_line[0])

with open(to_write, 'w') as write_file:
	for text in sentences:
		write_file.write(translator(text)[0]["translation_text"])
		write_file.write("\n")

#text = "Eu gosto de massa"
#print(translator(text)[0]["translation_text"])

