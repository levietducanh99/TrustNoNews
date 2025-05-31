from app.utils.Similarity.VectorSimilarity import get_similarity
from app.utils.Summary.summary_mistral import summarize_text
from app.prompt.clickbait_prompt import generate_clickbait_prompt
import ollama
import joblib
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import re
import os

# Define paths to model and tokenizer
MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clickbait', 'clickbait_model.h5')
TOKENIZER_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'clickbait', 'tokenizer.pkl')

# Define clickbait words for additional analysis
CLICKBAIT_WORDS = ['shocking', 'wow', 'unbelievable', 'amazing',
                  'you won\'t believe', 'mind-blowing', 'outrageous',
                  'secret', 'never seen before', 'warning', 'urgent',
                  'conspiracy', 'exposed', 'miracle', 'this is why',
                  'banned', 'controversial', 'breaking', 'things', 'NOT']

# Load the model and tokenizer
try:
    clickbait_model = load_model(MODEL_PATH)
    tokenizer = joblib.load(TOKENIZER_PATH)
    model_loaded = True
    print("Clickbait detection model and tokenizer loaded successfully.")
except Exception as e:
    model_loaded = False
    print(f"Error loading clickbait model: {str(e)}")

def preprocess_text(text):
    """Clean and normalize text data"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def predict_clickbait(title, maxlen=500):
    """Predict if a title is clickbait using the trained model"""
    if not model_loaded:
        return {"is_clickbait": False, "probability": 0.0, "clickbait_words": []}
        
    clean_title = preprocess_text(title)
    token_text = pad_sequences(tokenizer.texts_to_sequences([clean_title]), maxlen=maxlen)
    probability = clickbait_model.predict(token_text, verbose=0)[0][0]
    prediction = round(probability)

    clickbait_words_found = [word for word in CLICKBAIT_WORDS
                           if word.lower() in clean_title.lower()]

    return {
        'is_clickbait': bool(prediction),
        'probability': float(probability),
        'clickbait_words': clickbait_words_found
    }

def check_clickbait(title: str, content: str):
    # Get model-based clickbait prediction
    model_prediction = predict_clickbait(title)
    
    # Summarize the content
    summary = summarize_text(content)

    # Calculate similarity between the title and the summary
    try:
        similarity = get_similarity(title, summary)
    except Exception as e:
        similarity = 0.0  # Default similarity if error occurs
        print(f"Error calculating similarity: {e}")

    # Determine if the content is clickbait using both approaches
    # Consider it clickbait if either the model says so or similarity is low
    is_clickbait = model_prediction["is_clickbait"] or similarity < 0.65

    # Generate an explanation for the result
    prompt = generate_clickbait_prompt(
        title=title,
        content_summary=summary,
        similarity_score=similarity,
        is_clickbait=is_clickbait
    )

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )

    explanation = response.get("message", {}).get("content", "").strip()

    return {
        "is_clickbait": bool(is_clickbait),
        "similarity_score": float(similarity),
        "model_prediction": {
            "is_clickbait": model_prediction["is_clickbait"],
            "probability": model_prediction["probability"],
            "clickbait_words": model_prediction["clickbait_words"]
        },
        "explanation": explanation,
        "summary": summary,
        "title": title
    }
