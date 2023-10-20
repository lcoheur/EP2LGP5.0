import evaluate
import csv
import sys
import pyter

def abrir_csv(corpus, traducoes):
	"""
	Abre os ficheiros com as traduções de referência e as traduções do sistema.
	:param corpus: Ficheiro CSV com as referências
	:param traducoes: Ficheiro CSV com as traduções do sistema
	:return: As linhas do csv referentes traduçoes no corpus de teste e as traduçoes do sistema.
	"""
	references = []
	candidates = []
	with open(corpus) as csvfile:
		for l in csv.reader(csvfile, delimiter='\t'):
			refs = l[1].split("; ")
			references.append(refs)
	with open(traducoes) as csvfile:
		for l in csv.reader(csvfile, delimiter='\t'):
			if len(l):
				candidates.append(l[1])
			else:
				candidates.append('')
	return references, candidates

args = sys.argv
linhas_ref, linhas_cand = abrir_csv(args[1], args[2])

metric_bleu = evaluate.load("bleu")
metric_sacrebleu = evaluate.load("sacrebleu")
metric_rouge = evaluate.load("rouge")
metric_ter = evaluate.load("ter")
metric_meteor = evaluate.load("meteor")
#metric_bert = evaluate.load("bertscore")
#metric_wer = evaluate.load("wer")

results_bleu = metric_bleu.compute(predictions=linhas_cand, references=linhas_ref)
results_rouge = metric_rouge.compute(predictions=linhas_cand, references=linhas_ref)
results_meteor = metric_meteor.compute(predictions=linhas_cand, references=linhas_ref)
#results_bert = metric_bert.compute(predictions=linhas_cand, references=linhas_ref, lang="pt")

max_references = max(len(refs) for refs in linhas_ref)
for i in range(len(linhas_ref)):
	num_missing_refs = max_references - len(linhas_ref[i])
	linhas_ref[i].extend([''] * num_missing_refs)

results_ter = metric_ter.compute(predictions=linhas_cand, references=linhas_ref)
results_sacrebleu = metric_sacrebleu.compute(predictions=linhas_cand, references=linhas_ref)
#results_wer = metric_wer.compute(predictions=linhas_cand, references=linhas_ref)

print("Bleu: ", results_bleu)
print("Sacrebleu: ", results_sacrebleu)
#print("BERT score: ", results_bert)
print("Rouge: ", results_rouge)
print("TER: ", results_ter)
#print("WER: ", results_wer)
print("Meteor: ", results_meteor)