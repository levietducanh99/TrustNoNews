def combineResults(bm25_results: list[dict], semantic_results: list[dict]) -> list[dict]:
    """
    Kết hợp 2 danh sách kết quả dùng RRF (Reciprocal Rank Fusion)
    """
    def rrf(rank): return 1 / (rank + 60)  # RRF công thức

    scores = {}

    # Xếp hạng BM25
    for rank, item in enumerate(bm25_results):
        doc_id = item["id"]
        scores.setdefault(doc_id, {"id": doc_id, "title": item["title"]})
        scores[doc_id]["bm25_score"] = item["bm25_score"]
        scores[doc_id]["rrf_score"] = scores[doc_id].get("rrf_score", 0) + rrf(rank)

    # Xếp hạng semantic
    for rank, item in enumerate(semantic_results):
        doc_id = item["id"]
        scores.setdefault(doc_id, {"id": doc_id, "title": item["title"]})
        scores[doc_id]["semantic_score"] = item["semantic_score"]
        scores[doc_id]["rrf_score"] = scores[doc_id].get("rrf_score", 0) + rrf(rank)

    # Sắp xếp giảm dần theo rrf_score
    sorted_docs = sorted(scores.values(), key=lambda x: x["rrf_score"], reverse=True)

    # Gắn thứ hạng
    for i, doc in enumerate(sorted_docs, start=1):
        doc["ranking"] = i
        doc.setdefault("bm25_score", 0.0)
        doc.setdefault("semantic_score", 0.0)

    return sorted_docs
