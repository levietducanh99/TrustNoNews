from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.show_list_similarity import show_list_similarity
from app.utils.Scraper.scraper import scrape

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
    explanation: str

@router.post("/check-fake-news", response_model=FakeNewsResponse)
async def check_fake_news(request: FakeNewsRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")

    try:
        # Use the show_list_similarity function to get similar articles
        results = show_list_similarity(url)

        scrape_url = scrape(url)
        # Extract relevant data from the results
        input_title = scrape_url['title'] if scrape_url else "Unknown Title"
        similar_titles = [result['title'] for result in results]
        similarity_scores = [result['similarity'] for result in results]

        # Determine if the news is fake based on similarity scores
        is_fake = all(score < 0.3 for score in similarity_scores)  # Example threshold
        explanation = (
            "No credible sources support the headline. Low similarity detected."
            if is_fake
            else "Similar credible sources found."
        )

        # Prepare the response
        response = {
            "is_fake": is_fake,
            "input_title": input_title,
            "similar_titles": similar_titles,
            "similarity_scores": similarity_scores,
            "explanation": explanation,
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
