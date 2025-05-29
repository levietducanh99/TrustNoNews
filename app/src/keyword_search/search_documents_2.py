import spacy
from elasticsearch import Elasticsearch, ElasticsearchWarning
import warnings
import logging

# Suppress warnings
warnings.filterwarnings("ignore", category=ElasticsearchWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Elasticsearch settings
ES_URL = "http://localhost:9200"
INDEX_NAME = "web_scrap_data"

# Initialize Elasticsearch client
es = Elasticsearch([ES_URL])

# Load spaCy model for NER (Named Entity Recognition)
nlp = spacy.load("en_core_web_md")

def detect_proper_nouns(query):
    doc = nlp(query)
    proper_nouns = set()
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG", "GPE"):
            proper_nouns.add(ent.text.lower())
    return proper_nouns

def search_documents(query, size=5):
    if not es.indices.exists(index=INDEX_NAME):
        logger.error(f"❌ Index '{INDEX_NAME}' does not exist")
        return

    proper_nouns_in_query = detect_proper_nouns(query)
    logger.info(f"Detected proper nouns in query: {proper_nouns_in_query}")

    if proper_nouns_in_query:
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": [
                                    "headline^3",
                                    "keywords^2",
                                    "short_description"
                                ]
                            }
                        }
                    ],
                    "filter": {
                        "terms": {
                            "keywords_proper_nouns": list(proper_nouns_in_query)
                        }
                    }
                }
            },
            "highlight": {
                "fields": {
                    "headline": {},
                    "keywords": {}
                }
            },
            "size": size,
            "explain": True
        }
    else:
        query_body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": [
                        "headline^3",
                        "keywords^2",
                        "short_description"
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "headline": {},
                    "keywords": {}
                }
            },
            "size": size,
            "explain": True
        }

    response = es.search(index=INDEX_NAME, body=query_body)
    hits = response["hits"]["hits"]

    if not hits:
        print("⚠️ No results found.")
        return

    for i, hit in enumerate(hits, 1):
        source = hit["_source"]
        highlight = hit.get("highlight", {})
        explanation = hit.get("_explanation")

        print("=" * 100)
        print(f"[{i}] ID: {source.get('id')}")
        print(f"Headline: {source.get('headline')}")
        print(f"Category: {source.get('category')}")
        print(f"Short description: {source.get('short_description')}")
        print(f"Keywords: {source.get('keywords')}")
        print()

        if highlight:
            print("✨ Highlighted Matches:")
            for field, fragments in highlight.items():
                for fragment in fragments:
                    print(f" - {field}: {fragment}")
            print()

        print("🔍 Explanation Summary:")
        def print_expl(e, indent=0):
            print(" " * indent + f"{e['description']} (score: {e['value']})")
            for detail in e.get("details", []):
                print_expl(detail, indent + 2)

        print_expl(explanation)
        print()

if __name__ == "__main__":
    query = input("🔍 Nhập từ khóa để tìm kiếm: ")
    search_documents(query)
