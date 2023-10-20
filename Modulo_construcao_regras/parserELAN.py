###########################################################################################
#Funções que permitem extrair as seguintes informações do ficheiro html exportado do ELAN:#
# - LG_P1 transcrição -> Tradução para português do enunciado                             #
# - Glosas_p1 -> Glosas que representam o vocabulário em LGP da mão dominante             #
# - M1_classGram -> Classes gramaticais da glosa mão dominante                            #
# - M1_Constituintes -> Análise Sintática da frase em LGP da mão dominante				  #
# - Come_P1Literal -> identificam o tipo de frase                                         #
###########################################################################################
import sys
from Corpus import Info_Corpus
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
import lxml.html

def readTable(frases, root):
	glosas = []

	myDict = defaultdict(list)
	frase = Info_Corpus()

	frases_dict = {}
	pt_sentences = []
	lgp_glosses = []
	classgrams = []
	constituints = []
	type_sentences = []
	times_pt = []
	times_glosses = []
	times_classgrams = []
	times_constituints = []
	times_types = []
	all_times = []
	lgp_sentences = []

	gloss_class = {}

	# LP_P1_transcricao_livre
	index = 0
	index_pt_sentences = 0
	for i in root.findall(".//*[@class='ti-0']"):
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):
				for j in i.findall("*[@" + col + "]"):
					text = j.text
					if text:
						frase_pt = text
						#frase.set_frase_pt(frase_pt)
						#frases.append(frase)
						index += 1
						pt_sentences.append(text)

	index_pt_sentences = index
	
	# LGlosas_p1
	index_lgp_glosses = 0
	index = 0
	for i in root.findall(".//*[@class='ti-1']"):
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):
				for j in i.findall("*[@" + col + "]"):
					glosa = j.text
					if glosa:
						index += 1
						lgp_sentences.append(glosa)
					#frase.append_frase_lgp(glosa)
					#index_lgp_glosses += 1
					lgp_glosses.append(glosa)
					glosas.append(glosa)
	index_lgp_glosses = index_pt_sentences + index
	
	index_m1_classgram = 0
	index = 0
	# M1_clasgram
	for i in root.findall(".//*[@class='ti-2']"):
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):
				for l, j in enumerate(i.findall("*[@" + col + "]")):
					text = j.text
					if text:
						index += 1
					if len(glosas) > 0 and l < len(glosas):
						#frase.append_classes_gramaticais(glosas[l], text)
						#index_m1_classgram += 1
						classgrams.append(text)
	
	index_m1_classgram = index_pt_sentences + index
	
	lgp_glosses_aux = []
	classgrams_aux = []

	if classgrams:
		for i in range(len(lgp_glosses)):
			if lgp_glosses[i] or classgrams[i]:
				lgp_glosses_aux.append(lgp_glosses[i])
				classgrams_aux.append(classgrams[i])

	#tipo de frase
	index = 0
	index_type_sentences = 0
	for i in root.findall(".//*[@class='ti-3']"):
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):
				for j in i.findall("*[@" + col + "]"):
					if "hide" in j.get("class", ""):
						continue
					text = j.text
					#if text:
					#frase.append_tipo_frase(text)
					type_sentences.append(text)
					#index_type_sentences += 1 
					index += 1
	index_type_sentences = index_lgp_glosses + index

	# M1_constituintes
	index_m1_constituints = 0
	index = 0
	for i in root.findall(".//*[@class='ti-4']"):
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):# and len(glosas) > 0:
				for l,j in enumerate(i.findall("*[@" + col + "]")):
					if "hide" in j.get("class", ""):
						continue
					text = j.text
					if text and len(glosas) > 0 and l < len(glosas):
						#frase.append_analise_sintatica(glosas[l], text)
						#if(myDict[index+1]):
						constituints.append(text)
						#index_m1_constituints += 1
						index += 1
						#myDict[index].append(text)
					elif len(glosas) > 0 and l < len(glosas):
						index += 1
						constituints.append("")
						#frase.append_analise_sintatica(glosas[l], "")

	index_m1_constituints = index_type_sentences + index

	index = 0
	for i in root.findall(".//*[@class='null']"):
		for n in range(100):
			col = "colspan=" + '"' + str(n) + '"'
			if i.findall("*[@" + col + "]"):
				for j in i.findall("*[@" + col + "]"):
					text = j.text
					if text:
						index += 1
						all_times.append(text)
						if index <= index_pt_sentences:
							times_pt.append(text)
						if index > index_pt_sentences and index <= index_lgp_glosses:
							times_glosses.append(text)
							times_classgrams.append(text)
						if index > index_lgp_glosses and index <= index_type_sentences:
							times_types.append(text)
						if index > index_type_sentences and index <= index_m1_constituints:
							times_constituints.append(text)
	

	new_lgp_glosses = []
	new_classgrams = []
	new_times_glosses = []
	new_times_classgrams = []

	for i in range(len(lgp_glosses_aux)):
		if lgp_glosses_aux[i] and classgrams_aux[i]:
			new_lgp_glosses.append(lgp_glosses_aux[i])
			new_classgrams.append(classgrams_aux[i])
			new_times_classgrams.append(times_classgrams[i])
			new_times_glosses.append(times_glosses[i])

	new_times_type = []
	new_types_sentences = []


	if times_types:
		if len(times_types) != len(times_pt):
			
			times_pt_aux = times_pt.copy()
			times_types_aux = times_types.copy()
			pairs = []
			
			for time_range_1 in times_types_aux:
				best_match = None
				best_difference = float('inf')
				
				for time_range_2 in times_pt_aux:
					difference = abs(int(time_range_1.split(' - ')[0]) - int(time_range_2.split(' - ')[0]))
					if difference < best_difference:
						best_match = time_range_2
						best_difference = difference
				
				pairs.append((time_range_1, best_match))
				times_pt_aux.remove(best_match)

			for p in times_pt:
				flag = False
				for pair in pairs:
					if pair[1] == p:
						flag = True
				if not flag:
					index_time_pt = times_pt.index(p)
					times_types.insert(index_time_pt, pair[0])
					type_sentences.insert(index_time_pt, None)

		for i in range(len(pt_sentences)):
			if type_sentences[i] and times_types[i]:
				new_types_sentences.append(type_sentences[i])
				new_times_type.append(times_types[i])

	new_constituints = []
	new_times_constituints = []

	for i in range(len(constituints)):
		if constituints[i] and times_constituints[i]:
			new_constituints.append(constituints[i])
			new_times_constituints.append(times_constituints[i])
	
	glosses_LGP = [[] for _ in range(len(pt_sentences))]

	for i in pt_sentences:
		frase = Info_Corpus()
		frase.set_frase_pt(i)
		frases.append(frase)
	
	for t in times_pt:
		my_range_start, my_range_end = t.split(" - ")
		my_range_start = int(my_range_start)
		my_range_end = int(my_range_end)
		index_pt = times_pt.index(t)
		frase_pt = frases[index_pt]

		for g in times_glosses:
			g_start, g_end = g.split(" - ")
			g_start = int(g_start)
			g_end = int(g_end)

			if my_range_start <= g_end - 10 and my_range_end >= g_start + 10:
				new_index_pt = times_pt.index(t)
				index_lgp = times_glosses.index(g)
				glosses_LGP[new_index_pt].append(lgp_sentences[index_lgp])

		
		for r in range(len(new_times_glosses)):
			r_start, r_end = new_times_glosses[r].split(" - ")
			r_start = int(r_start)
			r_end = int(r_end)

			if my_range_start <= r_end - 10 and my_range_end >= r_start + 10:
				frase_pt.append_frase_lgp(new_lgp_glosses[r])
				frase_pt.append_time_frase_lgp(new_times_glosses[r])
				frase_pt.append_classes_gramaticais(new_lgp_glosses[r], new_classgrams[r])
			
		
		for ty in range(len(new_times_type)):
			ty_start, ty_end = new_times_type[ty].split(" - ")
			ty_start = int(ty_start)
			ty_end = int(ty_end)

			if my_range_start <= ty_end - 10 and my_range_end >= ty_start + 10:
				frase_pt.append_tipo_frase(new_types_sentences[ty])
		
		for c in range(len(new_times_constituints)):
			c_start, c_end = new_times_constituints[c].split(" - ")
			c_start = int(c_start)
			c_end = int(c_end)

			if my_range_start <= c_end - 10 and my_range_end >= c_start + 10:
				glosses = frase_pt.get_glosses()
				time_glosses = frase_pt.get_time_frase_lgp()
				
				index_glosses = 0

				for gloss in glosses:
					time = time_glosses[index_glosses]
					time_start, time_end = time.split(" - ")
					time_start = int(time_start)
					time_end = int(time_end)

					if time_start <= c_end - 10 and time_end >= c_start + 10:
						frase_pt.append_analise_sintatica(gloss, new_constituints[c])
					
					index_glosses += 1

	list_glosses = [' '.join(sub_list) for sub_list in glosses_LGP]

	#for i in frases:
	#	print(i)
	#sys.exit()
	return frases, pt_sentences, list_glosses



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
	# tree = ET.parse(file)
	# root = tree.getroot()
	# print(html_file)
	root = lxml.html.fromstring(html_file)
	# print(root)

	frases = []
	print(root.findall(".//td/table"))
	
	for j in root.findall(".//td/table"): #processa as frases todas de uma vez
		frases, pt_sentences, lgp_sentences = readTable(frases, j)

	indices =[]
	for m, i in enumerate(frases):
		if i.frase_pt == "" and i.frase_lgp == "":
			indices.append(m)

	for h in sorted(indices, reverse=True):
		del frases[h]


	file.close()
	os.remove("aux_file.html")

	return frases, pt_sentences, lgp_sentences

def main(ficheiro_html):
	"""
	Extração das informações do ficheiro html exportado do ELAN.
	:return:
	"""
	info_elan, pt_sentences, lgp_sentences = parse_file(ficheiro_html)
	return info_elan, pt_sentences, lgp_sentences
