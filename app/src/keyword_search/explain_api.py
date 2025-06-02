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

def explain_document(index, doc_id, query):
    """Use the explain API to analyze why a document matches a query."""
    try:
        if not es.indices.exists(index=index):
            logger.error(f"❌ Index '{index}' does not exist")
            return

        # Define the query for the explain API
        explain_query = {
            "query": {
                "match": {
                    "headline": query  # Replace 'headline' with the field you are querying
                }
            }
        }

        # Call the explain API
        response = es.explain(index=index, id=doc_id, body=explain_query)

        # Display the explanation
        if response.get("matched"):
            logger.info(f"✅ Document ID {doc_id} matches the query.")
            print("Explanation:")
            print(response["explanation"])
        else:
            logger.info(f"⚠️ Document ID {doc_id} does not match the query.")
    except Exception as e:
        logger.error(f"❌ Error using explain API: {e}")

if __name__ == "__main__":
    document_id = input("Enter the document ID to explain: ")
    query_text = input("Enter the query text: ")
    explain_document(INDEX_NAME, document_id, query_text)