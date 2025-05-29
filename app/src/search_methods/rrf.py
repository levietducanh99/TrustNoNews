from typing import List, Dict, Any
import logging
from app.src.models.search_models import (
    KeywordSearchResult,
    SemanticSearchResult,
    CombinedSearchResult
)

logger = logging.getLogger(__name__)

class RRFMerger:
    """
    Thực hiện kết hợp kết quả tìm kiếm bằng thuật toán Reciprocal Rank Fusion (RRF)
    """
    def __init__(self, k: int = 60):
        """
        Khởi tạo RRF Merger với tham số k
        
        Args:
            k: Tham số điều chỉnh (mặc định = 60)
        """
        self.k = k
        
    def merge(
        self, 
        keyword_results: List[KeywordSearchResult], 
        semantic_results: List[SemanticSearchResult]
    ) -> List[CombinedSearchResult]:
        """
        Kết hợp kết quả tìm kiếm từ khóa và tìm kiếm ngữ nghĩa bằng RRF
        
        Args:
            keyword_results: Danh sách kết quả tìm kiếm từ khóa
            semantic_results: Danh sách kết quả tìm kiếm ngữ nghĩa
            
        Returns:
            Danh sách kết quả đã kết hợp dưới dạng CombinedSearchResult
        """
        logger.info(f"Merging {len(keyword_results)} keyword results and {len(semantic_results)} semantic results")
        
        # Tạo từ điển để theo dõi điểm RRF và thông tin tài liệu
        scores = {}
        documents = {}
        
        # Tính điểm RRF cho kết quả tìm kiếm từ khóa
        for rank, result in enumerate(keyword_results):
            doc_id = result.id
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (self.k + rank)
            
            # Lưu thông tin tài liệu và điểm BM25
            if doc_id not in documents:
                documents[doc_id] = {
                    "id": doc_id,
                    "title": result.title,
                    "content": result.content,
                    "bm25_score": result.bm25_score,
                    "keywords": result.keywords,
                    "keyword_matched_count": result.matched_count
                }
            else:
                documents[doc_id]["bm25_score"] = result.bm25_score
                documents[doc_id]["keywords"] = result.keywords
                documents[doc_id]["keyword_matched_count"] = result.matched_count
        
        # Tính điểm RRF cho kết quả tìm kiếm ngữ nghĩa
        for rank, result in enumerate(semantic_results):
            doc_id = result.id
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (self.k + rank)
            
            # Lưu thông tin tài liệu và điểm semantic
            if doc_id not in documents:
                documents[doc_id] = {
                    "id": doc_id,
                    "title": result.title,
                    "content": result.content,
                    "semantic_score": result.semantic_score,
                    "semantic_context": result.semantic_context,
                    "semantic_matched_count": result.matched_count
                }
            else:
                documents[doc_id]["semantic_score"] = result.semantic_score
                documents[doc_id]["semantic_context"] = result.semantic_context
                documents[doc_id]["semantic_matched_count"] = result.matched_count
        
        # Sắp xếp theo điểm RRF giảm dần
        sorted_doc_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Tạo danh sách kết quả kết hợp
        combined_results = []
        for rank, (doc_id, rrf_score) in enumerate(sorted_doc_ids, 1):
            doc_info = documents[doc_id]
            
            # Tạo đối tượng CombinedSearchResult
            result = CombinedSearchResult(
                id=doc_id,
                title=doc_info.get("title", "Unknown"),
                content=doc_info.get("content", ""),
                bm25_score=doc_info.get("bm25_score", 0.0),
                semantic_score=doc_info.get("semantic_score", 0.0),
                rrf_score=rrf_score,
                ranking=rank,
                keywords=doc_info.get("keywords", None),
                semantic_context=doc_info.get("semantic_context", None),
                matched_count=max(
                    doc_info.get("keyword_matched_count", 0),
                    doc_info.get("semantic_matched_count", 0)
                )
            )
            combined_results.append(result)
        
        logger.info(f"Combined results: {len(combined_results)}")
        return combined_results
