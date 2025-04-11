from app.services.clickbait_detector import check_sensitive_language


def test_sensitive_language():
    content = "Bọn đó toàn là một lũ dốt nát, không làm được trò trống gì!"
    is_sensitive = True
    label = "Toxic language"

    result = check_sensitive_language(content, label, is_sensitive)

    # In ra kết quả
    print(result)



