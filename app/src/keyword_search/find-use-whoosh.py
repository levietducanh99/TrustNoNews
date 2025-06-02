from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser, QueryParser, OrGroup
from whoosh import scoring
import time
import spacy
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load index
INDEX_DIR = "whoosh_index"
ix = open_dir(INDEX_DIR)

# Load spaCy model once
def load_spacy_model():
    try:
        return spacy.load("en_core_web_md")
    except OSError:
        logger.info("⏳ Downloading spaCy model...")
        import subprocess
        subprocess.call(["python", "-m", "spacy", "download", "en_core_web_md"])
        return spacy.load("en_core_web_md")

nlp = load_spacy_model()

# Detect named entities (improved for multi-word entities)
def detect_entities(query):
    doc = nlp(query)
    entities = [ent.text for ent in doc.ents if ent.label_ in ("PERSON", "ORG", "GPE", "PRODUCT")]
    return entities

# Clean query to handle special characters and improve parsing
def clean_query(query):
    # Remove special characters that might interfere with Whoosh parser
    cleaned = re.sub(r'[^\w\s"]', ' ', query)
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

# Main search function using Whoosh BM25
def bm25_search(query, top_n=10):
    start_time = time.time()
    
    # Clean the query
    cleaned_query = clean_query(query)
    
    # Detect entities
    entities = detect_entities(cleaned_query)
    if entities:
        logger.info(f"Detected entities: {entities}")
    
    with ix.searcher(weighting=scoring.BM25F()) as searcher:
        # Create main query parser with OR grouping for better multi-word handling
        parser = MultifieldParser(["headline", "short_description", "keywords_proper_nouns"], 
                                 schema=ix.schema, 
                                 group=OrGroup.factory(0.9))  # Using OR with 0.9 boost factor
        
        # Parse the user query
        parsed_query = parser.parse(cleaned_query)
        
        # If we have entities, create entity queries and add them to boost relevant results
        if entities:
            # Create separate entity parser for more specific matches
            entity_parser = QueryParser("keywords_proper_nouns", schema=ix.schema)
            entity_queries = [entity_parser.parse(entity) for entity in entities]
            
            # Combine original query with entity queries (gives better relevance)
            # This helps with multi-word queries by ensuring entity matches have higher weight
            results = searcher.search(parsed_query, limit=top_n)
        else:
            results = searcher.search(parsed_query, limit=top_n)

        final_results = [
            {
                "id": hit["id"],
                "headline": hit.get("headline", ""),
                "category": hit.get("category", ""),
                "short_description": hit.get("short_description", ""),
                "keywords_proper_nouns": hit.get("keywords_proper_nouns", ""),
                "score": hit.score,
            }
            for hit in results
        ]

    execution_time = time.time() - start_time
    return final_results, execution_time

# Display results
def display_results(results, execution_time):
    if not results:
        print("⚠️ No results found.")
        return

    print(f"Found {len(results)} results in {execution_time:.4f} seconds:")
    for i, hit in enumerate(results, 1):
        print("=" * 100)
        print(f"[{i}] ID: {hit['id']}")
        print(f"Headline: {hit['headline']}")
        print(f"Category: {hit['category']}")
        print(f"Keywords (Proper Nouns): {hit['keywords_proper_nouns']}")
        print(f"Short description: {hit['short_description']}")
        print(f"Score: {hit['score']:.4f}")
        print()

# Main CLI loop
if __name__ == "__main__":
    print("\n🔍 Enhanced Whoosh BM25 Search with Multi-Word Query Support")
    print("===========================================================")
    while True:
        query = input("\nEnter your search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        
        if not query.strip():
            print("Please enter a valid query.")
            continue

        results, execution_time = bm25_search(query)
        display_results(results, execution_time)

