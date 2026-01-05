from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained("your_intent_model")

def classify_intents(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    scores = outputs.logits.softmax(-1).tolist()[0]
    # map to your taxonomy
    return scores




### (You’d fine-tune this on maritime intent data — docking, loitering, EEZ queries, etc.)