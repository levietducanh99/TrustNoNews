from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

# Base Models
class BaseSearchResult(BaseModel):
    """Model cơ sở cho kết quả tìm kiếm"""
    id: str = Field(..., description="ID của tài liệu")
    title: str = Field(..., description="Tiêu đề tài liệu")
    content: Optional[str] = Field(default=None, description="Nội dung tài liệu")

# Keyword Search Models
class KeywordSearchResult(BaseSearchResult):
    """Model cho kết quả tìm kiếm từ khóa"""
    bm25_score: float = Field(..., ge=0.0, description="Điểm BM25")
    keywords: List[str] = Field(..., description="Các từ khóa khớp")
    matched_count: int = Field(..., ge=0, description="Số từ khóa khớp")

class KeywordSearchResponse(BaseModel):
    """Model cho phản hồi tìm kiếm từ khóa"""
    results: List[KeywordSearchResult]
    total: int = Field(..., ge=0, description="Tổng số kết quả")
    processing_time_ms: float = Field(..., ge=0.0, description="Thời gian xử lý (ms)")

# Semantic Search Models
class SemanticSearchResult(BaseSearchResult):
    """Model cho kết quả tìm kiếm ngữ nghĩa"""
    semantic_score: float = Field(..., ge=0.0, le=1.0, description="Điểm ngữ nghĩa")
    semantic_context: List[str] = Field(..., description="Ngữ cảnh ngữ nghĩa")
    matched_count: int = Field(..., ge=0, description="Số khái niệm ngữ nghĩa khớp")

class SemanticSearchResponse(BaseModel):
    """Model cho phản hồi tìm kiếm ngữ nghĩa"""
    results: List[SemanticSearchResult]
    total: int = Field(..., ge=0, description="Tổng số kết quả")
    processing_time_ms: float = Field(..., ge=0.0, description="Thời gian xử lý (ms)")

# Combined Search Models
class CombinedSearchResult(BaseSearchResult):
    """Model cho kết quả tìm kiếm kết hợp"""
    bm25_score: float = Field(default=0.0, ge=0.0, description="Điểm BM25")
    semantic_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Điểm ngữ nghĩa")
    rrf_score: float = Field(..., ge=0.0, description="Điểm RRF kết hợp")
    ranking: int = Field(..., gt=0, description="Thứ hạng kết quả")
    keywords: Optional[List[str]] = Field(default=None, description="Các từ khóa khớp")
    semantic_context: Optional[List[str]] = Field(default=None, description="Ngữ cảnh ngữ nghĩa")
    matched_count: Optional[int] = Field(default=None, ge=0, description="Số từ khóa/khái niệm khớp")

# Request Models
class SearchRequest(BaseModel):
    """Model cho yêu cầu tìm kiếm"""
    query: str = Field(..., description="Truy vấn tìm kiếm")
    page: Optional[int] = Field(default=1, ge=1, description="Số trang (chỉ dùng cho combined search)")
    page_size: Optional[int] = Field(default=10, ge=1, le=100, description="Số kết quả mỗi trang (chỉ dùng cho combined search)")

    @classmethod
    def validate(cls, values):
        if not values.get("query"):
            raise ValueError("Truy vấn không được để trống.")
        return values

# Response Models
class UnifiedSearchResponse(BaseModel):
    """Model cho phản hồi tìm kiếm thống nhất, bao gồm 3 danh sách kết quả"""
    # Danh sách kết quả tìm kiếm từ khóa
    keyword_results: List[KeywordSearchResult] = Field(..., description="Danh sách kết quả tìm kiếm từ khóa (BM25)")
    total_keyword: int = Field(..., ge=0, description="Tổng số kết quả từ khóa")
    keyword_time_ms: float = Field(..., ge=0.0, description="Thời gian xử lý tìm kiếm từ khóa (ms)")
    
    # Danh sách kết quả tìm kiếm ngữ nghĩa
    semantic_results: List[SemanticSearchResult] = Field(..., description="Danh sách kết quả tìm kiếm ngữ nghĩa")
    total_semantic: int = Field(..., ge=0, description="Tổng số kết quả ngữ nghĩa")
    semantic_time_ms: float = Field(..., ge=0.0, description="Thời gian xử lý tìm kiếm ngữ nghĩa (ms)")
    
    # Danh sách kết quả đã kết hợp bằng RRF
    rrf_results: List[CombinedSearchResult] = Field(..., description="Danh sách kết quả đã kết hợp bằng RRF")
    total_rrf: int = Field(..., ge=0, description="Tổng số kết quả đã kết hợp")
    rrf_time_ms: float = Field(..., ge=0.0, description="Thời gian xử lý RRF (ms)")
    
    # Thông tin phân trang (chỉ áp dụng cho kết quả RRF)
    page: int = Field(..., ge=1, description="Trang hiện tại")
    page_size: int = Field(..., ge=1, le=100, description="Số kết quả mỗi trang")
    
    # Thời gian xử lý tổng
    total_time_ms: float = Field(..., ge=0.0, description="Thời gian xử lý tổng (ms)")

