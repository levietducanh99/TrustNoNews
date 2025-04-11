from app.services.generate_prompt import check_sensitive_language


def test_sensitive_language():
    content = "Those people are all a bunch of fools, incapable of doing anything useful!"
    is_sensitive = True
    label = "Toxic language"
    criteria = [
        {"label": "Offensive", "description": "Contains offensive language", "probability": 0.85},
        {"label": "Harmful", "description": "May cause harm to individuals or groups", "probability": 0.75},
    ]

    result = check_sensitive_language(content, label, is_sensitive, criteria)

    # Print the result
    print(result)
