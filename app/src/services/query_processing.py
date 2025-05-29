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
        self.stop_words = stop_words
    
    def process(self, query: str) -> str:
        if not query or not isinstance(query, str):
            logger.warning(f"Invalid query: {query}")
            return ""
        query = query.lower()
        query = re.sub(r"[^\w\s]", "", query)
        query = re.sub(r"\s+", " ", query).strip()
        words = query.split()
        filtered = [w for w in words if w not in self.stop_words]
        processed_query = " ".join(filtered)
        if not processed_query and query:
            logger.info(f"Query consists only of stopwords, keeping original: '{query}'")
            return query
        return processed_query

