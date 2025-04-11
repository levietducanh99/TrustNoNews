from app.services.clickbait_detector import check_suspicious_link


def test_sensitive_language():
    # Ví dụ sử dụng hàm để kiểm tra URL
    original_url = "https://example.com"
    redirected_url = "http://!suspicious-phishing-site.com"
    is_suspicious = True
    # Kiểm tra xem URL có chuyển hướng đến trang đáng ngờ không
    result = check_suspicious_link(original_url, redirected_url, is_suspicious)

    # In ra kết quả
    print(result)




