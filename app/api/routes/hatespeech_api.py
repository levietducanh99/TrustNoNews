from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from app.utils.Scraper.scraper import scrape
from app.services.check_hatespeech import check_hatespeech
from app.services.generate_prompt import check_sensitive_language

router = APIRouter()

# Load model and tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")
    model = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")
except Exception as e:
    raise Exception(f"Failed to load model or tokenizer: {e}")

# Define labels and descriptions
labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]
criteria_descriptions = {
    "toxic": "General hostile or negative language",
    "severe_toxic": "Severely hostile or extremely harmful language",
    "obscene": "Obscene or vulgar language",
    "threat": "Threatening or dangerous language",
    "insult": "Personal insults",
    "identity_hate": "Discrimination based on identity (region, gender, etc.)"
}

# Define request and response models
class HateSpeechRequest(BaseModel):
    url: str
    threshold: float = 0.5  # Default threshold

class HateSpeechResponse(BaseModel):
    content_snippet: str
    criteria: list[dict]
    detected: bool
    conclusion: str
    confidence: float
    main_label: str = None
    detected_labels: list[dict] = None
    title: str = None
    explanation: str = None

# Helper function to analyze content
def analyze_hatespeech(content: str, threshold: float) -> dict:
    if not content:
        return {"error": "No content to analyze"}

    inputs = tokenizer(content, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.sigmoid(outputs.logits).squeeze().tolist()
    results = {label: prob for label, prob in zip(labels, probabilities)}
    detected_labels = [(label, prob) for label, prob in results.items() if prob > threshold]

    response = {
        "content_snippet": content[:200] + "..." if len(content) > 200 else content,
        "criteria": [
            {"label": label, "description": criteria_descriptions[label], "probability": prob}
            for label, prob in results.items()
        ],
        "detected": bool(detected_labels)
    }

    if detected_labels:
        max_prob = max(prob for _, prob in detected_labels)
        max_label = [label for label, prob in detected_labels if prob == max_prob][0]
        # Call check_sensitive_language to generate explanation
        sensitive_result = check_sensitive_language(
            content=content,
            label=max_label,
            is_sensitive=True,
            criteria = response["criteria"]
        )
        response.update({
            "conclusion": "Content contains hate speech",
            "main_label": max_label,
            "confidence": max_prob,
            "detected_labels": [
                {"label": label, "probability": prob}
                for label, prob in detected_labels
            ],
            "explanation": sensitive_result.get("explanation", "No explanation available")
        })
    else:
        max_prob = max(probabilities)
        # Call check_sensitive_language to generate explanation for non-sensitive content
        sensitive_result = check_sensitive_language(
            content=content,
            label="none",
            is_sensitive=False,
            criteria = response["criteria"]
        )
        response.update({
            "conclusion": "Content does not contain hate speech",
            "confidence": max(1 - max_prob, 0),
            "explanation": sensitive_result.get("explanation", "No explanation available")
        })

    return response

# Endpoint to check hate speech from URL
@router.post("/check-hatespeech", response_model=HateSpeechResponse)
async def check_hatespeech(request: HateSpeechRequest):
    try:
        scrape_result = scrape(request.url)
        if "error" in scrape_result:
            raise HTTPException(status_code=400, detail=f"Scraping failed: {scrape_result['error']}")

        content = scrape_result.get("content", "")
        if not content:
            raise HTTPException(status_code=400, detail="Scraped content is empty")

        result = analyze_hatespeech(content, request.threshold)
        result["title"] = scrape_result.get("title", "No title available")
        result["criteria"] = result.get("criteria", [])  # Ensure criteria is included in the response
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

