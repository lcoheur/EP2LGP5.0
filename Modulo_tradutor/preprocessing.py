import sys
sys.path.append('../Modulo_construcao_regras')
import freeling
import csv

def tipo_de_frase(pred_tags, pont):
	"""
	Identifica o tipo da frase.
	:param pred_tags: lista com as etiquetas morfossintáticas
	:param pont: sinal de pontuação
	:return: lista com o tipo da frase
	"""
	tipo_frase = []
	if pont == "!" and "RN" not in pred_tags:
		tipo_frase.append("EXCL")

	elif pont == "?" and "RN" not in pred_tags:
		tipo_frase.append("INT")

	elif "RN" in pred_tags and pont =="!":
		tipo_frase.append("NEG")
		tipo_frase.append("EXCL")

	elif "RN" in pred_tags and pont =="?":
		tipo_frase.append("INT")
		tipo_frase.append("NEG")

	elif "RN" in pred_tags:
		tipo_frase.append("NEG")

	else:
		tipo_frase.append("CAN")

	return tipo_frase

def atualiza_tags(adv_quant, words, pred_tags, sub):
	"""
	Atualiza as etiquetas de advérbios e pronomes com os seus subtipos.
	:param adv_quant: string, advérbio
	:param words: lista com as words da frase
	:param pred_tags: lista com as etiquetas morfossintaticas das words
	:param sub: etiqueta a substituir
	:return:
	"""
	for adv in adv_quant:
		advs = list(filter(lambda x: adv.lower() == x[1].lower(), enumerate(words)))
		if advs:
			pred_tags[words.index(advs[0][1])] = sub


def preprocess(freeling_values):
	negativa_irregular = []
	with open('Verbos_excepcoes.csv') as csvfile:
			csvreader = csv.reader(csvfile, delimiter="\t")
			for row in csvreader:
				negativa_irregular.append(row[0])

	file_pairs = open("../Modulo_construcao_regras/new_pairs_pt_lgp.txt")
	line = file_pairs.readline()

	file_to_write = open("new_pairs_preprocessed.txt", "w")


	while line:
		exprFaciais = {}
		if line.startswith("File"):
			line = file_pairs.readline()
			continue
		
		split_line = line.split("\t")
		pt_sentence = split_line[0]
		lgp_sentence = split_line[1]

		lgp_sentence = lgp_sentence.rstrip("\n")

		words, lemmas, lemma_verdadeiro, pred_tags = freeling.main(pt_sentence, freeling_values)
		
		adv_quant = ["muito", "muitos", "muita", "muitas", "menos", "tanto", "pouco", "pouca", "demasiado", "bastante", "apenas", "mais", "tanto"]
		adv_temporal = ["fim_de_semana", "quando", "enquanto", "depois"]
		adv_tempo_passado = ['ontem', 'outrora', 'dantes', 'antigamente', 'antes', 'já', 'hoje_de_manhã']
		adv_tempo_futuro = ['logo', 'amanhã', 'doravante','em_breve']
		adv_int = ["onde", "quando", "como", "porque"]
		pronomes_int = ["qual", "quais", "quantos", "quantas", "quanto", "porquê", "quem"]
		adv_neg = ["nunca"]
		pron_relativo = ["é_que", "que"]
		
		atualiza_tags(adv_quant, words, pred_tags, "RGQ")
		atualiza_tags(adv_temporal, words, pred_tags, "RGT")
		atualiza_tags(adv_tempo_passado, words, pred_tags, "RGTP")
		atualiza_tags(adv_tempo_futuro, words, pred_tags, "RGTF")
		
		if pt_sentence[-1] == "?": #atualiza pronomes/advérbios interrogativos se for uma interrogativa
			atualiza_tags(pronomes_int, words, pred_tags, "PT")
			atualiza_tags(adv_int, words, pred_tags, "RGI")
		
		atualiza_tags(adv_neg, words, pred_tags, "NEGA")
		atualiza_tags(pron_relativo, words, pred_tags, "PR") #pronomes relativos
		
		tipo = tipo_de_frase(pred_tags, pt_sentence[-1])
		counter = 0

		
		for i in range(len(words)):
			word = words[i]
			lemma = lemmas[i]
			classe = pred_tags[i]
			indice = 0
			counter += 1
		
			if "NEG" in tipo:
				key = str(indice+counter) + "-" + str(indice+counter+1)
					
				# Adiciona a expressao negativa no verbo se for negação irregular
				if classe.startswith("VM") and "NEGA" in classe and lemma in negativa_irregular:
					if key in exprFaciais:
						exprFaciais[key].append("negativa_headshake")
					else:
						exprFaciais[key] = ["negativa_headshake"]
				# Adicionar expressão no adverbio de negação
				if classe.startswith("NEGA"):
					if key in exprFaciais:
						exprFaciais[key].append("negativa_headshake")
					else:
						exprFaciais[key] = ["negativa_headshake"]
					
			# Adicionar expressão da interrogativa
			if "INT" in tipo:
				key = str(indice+counter) + "-" + str(indice+counter+1)
				#Adiciona a expressao da interrogativa parcial no adverbio
				if (classe.startswith("PT") or classe.startswith("RGI")):
					if key in exprFaciais:
						exprFaciais[key].append("interrogativa_parcial")
					else:
						exprFaciais[key] = ["interrogativa_parcial"]
				#Adiciona a expressao da interrogativa total na preposição e no ultimo gesto da frase
				elif classe.startswith("Fc") or classe.startswith("CC") or classe.startswith("CS") or pt_sentence[-1] == "?":
					if key in exprFaciais:
						exprFaciais[key].append("interrogativa_total")
					else:
						exprFaciais[key] = ["interrogativa_total"]

		if ['interrogativa_total'] in exprFaciais.values():
			lgp_sentence = '{' + lgp_sentence + '}(q)'
		
		elif ['negativa_headshake'] in exprFaciais.values():
			if lgp_sentence.endswith("NÃO"):
				lgp_sentence = lgp_sentence[:-3] + '{' + lgp_sentence[-3:] + '}' + '(headshake)'
			else:
				lgp_sentence = lgp_sentence + " {" + "NÃO}(headshake)" 
			
		elif ['olhos_franzidos'] in exprFaciais.values():
			if lgp_sentence.endswith("NÃO"):
				lgp_sentence = lgp_sentence[:-3] + '(' + lgp_sentence[-3:] + ')'
			else:
				lgp_sentence = lgp_sentence + ' (NÃO)'
		
		file_to_write.write(pt_sentence + "\t" + lgp_sentence + "\n")
		
		line = file_pairs.readline()

def main():
	print("oi")
	freeling_values = freeling.load_freeling(True)
	preprocess(freeling_values)

main()