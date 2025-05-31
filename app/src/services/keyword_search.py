import time
import logging
import re
import asyncio
from typing import List
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser, QueryParser, OrGroup
from whoosh import scoring
import spacy

from app.src.models.search_models import KeywordSearchResult, KeywordSearchResponse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KeywordSearch:
    """
    Class thực hiện tìm kiếm dựa trên từ khóa sử dụng BM25
    """
    def __init__(self, index_dir="whoosh_index"):
        """Khởi tạo với thư mục chứa index Whoosh"""
        self.index_dir = index_dir
        self.ix = open_dir(index_dir)
        self.nlp = self._load_spacy_model()

    def _load_spacy_model(self):
        """Load model spaCy để xử lý ngôn ngữ tự nhiên"""
        try:
            return spacy.load("en_core_web_md")
        except OSError:
            logger.info("⏳ Downloading spaCy model...")
            import subprocess
            subprocess.call(["python", "-m", "spacy", "download", "en_core_web_md"])
            return spacy.load("en_core_web_md")

    def _detect_entities(self, query: str) -> List[str]:
        """Nhận diện các thực thể có tên trong truy vấn"""
        doc = self.nlp(query)
        entities = [ent.text for ent in doc.ents if ent.label_ in ("PERSON", "ORG", "GPE", "PRODUCT")]
        return entities

    def _clean_query(self, query: str) -> str:
        """Làm sạch truy vấn, loại bỏ ký tự đặc biệt"""
        # Remove special characters that might interfere with Whoosh parser
        cleaned = re.sub(r'[^\w\s"]', ' ', query)
        # Replace multiple spaces with single space
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    async def search(self, query: str, top_n: int = 10) -> KeywordSearchResponse:
        """
        Thực hiện tìm kiếm từ khóa và trả về kết quả phù hợp với model
        
        Args:
            query: Chuỗi truy vấn tìm kiếm
            top_n: Số lượng kết quả tối đa cần trả về
            
        Returns:
            KeywordSearchResponse chứa danh sách kết quả tìm kiếm từ khóa
        """
        start_time = time.time()
        
        # Clean the query
        cleaned_query = self._clean_query(query)
        
        # Detect entities
        entities = self._detect_entities(cleaned_query)
        if entities:
            logger.info(f"Detected entities: {entities}")
        
        with self.ix.searcher(weighting=scoring.BM25F()) as searcher:
            # Create main query parser with OR grouping for better multi-word handling
            parser = MultifieldParser(["headline", "short_description", "keywords_proper_nouns"], 
                                     schema=self.ix.schema, 
                                     group=OrGroup.factory(0.9))
            
            # Parse the user query
            parsed_query = parser.parse(cleaned_query)
            
            # If we have entities, handle them specially for better relevance
            if entities:
                entity_parser = QueryParser("keywords_proper_nouns", schema=self.ix.schema)
                entity_queries = [entity_parser.parse(entity) for entity in entities]
            
            # Execute search
            results = searcher.search(parsed_query, limit=top_n)
            
            # Construct results according to the model
            keyword_results = []
            for hit in results:
                # Extract query keywords that matched in the document
                keywords = [term for term in cleaned_query.split() 
                           if term.lower() in hit.get("headline", "").lower() or 
                              term.lower() in hit.get("short_description", "").lower()]
                
                # Add entity keywords if found
                for entity in entities:
                    if entity.lower() in hit.get("headline", "").lower() or entity.lower() in hit.get("short_description", "").lower():
                        if entity.lower() not in [k.lower() for k in keywords]:
                            keywords.append(entity)
                
                # Create result object
                result = KeywordSearchResult(
                    id=hit["id"],
                    title=hit.get("headline", ""),
                    content=hit.get("short_description", ""),
                    bm25_score=hit.score,
                    keywords=keywords,
                    matched_count=len(keywords)
                )
                keyword_results.append(result)

        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Create and return response
        return KeywordSearchResponse(
            results=keyword_results,
            total=len(keyword_results),
            processing_time_ms=execution_time
        )
