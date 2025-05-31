from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.Scraper.scraper import scrape
from app.services.generate_prompt import generate_fake_news_prompt
from app.src.models.search_models import SearchRequest
from app.src.services.search_pipeline import SearchPipeline
import ollama

router = APIRouter()

# Define the request model
class FakeNewsRequest(BaseModel):
    url: str

# Define the response model
class FakeNewsResponse(BaseModel):
    is_fake: bool
    input_title: str
    similar_titles: list[str]
    similarity_scores: list[float]
    urls: list[str]
    explanation: str

# Initialize the search pipeline once
search_pipeline = SearchPipeline()

@router.post("/check-fake-news", response_model=FakeNewsResponse)
async def check_fake_news(request: FakeNewsRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")

    try:
        # Scrape the URL to get the title
        scrape_url = scrape(url)
        input_title = scrape_url['title'] if scrape_url else "Unknown Title"
        
        # Create a search request using the title as the query
        search_request = SearchRequest(
            query=input_title,
            page=1,
            page_size=15  # Get top 15 results, matching previous functionality
        )
        
        # Execute the search using the pipeline
        search_results = await search_pipeline.execute_search(search_request)
        
        # Use the semantic results as they're most relevant for similarity checking
        results = search_results.rrf_results
        
        # Extract relevant data from the results
        similar_titles = [result.title for result in results]
        similarity_scores = [result.semantic_score for result in results]
        urls = [result.url if hasattr(result, 'url') and result.url else "" for result in results]

        # Determine if the news is fake based on similarity scores
        is_fake = not any(score > 0.7 for score in similarity_scores)  # Example threshold

        # Generate prompt and call Ollama for explanation
        prompt = generate_fake_news_prompt(
            title=input_title,
            similar_titles=similar_titles,
            scores=similarity_scores,
            is_fake=is_fake
        )
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
        explanation = response.get("message", {}).get("content", "").strip()

        # Prepare the response
        response = {
            "is_fake": is_fake,
            "input_title": input_title,
            "similar_titles": similar_titles,
            "similarity_scores": similarity_scores,
            "urls": urls,
            "explanation": explanation,
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
