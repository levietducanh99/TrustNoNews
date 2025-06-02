from src.utils.db_connect import get_supabase_client
import time
import spacy
from sentence_transformers import SentenceTransformer, util
import torch
from typing import List, Dict, Any
from app.src.models.search_models import SemanticSearchResult

def semantic_search(query: str, page_size=1000) -> List[SemanticSearchResult]:
    """
    Thực hiện tìm kiếm ngữ nghĩa sử dụng Sentence Transformers
    
    Args:
        query: Truy vấn tìm kiếm
        page_size: Số lượng kết quả mỗi trang
        
    Returns:
        List[SemanticSearchResult]: Danh sách kết quả tìm kiếm ngữ nghĩa
    """
    # Initialize Supabase client
    supabase = get_supabase_client()

    # Load spaCy model for text processing
    try:
        nlp = spacy.load("en_core_web_md")
    except OSError:
        print("Downloading spaCy model...")
        import subprocess
        subprocess.call(["python", "-m", "spacy", "download", "en_core_web_md"])
        nlp = spacy.load("en_core_web_md")

    # Load Sentence Transformer model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    start_time = time.time()

    # Process query with spaCy
    query_doc = nlp(query.lower())
    query_tokens = [token.text for token in query_doc if not token.is_stop and not token.is_punct]
    if not query_tokens:
        query_tokens = [token.text for token in query_doc]

    # Get query embedding
    query_embedding = model.encode(query, convert_to_tensor=True)

    # Process in batches to handle large data
    page = 0
    results = []

    while True:
        # Fetch data in batches
        response = supabase.table("WebScrapData").select("id, headline, content, keywords").range(
            page * page_size, (page + 1) * page_size - 1
        ).execute()

        if not response.data:
            break

        # Process documents in batch
        documents = []
        for row in response.data:
            if not row.get("content"):
                continue

            # Combine title and content for better context
            text = f"{row['headline']} {row['content']}"
            documents.append({
                "id": row["id"],
                "title": row["headline"],
                "content": row["content"],
                "text": text,
                "keywords": row.get("keywords", "").split(",") if row.get("keywords") else []
            })

        if not documents:
            continue

        # Get document embeddings
        doc_texts = [doc["text"] for doc in documents]
        doc_embeddings = model.encode(doc_texts, convert_to_tensor=True)

        # Calculate similarities
        similarities = util.pytorch_cos_sim(query_embedding, doc_embeddings)[0]

        # Process results
        for idx, similarity in enumerate(similarities):
            if similarity > 0.3:  # Only include documents with reasonable similarity
                doc = documents[idx]
                
                # Extract semantic context
                doc_doc = nlp(doc["text"])
                sentences = [sent.text.strip() for sent in doc_doc.sents]
                sentence_embeddings = model.encode(sentences, convert_to_tensor=True)
                sentence_similarities = util.pytorch_cos_sim(query_embedding, sentence_embeddings)[0]
                
                # Get top 3 most relevant sentences as context
                top_sentences = []
                if len(sentences) > 0:
                    top_indices = torch.topk(sentence_similarities, min(3, len(sentences)))[1]
                    top_sentences = [sentences[i] for i in top_indices]

                # Count matched keywords
                matched_count = 0
                if doc["keywords"]:
                    for keyword in doc["keywords"]:
                        if any(token in keyword.lower() for token in query_tokens):
                            matched_count += 1

                # Create SemanticSearchResult
                result = SemanticSearchResult(
                    id=doc["id"],
                    title=doc["title"],
                    content=doc["content"],
                    semantic_score=float(similarity),  # Convert tensor to float
                    semantic_context=top_sentences,
                    matched_count=matched_count
                )
                results.append(result)

        page += 1

        # Exit if we've processed all data
        if len(response.data) < page_size:
            break

    # Sort results by semantic score in descending order
    results.sort(key=lambda x: x.semantic_score, reverse=True)

    # Limit results to top 10
    return results[:10]

if __name__ == "__main__":
    # Test the semantic search
    query = "Messi Barcelona"
    results = semantic_search(query)
    for result in results:
        print(f"Title: {result.title}")
        print(f"Semantic Score: {result.semantic_score:.4f}")
        print(f"Semantic Context: {result.semantic_context}")
        print(f"Matched Count: {result.matched_count}")
        print("-" * 50)
