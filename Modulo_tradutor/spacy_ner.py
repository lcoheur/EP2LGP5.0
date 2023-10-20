import spacy
from spacy import displacy
from collections import Counter
import pandas as pd
pd.options.display.max_rows = 600
pd.options.display.max_colwidth = 400


import pt_core_news_md
nlp = pt_core_news_md.load()


document = nlp("O José é muito querido.")

for named_entity in document.ents:
    print(named_entity, named_entity.label_)

for named_entity in document.ents:
    if named_entity.label_ == "PER":
        print(named_entity)