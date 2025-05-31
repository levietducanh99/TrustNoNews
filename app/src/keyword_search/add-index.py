import os
import sys
import logging
import pymongo
from bson import ObjectId
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, KEYWORD, ID, STORED
from whoosh.qparser import MultifieldParser, OrGroup, PhrasePlugin
from whoosh.analysis import StemmingAnalyzer
import spacy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# MongoDB connection parameters
MONGO_CONFIG = {
    "uri": "mongodb+srv://trung7cyv:Pwrl2KClurSIANRy@cluster0.wwa6we5.mongodb.net/?retryWrites=true&w=majority",
    "database": "news_scraper",
    "collection": "articles"
}

# Whoosh settings
INDEX_DIR = "whoosh_index"

# Define Whoosh schema
schema = Schema(
    id=ID(stored=True, unique=True),
    link=TEXT(stored=True),
    headline=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    category=KEYWORD(stored=True, commas=True),
    short_description=TEXT(stored=True),
    keywords_proper_nouns=TEXT(stored=True)
)


# Get or create index
def get_index():
    try:
        if not os.path.exists(INDEX_DIR):
            os.makedirs(INDEX_DIR)
            ix = create_in(INDEX_DIR, schema)
            logger.info(f"Created new index directory: {INDEX_DIR}")
            return ix, True  # True indicates a new index
        elif not exists_in(INDEX_DIR):
            ix = create_in(INDEX_DIR, schema)
            logger.info(f"Created new index in existing directory: {INDEX_DIR}")
            return ix, True  # True indicates a new index
        else:
            ix = open_dir(INDEX_DIR)
            doc_count = ix.doc_count()
            logger.info(f"ℹUsing existing index with {doc_count} documents")
            return ix, False  # False indicates using existing index
    except Exception as e:
        logger.error(f" Error accessing index: {e}")
        sys.exit(1)


# Connect to MongoDB database
def connect_to_database():
    """Establish connection to MongoDB database"""
    try:
        client = pymongo.MongoClient(MONGO_CONFIG["uri"])
        db = client[MONGO_CONFIG["database"]]
        collection = db[MONGO_CONFIG["collection"]]
        logger.info("Successfully connected to MongoDB database")
        return collection
    except Exception as e:
        logger.error(f" Database connection error: {e}")
        raise


# Fetch documents from MongoDB database
def fetch_documents_from_db():
    """Fetch all documents from the MongoDB database"""
    documents = []
    try:
        collection = connect_to_database()
        cursor = collection.find({})
        
        for doc in cursor:
            # Map MongoDB document fields to Whoosh schema fields
            whoosh_doc = {
                "id": str(doc.get("_id", "")),  # Convert ObjectId to string
                "link": doc.get("url", ""),
                "headline": doc.get("title", ""),
                "category": doc.get("source", ""),
                "short_description": doc.get("content", ""),
                "keywords_proper_nouns": doc.get("keywords", "")
            }
            documents.append(whoosh_doc)
        
        logger.info(f"Retrieved {len(documents)} documents from MongoDB database")
        return documents
    except Exception as e:
        logger.error(f" Error fetching documents from database: {e}")
        sys.exit(1)


# Index documents to Whoosh
def index_documents(ix, documents):
    if not documents:
        logger.info("ℹ️ No documents to index")
        return

    try:
        writer = ix.writer()
        success = 0
        failed = 0

        for doc in documents:
            try:
                writer.update_document(
                    id=doc["id"],
                    link=doc["link"],
                    headline=doc["headline"],
                    category=doc["category"],
                    short_description=doc["short_description"],
                    keywords_proper_nouns=doc["keywords_proper_nouns"]
                )
                success += 1
            except Exception as e:
                failed += 1
                logger.warning(f"⚠️ Failed to index document id={doc['id']}: {e}")

        writer.commit()
        logger.info(f" Indexed {success} documents. Failed: {failed}")
    except Exception as e:
        logger.error(f" Error indexing documents: {e}")


# Load spaCy model for advanced search
def load_spacy_model():
    try:
        return spacy.load("en_core_web_md")
    except OSError:
        logger.info("⏳ Downloading spaCy model...")
        import subprocess
        subprocess.call(["python", "-m", "spacy", "download", "en_core_web_md"])
        return spacy.load("en_core_web_md")


# Detect entities in query
def detect_entities(nlp, query):
    doc = nlp(query)
    entities = set()
    for ent in doc.ents:
        if ent.label_ in ("PERSON", "ORG", "GPE", "PRODUCT"):
            entities.add(ent.text.lower())
    return entities


# Enhanced search function
def search_documents(query, size=5):
    ix = open_dir(INDEX_DIR)
    with ix.searcher() as searcher:
        # Build parser
        parser = MultifieldParser(["headline^3", "category", "short_description", "keywords_proper_nouns^2"],
                                  schema=ix.schema,
                                  group=OrGroup)  # default relevance behavior
        parser.remove_plugin_class(PhrasePlugin)  # ensure phrase search works better
        parser.add_plugin(PhrasePlugin())

        # Remove OR joining; use the query as-is
        q = parser.parse(f'"{query}"')  # treat whole input as a phrase

        results = searcher.search(q, limit=size)

        if not results:
            print(" No results found.")
            return

        seen_ids = set()
        print(f"Found {len(results)} results for '{query}':")
        for i, hit in enumerate(results, 1):
            if hit["id"] in seen_ids:
                continue  # Skip duplicates
            seen_ids.add(hit["id"])

            print("=" * 100)
            print(f"[{i}] ID: {hit['id']}")
            print(f"Headline: {hit['headline']}")
            print(f"Category: {hit['category']}")
            print(f"Short description: {hit['short_description']}")
            print(f"Keywords Proper Nouns: {hit['keywords_proper_nouns']}")
            print(f"Score: {hit.score}")
            print()


# Export index info
def export_index_info():
    ix = open_dir(INDEX_DIR)
    with open("index_info.txt", "w") as f:
        f.write(f"Whoosh Index Information\n")
        f.write(f"=====================\n\n")
        f.write(f"Index Location: {INDEX_DIR}\n")
        f.write(f"Number of Documents: {ix.doc_count()}\n\n")
        f.write(f"Schema:\n")
        for field_name, field_type in ix.schema.items():
            f.write(f"  - {field_name}: {field_type.__class__.__name__}\n")

    logger.info(f" Exported index information to index_info.txt")


# Main function
if __name__ == "__main__":
    # Check if this is a first-time run or using existing index
    ix, is_new_index = get_index()

    # Only index documents if this is a new index
    if is_new_index:
        logger.info(" Creating new index, starting indexing process...")
        documents = fetch_documents_from_db()
        index_documents(ix, documents)
        export_index_info()
    else:
        logger.info(" Using existing index, skipping indexing step")

    # Interactive search loop
    print("\n🔍 Search the document database")
    print("============================")
    while True:
        query = input("\nEnter search query (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
        search_documents(query)
