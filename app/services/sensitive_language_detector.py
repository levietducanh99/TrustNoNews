import os
from dotenv import load_dotenv
import google.generativeai as genai

from app.prompt.sensitive_prompt import generate_sensitive_explanation

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Create Gemini model
gemini_model = genai.GenerativeModel('gemini-1.0-pro')

def check_sensitive_language(url: str):
    """
    Kiểm tra xem nội dung tại URL có sử dụng ngôn từ nhạy cảm không và giải thích lý do.

    :param url: Đường dẫn bài viết
    :return: Dictionary chứa thông tin về nhạy cảm, nhãn phân loại và lời giải thích
    :raises RuntimeError: Nếu có lỗi khi gọi Gemini
    """
    # B1: Trích xuất nội dung
    content = extract_content(url)

    # B2: Dự đoán nhãn và mức độ nhạy cảm
    label, is_sensitive = predict_sensitive_label(content)

    # B3: Tạo prompt tiếng Việt
    prompt = generate_sensitive_explanation(
        label=label,
        text=content,
        is_sensitive=is_sensitive
    )

    try:
        # B4: Gọi Gemini API
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
