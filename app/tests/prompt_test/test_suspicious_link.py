from app.services.clickbait_detector import check_suspicious_link


def test_sensitive_language():
    # Example usage of the function to check a URL
    original_url = "https://example.com"
    redirected_url = "http://!suspicious-phishing-site.com"
    is_suspicious = True
    # Check if the URL redirects to a suspicious site
    result = check_suspicious_link(original_url, redirected_url, is_suspicious)

    # Print the result
    print(result)
