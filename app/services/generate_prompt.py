import os
from dotenv import load_dotenv
import google.generativeai as genai
from app.prompt.clickbait_prompt import generate_clickbait_prompt
from app.prompt.fake_news_prompt import generate_fake_news_prompt
from app.prompt.sensitive_prompt import generate_sensitive_prompt
from app.prompt.suspicious_link_prompt import generate_suspicious_link_prompt

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create Gemini model
gemini_model = genai.GenerativeModel('gemini-1.0-pro')

# phóng đại, giật gân
def check_clickbait_1(title: str, content: str, similarity: float):
    if not title or not content:
        raise ValueError("Tiêu đề và nội dung bài viết không được để trống.")
    is_clickbait = similarity < 0.6

    # Use Gemini to summarize the content
    try:
        summary_prompt = f"Tóm tắt nội dung: {content}"
        summary_response = gemini_model.generate_content(summary_prompt)
        summary = summary_response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Lỗi khi gọi API Gemini để tóm tắt: {str(e)}")

    # Sinh prompt tiếng Việt
    prompt = generate_clickbait_prompt(
        title=title,
        content_summary=summary,
        similarity_score=similarity,
        is_clickbait=is_clickbait
    )
    try:
        response = gemini_model.generate_content(prompt)
        explanation = response.text.strip()
        return explanation
    except Exception as e:
        # Xử lý lỗi nếu có trong khi gọi API
        raise RuntimeError(f"Lỗi khi gọi API Gemini: {str(e)}")

# tin giả
def check_fake_news(title: str, similar_titles: list, scores: list) -> dict:
    """
    Kiểm tra xem một tiêu đề có phải là tin giả không và giải thích lý do.
    :param title: Tiêu đề bài viết
    :param similar_titles: Danh sách các tiêu đề tương tự từ các nguồn tin uy tín
    :param scores: Danh sách các điểm tương đồng giữa tiêu đề cần kiểm tra và các tiêu đề uy tín
    :return: Dictionary chứa thông tin về tin giả, độ tương đồng và lời giải thích
    :raises ValueError: Nếu tiêu đề hoặc các thông tin liên quan bị thiếu
    :raises RuntimeError: Nếu có lỗi khi gọi API Gemini
    """
    # Kiểm tra đầu vào
    if not title or similar_titles or scores:
        raise ValueError("Tiêu đề, tiêu đề tương tự và điểm tương đồng không được để trống.")
    # Xác định tin có phải giả hay không dựa trên điểm tương đồng
    is_fake = all(score < 0.3 for score in scores)
    prompt = generate_fake_news_prompt(
        title=title,
        similar_titles=similar_titles,
        scores=scores,
        is_fake=is_fake
    )

    try:
        response = gemini_model.generate_content(prompt)
        explanation = response.text.strip()

        # Trả về kết quả dưới dạng dictionary
        return {
            "is_fake": is_fake,
            "similarity_scores": scores,
            "explanation": explanation
        }

    except Exception as e:
        # Xử lý lỗi khi gọi API
        raise RuntimeError(f"Lỗi khi gọi API Gemini: {str(e)}")

# ngôn ngữ nhạy cảm
def check_sensitive_language(content: str, label: str, is_sensitive: bool, criteria: list) -> dict:
    # B3: Tạo prompt tiếng Việt
    prompt = generate_sensitive_prompt(
        label=label,
        text=content,
        is_sensitive=is_sensitive,
        criteria=criteria
    )

    try:
        response = gemini_model.generate_content(prompt)
        explanation = response.text.strip()

        # B5: Trả về kết quả
        return {
            "is_sensitive": is_sensitive,
            "label": label,
            "explanation": explanation
        }

    except Exception as e:
        raise RuntimeError(f"Lỗi khi gọi Gemini: {str(e)}")


def check_suspicious_link(original_url: str, redirected_url: str, is_suspicious: bool) -> dict:
    """
    Kiểm tra xem một đường link có chuyển hướng đến trang đáng ngờ hay không và giải thích lý do.

    :param original_url: URL gốc (trước khi chuyển hướng)
    :param redirected_url: URL sau khi chuyển hướng
    :return: Dictionary chứa kết luận và lời giải thích
    :raises ValueError: Nếu URL gốc hoặc URL sau khi chuyển hướng bị thiếu
    :raises RuntimeError: Nếu có lỗi khi gọi API Gemini
    """
    # Kiểm tra đầu vào
    if not original_url or redirected_url:
        raise ValueError("Cả URL gốc và URL sau khi chuyển hướng đều không được để trống.")

    # Sinh prompt để gửi đến Gemini
    prompt = generate_suspicious_link_prompt(original_url, redirected_url, is_suspicious)

    try:
        response = gemini_model.generate_content(prompt)
        explanation = response.text.strip()

        # Trả về kết quả dưới dạng dictionary
        return {
            "is_suspicious": is_suspicious,
            "original_url": original_url,
            "redirected_url": redirected_url,
            "explanation": explanation
        }

    except Exception as e:
        # Xử lý lỗi khi gọi API
        raise RuntimeError(f"Lỗi khi gọi API Gemini: {str(e)}")
