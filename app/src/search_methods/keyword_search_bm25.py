from src.utils.db_connect import get_supabase_client
import time
import spacy
import re
from rank_bm25 import BM25Okapi


def keyword_search(query: str, page_size=1000):
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

    # First check if query exactly matches a headline
    exact_headline_match = supabase.table("WebScrapData").select("headline, keywords").eq("headline", query).execute()
    if exact_headline_match.data:
        row = exact_headline_match.data[0]
        query_doc = nlp(query.lower())
        query_tokens = [token.text for token in query_doc if not token.is_stop and not token.is_punct]
        if not query_tokens:
            query_tokens = [token.text for token in query_doc]

        results = [{
            "headline": row["headline"],
            "keywords": row["keywords"],
            "percent_match": 100.0,
            "matched_count": f"{len(query_tokens)}/{len(query_tokens)}",
            "token_matches": [{"query_token": t, "matched_db_tokens": [t]} for t in query_tokens]
        }]
        return results, time.time() - start_time

    # Process query with spaCy
    query_doc = nlp(query.lower())
    query_tokens = [token.text for token in query_doc if not token.is_stop and not token.is_punct]
    if not query_tokens:
        query_tokens = [token.text for token in query_doc]

    # Check for proper nouns in query
    has_proper_noun = False
    proper_nouns = []
    for token in query_doc:
        if token.pos_ == "PROPN":  # Check if token is a proper noun
            has_proper_noun = True
            proper_nouns.append(token.text)
    for ent in query_doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "EVENT"]:
            has_proper_noun = True
            proper_nouns.append(ent.text)

    print(f"Query tokens: {query_tokens}")
    print(f"Proper nouns detected: {proper_nouns}")

    if not query_tokens:
        return [], time.time() - start_time

    # Process in batches to handle large data
    page = 0
    corpus = []
    documents = []

    while True:
        # Fetch data in batches
        response = supabase.table("WebScrapData").select("headline, keywords, keywords_proper_nouns").range(
            page * page_size, (page + 1) * page_size - 1
        ).execute()

        if not response.data:
            break

        for row in response.data:
            # Skip rows with empty keywords
            if not row.get("keywords"):
                continue

            # Process keywords (already pre-processed in Supabase)
            db_keywords = row["keywords"].lower()
            db_tokens = [keyword.strip() for keyword in db_keywords.split(',')]

            # Include proper_nouns if query contains proper nouns and proper_nouns exist
            if has_proper_noun and row.get("keywords_proper_nouns"):
                db_proper_nouns = row["keywords_proper_nouns"].lower()
                proper_noun_tokens = [noun.strip() for noun in db_proper_nouns.split(',')]
                db_tokens.extend(proper_noun_tokens)  # Combine keywords and proper nouns

            # Store tokens for BM25 corpus
            corpus.append(db_tokens)
            # Store document info for results
            documents.append({
                "headline": row["headline"],
                "keywords": row["keywords"],
                "keywords_proper_nouns": row.get("keywords_proper_nouns", ""),
                "tokens": db_tokens
            })

        page += 1

        # Exit if we've processed all data
        if len(response.data) < page_size:
            break

    # Initialize BM25
    if not corpus:
        return [], time.time() - start_time

    bm25 = BM25Okapi(corpus)

    # Score documents using BM25
    scores = bm25.get_scores(query_tokens)

    # Process results
    results = []
    for idx, score in enumerate(scores):
        if score > 0:  # Only include documents with positive relevance
            doc = documents[idx]
            db_tokens = doc["tokens"]

            # Track matched tokens for token_matches
            matched_tokens = 0
            token_matches = []
            for query_token in query_tokens:
                match_found = False
                matching_db_tokens = []
                for db_token in db_tokens:
                    if query_token == db_token:
                        match_found = True
                        matching_db_tokens.append(db_token)
                if match_found:
                    matched_tokens += 1
                    token_matches.append({
                        "query_token": query_token,
                        "matched_db_tokens": matching_db_tokens
                    })

            results.append({
                "headline": doc["headline"],
                "keywords": doc["keywords"],
                "percent_match": score,  # Use BM25 score as relevance (not a percentage)
                "matched_count": f"{matched_tokens}/{len(query_tokens)}",
                "token_matches": token_matches
            })

    # Sort results by BM25 score in descending order
    results.sort(key=lambda x: x["percent_match"], reverse=True)

    # Limit results to top 10
    results = results[:10]

    return results, time.time() - start_time


if __name__ == "__main__":
    # Test the Keyword Search method with the WebScrapData table
    query = "Comedian Robert Dubac Talks About Settling Down and Performing His One-Man Show"
    results, execution_time = keyword_search(query)

    print("\nKeyword Search Results from WebScrapData (BM25):")
    for result in results:
        print(f"Headline: {result['headline']}")
        print(f"Keywords: {result['keywords']}")
        print(f"Matched: {result['matched_count']} tokens")
        print(f"BM25 Score: {result['percent_match']:.4f}")
        print("Token Matches:")
        for match in result['token_matches']:
            print(f"  Query token '{match['query_token']}' matched with: {', '.join(match['matched_db_tokens'])}")
        print("-" * 50)
    print(f"Execution Time: {execution_time:.4f} seconds")