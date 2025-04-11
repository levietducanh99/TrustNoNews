def generate_fake_news_prompt(title: str, similar_titles: list, scores: list, is_fake: bool) -> str:
    if is_fake:
        prompt = (
            "You are a fake news verification assistant. Please review the title and compare it with reliable sources.\n\n"
            f"Title: {title}\n"
            f"Similar Titles: {similar_titles}\n"
            f"Similarity Scores: {scores}\n"
            "Conclusion: This is fake news\n"
            "Explanation: The title significantly differs from official information or shows signs of exaggeration or distortion of facts to attract attention or spread misinformation."
            "Please provide a brief explanation (about 2-4 sentences) in simple, soft language as to why this content is labeled as such. "
            "The explanation should be aimed at a general audience (no technical jargon), and you may use illustrative examples or relatable terms. "
            "Respond as if you are having a conversation with the user."
        )
    else:
        prompt = (
            "You are a fake news verification assistant. Please review the title and compare it with reliable sources.\n\n"
            f"Title: {title}\n"
            f"Similar Titles: {similar_titles}\n"
            f"Similarity Scores: {scores}\n"
            "Conclusion: This news appears to be true\n"
            "Explanation: The title aligns with information from reliable sources and has a high similarity with official articles."
            "Please provide a brief explanation (about 2-4 sentences) in simple, soft language as to why this content is labeled as such. "
            "The explanation should be aimed at a general audience (no technical jargon), and you may use illustrative examples or relatable terms. "
            "Respond as if you are having a conversation with the user."
        )

    return prompt
