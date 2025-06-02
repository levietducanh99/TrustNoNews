from src.utils.db_connect import get_supabase_client
import time
import spacy
import re
from rank_bm25 import BM25Okapi
from typing import List, Dict, Any
from src.models.search_models import KeywordSearchResult

def keyword_search(query: str, page_size=1000) -> List[KeywordSearchResult]:
    """
    Thực hiện tìm kiếm từ khóa sử dụng BM25
    
    Args:
        query: Truy vấn tìm kiếm
        page_size: Số lượng kết quả mỗi trang
        
    Returns:
        List[KeywordSearchResult]: Danh sách kết quả tìm kiếm từ khóa
    """
    # Initialize Supabase client
    supabase = get_supabase_client()

    # Load spaCy model
    try:
        nlp = spacy.load("en_core_web_md")
    except OSError:
        print("Downloading spaCy model...")
        import subprocess
        subprocess.call(["python", "-m", "spacy", "download", "en_core_web_md"])
        nlp = spacy.load("en_core_web_md")

    start_time = time.time()

    # Process query with spaCy
    query_doc = nlp(query.lower())
    query_tokens = [token.text for token in query_doc if not token.is_stop and not token.is_punct]
    if not query_tokens:
        query_tokens = [token.text for token in query_doc]

    print(f"Query tokens: {query_tokens}")

    if not query_tokens:
        return []

    # Process in batches to handle large data
    page = 0
    corpus = []
    documents = []

    while True:
        # Fetch data in batches
        response = supabase.table("WebScrapData").select("id, headline, content, keywords").range(
            page * page_size, (page + 1) * page_size - 1
        ).execute()

        if not response.data:
            break

        for row in response.data:
            # Skip rows with empty keywords
            if not row.get("keywords"):
                continue

            # Process keywords
            db_keywords = row["keywords"].lower()
            db_tokens = [keyword.strip() for keyword in db_keywords.split(',')]

            # Store tokens for BM25 corpus
            corpus.append(db_tokens)
            # Store document info for results
            documents.append({
                "id": row["id"],
                "title": row["headline"],
                "content": row.get("content", ""),
                "keywords": db_tokens
            })

        page += 1

        # Exit if we've processed all data
        if len(response.data) < page_size:
            break

    # Initialize BM25
    if not corpus:
        return []

    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(query_tokens)

    # Process results
    results = []
    for idx, score in enumerate(scores):
        if score > 0:  # Only include documents with positive relevance
            doc = documents[idx]
            db_tokens = doc["keywords"]

            # Count matched tokens (improved matching logic)
            matched_tokens = 0
            matched_keywords = []
            for query_token in query_tokens:
                for db_token in db_tokens:
                    if query_token.strip().lower() in db_token.strip().lower() or db_token.strip().lower() in query_token.strip().lower():
                        matched_tokens += 1
                        matched_keywords.append(db_token)
                        break

            # Create KeywordSearchResult
            result = KeywordSearchResult(
                id=doc["id"],
                title=doc["title"],
                content=doc["content"],
                bm25_score=float(score),  # Convert numpy float to Python float
                keywords=matched_keywords,
                matched_count=matched_tokens
            )
            results.append(result)

    # Sort results by BM25 score in descending order
    results.sort(key=lambda x: x.bm25_score, reverse=True)

    # Limit results to top 10
    return results[:10]

if __name__ == "__main__":
    # Test the keyword search
    query = "Messi Barcelona"
    results = keyword_search(query)
    for result in results:
        print(f"Title: {result.title}")
        print(f"BM25 Score: {result.bm25_score:.4f}")
        print(f"Keywords: {result.keywords}")
        print(f"Matched Count: {result.matched_count}")
        print("-" * 50)