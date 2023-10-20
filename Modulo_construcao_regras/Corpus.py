class Info_Corpus:
	"""
	Classe das informações extraídas do corpus.
	"""

	def __init__(self):
		self.frase_pt = ""
		self.frase_lgp = ""
		self.glosses = []
		self.transcricao_lgp = ""
		self.tipo_frase = ""
		self.initial_time_final_time = 0
		self.initial_time = 0
		self.final_time = 0
		self.classes_gramaticais = {}
		self.analise_sintatica = {}
		self.lemmas = {}
		self.time_frase_lgp = []

	def set_frase_pt(self, frase_pt):
		if frase_pt == None:
			self.frase_pt == ""
		elif self.frase_pt == "":
			self.frase_pt += frase_pt
		else:
			self.frase_pt += ";" + frase_pt
		
	def get_frase_pt(self):
		return self.frase_pt

	def append_transcricao_lgp(self, sentence):
		if self.transcricao_lgp == "":
			self.transcricao_lgp += sentence
		else:
			self.transcricao_lgp += ";" + sentence

	def get_transcricao_lgp(self):
		return self.transcricao_lgp
	
	def set_time(self, init_final_time):
		self.initial_time_final_time = init_final_time

	def append_frase_lgp(self, text):
		self.frase_lgp += text if self.frase_lgp == "" else " " + text
		self.glosses.append(text)

	def get_frase_lgp(self):
		return self.frase_lgp

	def get_glosses(self):
		return self.glosses
	
	def append_time_frase_lgp(self, text):
		self.time_frase_lgp.append(text)

	def get_time_frase_lgp(self):
		return self.time_frase_lgp

	def append_classes_gramaticais(self, glosa, classe):
		self.classes_gramaticais[glosa] = classe

	def append_analise_sintatica(self, glosa, classe):
		if glosa not in self.analise_sintatica.keys():
			self.analise_sintatica[glosa] = classe

	def append_lemmas(self, glosa, lemma):
		self.lemmas[glosa] = lemma

	def append_tipo_frase(self, tipo):
		self.tipo_frase = tipo

	def get_tipo_frase(self):
		return self.tipo_frase

	def __str__(self):
		return f"Frase pt: {self.frase_pt}\nFrase lgp: {self.transcricao_lgp}\nGlosas: {self.frase_lgp}\nTipo frase: {self.tipo_frase}\nClasses Gramaticais: {self.classes_gramaticais}\
			\nAnalise Sintatica: {self.analise_sintatica}\nLemmas: {self.lemmas}"

