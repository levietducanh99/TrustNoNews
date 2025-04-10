from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
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
        "reason": "",
        "explanation": ""
    }

    # Kiểm tra xem URL có đáng ngờ hoặc nguy hiểm không
    is_suspicious, suspicious_reason = is_suspicious_url(url)
    is_dangerous, dangerous_reason = is_dangerous_domain(url)

    if is_dangerous:
        response["is_suspicious"] = True
        response["reason"] = dangerous_reason
        response["explanation"] = "URL trỏ đến một domain được biết là nguy hiểm."
    elif is_suspicious:
        response["is_suspicious"] = True
        response["reason"] = suspicious_reason
        response["explanation"] = "URL chứa từ khóa hoặc mẫu đáng ngờ."
    elif status:
        # Nếu có cảnh báo (ví dụ: redirect), đánh dấu là đáng ngờ
        response["is_suspicious"] = True
        response["reason"] = status
        original_domain = urlparse(url).netloc.lower().lstrip("www.")
        final_domain = urlparse(final_url).netloc.lower().lstrip("www.") if final_url else original_domain
        if original_domain != final_domain:
            response["explanation"] = f"URL chuyển hướng đến một domain khác ({final_domain}) thay vì domain gốc ({original_domain})."
        else:
            response["explanation"] = "URL có chuyển hướng hoặc các vấn đề khác."

    return response
