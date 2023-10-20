from transformers import AutoModelForTokenClassification, AutoTokenizer
import torch

# parameters
model_name = "pierreguillou/ner-bert-large-cased-pt-lenerbr"
model = AutoModelForTokenClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)


def entity_recognition(sentence):
    list_tokens = []
    entities = []

    # tokenization
    inputs = tokenizer(sentence, max_length=512, truncation=True, return_tensors="pt")
    tokens = inputs.tokens()

    # get predictions
    outputs = model(**inputs).logits
    predictions = torch.argmax(outputs, dim=2)

    person = ["B-PESSOA", "I-PESSOA", "O-PESSOA"]
    # print predictions
    for token, prediction in zip(tokens, predictions[0].numpy()):
        if model.config.id2label[prediction] in person:
            list_tokens.append(token)
            #print((token, model.config.id2label[prediction]))

    for token in list_tokens:
        if token.startswith("##"):
            if entities and not entities[-1].startswith("##"):
                entities[-1] += token[2:]
            else:
                entities.append(token)
        else:
            entities.append(token) 
    return entities

""" # tokenization
sentence = "é acolá, senhor Simão"

inputs = tokenizer(sentence, max_length=512, truncation=True, return_tensors="pt")
tokens = inputs.tokens()

# get predictions
outputs = model(**inputs).logits
predictions = torch.argmax(outputs, dim=2)

person = ["B-PESSOA", "I-PESSOA", "O-PESSOA"]
# print predictions
for token, prediction in zip(tokens, predictions[0].numpy()):
    if model.config.id2label[prediction] in person:
        #list_tokens.append(token)
        print(token, model.config.id2label[prediction]) """
