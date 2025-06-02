import os
from openai import OpenAI

from app.prompt.sensitive_prompt import generate_sensitive_explanation

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def check_sensitive_language(url: str):
    """
    Kiểm tra xem nội dung tại URL có sử dụng ngôn từ nhạy cảm không và giải thích lý do.

    :param url: Đường dẫn bài viết
    :return: Dictionary chứa thông tin về nhạy cảm, nhãn phân loại và lời giải thích
    :raises RuntimeError: Nếu có lỗi khi gọi OpenAI
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
        # B4: Gọi OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        explanation = response.choices[0].message.content.strip()

        # B5: Trả về kết quả
        return {
            "is_sensitive": is_sensitive,
            "label": label,
            "explanation": explanation
        }

    except Exception as e:
        raise RuntimeError(f"Lỗi khi gọi OpenAI: {str(e)}")
