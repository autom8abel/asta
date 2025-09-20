import spacy
from transformers import pipeline

# Load spaCy for entities
nlp_spacy = spacy.load("en_core_web_sm")

# Hugging Face pipeline (still useful, fallback sentiment check)
intent_classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")

# Minimal ASTA intents
ASTA_INTENTS = {
    "create_task": ["remind", "add", "schedule", "create"],
    "get_tasks": ["show", "list", "tasks", "what do I", "fetch"],
    "delete_task": ["delete", "remove", "cancel"],
}

def extract_entities(text: str):
    doc = nlp_spacy(text)
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text
    return entities

def detect_intent(text: str):
    # Rule-based mapping
    lowered = text.lower()
    for intent, keywords in ASTA_INTENTS.items():
        if any(keyword in lowered for keyword in keywords):
            return intent

    # Fallback to Hugging Face sentiment model
    result = intent_classifier(text)[0]['label']
    return f"general_chat_{result.lower()}"

def parse_input(text: str):
    intent = detect_intent(text)
    entities = extract_entities(text)
    return {
        "intent": intent,
        "entities": entities
    }

if __name__ == "__main__":
    samples = [
        "Remind me tomorrow at 5 pm to study math.",
        "Show me my tasks for today.",
        "Delete the meeting task.",
        "How are you today?"
    ]
    for s in samples:
        print(s, "->", parse_input(s))
