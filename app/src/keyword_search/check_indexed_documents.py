from elasticsearch import Elasticsearch, ElasticsearchWarning
import warnings
import logging

# Suppress Elasticsearch warnings
warnings.filterwarnings("ignore", category=ElasticsearchWarning)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Elasticsearch settings
ES_URL = "http://localhost:9200"
INDEX_NAME = "web_scrap_data"

# Initialize Elasticsearch client
es = Elasticsearch([ES_URL])

def check_documents():
    try:
        # Check if index exists
        if not es.indices.exists(index=INDEX_NAME):
            logger.error(f"❌ Index '{INDEX_NAME}' does not exist")
            return

        # Get total document count
        count = es.count(index=INDEX_NAME)["count"]
        logger.info(f"📊 Total documents in index '{INDEX_NAME}': {count}")

        # Get 5 sample documents
        response = es.search(index=INDEX_NAME, size=5, query={"match_all": {}})
        logger.info("📄 Sample documents:")
        for doc in response["hits"]["hits"]:
            source = doc["_source"]
            print("-" * 80)
            print(f"ID: {source.get('id')}")
            print(f"Headline: {source.get('headline')}")
            print(f"Category: {source.get('category')}")
            print(f"Keywords: {source.get('keywords')}")
            print(f"Keywords TSV: {source.get('keywords_tsv')[:100]}...")
    except Exception as e:
        logger.error(f"❌ Error retrieving documents: {e}")

if __name__ == "__main__":
    check_documents()
