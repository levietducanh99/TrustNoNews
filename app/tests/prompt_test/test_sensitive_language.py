from app.services.clickbait_detector import check_sensitive_language


def test_sensitive_language():
    content = "Those people are all a bunch of fools, incapable of doing anything useful!"
    is_sensitive = True
    label = "Toxic language"

    result = check_sensitive_language(content, label, is_sensitive)

    # Print the result
    print(result)
