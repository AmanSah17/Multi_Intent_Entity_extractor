# Use lighter transformer NER or spaCy + rules
from transformers import pipeline

ner = pipeline("ner", model="distilbert-ner", grouped_entities=True)

def extract_probabilistic_entities(text):
    return ner(text)





#🔁 Session Context & Multi-Staged Intents


"""
You can represent complex hierarchical intents as:

[
  {"intent": "ANALYZE_BEHAVIOR", "children": [
      {"intent": "LOITERING"},
      {"intent": "EEZ_VIOLATION"}
  ]}
]


Your orchestrator can convert this to a DAG or workflow for execution.
"""