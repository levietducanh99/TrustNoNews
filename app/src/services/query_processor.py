import re
import logging

try:
    from nltk.corpus import stopwords
except ModuleNotFoundError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "nltk"])
    from nltk.corpus import stopwords

try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    import nltk
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

logger = logging.getLogger(__name__)

class QueryProcessor:
    """
    Class xử lý truy vấn tìm kiếm, bao gồm làm sạch truy vấn và loại bỏ stop words
    """
    def __init__(self):
        """Khởi tạo QueryProcessor"""
        self.stop_words = stop_words
    
    def process(self, query: str) -> str:
        """
        Xử lý truy vấn bằng cách làm sạch và loại bỏ stop words
        
        Args:
            query: Chuỗi truy vấn đầu vào
            
        Returns:
            Chuỗi truy vấn đã được xử lý
        """
        if not query or not isinstance(query, str):
            logger.warning(f"Invalid query: {query}")
            return ""
            
        # Chuyển về chữ thường
        query = query.lower()
        
        # Loại bỏ ký tự đặc biệt
        query = re.sub(r"[^\w\s]", "", query)
        
        # Loại bỏ khoảng trắng thừa
        query = re.sub(r"\s+", " ", query).strip()

        # Bỏ stopwords
        words = query.split()
        filtered = [w for w in words if w not in self.stop_words]
        
        processed_query = " ".join(filtered)
        
        # Nếu sau khi lọc hết thì giữ nguyên truy vấn gốc
        if not processed_query and query:
            logger.info(f"Query consists only of stopwords, keeping original: '{query}'")
            return query
            
        return processed_query
