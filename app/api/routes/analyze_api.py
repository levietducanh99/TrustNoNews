from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.routes.check_clickbait_api import detect_clickbait, ClickbaitRequest
from app.api.routes.check_link_api import check_link, URLRequest
from app.api.routes.check_similarity_api import check_fake_news, FakeNewsRequest
from app.api.routes.hatespeech_api import check_hatespeech, HateSpeechRequest
import numpy as np

from app.utils.Scraper.scraper import scrape

router = APIRouter()

# Define the request model
class AnalyzeRequest(BaseModel):
    url: str

# Define the response model
class AnalyzeResponse(BaseModel):
    url: str
    link_check: dict
    clickbait: dict
    fake_news: dict
    sensitive_language: dict

def convert_numpy_types(obj):
    """
    Recursively convert numpy types to Python native types to ensure JSON serializability.
    """
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return convert_numpy_types(obj.tolist())
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")
    try:
        # Step 1: Check link
        link_check_result = await check_link(URLRequest(url=url))

        # Step 2: Check clickbait
        clickbait_result = detect_clickbait(ClickbaitRequest(url=url))

        # Step 3: Check fake news
        fake_news_result = await check_fake_news(FakeNewsRequest(url=url))

        # Step 4: Check hate speech
        hatespeech_result = await check_hatespeech(HateSpeechRequest(url=url))

        # Convert NumPy types to Python native types for all results
        link_check_result = convert_numpy_types(link_check_result)
        clickbait_result = convert_numpy_types(clickbait_result)
        fake_news_result = convert_numpy_types(fake_news_result)
        hatespeech_result = convert_numpy_types(hatespeech_result)

        # Aggregate results
        response = {
            "url": url,
            "link_check": link_check_result,
            "clickbait": clickbait_result,
            "fake_news": fake_news_result,
            "sensitive_language": hatespeech_result,
        }
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
