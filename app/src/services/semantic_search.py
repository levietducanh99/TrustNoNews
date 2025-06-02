import pandas as pd
import numpy as np
import torch
import time
import logging
import asyncio
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
import ast
import os
import pymongo
from bson import ObjectId

from app.src.models.search_models import SemanticSearchResult, SemanticSearchResponse

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SemanticSearch:
    """
    Class thực hiện tìm kiếm ngữ nghĩa sử dụng mô hình Sentence Transformers
    """

    def __init__(self,
                 model_name: str = "all-MiniLM-L6-v2",
                 vector_path: str = None,
                 csv_path: str = None,
                 use_npy: bool = True,
                 mongo_uri: str = "mongodb+srv://trung7cyv:Pwrl2KClurSIANRy@cluster0.wwa6we5.mongodb.net/?retryWrites=true&w=majority",
                 mongo_db: str = "news_scraper",
                 mongo_collection: str = "articles"):
        """
        Khởi tạo với các tham số cho semantic search

        Args:
            model_name: Tên mô hình sentence transformer
            vector_path: Đường dẫn đến file npy chứa vectors
            csv_path: Đường dẫn đến file csv chứa vectors
            use_npy: Có sử dụng file npy không
            mongo_uri: MongoDB connection URI
            mongo_db: MongoDB database name
            mongo_collection: MongoDB collection name
        """
        self.model_name = model_name
        self.use_npy = use_npy
        self.model = None
        self.corpus_embeddings = None
        self.corpus_ids = None
        self.document_data = None

        # MongoDB connection settings
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.mongo_client = None
        self.mongo_collection_obj = None

        # Định nghĩa base path tương đối đến thư mục gốc dự án
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        data_dir = os.path.join(root_dir, "tests", "data_test")

        # Thiết lập đường dẫn mặc định nếu không được truyền vào
        self.vector_path = vector_path or os.path.join(data_dir, "vectors.npy")
        self.csv_path = csv_path or os.path.join(data_dir, "vectors_clean.csv")

        # Log thông tin đường dẫn
        logger.info(f"Using vector file: {self.vector_path}")
        logger.info(f"Using CSV file: {self.csv_path}")
        logger.info(f"Using MongoDB: {self.mongo_db}.{self.mongo_collection}")

    def _get_mongo_collection(self):
        """Get MongoDB collection object, initializing connection if needed"""
        if self.mongo_client is None:
            logger.info(f"Connecting to MongoDB: {self.mongo_uri}")
            self.mongo_client = pymongo.MongoClient(self.mongo_uri)
            db = self.mongo_client[self.mongo_db]
            self.mongo_collection_obj = db[self.mongo_collection]
        return self.mongo_collection_obj

    async def _load_model(self):
        """Load mô hình sentence transformer"""
        if self.model is None:
            logger.info(f"Loading model: {self.model_name}...")
            self.model = SentenceTransformer(self.model_name)
        return self.model

    async def _load_embeddings(self):
        """Load vectors từ file npy hoặc csv"""
        if self.corpus_embeddings is None:
            if self.use_npy and os.path.exists(self.vector_path):
                logger.info("Loading vectors from NPY...")
                embeddings = torch.from_numpy(np.load(self.vector_path))
                df = pd.read_csv(self.csv_path)
                ids = df["id"].tolist()
            else:
                logger.info("Loading vectors from CSV...")
                df = pd.read_csv(self.csv_path)
                vectors = df["vector"].apply(ast.literal_eval).tolist()
                ids = df["id"].tolist()
                embeddings = torch.tensor(vectors, dtype=torch.float32)

            self.corpus_embeddings = util.normalize_embeddings(embeddings)
            self.corpus_ids = ids

        return self.corpus_embeddings, self.corpus_ids

    async def _load_document_data(self):
        """Initialize MongoDB connection - actual data will be fetched on demand"""
        if self.document_data is None:
            logger.info(f"Initializing MongoDB connection for document data...")
            # Just ensure the connection is ready
            self._get_mongo_collection()
            # Use a placeholder for document_data since we'll fetch documents on demand
            self.document_data = True
        return self.document_data

    def _get_documents_by_ids(self, ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """Lấy thông tin tài liệu theo ID từ MongoDB"""
        collection = self._get_mongo_collection()

        # Convert string IDs to integers (assuming they're stored as integers in vectors)
        int_ids = [int(id_str) for id_str in ids if id_str.isdigit()]

        # Read the ID mapping from vectors_clean.csv (to map between integer IDs and MongoDB IDs)
        df_vectors = pd.read_csv(self.csv_path)
        if 'mongo_id' in df_vectors.columns:
            # If we have mongo_id column, use it to map to actual MongoDB ObjectIds
            id_mapping = {str(row['id']): row['mongo_id'] for _, row in df_vectors.iterrows()}

            # # Log mapping for debugging
            # logger.info(f"ID mapping from CSV (id -> mongo_id): {id_mapping}")

            mongo_ids = [id_mapping.get(id_str) for id_str in ids if id_str in id_mapping]

            # # Log mongo_ids before conversion
            # logger.info(f"Mongo IDs extracted for requested ids: {mongo_ids}")

            # Filter out None and invalid mongo_ids
            mongo_ids_filtered = [m for m in mongo_ids if m]
            # logger.info(f"Filtered Mongo IDs (non-empty): {mongo_ids_filtered}")

            # Convert string ObjectIds to actual ObjectId objects with error handling
            object_ids = []
            for mid in mongo_ids_filtered:
                try:
                    oid = ObjectId(mid)
                    object_ids.append(oid)
                except Exception as e:
                    logger.warning(f"Invalid ObjectId '{mid}' skipped. Error: {e}")

            # logger.info(f"Converted ObjectIds for Mongo query: {object_ids}")

            # Fetch documents from MongoDB using ObjectIds
            if object_ids:
                logger.info(f"Fetching {len(object_ids)} documents from MongoDB...")
                cursor = collection.find({"_id": {"$in": object_ids}})
                documents = list(cursor)
                logger.info(f"Fetched {len(documents)} documents from MongoDB.")

                # Map documents by their ObjectId string for easy lookup
                docs_map = {str(doc['_id']): doc for doc in documents}

                result = {}
                for id_str in ids:
                    mongo_id = id_mapping.get(id_str)
                    if mongo_id and mongo_id in docs_map:
                        result[id_str] = self._transform_mongo_doc(docs_map[mongo_id], id_str)
                    else:
                        logger.warning(f"Document not found in MongoDB for id_str={id_str} with mongo_id={mongo_id}")
                        result[id_str] = {
                            'id': id_str,
                            'headline': 'Unknown Title',
                            'short_description': '',
                            'category': '',
                            'keywords_proper_nouns': '',
                            'url': '',
                            'published_at': ''
                        }
                return result

        # Fallback: Fetch documents using integer IDs (assuming sequential numbering in make_data.py)
        logger.info(f"Fetching documents from MongoDB using fallback method")
        cursor = collection.find({}).limit(max(int_ids) if int_ids else 0)
        documents = list(cursor)

        # Create a mapping from 1-based index to document
        return {str(i + 1): self._transform_mongo_doc(doc, str(i + 1))
                for i, doc in enumerate(documents) if str(i + 1) in ids}

    def _transform_mongo_doc(self, doc: Dict, str_id: str) -> Dict:
        """Transform MongoDB document to format expected by the application"""
        return {
            'id': str_id,
            'headline': doc.get('title', 'Unknown Title'),
            'short_description': doc.get('content', ''),
            'category': doc.get('source', ''),
            'keywords_proper_nouns': doc.get('keywords', ''),
            'url': doc.get('url', ''),
            'published_at': doc.get('published_at', '')
        }

    async def search(self, query: str, top_k: int = 10) -> SemanticSearchResponse:
        """
        Thực hiện tìm kiếm ngữ nghĩa và trả về kết quả

        Args:
            query: Chuỗi truy vấn tìm kiếm
            top_k: Số lượng kết quả tối đa cần trả về

        Returns:
            SemanticSearchResponse chứa danh sách kết quả tìm kiếm ngữ nghĩa
        """
        start_time = time.time()

        # Load model, embeddings, và khởi tạo kết nối MongoDB song song
        model, (corpus_embeddings, corpus_ids), _ = await asyncio.gather(
            self._load_model(),
            self._load_embeddings(),
            self._load_document_data()
        )

        # Encode query
        logger.info("Encoding query...")
        query_embedding = model.encode(query, convert_to_tensor=True)

        # Fix: Reshape query embedding to 2D before normalizing
        # This prevents the "Dimension out of range" error
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)

        query_embedding = util.normalize_embeddings(query_embedding)

        # Thực hiện semantic search
        logger.info("Performing semantic search...")
        hits = util.semantic_search(query_embedding, corpus_embeddings, top_k=top_k)[0]

        # Lấy ID của các kết quả
        hit_ids = [str(corpus_ids[hit['corpus_id']]) for hit in hits]

        # Lấy thông tin chi tiết của các tài liệu từ MongoDB
        document_info = self._get_documents_by_ids(hit_ids)

        # Tạo danh sách kết quả theo mô hình
        semantic_results = []
        for hit in hits:
            doc_id = str(corpus_ids[hit['corpus_id']])
            doc_info = document_info.get(doc_id, {})

            # Tạo ngữ cảnh ngữ nghĩa từ thông tin tài liệu
            semantic_context = []
            if 'category' in doc_info and doc_info['category']:
                semantic_context.append(f"Source: {doc_info['category']}")
            if 'keywords_proper_nouns' in doc_info and doc_info['keywords_proper_nouns']:
                semantic_context.append(f"Keywords: {doc_info['keywords_proper_nouns']}")
            if 'published_at' in doc_info and doc_info['published_at']:
                semantic_context.append(f"Published: {doc_info['published_at']}")
            if 'url' in doc_info and doc_info['url']:
                semantic_context.append(f"URL: {doc_info['url']}")

            # Tạo đối tượng kết quả
            result = SemanticSearchResult(
                id=doc_id,
                title=doc_info.get('headline', 'Unknown Title'),
                content=str(doc_info.get('short_description') or ''),
                semantic_score=float(hit['score']),
                semantic_context=semantic_context,
                matched_count=len(semantic_context)
            )
            semantic_results.append(result)

        execution_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Tạo và trả về phản hồi
        return SemanticSearchResponse(
            results=semantic_results,
            total=len(semantic_results),
            processing_time_ms=execution_time
        )
