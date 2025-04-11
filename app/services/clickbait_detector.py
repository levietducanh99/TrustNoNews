from app.prompt.clickbait_prompt import generate_clickbait_prompt
from app.prompt.fake_news_prompt import generate_fake_news_prompt
from app.prompt.sensitive_prompt import generate_sensitive_prompt
from app.prompt.suspicious_link_prompt import generate_suspicious_link_prompt
import ollama
# phóng đại, giật gân
def check_clickbait(title: str, content: str, similarity: float):
    if not title or not content:
        raise ValueError("Tiêu đề và nội dung bài viết không được để trống.")
    is_clickbait = similarity < 0.6
    summary = content
    # Sinh prompt tiếng Việt
    prompt = generate_clickbait_prompt(
        title=title,
        content_summary=summary,
        similarity_score=similarity,
        is_clickbait=is_clickbait
    )
    try:
# Gọi mô hình Ollama (stream)
        response_stream = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        explanation = ""
        # In ra từng chunk từ stream
        for chunk in response_stream:
            if "message" in chunk:
                explanation += chunk["message"]["content"]

        # Trả về kết quả dưới dạng dictionary
        return {
            "is_clickbait": is_clickbait,
            "similarity_score": similarity,
            "explanation": explanation.strip()
        }
    except Exception as e:
        # Xử lý lỗi nếu có trong khi gọi API
        raise RuntimeError(f"Lỗi khi gọi API Ollama: {str(e)}")

# tin giả
def check_fake_news(title: str, similar_titles: list, scores: list) -> dict:
    """
    Kiểm tra xem một tiêu đề có phải là tin giả không và giải thích lý do.
    :param title: Tiêu đề bài viết
    :param similar_titles: Danh sách các tiêu đề tương tự từ các nguồn tin uy tín
    :param scores: Danh sách các điểm tương đồng giữa tiêu đề cần kiểm tra và các tiêu đề uy tín
    :return: Dictionary chứa thông tin về tin giả, độ tương đồng và lời giải thích
    :raises ValueError: Nếu tiêu đề hoặc các thông tin liên quan bị thiếu
    :raises RuntimeError: Nếu có lỗi khi gọi API Ollama
    """
    # Kiểm tra đầu vào
    if not title or not similar_titles or not scores:
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
        # Gọi mô hình Ollama với stream
        response_stream = ollama.chat(
            model="mistral",  # Mô hình sử dụng
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        explanation = ""
        # Duyệt qua từng chunk từ stream
        for chunk in response_stream:
            if "message" in chunk:
                explanation += chunk["message"]["content"]

        # Trả về kết quả dưới dạng dictionary
        return {
            "is_fake": is_fake,
            "similarity_scores": scores,
            "explanation": explanation.strip()
        }

    except Exception as e:
        # Xử lý lỗi khi gọi API
        raise RuntimeError(f"Lỗi khi gọi API Ollama: {str(e)}")
# ngôn ngữ nhạy cảm
def check_sensitive_language(content: str, label: str, is_sensitive: bool) -> dict:
    # B3: Tạo prompt tiếng Việt
    prompt = generate_sensitive_prompt(
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


def check_suspicious_link(original_url: str, redirected_url: str, is_suspicious: bool) -> dict:
    """
    Kiểm tra xem một đường link có chuyển hướng đến trang đáng ngờ hay không và giải thích lý do.

    :param original_url: URL gốc (trước khi chuyển hướng)
    :param redirected_url: URL sau khi chuyển hướng
    :return: Dictionary chứa kết luận và lời giải thích
    :raises ValueError: Nếu URL gốc hoặc URL sau khi chuyển hướng bị thiếu
    :raises RuntimeError: Nếu có lỗi khi gọi API Ollama
    """
    # Kiểm tra đầu vào
    if not original_url or not redirected_url:
        raise ValueError("Cả URL gốc và URL sau khi chuyển hướng đều không được để trống.")

    # Logic xác định xem URL có đáng ngờ hay không
    # Bạn có thể thay đổi cách xác định này tùy theo yêu cầu

    # Sinh prompt để gửi đến Ollama
    prompt = generate_suspicious_link_prompt(original_url, redirected_url, is_suspicious)

    try:
        # Gọi mô hình Ollama để lấy lời giải thích
        response_stream = ollama.chat(
            model="mistral",  # Mô hình sử dụng
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )

        explanation = ""
        # Duyệt qua từng chunk từ stream
        for chunk in response_stream:
            if "message" in chunk:
                explanation += chunk["message"]["content"]

        # Trả về kết quả dưới dạng dictionary
        return {
            "is_suspicious": is_suspicious,
            "original_url": original_url,
            "redirected_url": redirected_url,
            "explanation": explanation.strip()
        }

    except Exception as e:
        # Xử lý lỗi khi gọi API
        raise RuntimeError(f"Lỗi khi gọi API Ollama: {str(e)}")