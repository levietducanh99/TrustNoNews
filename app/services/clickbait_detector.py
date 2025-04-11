from app.utils.Similarity.VectorSimilarity import get_similarity
from app.utils.Summary.summary_t5 import summarize_text
from app.prompts.clickbait_prompt import generate_clickbait_explanation

def check_clickbait(title: str, content: str):
    # Summarize the content
    summary = summarize_text(content)

    # Calculate similarity between the title and the summary
    try:
        similarity = get_similarity(title, summary)
    except Exception as e:
        similarity = 0.0  # Default similarity if error occurs
        print(f"Error calculating similarity: {e}")

    # Determine if the content is clickbait
    is_clickbait = similarity < 0.6

    # Generate an explanation for the result
    explanation = generate_clickbait_explanation(
        title=title,
        content_summary=summary,
        similarity_score=similarity,
        is_clickbait=is_clickbait
    )

    return {
        "is_clickbait": bool(is_clickbait),  # Convert to standard Python bool
        "similarity_score": float(similarity),  # Convert to standard Python float
        "explanation": explanation,
        "summary": summary,
        "title": title
    }
