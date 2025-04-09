
# ----------- MOCKUP DATA (for demo purposes) ------------ #
TRUSTED_DOMAINS = ["example.com", "trustednews.org", "reliable.net"]

# ------------- SERVICE FUNCTIONS ------------------- #
def is_phishing_link(url: str) -> bool:
    return not any(domain in url for domain in TRUSTED_DOMAINS)

def is_clickbait(title: str, content: str) -> bool:
    return "shocking" in title.lower() and len(content) > 20

def has_sensitive_language(content: str) -> bool:
    return any(word in content.lower() for word in ["provocative", "offensive", "inflammatory"])

def is_fake_news(title: str) -> bool:
    return "illegal" in title.lower()
