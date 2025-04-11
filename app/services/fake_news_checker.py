from utils.scraper import extract_title
from utils.web_search import search_similar_titles
from utils.embedder import get_similarity
from prompts.fake_news_prompt import generate_fake_news_explanation

def check_fake_news(url: str):
    title = extract_title(url)
    similar_titles = search_similar_titles(title)
    scores = [get_similarity(title, sim_title) for sim_title in similar_titles]
    is_fake = all(score < 0.3 for score in scores)

    explanation = generate_fake_news_explanation(
        title=title,
        similar_titles=similar_titles,
        scores=scores,
        is_fake=is_fake
    )

    return {
        "is_fake": is_fake,
        "input_title": title,
        "similar_titles": similar_titles,
        "similarity_scores": scores,
        "explanation": explanation
    }
