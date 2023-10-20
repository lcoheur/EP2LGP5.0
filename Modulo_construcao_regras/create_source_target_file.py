###########################################################################################
#Funções que permitem extrair as seguintes informações do ficheiro html exportado do ELAN:#
# - LG_P1 transcrição -> Tradução para português do enunciado                             #
# - LGP_P1_Trans_Literal -> Tradução para LGP glosas                                      #
###########################################################################################
import sys
from Corpus import Info_Corpus
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import lxml.html
import Levenshtein

def readTable(frases, root):
	time_inits_fins_pt = []
	time_inits_fins_lgp = []
	pt_sentences = []
	lgp_sentences = []

	# LP_P1_transcricao_livre
	index = 0
	#index_aux = 0
	for i in root.findall(".//*[@class='ti-0']"):
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):
				for j in i.findall("*[@" + col + "]"):
					text = j.text
					#index_aux += 1
					#if text:
					index += 1
					pt_sentences.append(text)
	index_aux = index
	print("index aux: ", index_aux)

	# GLOSAS_P1
	for i in root.findall(".//*[@class='ti-1']"):
		index = 0
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):
				for j in i.findall("*[@" + col + "]"):
					text = j.text
					if text:
						lgp_sentences.append(text)
	
	# initial time - final time
	index = 0
	for i in root.findall(".//*[@class='null']"):
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):
				for j in i.findall("*[@" + col + "]"):
					text = j.text
					if text:
						index += 1
						if index <= index_aux:
							time_inits_fins_pt.append(text)
						else:
							time_inits_fins_lgp.append(text)

	glosses_LGP = [[] for _ in range(len(pt_sentences))]

	for t in time_inits_fins_pt:
		for r in time_inits_fins_lgp:
			r_start, r_end = r.split(" - ")
			r_start = int(r_start)
			r_end = int(r_end)
			
			my_range_start, my_range_end = t.split(" - ")
			my_range_start = int(my_range_start)
			my_range_end = int(my_range_end)
			
			if my_range_start <= r_end - 10 and my_range_end >= r_start + 10:
				new_index_pt = time_inits_fins_pt.index(t)
				index_lgp = time_inits_fins_lgp.index(r)
				glosses_LGP[new_index_pt].append(lgp_sentences[index_lgp])
	
	list_glosses = [' '.join(sub_list) for sub_list in glosses_LGP]
	
	return pt_sentences, list_glosses



def parse_file(ficheiro_html):

	global root, outputfile

	inputfile = open(ficheiro_html, "r", encoding='utf-8')
	file = open("aux_file.html", "w+", encoding='utf-8')

	html_file = ""
	for line in inputfile:
		if "nbsp;" in line:
			line = ""
		html_file += line		
		file.write(line)

	file.seek(0)
	root = lxml.html.fromstring(html_file)

	frases = []
	print(root.findall(".//td/table"))
	for j in root.findall(".//td/table"): #processa as frases todas de uma vez
		pt_sentences, lgp_sentences = readTable(frases, j)

	file.close()
	os.remove("aux_file.html")

	return pt_sentences, lgp_sentences

def main(ficheiro_html):
	"""
	Extração das informações do ficheiro html exportado do ELAN.
	:return:
	"""
	info_elan = parse_file(ficheiro_html)
	return info_elan
