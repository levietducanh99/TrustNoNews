from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from app.src.models.search_models import (
    SearchRequest,
    UnifiedSearchResponse,
    CombinedSearchResult,
    KeywordSearchResult,
    SemanticSearchResult
)
from app.src.services.search_pipeline import SearchPipeline
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()
search_pipeline = SearchPipeline()

# Thêm metadata về API
API_METADATA = {
    "name": "Search Engine API",
    "version": "1.0.0",
    "description": "API tìm kiếm kết hợp từ khóa (BM25) và ngữ nghĩa",
    "features": [
        "Tìm kiếm từ khóa sử dụng BM25",
        "Tìm kiếm ngữ nghĩa sử dụng Sentence Transformers",
        "Kết hợp kết quả bằng Reciprocal Rank Fusion (RRF)",
        "Phân trang và sắp xếp kết quả",
        "Trả về thông tin chi tiết về điểm số và ngữ cảnh"
    ],
    "endpoints": {
        "/search": "Trả về đầy đủ kết quả từ khóa, ngữ nghĩa và RRF",
        "/search/reranked": "Chỉ trả về kết quả đã rerank",
        "/search/keyword": "Chỉ trả về kết quả tìm kiếm từ khóa",
        "/search/semantic": "Chỉ trả về kết quả tìm kiếm ngữ nghĩa",
        "/search/metadata": "Trả về metadata về kết quả tìm kiếm"
    }
}

@router.get("/search/metadata")
async def get_search_metadata():
    """
    Trả về metadata về API và các endpoint
    """
    return {
        **API_METADATA,
        "timestamp": datetime.now().isoformat(),
        "status": "active"
    }

@router.get("/search/keyword", response_model=list[KeywordSearchResult])
async def search_keyword_only(
    query: str = Query(..., min_length=1, description="Truy vấn tìm kiếm"),
    page: int = Query(1, ge=1, description="Số trang kết quả"),
    page_size: int = Query(10, ge=1, le=100, description="Số kết quả mỗi trang")
):
    """
    API endpoint chỉ trả về kết quả tìm kiếm từ khóa (BM25)
    """
    try:
        search_request = SearchRequest(query=query, page=page, page_size=page_size)
        results = await search_pipeline.execute_search(search_request)
        return results.keyword_results
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm từ khóa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search/semantic", response_model=list[SemanticSearchResult])
async def search_semantic_only(
    query: str = Query(..., min_length=1, description="Truy vấn tìm kiếm"),
    page: int = Query(1, ge=1, description="Số trang kết quả"),
    page_size: int = Query(10, ge=1, le=100, description="Số kết quả mỗi trang")
):
    """
    API endpoint chỉ trả về kết quả tìm kiếm ngữ nghĩa
    """
    try:
        search_request = SearchRequest(query=query, page=page, page_size=page_size)
        results = await search_pipeline.execute_search(search_request)
        return results.semantic_results
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm ngữ nghĩa: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=UnifiedSearchResponse)
async def search(
    query: str = Query(..., min_length=1, description="Truy vấn tìm kiếm"),
    page: int = Query(1, ge=1, description="Số trang kết quả"),
    page_size: int = Query(10, ge=1, le=100, description="Số kết quả mỗi trang"),
    include_metadata: bool = Query(False, description="Bao gồm metadata trong kết quả")
):
    """
    API endpoint cho tìm kiếm
    Trả về 3 danh sách kết quả: từ khóa, ngữ nghĩa và kết quả RRF
    
    Args:
        query: Truy vấn tìm kiếm
        page: Số trang kết quả (mặc định = 1)
        page_size: Số kết quả mỗi trang (mặc định = 10)
        include_metadata: Bao gồm metadata trong kết quả
    
    Returns:
        UnifiedSearchResponse chứa kết quả từ khóa, ngữ nghĩa và RRF
    """
    try:
        start_time = time.time()
        search_request = SearchRequest(query=query, page=page, page_size=page_size)
        
        logger.info(f"Nhận yêu cầu tìm kiếm: {search_request.dict()}")
        results = await search_pipeline.execute_search(search_request)
        
        # Thêm metadata nếu được yêu cầu
        if include_metadata:
            results_dict = results.dict()
            results_dict["metadata"] = {
                "query_processed": search_pipeline.query_processor(query),
                "timestamp": datetime.now().isoformat(),
                "api_version": API_METADATA["version"],
                "total_processing_time": time.time() - start_time
            }
            return results_dict
        
        logger.info(
            f"Hoàn thành tìm kiếm:\n"
            f"1. Kết quả từ khóa:\n"
            f"   - Số lượng: {results.total_keyword} kết quả\n"
            f"   - Thời gian: {results.keyword_time_ms:.2f}ms\n"
            f"2. Kết quả ngữ nghĩa:\n"
            f"   - Số lượng: {results.total_semantic} kết quả\n"
            f"   - Thời gian: {results.semantic_time_ms:.2f}ms\n"
            f"3. Kết quả RRF:\n"
            f"   - Số lượng: {results.total_rrf} kết quả\n"
            f"   - Trang: {results.page}/{results.page_size}\n"
            f"   - Thời gian: {results.rrf_time_ms:.2f}ms\n"
            f"Tổng thời gian xử lý: {results.total_time_ms:.2f}ms"
        )
        return results
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý tìm kiếm: {str(e)}"
        )

@router.get("/search/reranked", response_model=list[CombinedSearchResult])
async def search_reranked(
    query: str = Query(..., min_length=1, description="Truy vấn tìm kiếm"),
    page: int = Query(1, ge=1, description="Số trang kết quả"),
    page_size: int = Query(10, ge=1, le=100, description="Số kết quả mỗi trang")
):
    """
    API endpoint chỉ trả về kết quả đã rerank bằng RRF
    
    Args:
        query: Truy vấn tìm kiếm
        page: Số trang kết quả (mặc định = 1)
        page_size: Số kết quả mỗi trang (mặc định = 10)
    
    Returns:
        Danh sách CombinedSearchResult đã được rerank
    """
    try:
        # Tạo SearchRequest từ query parameters
        search_request = SearchRequest(
            query=query,
            page=page,
            page_size=page_size
        )
        
        # Gọi trực tiếp search_pipeline thay vì gọi qua search endpoint
        results = await search_pipeline.execute_search(search_request)
        return results.rrf_results
    except Exception as e:
        logger.error(f"Lỗi tìm kiếm reranked: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý tìm kiếm reranked: {str(e)}"
        )
