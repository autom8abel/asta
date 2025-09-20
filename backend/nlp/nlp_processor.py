import spacy
from transformers import pipeline

# Load spaCy model for entity extraction
nlp_spacy = spacy.load("en_core_web_sm")

# Load Hugging Face pipeline for intent classification
# For MVP, we use a general-purpose text classification model
intent_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

def extract_entities(text: str):
    """
    Extracts entities (like dates, times, people, orgs) using spaCy.
    Returns a dictionary of entity label -> text.
    """
    doc = nlp_spacy(text)
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text
    return entities

def detect_intent(text: str):
    """
    Detects user intent using Hugging Face pipeline.
    Returns the predicted intent label.
    """
    results = intent_classifier(text)
    return results[0]['label']

def parse_input(text: str):
    """
    Processes raw user input into structured JSON.
    - Detects intent
    - Extracts entities
    """
    intent = detect_intent(text)
    entities = extract_entities(text)
    return {
        "intent": intent,
        "entities": entities
    }

if __name__ == "__main__":
    sample = "Remind me tomorrow at 5 pm to study math."
    print(parse_input(sample))
