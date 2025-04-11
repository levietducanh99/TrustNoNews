from app.services.clickbait_detector import check_fake_news


def test_clickbait_explain():
    title = "Cảnh báo: Tội phạm mạng đang tấn công tất cả các ngân hàng!"
    similar_titles = ["Các ngân hàng cảnh báo về các cuộc tấn công mạng",
                      "Tội phạm mạng gia tăng tại các tổ chức tài chính"]
    scores = [0.65, 0.9]

    result = check_fake_news(title, similar_titles, scores)

    # In ra kết quả
    print(result)



