def generate_clickbait_prompt(title: str, content_summary: str, similarity_score: float, is_clickbait: bool) -> str:
    if is_clickbait:
        prompt = (
            "Imagine you are an assistant explaining clickbait. Please review the title and the article summary below. "
            "Based on the similarity between the title and the content and our clickbait detection model, can you determine whether the title is clickbait and why?\n\n"
            f"Title: {title}\n"
            f"Article Summary: {content_summary}\n"
            f"Similarity Score: {similarity_score:.2f}\n"
            "Conclusion: This is clickbait\n"
            "Explanation: This title might exaggerate or mislead about the article's content, not accurately reflecting the truth."
            "Please provide a brief explanation (about 2-4 sentences) in simple, soft language as to why this content is labeled as such. "
            "The explanation should be aimed at a general audience (no technical jargon), and you may use illustrative examples or relatable terms. "
            "Respond as if you are having a conversation with the user."
        )
    else:
        prompt = (
            "Imagine you are an assistant explaining clickbait. Please review the title and the article summary below. "
            "Based on the similarity between the title and the content and our clickbait detection model, can you determine whether the title is clickbait and why?\n\n"
            f"Title: {title}\n"
            f"Article Summary: {content_summary}\n"
            f"Similarity Score: {similarity_score:.2f}\n"
            "Conclusion: This is not clickbait\n"
            "Explanation: The title aligns with the article's content, not misleading or exaggerated."
            "Please provide a brief explanation (about 2-4 sentences) in simple, soft language as to why this content is labeled as such. "
            "The explanation should be aimed at a general audience (no technical jargon), and you may use illustrative examples or relatable terms. "
            "Respond as if you are having a conversation with the user."
        )
    return prompt
