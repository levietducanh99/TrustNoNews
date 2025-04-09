from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from services.checks import is_phishing_link, is_clickbait, has_sensitive_language, is_fake_news

router = APIRouter()

# ------------- REQUEST MODEL ---------------------- #
class AnalyzeRequest(BaseModel):
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    step: str  # "link_check", "clickbait_check", "sensitive_check", "fakenews_check"
    user_accept_warning: bool = False

# ------------- RESPONSE MODEL --------------------- #
class AnalyzeResponse(BaseModel):
    passed: bool
    warning: Optional[str] = None
    explanation: Optional[str] = None
    next_step: Optional[str] = None

# ------------- MAIN ENDPOINT ---------------------- #
@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if req.step == "link_check":
        if req.url and is_phishing_link(req.url):
            return AnalyzeResponse(
                passed=False,
                warning="Warning: The link may be phishing or not from a trusted domain.",
                explanation="The URL is not in the list of trusted domains like example.com or trustednews.org.",
                next_step="clickbait_check"
            )
        return AnalyzeResponse(passed=True, next_step="clickbait_check")

    elif req.step == "clickbait_check":
        if req.title and req.content and is_clickbait(req.title, req.content):
            return AnalyzeResponse(
                passed=False,
                warning="The title appears to be clickbait.",
                explanation="The title contains shocking words and does not reflect the content accurately.",
                next_step="sensitive_check"
            )
        return AnalyzeResponse(passed=True, next_step="sensitive_check")

    elif req.step == "sensitive_check":
        if req.content and has_sensitive_language(req.content):
            return AnalyzeResponse(
                passed=False,
                warning="The content contains sensitive language.",
                explanation="The article includes provocative or offensive words.",
                next_step="fakenews_check"
            )
        return AnalyzeResponse(passed=True, next_step="fakenews_check")

    elif req.step == "fakenews_check":
        if req.title and is_fake_news(req.title):
            return AnalyzeResponse(
                passed=False,
                warning="The title appears to contain false information.",
                explanation="The term 'illegal' is often used in fake or unverified news.",
                next_step=None
            )
        return AnalyzeResponse(passed=True, explanation="This news appears to be trustworthy.")

    return AnalyzeResponse(passed=False, warning="Invalid step provided.")
