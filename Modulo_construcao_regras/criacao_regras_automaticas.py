import re
import argparse
from gensim.models import KeyedVectors
from Elementos_Frasicos import Elementos_frasicos
from Alinhamento import alinhamento_por_elemento
import informacao_gramatical
import create_source_target_file
import subprocess
import sys
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


def criar_objeto(info_lingua, lingua):
	"""
	Guarda um tuplo com a palavra, lema e classe gramatical das palavras que constituem cada elemento frásico.
	:param info_lingua: lista com as informações gramaticais
	:param lingua: lgp ou pt
	:return: lista 25,com o objeto que guarda os elementos frásicos
	"""
	classes = []

	for j in info_lingua:
		info = Elementos_frasicos() #objeto para guardar os elementos frasicos das frases em LGP

		if lingua == "lgp":
			info.tipo_de_frase(j.get_tipo_frase())
			info.set_frase_PT(j.get_frase_pt())
			info.set_transcricao_LGP(j.get_transcricao_lgp())
		for m,v in j.analise_sintatica.items():
			if(m):
				print("m " + m)
			if(v):
				print("v " + v)
			if "ARG_EXT" in v and m in j.lemmas and m in j.classes_gramaticais:
				info.append_sujeito(m.lower(), j.lemmas[m], j.classes_gramaticais[m])

			if "ARG_INT" in v and m in j.lemmas and m in j.classes_gramaticais:
				info.append_objeto(m.lower(),j.lemmas[m], j.classes_gramaticais[m])
				info.append_predicado(m.lower(),j.lemmas[m], j.classes_gramaticais[m])

			if m and len(re.findall(r"v\w*", v.lower()))>0 and m in j.classes_gramaticais and m in j.lemmas:
				info.append_verbo(m.lower(),j.lemmas[m], j.classes_gramaticais[m])
				info.append_predicado(m.lower(),j.lemmas[m], j.classes_gramaticais[m])

			if v=="" and m and m.lower() and m in j.classes_gramaticais and m in j.lemmas:
				info.append_outros(m.lower(),j.lemmas[m],j.classes_gramaticais[m])

		classes.append(info)

	return classes




def main():
	"""
	Função principal para a construção de regras de tradução automáticas.
	Analisa sintatica e morfossintática.
	Alinhamento das palavras e gestos.
	Guarda a frequência das regras de tradução.
	Guarda as regras de tradução.

	:return:
	"""

	parser = argparse.ArgumentParser()

	parser.add_argument('ELANFileComplete', help='ficheiro do ELAN com todas as informações')
	#parser.add_argument('ELANFilePTLGP', help='ficheiro do ELAN apenas com as transcricoes em PT e LGP')

	argss = parser.parse_args()

	ficheiro_html = argss.ELANFileComplete
	#ficheiro_html_PT_LGP = argss.ELANFilePTLGP
	
	

	info_pt, info_lgp, pt_sentences, lgp_sentences = informacao_gramatical.main(ficheiro_html)

	#classes_pt = criar_objeto(info_pt, "pt")
	#classes_lgp = criar_objeto(info_lgp, "lgp")

	#pt_sentences, lgp_sentences = create_source_target_file.main(ficheiro_html_PT_LGP)

	#embeddings = KeyedVectors.load_word2vec_format(
	#	'Word_embeddings/glove_s600.txt', binary=False,
	#	unicode_errors="ignore")
	
	nltk.download('stopwords')

	src_file = open("source_corpus_new.txt", "a")
	trg_file = open("target_corpus_new.txt", "a")
	pairs_file = open("new_pairs_pt_lgp.txt", "a")

	pairs_file.write("File: " + ficheiro_html + "\n")

	for i in range(len(pt_sentences)):
		frasept = pt_sentences[i]
		fraselgp = lgp_sentences[i]

		if frasept and fraselgp:
			frasept.lower()
			fraselgp.lower()

			frasept_tokens = word_tokenize(frasept)
			frasept_tokens_without_sw = [word for word in frasept_tokens if not word in stopwords.words()]

			fraselgp_tokens = word_tokenize(fraselgp)
			fraselgp_tokens_without_sw = [word for word in fraselgp_tokens if not word in stopwords.words()]

			frasept_clean = ""
			fraselgp_clean = ""

			punctuation = "!;‘“\,<>./?@#$%^&*`'"

			for c in frasept_tokens:
				#if c not in punctuation:
				if frasept_clean:
					frasept_clean = frasept_clean + " " + c
				else:
					frasept_clean += c
			
			for c in fraselgp_tokens:
				#if c not in punctuation:
				if fraselgp_clean:
					fraselgp_clean = fraselgp_clean + " " + c
				else:
					fraselgp_clean += c


			if frasept_clean and fraselgp_clean:
				src_file.write(frasept_clean + "\n")
				trg_file.write(fraselgp_clean + "\n")
				pairs_file.write(frasept_clean + "\t" + fraselgp_clean + "\n")

	#alinhamento_por_elemento(classes_pt, classes_lgp, embeddings)

 
main()

