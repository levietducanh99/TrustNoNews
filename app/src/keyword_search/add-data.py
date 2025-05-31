import csv
import ast
from elasticsearch import Elasticsearch, helpers, ElasticsearchWarning
import sys
import logging
import warnings

# Suppress Elasticsearch warnings
warnings.filterwarnings('ignore', category=ElasticsearchWarning)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Elasticsearch settings
ES_URL = "http://localhost:9200"
INDEX_NAME = "web_scrap_data"

# Initialize Elasticsearch client
try:
    client_kwargs = {
        "hosts": [ES_URL],
        "request_timeout": 30,
        "max_retries": 3,
        "retry_on_timeout": True,
    }
    logger.debug("Connecting to Elasticsearch without authentication")
    es = Elasticsearch(**client_kwargs)

    # Test connection
    logger.debug(f"Connecting to Elasticsearch at {ES_URL}")
    response = es.transport.perform_request("GET", "/")
    if not response.body.get("version", {}).get("number"):
        raise ConnectionError(f"Connection test failed: {response.body}")
    logger.info(f"✅ Connected to Elasticsearch version: {response.body['version']['number']}")
except Exception as e:
    logger.error(f"❌ Elasticsearch connection error: {e}")
    sys.exit(1)

# Create index if not exists
def create_index():
    try:
        if not es.indices.exists(index=INDEX_NAME):
            es.indices.create(
                index=INDEX_NAME,
                body={
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1
                    },
                    "mappings": {
                        "properties": {
                            "link": {"type": "text"},
                            "headline": {"type": "text"},
                            "category": {"type": "keyword"},
                            "short_description": {"type": "text"},
                            "keywords": {"type": "text"},
                            "id": {"type": "integer"},
                            "keywords_proper_nouns": {"type": "text"},
                            "keywords_tsv": {"type": "text"}
                        }
                    }
                }
            )
            logger.info(f"✅ Created index: {INDEX_NAME}")
        else:
            logger.info(f"ℹ️ Index '{INDEX_NAME}' already exists")
    except Exception as e:
        logger.error(f"❌ Error creating index: {e}")
        sys.exit(1)

# Read and parse CSV file
def parse_csv_file(csv_path):
    documents = []
    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    doc = {
                        "link": row.get("link", ""),
                        "headline": row.get("headline", ""),
                        "category": row.get("category", ""),
                        "short_description": row.get("short_description", ""),
                        "keywords": ast.literal_eval(row.get("keywords", "[]")),
                        "id": int(row["id"]) if row.get("id", "").isdigit() else None,
                        "keywords_proper_nouns": ast.literal_eval(row.get("keywords_proper_nouns", "[]")),
                        "keywords_tsv": row.get("keywords_tsv", "")
                    }
                    if doc["id"] is not None:
                        documents.append(doc)
                    else:
                        logger.warning(f"⚠️ Skipping row with invalid ID: {row}")
                except Exception as e:
                    logger.warning(f"⚠️ Skipping malformed row: {row} - Error: {e}")
        logger.info(f"✅ Parsed {len(documents)} valid documents from CSV")
    except FileNotFoundError:
        logger.error(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error reading CSV: {e}")
        sys.exit(1)
    return documents

# Bulk index to Elasticsearch
def index_documents(documents):
    if not documents:
        logger.info("ℹ️ No documents to index")
        return
    try:
        actions = [
            {
                "_index": INDEX_NAME,
                "_id": doc["id"],
                "_source": doc
            } for doc in documents
        ]
        success, failed = helpers.bulk(es, actions, raise_on_error=False)
        logger.info(f"✅ Indexed {success} documents. Failed: {len(failed)}")
        if failed:
            logger.warning(f"⚠️ Some documents failed to index")
    except Exception as e:
        logger.error(f"❌ Error indexing documents: {e}")

# Main
if __name__ == "__main__":
    create_index()
    csv_file_path = "WebScrapData_rows.csv"  # Đổi tên file tại đây nếu cần
    documents = parse_csv_file(csv_file_path)
    index_documents(documents)
