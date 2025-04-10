# services/clickbait_detector.py
from utils.scraper import extract_title_and_content
from utils.summarizer import summarize_text
from utils.embedder import get_similarity
from prompts.clickbait_prompt import generate_clickbait_explanation


def check_clickbait(url: str):
    title, content = extract_title_and_content(url)
    summary = summarize_text(content)
    similarity = get_similarity(title, summary)

    is_clickbait = similarity < 0.6

    explanation = generate_clickbait_explanation(
        title=title,
        content_summary=summary,
        similarity_score=similarity,
        is_clickbait=is_clickbait
    )

    return {
        "is_clickbait": is_clickbait,
        "similarity_score": similarity,
        "explanation": explanation
    }
