from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.Scraper.scraper import scrape
from app.services.clickbait_detector import check_clickbait

router = APIRouter()

class ClickbaitRequest(BaseModel):
    url: str

@router.post("/check-clickbait")
def detect_clickbait(request: ClickbaitRequest):
    try:
        # Scrape the webpage to extract title and content
        scrape_result = scrape(request.url)
        title = scrape_result.get("title", "")
        content = scrape_result.get("content", "")

        # Call the clickbait detector service
        result = check_clickbait(title, content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
