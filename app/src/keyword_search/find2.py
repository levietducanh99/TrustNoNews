from whoosh.index import open_dir
from whoosh.analysis import StemmingAnalyzer
from rank_bm25 import BM25Plus
import time

# Open the existing Whoosh index
INDEX_DIR = "whoosh_index"
ix = open_dir(INDEX_DIR)

# Tokenize text using the same analyzer as the index
analyzer = StemmingAnalyzer()


def tokenize(text):
    return [token.text for token in analyzer(text)]


# BM25 search using rank_bm25 library
def bm25_search(query, top_n=10):
    start_time = time.time()

    with ix.searcher() as searcher:
        # Get all documents from the index
        all_docs = list(searcher.all_stored_fields())
        if not all_docs:
            print("No documents in index")
            return []

        # Prepare corpus and document mapping
        corpus = []
        doc_mapping = []
        for doc in all_docs:
            tokens = tokenize(doc["headline"])
            corpus.append(tokens)
            doc_mapping.append(doc)

        # Initialize BM25Plus model
        bm25 = BM25Plus(corpus)

        # Tokenize the query
        query_tokens = tokenize(query)

        # Get BM25 scores
        scores = bm25.get_scores(query_tokens)

        # Combine scores with documents
        scored_docs = [
            {"id": doc_mapping[i]["id"], "headline": doc_mapping[i]["headline"], "score": scores[i]}
            for i in range(len(doc_mapping))
        ]

        # Sort and return top results
        top_docs = sorted(scored_docs, key=lambda x: x["score"], reverse=True)[:top_n]

        execution_time = time.time() - start_time
        return top_docs, execution_time


# Example usage
if __name__ == "__main__":
    query = input("Enter your search query: ")
    results, execution_time = bm25_search(query)
    print("\nSearch Results:")
    print(f"Execution time: {execution_time:.4f} seconds")
    if results:
        for result in results:
            print(f"ID: {result['id']}, Headline: {result['headline']}, Score: {result['score']:.4f}")
    else:
        print("No results found")