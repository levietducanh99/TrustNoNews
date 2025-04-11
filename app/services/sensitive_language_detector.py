import ollama

from app.prompt.sensitive_prompt import generate_sensitive_explanation

def check_sensitive_language(url: str):
    """
    Kiểm tra xem nội dung tại URL có sử dụng ngôn từ nhạy cảm không và giải thích lý do.

    :param url: Đường dẫn bài viết
    :return: Dictionary chứa thông tin về nhạy cảm, nhãn phân loại và lời giải thích
    :raises RuntimeError: Nếu có lỗi khi gọi Ollama
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
        # B4: Gọi mô hình Ollama với stream
        response_stream = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        explanation = ""
        for chunk in response_stream:
            if "message" in chunk:
                explanation += chunk["message"]["content"]

        # B5: Trả về kết quả
        return {
            "is_sensitive": is_sensitive,
            "label": label,
            "explanation": explanation.strip()
        }

    except Exception as e:
        raise RuntimeError(f"Lỗi khi gọi Ollama: {str(e)}")
