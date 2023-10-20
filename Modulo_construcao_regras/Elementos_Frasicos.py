class Elementos_frasicos:
	"""Guardar as palavras, lemmas e classes gramaticais do léxico que constitui os diferentes elementos frásicos."""

	def __init__(self):
		self.sujeito = []
		self.verbo = []
		self.objeto = []
		self.predicado = []
		self.outros = []
		self.tipo_frase = ""
		self.transcricao_LGP = ""
		self.frase_PT = ""

	def tipo_de_frase(self, info):
		self.tipo_frase = info

	def get_tipo_de_frase(self):
		return self.tipo_frase

	def set_frase_PT(self, frase_pt):
		self.frase_PT += frase_pt if self.frase_PT == "" else self.frase_pt

	def get_frase_PT(self):
		return self.frase_PT
	
	def set_transcricao_LGP(self, sentence):
		self.transcricao_LGP += sentence if self.transcricao_LGP == "" else self.transcricao_LGP
	
	def get_transcricao_LGP(self):
		return self.transcricao_LGP

	def append_sujeito(self, info_1, info_2, info_3):
		self.sujeito.append((info_1, info_2, info_3))

	def append_verbo(self, info_1, info_2, info_3):
		self.verbo.append((info_1, info_2, info_3))

	def append_objeto(self, info_1, info_2, info_3):
		self.objeto.append((info_1, info_2, info_3))

	def append_predicado(self, info_1, info_2, info_3):
		self.predicado.append((info_1, info_2, info_3))

	def append_outros(self, info_1, info_2, info_3):
		self.outros.append((info_1, info_2, info_3))

	def get_objeto(self):
		return self.objeto

	def get_sujeito(self):
		return self.sujeito

	def get_verbo(self):
		return self.verbo




