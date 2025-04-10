# prompts/clickbait_prompt.py

def generate_clickbait_explanation(title: str, content_summary: str, similarity_score: float, is_clickbait: bool) -> str:
    if is_clickbait:
        prompt = (
            "You are a clickbait explanation assistant. Given a news title, the summary of the article, and their similarity score, "
            "explain whether the title is clickbait or not and why.\n\n"
            f"Title: {title}\n"
            f"Article Summary: {content_summary}\n"
            f"Similarity Score: {similarity_score:.2f}\n"
            f"Clickbait: True\n\n"
            "Clickbait: The title exaggerates key points not mentioned in content."
        )
    else:
        prompt = (
            "You are a clickbait explanation assistant. Given a news title, the summary of the article, and their similarity score, "
            "explain whether the title is clickbait or not and why.\n\n"
            f"Title: {title}\n"
            f"Article Summary: {content_summary}\n"
            f"Similarity Score: {similarity_score:.2f}\n"
            f"Clickbait: False\n\n"
            "Not clickbait: The title aligns well with the content."
        )

    return prompt
