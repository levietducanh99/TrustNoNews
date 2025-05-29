from src.utils.db_connect import get_supabase_client
import time
import spacy
import re


def keyword_search(query: str):
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

    # Start timing
    start_time = time.time()

    # Process query with spaCy
    query_doc = nlp(query.lower())

    # Extract meaningful tokens (remove stopwords and punctuation)
    query_tokens = [token.text for token in query_doc if not token.is_stop and not token.is_punct]

    # If no meaningful tokens found, use all tokens
    if not query_tokens:
        query_tokens = [token.text for token in query_doc]

    print(f"Query tokens: {query_tokens}")

    if not query_tokens:
        end_time = time.time()
        execution_time = end_time - start_time
        return [], execution_time

    # Fetch all rows with headline and keywords from the database
    response = supabase.table("WebScrapData").select("headline, keywords").execute()

    # Check if the response contains data
    if not response.data:
        end_time = time.time()
        execution_time = end_time - start_time
        return [], execution_time

    # Process results
    results = []
    for row in response.data:
        # Clean and normalize database keywords
        db_keywords = re.sub(r'[^\w\s,]', '', row["keywords"].lower())

        # Process database keywords into tokens
        db_keywords_doc = nlp(db_keywords)
        db_tokens = [token.text for token in db_keywords_doc if not token.is_stop and not token.is_punct]

        # Count matching tokens
        matched_tokens = 0
        for query_token in query_tokens:
            # Check for word-level match using exact match or semantic similarity
            best_match = False
            best_match_score = 0

            for db_token in db_tokens:
                # Exact match
                if query_token == db_token:
                    best_match = True
                    break

                # Semantic similarity as fallback
                query_token_doc = nlp(query_token)
                db_token_doc = nlp(db_token)
                if query_token_doc.has_vector and db_token_doc.has_vector:
                    similarity = query_token_doc.similarity(db_token_doc)
                    if similarity > 0.8 and similarity > best_match_score:  # High threshold for similarity
                        best_match = True
                        best_match_score = similarity

            if best_match:
                matched_tokens += 1

        # Calculate percent match according to the formula:
        # number of tokens in query that match / number of tokens in query
        if len(query_tokens) > 0:
            percent_match = (matched_tokens / len(query_tokens)) * 100

            if percent_match > 0:  # Include any match
                results.append({
                    "headline": row["headline"],
                    "keywords": row["keywords"],
                    "percent_match": percent_match,
                    "matched_count": f"{matched_tokens}/{len(query_tokens)}"
                })

    # Sort results by percent match in descending order
    results.sort(key=lambda x: x["percent_match"], reverse=True)

    # Limit results to top 10
    results = results[:10]

    # End timing
    end_time = time.time()
    execution_time = end_time - start_time

    return results, execution_time


if __name__ == "__main__":
    # Test the Keyword Search method with the WebScrapData table
    query = "children health cold season"
    results, execution_time = keyword_search(query)

    print("\nKeyword Search Results from WebScrapData:")
    for result in results:
        print(f"Headline: {result['headline']}")
        print(f"Keywords: {result['keywords']}")
        print(f"Matched: {result['matched_count']} tokens")
        print(f"Percent Match: {result['percent_match']:.2f}%")
        print("-" * 50)
    print(f"Execution Time: {execution_time:.4f} seconds")