#########################################
#Módulo de tradução de português para LGP
#########################################
import csv
import sys
import re
import string
import argparse
from escolhaRegra import *
from geracao_fase import geracao
from processarFrasePT import *
from nltk import sent_tokenize
from escolhaRegra import distancia, escolher_regra_melhor
from freq_json import freq, abrir_freq
sys.path.append('../Modulo_construcao_regras')
from freeling import load_freeling
from phonemizer.phonemize import phonemize
from entity_recognition import entity_recognition
import unidecode
import time
import json
from transformers import pipeline
import argparse
# import pyphen --> silabas
# epitran --> fonemas
import traceback
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

from separate_syllables import silabizer

def update_elemento_sintatico(i, frase, gesto, classe_gesto):
	"""
	Atualiza a lista do elemento frásico (sujeito, predicado, verbo e modificador) a que pertence a palavra com as características
	do gesto correspondente.
	:param i: inteiro, indice da palavra
	:param frase: frase em português, objeto da classe Frase_input
	:param gesto: string, gesto
	:param classe_gesto: string, classe gramatical do gesto
	:return:
	"""
	for j in frase.indices_verbo:
		if j == i:
			index = frase.indices_verbo.index(j)
			if len(frase.classes_verbo) > index and len(frase.classes_antes_verbo) > index:
				frase.classes_verbo[frase.indices_verbo.index(j)] = classe_gesto
				frase.classes_antes_verbo[frase.indices_verbo.index(j)] = (gesto, classe_gesto)

	for j in frase.indices_suj:
		if j == i:
			index = frase.indices_suj.index(j)
			if len(frase.classes_suj) > index and len(frase.classes_antes_suj) > index:
				frase.classes_suj[frase.indices_suj.index(j)] = classe_gesto
				frase.classes_antes_suj[frase.indices_suj.index(j)] = (gesto, classe_gesto)
	for j in frase.indices_obj:
		if j == i:
			index = frase.indices_obj.index(j)
			if len(frase.classes_obj) > index and len(frase.classes_antes_obj) > index:
				frase.classes_obj[frase.indices_obj.index(j)] = classe_gesto
				frase.classes_antes_obj[frase.indices_obj.index(j)] = (gesto, classe_gesto)
	for j in frase.indices_outros:
		if j == i:
			index = frase.indices_outros.index(j)
			if len(frase.classes_outro) > index and len(frase.classes_antes_outro) > index:
				frase.classes_outro[frase.indices_outros.index(j)] = classe_gesto
				frase.classes_antes_outro[frase.indices_outros.index(j)] = (gesto, classe_gesto)
	for j in frase.indices_pred:
		if j == i:
			index = frase.indices_pred.index(j)
			if len(frase.classes_pred) > index and len(frase.classes_antes_pred) > index:
				frase.classes_pred[frase.indices_pred.index(j)] = classe_gesto
				frase.classes_antes_pred[frase.indices_pred.index(j)] = (gesto, classe_gesto)


def del_elemento_sintatico(i, frase, gesto, classe_gesto):
	"""
	Elimina do elemento frásico original a palavra que com a conversão de léxico passou a pertencer ao verbo.
	Atualiza todas as listas que tinham essa palavra.
	:param i: inteiro, indice da palavras na frase
	:param frase: frase em português, objeto da classe Frase_input
	:param gesto: gesto correspondente
	:param classe_gesto: classe gramatical do gesto
	:return:
	"""

	for j in frase.indices_verbo:
		if j == i:
			frase.classes_verbo[frase.indices_verbo.index(j)] = classe_gesto
			frase.classes_antes_verbo[frase.indices_verbo.index(j)] = (gesto, classe_gesto)

	for j in frase.indices_suj:
		if j == i:
			del frase.classes_suj[frase.indices_suj.index(j)]
			del frase.classes_antes_suj[frase.indices_suj.index(j)]
	for j in frase.indices_obj:
		if j == i:
			del frase.classes_obj[frase.indices_obj.index(j)]
			del frase.classes_antes_obj[frase.indices_obj.index(j)]
	for j in frase.indices_outros:
		if j == i:
			del frase.classes_outro[frase.indices_outros.index(j)]
			del frase.classes_antes_outro[frase.indices_outros.index(j)]
	for j in frase.indices_pred:
		if j == i:
			del frase.classes_pred[frase.indices_pred.index(j)]
			del frase.classes_antes_pred[frase.indices_pred.index(j)]

	del frase.classes[i]
	del frase.dep_tags[i]


def update_frase(index_pt, c, classes, gesto, frase):
	"""
	Atualiza o elemento frásico (sujeito ou predicado ou modificador) e a frase em português de acordo com
	o correspondente gesto.
	:param index_pt: Lista com os indices das palavras
	:param c: Indice da classe gramatical da palavra
	:param classes: Lista com as classes gramaticais das palavras.
	:param gesto: String, gesto correspondente
	:param frase: Frase em português, objeto da classe Frase_input
	:return:
	"""

	classe_gesto = classes[c]
	frase.frase_sem_det[index_pt[c]] = (gesto, gesto, classe_gesto)

	update_elemento_sintatico(index_pt[c], frase, gesto, classe_gesto)

	del index_pt[c]

	for i in sorted(index_pt, reverse=True):

		del frase.frase_sem_det[i]

		del_elemento_sintatico(i, frase, gesto, classe_gesto)


def saber_glosa(palavra, palavras_glosas, freq, classe, palavra_pt):
	"""
	Retorna a glosa/gesto mais frequente associado à palavra.
	:param palavra: lema(s) palavra(s) em português
	:param palavras_glosas: Lista com as entradas do dicionário
	:param freq: Lista com as frequências das entradas no dicionário
	:param classe: Classe gramatical da(s) palavra(s)
	:param palavra_pt: Palavra(s) em português
	:return: Gesto
	"""

	freq_indices = []
	indices = []
	for i,v in enumerate(palavras_glosas):
		if classe[0] !="N":

			if v[1] == palavra:
				freq_indices.append(freq[i])
				indices.append(i)

			else:
				continue
		else:
			if v[0] == palavra_pt:
				freq_indices.append(freq[i])
				indices.append(i)
			else:
				continue

	gesto = palavras_glosas[indices[freq_indices.index(max(freq_indices))]][2]
	return gesto



def update_elemento(frase, indices_outro, c):
	"""
	Atualiza os modificadores de frase.
	:param frase: frase em português
	:param indices_outro: lista com os indices de palavras que pertencem a modificadores
	:param c: inteiro, indice da palavra que deixou de pertencer ao modificador
	:return:
	"""
	try:
		del frase[indices_outro.index(c)]
	except:
		del frase[0]

def transferencia_lexical(frase, palavras_glosas, freq):
	"""
	Realiza a conversão do léxico português no léxico da LGP.
	:param frase: Frase em português
	:param palavras_glosas: Lista com as entradas do dicionário, Lista de tuplos.
	:param freq: Lista com as frequências das entradas do dicionário no dicionário.
	:return:
	"""

	list_explain = []
	for i,v in enumerate(palavras_glosas):
		
		if len(list(zip(*frase.frase_sem_det))) > 1:
			palavra_pt = list(list(zip(*frase.frase_sem_det))[1])
			
			if len(list(zip(*frase.frase_sem_det))) > 0:
				palavra_pt_not_lema = list(list(zip(*frase.frase_sem_det))[0])

				for s,p in enumerate(palavra_pt):
					palavra_pt[s] = p.translate(str.maketrans('', '', string.punctuation))

				palavras = " ".join(palavra_pt)
				classes_pt = list(list(zip(*frase.frase_sem_det))[2])
				palavra = re.search(r'\b(?<![\w-])' + v[1] + r'(?![\w-])\b', palavras.lower())


				for i in range(len(palavra_pt)):
					flag = False
					for t in list_explain:
						if palavra_pt[i] in t or palavra_pt_not_lema[i] in t:
							flag = True
					if not flag:
						list_explain.append((palavra_pt[i], palavra_pt_not_lema[i]))

				if palavra:
					palavras_pt = palavra.group(0).split()

					classes = []
					index_pt = []
					pt = []

					for p in palavras_pt:
						if p in palavra_pt:
							index_pt.append(palavra_pt.index(p))

					for i in index_pt:
						classes.append(classes_pt[i])
						pt.append(palavra_pt_not_lema[i])

					# No caso em que mais do que uma palavra é convertida num gesto. Ex: haver grande -> TER-MUITO
					if classes:
						gesto = saber_glosa(v[1], palavras_glosas, freq, classes, pt)

						flag = False
						for t in list_explain:
							if v[1] in t or gesto in t:
								flag = True
						if not flag:
							list_explain.append((v[1], gesto))

						tags_c = []
						if frase.classes_antes_outro:
							tags_c = list(list(zip(*frase.classes_antes_outro))[1])

						for c in range(len(classes)):

							if all(e in frase.classes_antes_verbo for e in classes) and any(e in tags_c for e in classes):
								update_elemento(frase.classes_outro, frase.indices_outros, index_pt[c])
								update_elemento(frase.classes_antes_outro, frase.indices_outros, index_pt[c])
								update_elemento(frase.indices_outros, frase.indices_outros, index_pt[c])

							if len(index_pt)>1:

								update_frase(index_pt, c, classes, gesto, frase)
								break
							if len(index_pt)<=1:
								classe_gesto = classes[c]
								frase.frase_sem_det[index_pt[c]] = (palavra_pt[index_pt[c]], gesto, classe_gesto)
								update_elemento_sintatico(index_pt[c], frase, gesto, classe_gesto)
	return list_explain

def map_bijecao(pred_pt, classes_antes_pred):
	"""
	Mapea as classes gramaticais com as palavra originais da frase.
	Ex: {"ADV3": ("rato", "n")}
	:param pred_pt:
	:param classes_antes_pred:
	:return: Um dicionário com o mapeamento. Ex: {"ADV3": ("rato", "n")}
	"""
	map_bij = {}
	for n, b in enumerate(pred_pt):
		if b not in map_bij.keys() and len(classes_antes_pred) > n:
			map_bij[b] = classes_antes_pred[n]

	return map_bij


def freq_dicionario():
	"""
	Contabiliza a frequência de uma entrada (lema, palabra, gesto) no dicionário.
	:return: duas listas, uma com os tuplos com lema, palavra e gesto e outra com a frequência de cada tuplo no dicionário.
	"""
	with open("../Modulo_construcao_regras/Dicionario/dicionario.csv") as f:
		csvreader = csv.reader(f, delimiter="\t")
		palavra_glosas = []
		frequencia = []

		for row in csvreader:
			if (row[0].lower(), row[1].lower(), row[2].lower()) in palavra_glosas:
				frequencia[palavra_glosas.index((row[0].lower(), row[1].lower(), row[2].lower()))] +=1
			else:
				palavra_glosas.append((row[0].lower(), row[1].lower(), row[2].lower()))
				frequencia.append(1)

	return palavra_glosas, frequencia


def ordena_palavras(i, freeling_model):
	"""
	Ordena as palavras na frase de acordo com a ordem original das mesmas.
	:param i: objeto do tipo Frase_input, frase em português.
	:return:
	"""

	dict_lemas = {}
	for j in i.frase_sem_det:
		dict_lemas[j[0]] = j[1]
	i.reset_frase_sem_det()

	for l,v in enumerate(i.traducao):
		word = v[0]
		_, lemma, _, _ = freeling.main(word, freeling_model)
		if v[0] in dict_lemas:
			i.traducao[l] = (v[0],dict_lemas[v[0]], v[1])
			i.update_frase_sem_det((v[0],dict_lemas[v[0]], v[1]))
		
		elif lemma[0] in dict_lemas:
			i.traducao[l] = (v[0],dict_lemas[lemma[0]], v[1])
			i.update_frase_sem_det((v[0],dict_lemas[lemma[0]], v[1]))
		else:
			continue


def retira_cor_de(f, palavras_unidas):
	"""
	Retira as palavras "cor de" nas cores.
	:param f: string, palavra em português
	:param palavras_unidas: lista com as excepções de cores.
	:return: string, cor sem as palavras "cor de".
	"""

	for i in palavras_unidas:
		laranja = i.split()[-1]

		cor_de = re.search(i, f)
		if cor_de:
			f =f.replace(cor_de.group(0), laranja)

	return f

def verifica_frase(f, frases_comuns):

	for i in frases_comuns:

		if i[:-1] in f.lower().translate(str.maketrans('', '', string.punctuation)):
			return True
		else:
			continue

def set_traducao_regras(classes_antes_verbo, traducao_regras_pred):
	"""
	Divide o verbo e os objetos do predicado.
	:param classes_antes_verbo: Lista com as classes gramaticais dos verbos.
	:param traducao_regras_pred: Lista com as classes gramaticais pertencentes ao predicado.
	:return: Lista com as classes que pertencem ao objeto e lista com as classes que pertencem aos verbos.
	"""
	objs = []
	verbos = []
	for l in classes_antes_verbo:
		verbos.append(l)

	for k in traducao_regras_pred:
		if k not in verbos:
			objs.append(k)

	return objs, verbos


def abre_corpus_teste(corpus):
	references = []
	with open(corpus) as csvfile:
		for l in csv.reader(csvfile, delimiter='\t'):
			references.append(l[0])
	return references

def translate_sentence(freeling_model, palavras_glosas, freq_dic, sentence, negativa_irregular, gestos_compostos):

	frase_lgp = []
	start_time = time.time()

	# frase = input("Escreva a frase a traduzir: ")

	# modo = input("Carregue na tecla F depois enter, caso queira o modo formal, caso contrário, carregue enter :")
	modo = ""

	frases_input = []

	frases_comuns = ["bom dia", "boa tarde", "boa noite", "por favor"] #listas de palavras que não devem ser processadas pelo tradutor

	palavras_unidas = ["cor de rosa", "cor de laranja"]

	frases = sent_tokenize(sentence)
	print(frases)

	indice = 0
	for f in frases:
		# if verifica_frase(f, frases_comuns) and len(f.lower().translate(str.maketrans('', '', string.punctuation)).split())< 3:
		# 	lgp = f.upper().translate(str.maketrans('', '', string.punctuation))
		# 	lgp = "-".join(lgp.split())
		# 	#frase_lgp = [lgp.upper()]
		# 	print("lgpp")
		# 	print(lgp)
		# 	frase_lgp.append(lgp.upper())
		# else:
		# 	if verifica_frase(f, frases_comuns):
		# 		for i in frases_comuns:
		# 			except_palavra = re.search(i, f[:-1].lower())
		# 			if except_palavra:
		# 				glosa = "-".join(except_palavra.group(0).split())
		# 				f = f.lower().replace(except_palavra.group(0), glosa)

		# 		# nova_frase = retira_cor_de(f, palavras_unidas)
		# 		# frases_input.append(preprocessar(nova_frase, freeling_model)) #fase de análise
		# 	else:
		# 		if len(f.lower().translate(str.maketrans('', '', string.punctuation)).split()) == 1:
		# 			#frase_lgp = [f.upper().translate(str.maketrans('', '', string.punctuation))]
		# 			frase_lgp.append(f.upper().translate(str.maketrans('', '', string.punctuation)))
			#fase de análise
		nova_frase = retira_cor_de(f, palavras_unidas)
		frases_input += preprocessar(nova_frase, freeling_model, indice)

		indice += 1

	print("--- %s pre-processamento ---" % (time.time() - start_time))
	exprFaciais = {}
	indice = 0
	frase_lgp = []
	mouthing = ""
	gestos_compostos_frases = []
	pausas = []
	adv_cond_frases = []
	adv_intensidade_frases = []
	map_valor = {}
	map_valor_o = {}
	map_valor_suj = {}

	for index, i in enumerate(frases_input):
		# fase de transferência lexical
		list_word_sign = transferencia_lexical(i, palavras_glosas, freq_dic)

		sim_pred, dist_obj_pred, freq_pred = distancia(i, "pred")
		sim_suj, dist_obj_suj, freq_suj = distancia(i, "suj")
		sim_mod, dist_obj_mod, freq_mod = distancia(i, "mod")
		total_distance = 0

		print("--- %s trasferência lexicalll ---" % (time.time() - start_time))
		# Escolha da regra mais semelhante por elemento frásico
		if dist_obj_pred:
			pred_pt, pred_lgp, distance = escolher_regra_melhor(i, sim_pred, dist_obj_pred, i.classes_pred, freq_pred)
			map_valor = map_bijecao(pred_pt, i.classes_antes_pred)

			traducao_ordenado = list(map(lambda x: map_valor[x] if x in map_valor else None, pred_lgp))
			traducao_ordenado = [value for value in traducao_ordenado if value is not None]

			total_distance += distance

			print("traducaoooo")
			print(traducao_ordenado)

			i.set_traducao_regras_pred(traducao_ordenado)

			objs, verbos = set_traducao_regras(i.classes_antes_verbo, i.traducao_regras_pred)

			i.set_traducao_regras_obj(objs)
			i.set_traducao_regras_verbo(verbos)

		if dist_obj_suj:
			suj_pt, suj_lgp, distance = escolher_regra_melhor(i, sim_suj, dist_obj_suj, i.classes_suj, freq_suj)
			map_valor_suj = map_bijecao(suj_pt, i.classes_antes_suj)

			total_distance += distance

			traducao_ordenado_suj = list(map(lambda x: map_valor_suj[x] if x in map_valor_suj else None, suj_lgp))
			traducao_ordenado_suj = [value for value in traducao_ordenado_suj if value is not None]

			i.set_traducao_regras_suj(traducao_ordenado_suj)
		
		if dist_obj_mod:
			mod_pt, mod_lgp, distance = escolher_regra_melhor(i, sim_mod, dist_obj_mod, i.classes_outro, freq_mod)
			map_valor_o = map_bijecao(mod_pt, i.classes_antes_outro)

			total_distance += distance

			traducao_ordenado_o = list(map(lambda x: map_valor_o[x] if x in map_valor_o else None, mod_lgp))
			traducao_ordenado_o = [value for value in traducao_ordenado_o if value is not None]

			i.set_traducao_regras_outro(traducao_ordenado_o)

		freq_estrutura = abrir_freq("../Modulo_construcao_regras/Estatisticas/estruturas_frasicas/regras_frasicas.json")
		if "cop" in i.dep_tags:
			max_keys, rule_prob = freq(freq_estrutura, i.tipo, True)
		else:
			max_keys, rule_prob = freq(freq_estrutura, i.tipo, False)

		estrutura = max_keys.lower()

		print("--- %s ordena elemento frásicos dentro de cada constituinte ---" % (time.time() - start_time))
		
		
		#Ordenar os elementos frásicos consoante a ordem frásica
		if modo !="": #Ordem SOV
			suj = i.traducao_regras_outro + i.traducao_regras_suj
			i.set_traducao(suj, i.traducao_regras_obj, i.traducao_regras_verbo)
			ordena_palavras(i, freeling_model)
		else:
			suj = i.traducao_regras_outro + i.traducao_regras_suj

			if len(i.traducao_regras_suj) == 1 and i.traducao_regras_suj[0][1].startswith("PT"):
				#interrogativas parciais de sujeito
				int_suj = True
			else:
				int_suj = False

			# estrutura = "osv" #default é o sov
			print("estrutura: ", estrutura)

			if estrutura.startswith('svo'):
				i.set_traducao(suj, i.traducao_regras_verbo, i.traducao_regras_obj)
				ordena_palavras(i, freeling_model)

			if estrutura.startswith('osv'):
				i.set_traducao(i.traducao_regras_obj, suj, i.traducao_regras_verbo)
				ordena_palavras(i, freeling_model)
			if estrutura.startswith('vos'):
				i.set_traducao(i.traducao_regras_verbo, suj, i.traducao_regras_suj)
				ordena_palavras(i, freeling_model)
			if estrutura.startswith('sov'):
				if int_suj:
					i.set_traducao(i.traducao_regras_verbo,i.traducao_regras_obj, suj)
				else:
					i.set_traducao(suj, i.traducao_regras_obj, i.traducao_regras_verbo)
				ordena_palavras(i, freeling_model)
			if estrutura == 'vso':
				i.set_traducao(i.traducao_regras_verbo, i.traducao_regras_suj, i.traducao_regras_obj)
				ordena_palavras(i, freeling_model)

			if estrutura == 'sv':
				if int_suj:
					i.set_traducao(i.traducao_regras_verbo,i.traducao_regras_obj, suj)
				else:
					i.set_traducao(suj, i.traducao_regras_verbo, i.traducao_regras_obj)
				ordena_palavras(i, freeling_model)

			if estrutura == 'vs':
				if int_suj:
					i.set_traducao(i.traducao_regras_verbo,i.traducao_regras_obj, suj)
				else:
					i.set_traducao(i.traducao_regras_verbo, i.traducao_regras_obj, suj)
				ordena_palavras(i, freeling_model)

			if estrutura == 'vo':
				i.set_traducao(suj, i.traducao_regras_verbo, i.traducao_regras_obj)
				ordena_palavras(i, freeling_model)

			if estrutura == 'ov':
				if int_suj:
					i.set_traducao(i.traducao_regras_verbo,i.traducao_regras_obj, suj)
				else:
					i.set_traducao(suj, i.traducao_regras_obj, i.traducao_regras_verbo)
				ordena_palavras(i, freeling_model)
			
			if estrutura == 'v':
				i.set_traducao(suj, i.traducao_regras_obj, i.traducao_regras_verbo)
				ordena_palavras(i, freeling_model)
			
			if estrutura == 's':
				i.set_traducao(suj, i.traducao_regras_obj, i.traducao_regras_verbo)
				ordena_palavras(i, freeling_model)
			
			if estrutura == 'o':
				i.set_traducao(suj, i.traducao_regras_obj, i.traducao_regras_verbo)
				ordena_palavras(i, freeling_model)

		
		print("--- %s ordenar consituinte frásicoo ---" % (time.time() - start_time))

		#fase de geracao
		list_geracao = []
		f_lgp, exprFaciais, traducao_lgp, gest_comp_frase  = geracao(i, indice, exprFaciais, negativa_irregular, gestos_compostos, list_geracao)

		if f_lgp:
			indice += len(f_lgp)
			frase_lgp += f_lgp
			mouthing += traducao_lgp + " "

			# gestos_compostos += gest_comp_frase

			#gestos_compostos
			# gest_comp_frase = [False] * len(f_lgp)
			# if "MULHER" in f_lgp:
			# 	indices = [i for i, e in enumerate(f_lgp) if e == "MULHER"]
			# 	print(indices)
			# 	for indice in indices:
			# 		gest_comp_frase[indice+1] = True

			# print(gest_comp_frase)			
			gestos_compostos_frases += gest_comp_frase
			
			# Identifica as pausas
			pausas_frase = ["false"] * len(f_lgp)

			if index < len(frases_input)-1:
				if i.frase_indice == frases_input[index+1].frase_indice and len(f_lgp)>1:
					pausas_frase[-1] = "oracao"
				elif i.frase_indice != frases_input[index+1].frase_indice:
					pausas_frase[-1] = "frase"
			if index == len(frases_input)-1:
				pausas_frase[-1] = "frase"

			pausas += pausas_frase

			#identifica clausulas adverbiais condicionais com o "se"
			adv_cond_frase = ["false"] * len(f_lgp)

			if i.clausula_adv_cond and i.clausula_adv_cond[0][1].upper() in traducao_lgp.split(" "):
				indices = [index for index, e in enumerate(traducao_lgp.split(" ")) if e == i.clausula_adv_cond[0][1].upper()]
				for index in indices:
					if len(adv_cond_frase) > index:
						adv_cond_frase[index] = "true"
			
			if "SE" in traducao_lgp.split(" "):
				indices = [index for index, e in enumerate(traducao_lgp.split(" ")) if e == "SE"]
				for index in indices:
					if len(adv_cond_frase) > index:
						adv_cond_frase[index] = "true"
			
			adv_cond_frases += adv_cond_frase

			#identifica adverbios de intensidade
			adv_int_frase = ["false"] * len(f_lgp)

			for adv in i.adverbial_mod:
				if adv.upper() in traducao_lgp.split(" "):
					# retorna tuplo com (indice, adverbio de intensidade)
					indices = [(index, i.adverbial_mod[adv]) for index, e in enumerate(traducao_lgp.split(" ")) if e == adv.upper()]
					for index in indices:
						adv_int_frase[index[0]] = index[1]
			adv_intensidade_frases += adv_int_frase

		print("--- %s fase de geracaooo ---" % (time.time() - start_time))
	# traducao_lgp = " ".join(frase_lgp)

	print("frase_lgp")
	print(frase_lgp)

	print("mouthinggg")
	print(mouthing)

	fonemas = phonemize(mouthing, language="pt-br", backend="espeak")
	print(fonemas)
	# fonemas = "u gatu ɡɔʃtɐ dɨ kumeɾ"

	table = {
			ord('ɐ'): 'a',
			ord('ʎ'): 'l',
			ord('Ʒ'): 'j',
			ord('ɲ'): 'j',
			ord('ɛ'): 'e',
			ord('ə'): 'e',
			ord('ɹ'): 'r',
			ord('ɾ'): 'r',
			ord('ʁ'): 'r',
			ord('ʃ'): 's',
			ord('Z'): 's',
			ord('ɔ'): 'o',
			ord('w'): 'u',
			ord('ʊ'): 'u',
			ord('ŋ'): 'n',
		}
		
	fonemas = fonemas.translate(table)
	fonemas = fonemas.replace("re", "r")
	fonemas = unidecode.unidecode(fonemas)
	fonemas = fonemas.split(" ")
	fonemas = list(filter(None, fonemas))

	print("Fonemas: ", fonemas)

	# syllables = find_syllables(fonemas)

	visemas = []
	silabas = silabizer()
	for glosa in fonemas:
		glosa = glosa.lower()
		visemas.append(silabas(glosa))

	# print(syllables)

	# 'adv_intensidade': adv_intensidade_frases

	print("Visemas: ", visemas)

	pt_rule, lgp_rule, pt_sentence = "", "", ""
	pt_match_word_rule, lgp_match_word_rule = [], []
	final_dot = False

	words = sentence.split()
	for s in words:
		_, lemma, _, _ = freeling.main(s, freeling_model)
		s_aux = s
		if s[-1] in ".?!":
			final_dot = True
			dot = s[-1]
			s = s[:-1]
		if pt_sentence and pt_sentence[-1] != " ":
			pt_sentence += " " + s# if final_dot else " " + s
		else:
			pt_sentence += s #if final_dot else s
		for m in list_word_sign:
			if s.startswith(m[0]) or lemma[0].startswith(m[0]):
				s = m[1]
		for m in map_valor.keys():
			if map_valor.get(m)[0] == s:
				pt_sentence = pt_sentence + "(" + m + ")" + " "
				pt_rule = pt_rule + " " + m
				pt_match_word_rule.append((s_aux, m))
				break
		for m in map_valor_o.keys():
			if map_valor_o.get(m)[0] == s:
				pt_sentence = pt_sentence + "(" + m + ")" + " "
				pt_rule = pt_rule + " " + m
				pt_match_word_rule.append((s_aux, m))
				break
		for m in map_valor_suj.keys():
			if map_valor_suj.get(m)[0] == s:
				pt_sentence = pt_sentence + "(" + m + ")" + " "
				pt_rule = pt_rule + " " + m
				pt_match_word_rule.append((s_aux, m))
				break

	if final_dot:
		if pt_sentence[-1] == " ":
			pt_sentence = pt_sentence[:-1]
			pt_sentence += dot
		else:
			pt_sentence += dot

	for s in frase_lgp:
		s_aux = s
		s = s.lower()
		_, lemma, _, _ = freeling.main(s, freeling_model)
		for m in list_word_sign:
			if s.startswith(m[0]) or lemma[0].startswith(m[0]):
				s = m[1]
		for m in list_geracao:
			_, lemma_list, _, _ = freeling.main(m[0], freeling_model)
			if s.startswith(m[0]) or lemma[0].startswith(m[0]):
				s = m[1]
			elif s.startswith(lemma_list[0]):
				joined_words = [m[0]] + m[1].split()
				if len(joined_words) > 2 and joined_words[1] == "mulher":
					s = joined_words[0]
			else:
				joined_words = [m[0]] + m[1].split()
				if len(joined_words) > 2:
					if joined_words[2] == "pequeno" and s == joined_words[1] or s == joined_words[2]:
						s = joined_words[0]
		for m in map_valor.keys():
			if map_valor.get(m)[0] == s:
				lgp_rule = lgp_rule + " " + m
				lgp_match_word_rule.append((s_aux, m))
				break
		for m in map_valor_o.keys():
			if map_valor_o.get(m)[0] == s:
				lgp_rule = lgp_rule + " " + m
				lgp_match_word_rule.append((s_aux, m))
				break
		for m in map_valor_suj.keys():
			if map_valor_suj.get(m)[0] == s:
				lgp_rule = lgp_rule + " " + m
				lgp_match_word_rule.append((s_aux, m))
				break

	alignment_string = ""
	pt_converted = []
	flag_mulher, flag_pequeno = False, False
	for lgp in frase_lgp:
		if lgp == "MULHER":
			if "MULHER" not in words and "mulher" not in words:
				flag_mulher = True
				continue
		if lgp == "PEQUENO":
			if "PEQUENO" not in words and "pequeno" not in words:
				flag_pequeno = True
		lgp_aux = lgp.lower()
		
		for pt in words:
			_, lemma, _, _ = freeling.main(pt, freeling_model)
			if lgp_aux == pt or lgp_aux == lemma:
				if flag_mulher:
					pt_converted.append(pt)
					if pt[-1] in ".?!":
						alignment_string = alignment_string + "\t" + pt[:-1] + " -> " +  "MULHER " + lgp + "\n"
					else:
						alignment_string = alignment_string + "\t" + pt + " -> " +  "MULHER " + lgp + "\n"
					flag_mulher = False
				elif flag_pequeno:
					pt_converted.append(pt)
					index = frase_lgp.index(lgp)
					if pt[-1] in ".?!":
						alignment_string = alignment_string + "\t" + pt[:-1] + " -> " + frase_lgp[index - 1] + " PEQUENO" + "\n"
					else:
						alignment_string = alignment_string + "\t" + pt + " -> " + frase_lgp[index - 1] + " PEQUENO" + "\n"

					flag_pequeno = False
				else:
					pt_converted.append(pt)
					if pt[-1] in ".?!":
						alignment_string = alignment_string + "\t" +  pt[:-1] + " -> " + lgp + "\n"
					else:
						alignment_string = alignment_string + "\t" +  pt + " -> " + lgp + "\n"

			elif lgp_aux == lemma[0]:
				if flag_mulher:
					pt_converted.append(pt)
					if pt[-1] in ".?!":
						alignment_string = alignment_string + "\t" + pt[:-1] + " -> " + "MULHER " + lgp + "\n"
					else:
						alignment_string = alignment_string + "\t" + pt + " -> " + "MULHER " + lgp + "\n"
					flag_mulher = False
				elif flag_pequeno:
					pt_converted.append(pt)
					index = frase_lgp.index(lgp)
					if pt[-1] in ".?!":
						alignment_string = alignment_string + "\t" + pt[:-1] + " -> " +  frase_lgp[index - 1] + " PEQUENO" + "\n"
					else:
						alignment_string = alignment_string + "\t" + pt + " -> " +  frase_lgp[index - 1] + " PEQUENO" + "\n"
					flag_pequeno = False
				else:
					pt_converted.append(pt)
					if pt[-1] in ".?!":
						alignment_string = alignment_string + "\t" + pt[:-1] + " -> " + lgp + "\n"
					else:
						alignment_string = alignment_string + "\t" + pt + " -> " + lgp + "\n"
			else:
				for pair in list_word_sign:
					if pt.startswith(pair[0]) and lgp_aux == pair[1]:
						if flag_mulher:
							pt_converted.append(pt)
							if pair[0][-1] in ".?!":
								alignment_string = alignment_string + "\t" + pair[0][:-1] + " -> " + "MULHER " + lgp + "\n"
							else:
								alignment_string = alignment_string + "\t" + pair[0] + " -> " + "MULHER " + lgp + "\n"
							flag_mulher = False
						elif flag_pequeno:
							pt_converted.append(pt)
							index = frase_lgp.index(lgp)
							if pt[-1] in ".?!":
								alignment_string = alignment_string + "\t" + pt[:-1] + " -> " + frase_lgp[index - 1] + " PEQUENO" + "\n"
							else:
								alignment_string = alignment_string + "\t" + pt + " -> " + frase_lgp[index - 1] + " PEQUENO" + "\n"
							flag_pequeno = False
						else:
							pt_converted.append(pt)
							if pair[0][-1]:
								alignment_string = alignment_string + "\t" + pair[0][:-1] + " -> " + lgp + "\n"
							else:
								alignment_string = alignment_string + "\t" + pair[0] + " -> " + lgp + "\n"
					elif lgp.lower() == pair[0] and pt == pair[1]:
						pt_converted.append(pt)
						alignment_string = alignment_string + "\t" + pair[1] + " -> " + lgp + "\n"

				for pair in list_geracao:
					if len(pair[1]) > 1:
						joined_words = [pair[0]] + pair[1].split()
						if len(joined_words) > 2 and pt == joined_words[0] and joined_words[1] == "mulher" and flag_mulher:
							pt_converted.append(pt)
							if pair[0][-1] in ".?!":
								alignment_string = alignment_string + "\t" + pair[0][:-1] + " -> " + "MULHER " + lgp + "\n"
							else:
								alignment_string = alignment_string + "\t" + pair[0] + " -> " + "MULHER " + lgp + "\n"
							flag_mulher = False
						elif len(joined_words) > 2 and pt == joined_words[0] and joined_words[2] == "pequeno":
							if flag_pequeno:
								pt_converted.append(pt)
								index = frase_lgp.index(lgp)
								if pt[-1] in ".?!":
									alignment_string = alignment_string + "\t" + pt[:-1] + " -> " + frase_lgp[index - 1] + " PEQUENO" + "\n"
								else:
									alignment_string = alignment_string + "\t" + pt + " -> " + frase_lgp[index - 1] + " PEQUENO" + "\n"
								flag_pequeno = False

	
	deleted_words = []
	
	for w in words:
		if w not in pt_converted:
			deleted_words.append(w)
	
	deleted_words = list(dict.fromkeys(deleted_words))

	print("\n--------------------------------------------------------------------------------\n")
	print("- Portuguese Sentence:\t", pt_sentence)
	print("- LGP glosses:\t", ' '.join(frase_lgp))
	
	print("\n--------------------------------------------------------------------------------\n")
	print("Conversion between Portuguese sentence and LGP sentence:")
	print("- Portuguese structure:\t", pt_rule)
	print("- LGP structure:\t", lgp_rule)
	print("- ", pt_rule + " ->", lgp_rule)
	
	print("\n--------------------------------------------------------------------------------\n")
	print("Alignment between Portuguese words and LGP glosses:")
	print(alignment_string)
	print("Deleted Portuguese words: ", deleted_words)

	print("\n--------------------------------------------------------------------------------\n")

	dictionary = {'glosas': frase_lgp, 'fonemas': visemas, 'gestos_compostos': gestos_compostos_frases,
	'pausas': pausas, 'adv_cond': adv_cond_frases}
	if exprFaciais:
		dictionary['exprFaciais'] = exprFaciais

	""" print("--- %s dicionario ---" % (time.time() - start_time))
	print("--------------------------")
	print("Frase em LGP:")
	for i in dictionary:
		print(i, ": ", dictionary[i]) """
	
	return dictionary, rule_prob, total_distance, alignment_string, deleted_words

def find_syllables(frase_lgp):
	syllables_split = []
	for glosa in frase_lgp:
		syllables = []
		print(glosa)
		vowels = 'aeiouy'
		if glosa[0] in vowels and glosa[1] not in vowels and glosa[2] in vowels:
			syllables.append(glosa[0])
			glosa = glosa[1:len(glosa)]
		syllables, glosa = find_syllables_aux(glosa, syllables, vowels)
		print(syllables)
		print(glosa)
		if glosa.endswith('le'):
			glosa = glosa.split("le")
		else:
			syllables[len(syllables)-1] += glosa
		print(syllables)
		syllables_split.append(str(syllables))
	return syllables_split
	
	print(syllables_split)

def find_syllables_aux(glosa, syllables, vowels):
	for index in range(1,len(glosa)):
		if len(glosa) != 0 and glosa[index] in vowels and glosa[index-1] not in vowels:
			syllables.append(glosa[0:index+1])
			glosa = glosa[index+1:len(glosa)]
			print(syllables)
			return find_syllables_aux(glosa, syllables, vowels)
	return syllables, glosa

def replace_name(name):
	dt_name = "DT(" + "-".join(list(name)) + ")"
	return dt_name
			
					

def tradutor_main():
	"""
	Função principal do tradutor.
	Segmenta o input em frases.
	As frases são analisadas sintatica e morfossintaticamente.
	Executa a transferência gramatical.
	Executa a fase de geração.
	:param frases: string, uma ou mais frases em português.
	:return: string, uma ou mais frases em LGP
	"""

	try:

		#Carregar o modelo do freeling
		freeling_model = load_freeling(True)
		palavras_glosas, freq_dic = freq_dicionario()

		#Identifica verbos com uma negativa irregular --> modificação morfológica
		negativa_irregular = []
		with open('Verbos_excepcoes.csv') as csvfile:
			csvreader = csv.reader(csvfile, delimiter="\t")
			for row in csvreader:
				negativa_irregular.append(row[0])

		print(negativa_irregular)

		#Identifica gestos compostos
		f = open('gestos_compostos.json',)
		data = json.load(f)
		# for i in data['gestos_compostos']:
		# 	print(i)
		# 	print(data['gestos_compostos'][i])
		f.close()

		return freeling_model, palavras_glosas, freq_dic, negativa_irregular, data['gestos_compostos']

		#return traducao_lgp

	except KeyboardInterrupt:
		pass

threshold = 0.5

# to test all the sentences from the test corpus with hybrid approach

parser = argparse.ArgumentParser()

parser.add_argument('FileToTranslate', help='Ficheiro com as frases em português')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()

file_sentences = argss.FileToTranslate
file_to_write = argss.FileToWrite

portuguese_sentences = []
with open(file_to_write, 'r') as training_pairs:
	training_lines = training_pairs.readlines()
	for training_line in training_lines:
		split_line = training_line.strip().split("\t")
		portuguese_sentences.append(split_line[0])

with open(file_to_write, 'a', newline='') as file_translations:
	with open(file_sentences, 'r') as file_test:
		lines = file_test.readlines()
		for line in lines:

			split_line = line.strip().split("\t")
			sentence = split_line[0]

			if sentence == "\n":
				continue
			
			s = sentence

			if s in portuguese_sentences:
				continue

			freeling_model, palavras_glosas, freq_dic, negativa_irregular, gestos_compostos = tradutor_main()
			try:
				dictionary, rule_prob, distance, alignment_string, deleted_words = translate_sentence(freeling_model, palavras_glosas, freq_dic, s, negativa_irregular, gestos_compostos)

				rule_prediction = ' '.join(dictionary['glosas'])
				number_glosses = len(rule_prediction.split())
				number_words = len(s.split())
				ratio = number_glosses / number_words

				if ratio < threshold or ratio > 1 or rule_prob < 0.1 or distance > 4:
					translator = pipeline("translation", model="m2m-418-35000", src_lang= "pt", tgt_lang = "pt")
					m2m_predicition = translator(s)[0]["translation_text"]
					output = m2m_predicition

				else:
					if 'exprFaciais' in dictionary:
						if ['interrogativa_total'] in dictionary['exprFaciais'].values():
							rule_prediction = '{' + rule_prediction + '}(q)'

						elif ['negativa_headshake'] in dictionary['exprFaciais'].values():
							if rule_prediction.endswith("NÃO"):
								rule_prediction = rule_prediction[:-3] + '{' + rule_prediction[-3:] + '}' + '(headshake)'
							else:
								rule_prediction = rule_prediction + " {" + "NÃO}(headshake)" 

						elif ['olhos_franzidos'] in dictionary['exprFaciais'].values():
							if rule_prediction.endswith("NÃO"):
								rule_prediction = rule_prediction[:-3] + '(' + rule_prediction[-3:] + ')'
							else:
								rule_prediction = rule_prediction + ' (NÃO)'
					output = rule_prediction
				
				if output != "":
				
					glosses = output.split()
					list_entities = entity_recognition(s)
					list_entities = list(map(str.upper, list_entities))
					for entity in list_entities:
						replacement = "DT(" + "-".join(list(entity.upper())) + ")"
						output = output.replace(entity, replacement)

					file_translations.write(s + '\t' + output + '\n')
			
			except Exception as e:
				print(traceback.format_exc())

# to test a particular sentence
""" 
sentence = "O João de Sousa gosta de comer massa."
#sentence = "Gostas de comer massa?"
#sentence = "Eu não gosto de comer massa."

parser = argparse.ArgumentParser()
parser.add_argument('FileToTranslate', help='Ficheiro com as frases em português')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()

file_sentences = argss.FileToTranslate
file_to_write = argss.FileToWrite

freeling_model, palavras_glosas, freq_dic, negativa_irregular, gestos_compostos = tradutor_main()
try:
	sentences = re.split(r'[.!?]+(?= )', sentence)
	
	for s in sentences:
		if s[0] == " ":
			s = s[1:]

		dictionary, rule_prob, distance, alignment_string, deleted_words = translate_sentence(freeling_model, palavras_glosas, freq_dic, s, negativa_irregular, gestos_compostos)
		rule_prediction = ' '.join(dictionary['glosas'])
		
		number_glosses = len(rule_prediction.split())
		number_words = len(s.split())
		ratio = number_glosses / number_words

		#if ratio < threshold or ratio > 1 or rule_prob < 0.1 or distance > 4:
		#	translator = pipeline("translation", model="mbart-finetuned-pt-lgp-20000", src_lang= "ept", tgt_lang = "lgp")
		#	mbart_prediction = translator(s)[0]["translation_text"]
		#	output = mbart_prediction

		#else:
		if 'exprFaciais' in dictionary:
			if ['interrogativa_total'] in dictionary['exprFaciais'].values() or ['interrogativa_parcial'] in dictionary['exprFaciais'].values():
				rule_prediction = '{' + rule_prediction + '}(q)'

			elif ['negativa_headshake'] in dictionary['exprFaciais'].values():
							if rule_prediction.endswith("NÃO"):
								rule_prediction = rule_prediction[:-3] + '{' + rule_prediction[-3:] + '}' + '(headshake)'
							else:
								rule_prediction = rule_prediction + " {" + "NÃO}(headshake)" 

			elif ['olhos_franzidos'] in dictionary['exprFaciais'].values():
				if rule_prediction.endswith("NÃO"):
					rule_prediction = rule_prediction[:-3] + '(' + rule_prediction[-3:] + ')'
				else:
					rule_prediction = rule_prediction + ' (NÃO)'	
		output = rule_prediction
		
		#print(dictionary['exprFaciais'])

		glosses = output.split()

		list_entities = entity_recognition(sentence)
		list_entities = list(map(str.upper, list_entities))
		print(list_entities)

		for entity in list_entities:
			replacement = "DT(" + "-".join(list(entity.upper())) + ")"
			output = output.replace(entity, replacement)
					


		print("\n")
		print("output: ", output)
		#with open(file_to_write, 'a', newline='') as file_translations:
		#	file_translations.write(sentence + '\t' + output + '\n')
		
		print("\n")
		print("--- Questão? ---")
		x = input("Tendo em conta o output de glosas fornecido, pretende observar o alinhamento entre as palavras em Português e as glosas em LGP? Por favor, responda \"Sim\" ou \"Não\".\n")
		
		if x.lower() == "sim":
			print("\n--------------------------------------------------------------------------------\n")
			print("Alignment between Portuguese words and LGP glosses:")
			print(alignment_string)
			print("Deleted Portuguese words: ", deleted_words)

except Exception as e:
	print(traceback.format_exc())
 """

""" # to test all the sentences from the simple sentences corpus

parser = argparse.ArgumentParser()

parser.add_argument('FileToTranslate', help='Ficheiro com as frases em português')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()

file_sentences = argss.FileToTranslate
file_to_write = argss.FileToWrite

portuguese_sentences = []
with open(file_to_write, 'r') as training_pairs:
	training_lines = training_pairs.readlines()
	for training_line in training_lines:
		split_line = training_line.strip().split("\t")
		portuguese_sentences.append(split_line[0])

with open(file_to_write, 'a', newline='') as file_translations:
	with open(file_sentences, 'r') as file_test:
		lines = file_test.readlines()
		for line in lines:

			split_line = line.strip().split("\t")
			sentence = split_line[2]

			if sentence == "\n":
				continue
			
			s = sentence

			if s in portuguese_sentences:
				continue

			freeling_model, palavras_glosas, freq_dic, negativa_irregular, gestos_compostos = tradutor_main()
			try:
				dictionary, rule_prob, distance, alignment_string, deleted_words = translate_sentence(freeling_model, palavras_glosas, freq_dic, s, negativa_irregular, gestos_compostos)

				output = ' '.join(dictionary['glosas'])

				if 'exprFaciais' in dictionary:
					if ['interrogativa_total'] in dictionary['exprFaciais'].values():
						output = '{' + output + '}(q)'

					elif ['negativa_headshake'] in dictionary['exprFaciais'].values():
						if output.endswith("NÃO"):
							output = output[:-3] + '{' + output[-3:] + '}' + '(headshake)'
						else:
							output = output + " {" + "NÃO}(headshake)" 

					elif ['olhos_franzidos'] in dictionary['exprFaciais'].values():
						if output.endswith("NÃO"):
							output = output[:-3] + '(' + output[-3:] + ')'
						else:
							output = output + ' (NÃO)'
				if output != "":
					
					glosses = output.split()

					list_entities = entity_recognition(s)
					list_entities = list(map(str.upper, list_entities))
					for entity in list_entities:
						replacement = "DT(" + "-".join(list(entity.upper())) + ")"
						output = output.replace(entity, replacement)

					file_translations.write(s + '\t' + output + '\n')
			except Exception as e:
				print(traceback.format_exc()) """


""" # to test all the sentences from the dialogue corpus

parser = argparse.ArgumentParser()

parser.add_argument('FileToTranslate', help='Ficheiro com as frases em português')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()

file_sentences = argss.FileToTranslate
file_to_write = argss.FileToWrite

portuguese_sentences = []
with open(file_to_write, 'r') as training_pairs:
	training_lines = training_pairs.readlines()
	for training_line in training_lines:
		split_line = training_line.strip().split("\t")
		portuguese_sentences.append(split_line[0])

with open(file_to_write, 'a', newline='') as file_translations:
	with open(file_sentences, 'r') as file_test:
		lines = file_test.readlines()
		for line in lines:

			#index = lines.index(line)
			#if index < 6000:
			#	continue
			#sentence = line

			if line == "\n":
				continue

			# Use regular expressions to remove spaces before punctuation
			processed_string = re.sub(r'\s+([.,!?])', r'\1', line)

			processed_string = processed_string.rstrip('\n')
	
			if processed_string in portuguese_sentences:
				continue

			sentences = re.split(r'(?<=[.!?]) +', processed_string)

			for s in sentences:
				
				if len(s) and s[0] == " ":
						s = s[1:]
				
				if s in portuguese_sentences:
					continue

				freeling_model, palavras_glosas, freq_dic, negativa_irregular, gestos_compostos = tradutor_main()
				try:
					dictionary, rule_prob, distance, alignment_string, deleted_words = translate_sentence(freeling_model, palavras_glosas, freq_dic, s, negativa_irregular, gestos_compostos)

					output = ' '.join(dictionary['glosas'])

					if 'exprFaciais' in dictionary:
						if ['interrogativa_total'] in dictionary['exprFaciais'].values():
							output = '{' + output + '}(q)'

						elif ['negativa_headshake'] in dictionary['exprFaciais'].values():
							if output.endswith("NÃO"):
								output = output[:-3] + '{' + output[-3:] + '}' + '(headshake)'
							else:
								output = output + " {" + "NÃO}(headshake)" 

						elif ['olhos_franzidos'] in dictionary['exprFaciais'].values():
							if output.endswith("NÃO"):
								output = output[:-3] + '(' + output[-3:] + ')'
							else:
								output = output + ' (NÃO)'
					if output != "":
						
						glosses = output.split()

						list_entities = entity_recognition(s)
						list_entities = list(map(str.upper, list_entities))
						for entity in list_entities:
							replacement = "DT(" + "-".join(list(entity.upper())) + ")"
							output = output.replace(entity, replacement)

						file_translations.write(s + '\t' + output + '\n')
				except Exception as e:
					print(traceback.format_exc())
 """
""" # to test all the sentences from the twitter corpus

parser = argparse.ArgumentParser()

parser.add_argument('FileToTranslate', help='Ficheiro com as frases em português')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()

file_sentences = argss.FileToTranslate
file_to_write = argss.FileToWrite

portuguese_sentences = []
with open(file_to_write, 'r') as training_pairs:
	training_lines = training_pairs.readlines()
	for training_line in training_lines:
		split_line = training_line.strip().split("\t")
		portuguese_sentences.append(split_line[0])

with open(file_to_write, 'a', newline='') as file_translations:
	with open(file_sentences, 'r') as file_test:
		lines = file_test.readlines()
		for line in lines:

			index = lines.index(line)
			#if index < 6000:
			#	continue
			sentence = line

			if sentence in portuguese_sentences:
				continue
			
			sentence = re.sub(r'https?://\S+', '', sentence)

			sentence.rstrip('\n')

			list_words = sentence.split()
			new_list = [item for item in list_words if not item.startswith('@')]
			

			sentence = " ".join(new_list)


			sentences = re.split(r'[.!?]+(?= )', sentence)

			for s in sentences:
				
				if len(s) and s[0] == " ":
						s = s[1:]
				
				if s in portuguese_sentences:
					continue

				if s == ":)" or s == ":-)":
					continue

				freeling_model, palavras_glosas, freq_dic, negativa_irregular, gestos_compostos = tradutor_main()
				try:
					dictionary, rule_prob, distance, alignment_string, deleted_words = translate_sentence(freeling_model, palavras_glosas, freq_dic, s, negativa_irregular, gestos_compostos)

					output = ' '.join(dictionary['glosas'])

					if 'exprFaciais' in dictionary:
						if ['interrogativa_total'] in dictionary['exprFaciais'].values():
							output = '{' + output + '}(q)'

						elif ['negativa_headshake'] in dictionary['exprFaciais'].values():
							if output.endswith("NÃO"):
								output = output[:-3] + '{' + output[-3:] + '}' + '(headshake)'
							else:
								output = output + " {" + "NÃO}(headshake)" 

						elif ['olhos_franzidos'] in dictionary['exprFaciais'].values():
							if output.endswith("NÃO"):
								output = output[:-3] + '(' + output[-3:] + ')'
							else:
								output = output + ' (NÃO)'
					print("output: ", output)
					if output != "":
						glosses = output.split()

						list_entities = entity_recognition(s)
						list_entities = list(map(str.upper, list_entities))
						for entity in list_entities:
							replacement = "DT(" + "-".join(list(entity.upper())) + ")"
							output = output.replace(entity, replacement)

						file_translations.write(s + '\t' + output + '\n')
				except Exception as e:
					print(traceback.format_exc()) """
""" 
# to test all the sentences from the literature corpus

parser = argparse.ArgumentParser()

parser.add_argument('FileToTranslate', help='Ficheiro com as frases em português')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()

file_sentences = argss.FileToTranslate
file_to_write = argss.FileToWrite

portuguese_sentences = []
with open(file_to_write, 'r') as training_pairs:
	training_lines = training_pairs.readlines()
	for training_line in training_lines:
		split_line = training_line.strip().split("\t")
		portuguese_sentences.append(split_line[0])

with open(file_to_write, 'a', newline='') as file_translations:
	with open(file_sentences, 'r') as file_test:
		lines = file_test.readlines()
		for line in lines:

			#index = lines.index(line)
			#if index < 412:
			#	continue

			if line[:2] != "pt":
				continue

			line = line.rstrip(',\n')
			lst = re.findall(r"'(.*?)'", line[3:])

			for sentence in lst:
				if sentence in portuguese_sentences:
					continue

				sentences = re.split(r'[.!?]+(?= )', sentence)

				for s in sentences:
					
					if s == "":
						continue
					if len(s) >= 1 and s[0] == " ":
						s = s[1:]

					if s in portuguese_sentences or not s or s == "," or s == ", ":
						continue

					freeling_model, palavras_glosas, freq_dic, negativa_irregular, gestos_compostos = tradutor_main()
					try:
						dictionary, rule_prob, distance, alignment_string, deleted_words = translate_sentence(freeling_model, palavras_glosas, freq_dic, s, negativa_irregular, gestos_compostos)

						output = ' '.join(dictionary['glosas'])

						if 'exprFaciais' in dictionary:
							if ['interrogativa_total'] in dictionary['exprFaciais'].values():
								output = '{' + output + '}(q)'

							elif ['negativa_headshake'] in dictionary['exprFaciais'].values():
								if output.endswith("NÃO"):
									output = output[:-3] + '{' + output[-3:] + '}' + '(headshake)'
								else:
									output = output + " {" + "NÃO}(headshake)" 

							elif ['olhos_franzidos'] in dictionary['exprFaciais'].values():
								if output.endswith("NÃO"):
									output = output[:-3] + '(' + output[-3:] + ')'
								else:
									output = output + ' (NÃO)'
						print("output: ", output)
						if output != "":
							glosses = output.split()

							list_entities = entity_recognition(s)
							list_entities = list(map(str.upper, list_entities))
							for entity in list_entities:
								replacement = "DT(" + "-".join(list(entity.upper())) + ")"
								output = output.replace(entity, replacement)

							file_translations.write(s + '\t' + output + '\n')

					except Exception as e:
						print(traceback.format_exc())
"""
""" # to test all the sentences from the news corpus

parser = argparse.ArgumentParser()

parser.add_argument('FileToTranslate', help='Ficheiro com as frases em português')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()

file_sentences = argss.FileToTranslate
file_to_write = argss.FileToWrite

portuguese_sentences = []
with open(file_to_write, 'r') as training_pairs:
	training_lines = training_pairs.readlines()
	for training_line in training_lines:
		split_line = training_line.strip().split("\t")
		portuguese_sentences.append(split_line[0])

with open(file_to_write, 'a', newline='') as file_translations:
	with open(file_sentences, 'r') as file_test:
		lines = file_test.readlines()
		for line in lines:
			
			# for tatoeba
			#index = lines.index(line)
			#if index < 5100:
			#	continue
			
			#if line.startswith("#"):
			#	continue

			#line = line.split("\t")[2] #for tatoeba
			

			if line in portuguese_sentences:
				continue

			sentences = re.split(r'[.!?]+(?= )', line)

			for s in sentences:
				if len(s) and s[0] == " ":
					s = s[1:]
				
				if len(s) and s[-1] == "\n":
					s = s[:-1]
				
				if s in portuguese_sentences or not s or s == ",":
					continue
			
				freeling_model, palavras_glosas, freq_dic, negativa_irregular, gestos_compostos = tradutor_main()
				try:
					dictionary, rule_prob, distance, alignment_string, deleted_words = translate_sentence(freeling_model, palavras_glosas, freq_dic, s, negativa_irregular, gestos_compostos)
					output = ' '.join(dictionary['glosas'])

					if 'exprFaciais' in dictionary:
						if ['interrogativa_total'] in dictionary['exprFaciais'].values():
							output = '{' + output + '}(q)'
						
						elif ['negativa_headshake'] in dictionary['exprFaciais'].values():
							if output.endswith("NÃO"):
								output = output[:-3] + '{' + output[-3:] + '}' + '(headshake)'
							else:
								output = output + " {" + "NÃO}(headshake)" 
							
						elif ['olhos_franzidos'] in dictionary['exprFaciais'].values():
							if output.endswith("NÃO"):
								output = output[:-3] + '(' + output[-3:] + ')'
							else:
								output = output + ' (NÃO)'
					print("output: ", output)

					if output != "":
							glosses = output.split()

							list_entities = entity_recognition(s)
							list_entities = list(map(str.upper, list_entities))
							for entity in list_entities:
								replacement = "DT(" + "-".join(list(entity.upper())) + ")"
								output = output.replace(entity, replacement)

							file_translations.write(s + '\t' + output + '\n')
				except Exception as e:
					print(traceback.format_exc()) """


""" # Test sentences from test corpus

parser = argparse.ArgumentParser()

parser.add_argument('FileToTranslate', help='Ficheiro com as frases em português')
parser.add_argument('FileToWrite', help='Ficheiro onde escrever as traduções')

argss = parser.parse_args()

file_sentences = argss.FileToTranslate
file_to_write = argss.FileToWrite

translator = pipeline("translation", model="m2m-1_2B-35000", src_lang= "pt", tgt_lang = "pt")


portuguese_sentences = []
with open(file_to_write, 'r') as training_pairs:
	training_lines = training_pairs.readlines()
	for training_line in training_lines:
		split_line = training_line.strip().split("\t")
		portuguese_sentences.append(split_line[0])

with open(file_to_write, 'a', newline='') as file_translations:
	with open(file_sentences, 'r') as file_test:
		lines = file_test.readlines()
		for line in lines:
			split_line = line.strip().split("\t")
			#sentence = line
			sentence = split_line[0]
			#sentence = sentence.rstrip('\n')

			freeling_model, palavras_glosas, freq_dic, negativa_irregular, gestos_compostos = tradutor_main()
			dictionary, rule_prob, distance, alignment_string, deleted_words = translate_sentence(freeling_model, palavras_glosas, freq_dic, sentence, negativa_irregular, gestos_compostos)
			rule_prediction = ' '.join(dictionary['glosas'])
			try:

				number_glosses = len(rule_prediction.split())
				number_words = len(sentence.split())
				ratio = number_glosses / number_words

				if ratio <= 0.5 or ratio > 1 or rule_prob < 0.2 or distance > 2:
					print("--------- Predicting with M2M ---------")
					mbart_prediction = translator(sentence)[0]["translation_text"]
					output = mbart_prediction
				
				else:
					print("--------- Using the Rule Based ---------")
					if 'exprFaciais' in dictionary:
						if ['interrogativa_total'] in dictionary['exprFaciais'].values():
							rule_prediction = '{' + rule_prediction + '}(q)'
						
						elif ['negativa_headshake'] in dictionary['exprFaciais'].values():
							if rule_prediction.endswith("NÃO"):
								rule_prediction = rule_prediction[:-3] + '{' + rule_prediction[-3:] + '}' + '(headshake)'
							else:
								rule_prediction = rule_prediction + " {" + "NÃO}(headshake)" 
							
						elif ['olhos_franzidos'] in dictionary['exprFaciais'].values():
							if rule_prediction.endswith("NÃO"):
								rule_prediction = rule_prediction[:-3] + '(' + rule_prediction[-3:] + ')'
							else:
								rule_prediction = rule_prediction + ' (NÃO)'
					output = rule_prediction
					
					list_entities = entity_recognition(sentence)
					list_entities = list(map(str.upper, list_entities))
					print(list_entities)

					for entity in list_entities:
						replacement = "DT(" + "-".join(list(entity.upper())) + ")"
						output = output.replace(entity, replacement)
					
				print("output: ", output)
				file_translations.write(output + '\n')
				#file_translations.write(output + '\n')
			except Exception as e:
				print(traceback.format_exc()) """
