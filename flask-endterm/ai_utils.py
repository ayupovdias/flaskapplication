from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")


def analyze_description(text):
    result = sentiment_pipeline(text[:1500])[0]
    return result['label'], result['score']
