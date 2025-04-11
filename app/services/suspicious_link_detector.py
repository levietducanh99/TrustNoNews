import requests
from prompts.suspicious_link_prompt import generate_suspicious_link_explanation

def check_suspicious_link(url: str):
    try:
        response = requests.get(url, allow_redirects=True, timeout=5)
        redirected_url = response.url
        is_suspicious = redirected_url != url and (
                any(domain in redirected_url for domain in
                    ["shopee.vn", "bit.ly", "tinyurl", "click"]) or "promo" in redirected_url
        )

    except Exception as e:
        redirected_url = "Không xác định"
        is_suspicious = True

    explanation = generate_suspicious_link_explanation(
        original_url=url,
        redirected_url=redirected_url,
        is_suspicious=is_suspicious
    )

    return {
        "is_suspicious": is_suspicious,
        "redirected_url": redirected_url,
        "reason": "Redirects to suspicious domain" if is_suspicious else "Looks normal",
        "explanation": explanation
    }
