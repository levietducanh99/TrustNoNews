from app.services.clickbait_detector import check_fake_news


def test_clickbait_explain():
    title = "Warning: Cybercriminals are attacking all banks!"
    similar_titles = ["Banks warn about cyberattacks",
                      "Cybercrime increases at financial institutions"]
    scores = [0.65, 0.9]

    result = check_fake_news(title, similar_titles, scores)

    # Print the result
    print(result)
