import logging
import os
from dotenv import load_dotenv  # Add this import
from openai import OpenAI

from app.utils.Scraper.scraper import scrape
from app.src.models.search_models import SearchRequest
from app.src.services.search_pipeline import SearchPipeline
from app.services.generate_prompt import generate_fake_news_prompt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()  # Add this line

# Initialize the search pipeline
search_pipeline = SearchPipeline()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def check_fake_news(url: str):
    # Extract title from URL
    scrape_result = scrape(url)
    title = scrape_result.get('title', 'Unknown Title')

    # Create search request
    search_request = SearchRequest(
        query=title,
        page=1,
        page_size=15
    )

    # Execute search using pipeline
    search_results = await search_pipeline.execute_search(search_request)

    # Use semantic results for similarity comparison
    results = search_results.semantic_results

    similar_titles = [result.title for result in results]
    similarity_scores = [result.semantic_score for result in results]
    urls = [result.url if hasattr(result, 'url') and result.url else "" for result in results]

    # Log all similarity scores
    logger.debug(f"Similarity scores: {similarity_scores}")

    # Determine if news is fake
    is_fake = not any(score > 0.7 for score in similarity_scores)

    # Log detailed explanation for debug
    for idx, score in enumerate(similarity_scores):
        logger.debug(f"Title {idx + 1}: Score = {score} -> {'Above' if score > 0.7 else 'Below'} threshold")

    logger.info(f"Determined is_fake = {is_fake} for title: {title}")

    # Generate explanation
    prompt = generate_fake_news_prompt(
        title=title,
        similar_titles=similar_titles,
        scores=similarity_scores,
        is_fake=is_fake
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    explanation = response.choices[0].message.content.strip()

    return {
        "is_fake": is_fake,
        "input_title": title,
        "similar_titles": similar_titles,
        "similarity_scores": similarity_scores,
        "urls": urls,
        "explanation": explanation
    }

