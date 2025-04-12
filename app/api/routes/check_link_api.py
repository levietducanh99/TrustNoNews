from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
import re
from typing import List, Optional, Dict, Any
from app.services.redirect_checker import check_redirect_and_validate, is_suspicious_url, is_dangerous_domain

router = APIRouter()

# Định nghĩa model cho request body
class URLRequest(BaseModel):
    url: str

# Định nghĩa model cho response
class URLResponse(BaseModel):
    is_suspicious: bool
    redirected_url: str
    reason: str
    explanation: str
    redirect_chain: List[Dict[str, Any]]

def clean_reason_message(message):
    """Clean up and format the reason message to avoid duplication."""
    if not message:
        return ""
    
    # Extract the most significant reason if there are multiple
    if " | " in message:
        parts = message.split(" | ")
        # Prioritize dangerous domains
        for part in parts:
            if "NGUY HIỂM" in part:
                return part
        # Then consider the first suspicious item
        for part in parts:
            if "ĐÁNG NGỜ" in part:
                return part
        # Fall back to the first message
        return parts[0]
    
    return message

@router.post("/check-link", response_model=URLResponse)
async def check_link(request: URLRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="Thiếu 'url' trong body yêu cầu")

    final_url, status, redirect_chain = check_redirect_and_validate(url)

    # Chuẩn bị phản hồi
    response = {
        "is_suspicious": False,
        "redirected_url": final_url if final_url else url,
        "reason": "Looks normal",
        "explanation": "No issues detected",
        "redirect_chain": redirect_chain or []
    }

    # Kiểm tra xem URL có đáng ngờ hoặc nguy hiểm không
    is_suspicious, suspicious_reason = is_suspicious_url(url)
    is_dangerous, dangerous_reason = is_dangerous_domain(url)

    if is_dangerous:
        response["is_suspicious"] = True
        response["reason"] = dangerous_reason
        response["explanation"] = "The URL points to a domain known to be dangerous."
    elif is_suspicious:
        response["is_suspicious"] = True
        response["reason"] = suspicious_reason
        response["explanation"] = "The URL contains suspicious keywords or patterns."
    elif status:
        # If there is a warning (e.g., redirect), mark as suspicious
        response["is_suspicious"] = True
        response["reason"] = clean_reason_message(status)
        
        original_domain = urlparse(url).netloc.lower().lstrip("www.")
        final_domain = urlparse(final_url).netloc.lower().lstrip("www.") if final_url else original_domain
        
        if original_domain != final_domain:
            response[
                "explanation"] = f"The URL redirects to a different domain ({final_domain}) instead of the original domain ({original_domain})."
        else:
            response["explanation"] = "The URL has a redirect or other issues."

    return response
