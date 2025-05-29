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

def search_documents(query, field="headline", size=5):
    try:
        if not es.indices.exists(index=INDEX_NAME):
            logger.error(f"❌ Index '{INDEX_NAME}' does not exist")
            return

        logger.info(f"🔍 Searching for '{query}' in field '{field}'")

        body = {
            "query": {
                "match": {
                    field: query
                }
            }
        }

        response = es.search(index=INDEX_NAME, body=body, size=size)
        hits = response["hits"]["hits"]

        if not hits:
            logger.info("⚠️ No results found")
            return

        for i, hit in enumerate(hits, 1):
            source = hit["_source"]
            print("-" * 80)
            print(f"[{i}] ID: {source.get('id')}")
            print(f"Headline: {source.get('headline')}")
            print(f"Category: {source.get('category')}")
            print(f"Short description: {source.get('short_description')}")
            print(f"Keywords: {source.get('keywords')}")
    except Exception as e:
        logger.error(f"❌ Search error: {e}")

if __name__ == "__main__":
    keyword = input("Nhập từ khóa để tìm kiếm trong 'headline': ")
    search_documents(keyword)
