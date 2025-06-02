from whoosh.index import open_dir
from whoosh.analysis import StemmingAnalyzer
from rank_bm25 import BM25Plus
import nltk
from nltk.corpus import wordnet
import time
import spacy
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Download WordNet if not already present
nltk.download('wordnet')

# Open the existing Whoosh index
INDEX_DIR = "whoosh_index"
ix = open_dir(INDEX_DIR)

# Tokenizer using same analyzer as index
analyzer = StemmingAnalyzer()


def tokenize(text):
    if not text:
        return []
    return [token.text for token in analyzer(text)]


def load_spacy_model():
    try:
        return spacy.load("en_core_web_md")
    except OSError:
        logger.info("⏳ Downloading spaCy model...")
        import subprocess
        subprocess.call(["python", "-m", "spacy", "download", "en_core_web_md"])
        return spacy.load("en_core_web_md")


def detect_entities(nlp, query):
    doc = nlp(query)
    entities = set()
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG", "GPE", "PRODUCT"):
            entities.add(ent.text.lower())
    return entities


# Function removed as it's no longer needed without keyword expansion
# def expand_query_with_wordnet(query_tokens):
#     ...


def bm25_search(query, top_n=10):
    start_time = time.time()

    nlp = load_spacy_model()
    entities = detect_entities(nlp, query)
    entity_tokens = []
    for entity in entities:
        entity_tokens.extend(tokenize(entity))

    logger.info(f"Detected entities: {entities}")

    with ix.searcher() as searcher:
        all_docs = list(searcher.all_stored_fields())
        if not all_docs:
            logger.warning("No documents in index")
            return [], 0

        headline_corpus = []
        proper_noun_corpus = []
        doc_mapping = []

        for doc in all_docs:
            headline_corpus.append(tokenize(doc.get("headline", "")))
            proper_noun_corpus.append(tokenize(doc.get("keywords_proper_nouns", "")))
            doc_mapping.append(doc)

        query_tokens = tokenize(query)

        headline_bm25 = BM25Plus(headline_corpus)
        proper_noun_bm25 = BM25Plus(proper_noun_corpus)

        headline_scores = headline_bm25.get_scores(query_tokens)
        proper_noun_scores = proper_noun_bm25.get_scores(query_tokens)

        if entities:
            entity_scores = proper_noun_bm25.get_scores(entity_tokens)
            for i in range(len(proper_noun_scores)):
                proper_noun_scores[i] += entity_scores[i] * 1.5

        # Combined scores now only use headline and proper noun scores
        combined_scores = [
            headline_scores[i] * 1.0 +
            proper_noun_scores[i] * 1.5
            for i in range(len(doc_mapping))
        ]

        scored_docs = [
            {
                "id": doc_mapping[i]["id"],
                "headline": doc_mapping[i]["headline"],
                "category": doc_mapping[i].get("category", ""),
                "short_description": doc_mapping[i].get("short_description", ""),
                "keywords_proper_nouns": doc_mapping[i].get("keywords_proper_nouns", ""),
                "headline_score": headline_scores[i],
                "proper_noun_score": proper_noun_scores[i],
                "score": combined_scores[i],
            }
            for i in range(len(doc_mapping))
        ]

        top_docs = sorted(scored_docs, key=lambda x: x["score"], reverse=True)[:top_n]
        execution_time = time.time() - start_time
        return top_docs, execution_time


def display_results(results, execution_time):
    if not results:
        print("⚠️ No results found.")
        return

    print(f"Found {len(results)} results in {execution_time:.4f} seconds:")
    for i, hit in enumerate(results, 1):
        print("=" * 100)
        print(f"[{i}] ID: {hit['id']}")
        print(f"Headline: {hit['headline']}")
        print(f"Category: {hit.get('category', 'N/A')}")
        print(f"Keywords (Proper Nouns): {hit.get('keywords_proper_nouns', 'N/A')}")
        print(f"Short description: {hit.get('short_description', 'N/A')}")
        print(f"Score: {hit['score']:.4f}")
        print(f"  - Headline Score: {hit.get('headline_score', 0):.4f}")
        print(f"  - Proper Noun Score: {hit.get('proper_noun_score', 0):.4f}")
        print()


if __name__ == "__main__":
    print("\n🔍 Enhanced BM25 Search with Entity Detection")
    print("============================================")

    while True:
        query = input("\nEnter your search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break

        results, execution_time = bm25_search(query)
        display_results(results, execution_time)
