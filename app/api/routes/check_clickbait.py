# routers/check_clickbait.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.clickbait_detector import check_clickbait

router = APIRouter()

class ClickbaitRequest(BaseModel):
    url: str

@router.post("/")
def detect_clickbait(request: ClickbaitRequest):
    try:
        result = check_clickbait(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
