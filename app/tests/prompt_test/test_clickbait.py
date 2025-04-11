from app.services.clickbait_detector import check_clickbait

def test_clickbait_explain():

    title = "You won't believe this!"
    content = "An article about effective weight loss methods. We will reveal a new method you've never heard of."
    similarity = 0.55

    result = check_clickbait(title, content, similarity)

    # Print the result

    print(result)

