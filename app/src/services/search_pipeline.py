from typing import List, Dict, Any
import logging
import time
import os
import asyncio
from app.src.models.search_models import (
    SearchRequest,
    UnifiedSearchResponse,
    KeywordSearchResult,
    SemanticSearchResult,
    CombinedSearchResult,
    KeywordSearchResponse
)
from app.src.services.query_processor import QueryProcessor
from app.src.services.semantic_search import SemanticSearch
from app.src.search_methods.rrf import RRFMerger
from app.src.services.keyword_search import KeywordSearch

# Conditional import to handle case when Whoosh index doesn't exist
try:
    HAS_WHOOSH_INDEX = True
except Exception as e:
    HAS_WHOOSH_INDEX = False
    logging.warning(f"KeywordSearch initialization will be deferred: {str(e)}")

logger = logging.getLogger(__name__)

class SearchPipeline:
    """
    Pipeline chính điều phối toàn bộ quá trình tìm kiếm
    """
    def __init__(self,
                 index_dir: str = None,
                 model_name: str = "all-MiniLM-L6-v2",
                 vector_path: str = None,
                 csv_path: str = None,
                 data_path: str = None):
        """
        Khởi tạo pipeline với các thành phần cần thiết và đường dẫn đến dữ liệu
        """
        # Đường dẫn tương đối đến thư mục gốc dự án
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        data_dir = os.path.join(root_dir, "tests", "data_test")

        # Đảm bảo đường dẫn index giống file find-use-whoosh.py
        if index_dir is None:
            # Đường dẫn index chuẩn
            default_index_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "keyword_search", "whoosh_index"))
            if os.path.exists(default_index_path):
                self.index_dir = default_index_path
                logger.info(f"[KeywordSearch] Using Whoosh index at: {default_index_path}")
            else:
                self.index_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "whoosh_index"))
                logger.warning(f"[KeywordSearch] Whoosh index not found, using fallback: {self.index_dir}")
        else:
            self.index_dir = index_dir
            logger.info(f"[KeywordSearch] Using custom Whoosh index at: {self.index_dir}")

        # Thiết lập đường dẫn đến thư mục data_test
        self.vector_path = vector_path or os.path.join(data_dir, "vectors.npy")
        self.csv_path = csv_path or os.path.join(data_dir, "vectors_clean.csv")
        self.data_path = data_path or os.path.join(data_dir, "WebScrapData_rows.csv")

        # Log thông tin đường dẫn cuối cùng
        logger.info(f"Using vector file: {self.vector_path}")
        logger.info(f"Using CSV file: {self.csv_path}")
        logger.info(f"Using data file: {self.data_path}")

        # Khởi tạo các thành phần
        self.query_processor = QueryProcessor()
        try:
            self.keyword_search = KeywordSearch(index_dir=self.index_dir)
            logger.info(f"[KeywordSearch] Initialized with index: {self.index_dir}")
        except Exception as e:
            self.keyword_search = None
            logger.error(f"[KeywordSearch] Failed to initialize: {str(e)}")
        
        # Remove data_path from SemanticSearch initialization since it's not a valid parameter
        self.semantic_search = SemanticSearch(
            model_name=model_name,
            vector_path=self.vector_path,
            csv_path=self.csv_path,
            use_npy=True,
            mongo_uri="mongodb+srv://trung7cyv:Pwrl2KClurSIANRy@cluster0.wwa6we5.mongodb.net/?retryWrites=true&w=majority",
            mongo_db="news_scraper",
            mongo_collection="articles"
        )
        self.rrf_merger = RRFMerger()

    async def execute_search(self, request: SearchRequest) -> UnifiedSearchResponse:
        """
        Thực hiện tìm kiếm thống nhất, trả về 3 danh sách kết quả riêng biệt

        Args:
            request: SearchRequest chứa truy vấn tìm kiếm và thông tin phân trang

        Returns:
            UnifiedSearchResponse chứa kết quả tìm kiếm từ khóa, ngữ nghĩa và kết hợp
        """
        total_start_time = time.time()

        # Xử lý truy vấn - gọi trực tiếp hàm queryProcessing
        processed_query = self.query_processor.process(request.query)
        logger.info(f"Processed query: '{processed_query}' (original: '{request.query}')")

        # Thực hiện tìm kiếm từ khóa (nếu có)
        if self.keyword_search:
            keyword_response = await self.keyword_search.search(processed_query)
            keyword_results = keyword_response.results
            keyword_time = keyword_response.processing_time_ms
        else:
            keyword_results = []
            keyword_time = 0.0

        # Thực hiện tìm kiếm ngữ nghĩa
        semantic_response = await self.semantic_search.search(processed_query)
        semantic_results = semantic_response.results

        # Bắt đầu tính thời gian RRF
        rrf_start_time = time.time()

        # Kết hợp kết quả bằng RRF
        merged_results = self.rrf_merger.merge(keyword_results, semantic_results)

        # Phân trang kết quả RRF
        start_idx = (request.page - 1) * request.page_size
        end_idx = start_idx + request.page_size
        paginated_results = merged_results[start_idx:end_idx] if start_idx < len(merged_results) else []

        # Tính thời gian xử lý
        rrf_time = (time.time() - rrf_start_time) * 1000
        total_time = (time.time() - total_start_time) * 1000

        # Trả về kết quả thống nhất với 3 danh sách
        return UnifiedSearchResponse(
            # Kết quả tìm kiếm từ khóa
            keyword_results=keyword_results,
            total_keyword=len(keyword_results),
            keyword_time_ms=keyword_time,

            # Kết quả tìm kiếm ngữ nghĩa
            semantic_results=semantic_results,
            total_semantic=len(semantic_results),
            semantic_time_ms=semantic_response.processing_time_ms,

            # Kết quả RRF
            rrf_results=paginated_results,
            total_rrf=len(merged_results),
            rrf_time_ms=rrf_time,

            # Thông tin phân trang
            page=request.page,
            page_size=request.page_size,

            # Thời gian xử lý tổng
            total_time_ms=total_time
        )
