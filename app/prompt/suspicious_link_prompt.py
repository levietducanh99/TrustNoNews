def generate_suspicious_link_prompt(original_url: str, redirected_url: str, is_suspicious: bool) -> str:
    if is_suspicious:
        prompt = (
            "You are a cybersecurity assistant. Please help me check if a link redirects to a suspicious website.\n\n"
            f"Original URL: {original_url}\n"
            f"Redirected URL: {redirected_url}\n"
            "Conclusion: This link **might be suspicious**\n"
            "Explanation: Clicking on this link might redirect you to an untrustworthy website, or it could pose risks such as scams, malware, or phishing pages. "
            "We need to be cautious when accessing this link. For example, if the domain name is strange or contains unusual characters, it could be a sign of a fraudulent site."
            "In summary, be careful and avoid clicking on links whose origins you are unsure of."
        )
    else:
        prompt = (
            "You are a cybersecurity assistant. Please help me check if a link redirects to a suspicious website.\n\n"
            f"Original URL: {original_url}\n"
            f"Redirected URL: {redirected_url}\n"
            "Conclusion: This link **does not appear suspicious**\n"
            "Explanation: Clicking on this link will redirect you to a trustworthy website with no risks of scams or malware. "
            "This site shows no signs of being dangerous. For example, if the website has a familiar domain name and no unusual characters, it is a sign that the site is safe."
            "In summary, you can access this site without worrying about security issues."
        )
    return prompt
