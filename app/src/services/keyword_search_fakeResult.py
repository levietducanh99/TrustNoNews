from typing import List
import time
from app.src.models.search_models import KeywordSearchResult, KeywordSearchResponse

def keywordSearch(query: str) -> KeywordSearchResponse:
    """
    Simulate keyword search results using BM25 scoring.
    
    Args:
        query (str): The search query string
        
    Returns:
        KeywordSearchResponse: Response containing keyword search results
    """
    start_time = time.time()
    
    # Simulated keyword search results
    raw_results = [
        {
            "id": "doc1",
            "title": "Introduction to Artificial Intelligence",
            "bm25_score": 15.8,
            "keywords": ["artificial", "intelligence", "machine", "learning"],
            "matched_count": 4,
            "content": "A comprehensive guide to the fundamentals of artificial intelligence and its applications in modern technology."
        },
        {
            "id": "doc2",
            "title": "Deep Learning for Computer Vision",
            "bm25_score": 14.2,
            "keywords": ["deep", "learning", "computer", "vision", "neural"],
            "matched_count": 5,
            "content": "Advanced techniques in deep learning applied to computer vision tasks, including object detection and image classification."
        },
        {
            "id": "doc3",
            "title": "Natural Language Processing with Transformers",
            "bm25_score": 13.5,
            "keywords": ["natural", "language", "processing", "transformers", "bert"],
            "matched_count": 5,
            "content": "Modern approaches to NLP using transformer architectures and their applications in text understanding."
        },
        {
            "id": "doc4",
            "title": "Machine Learning Algorithms Explained",
            "bm25_score": 12.9,
            "keywords": ["machine", "learning", "algorithms", "supervised", "unsupervised"],
            "matched_count": 4,
            "content": "Detailed explanation of various machine learning algorithms and their practical applications."
        },
        {
            "id": "doc5",
            "title": "AI Ethics and Responsible Development",
            "bm25_score": 12.3,
            "keywords": ["ai", "ethics", "responsible", "development", "governance"],
            "matched_count": 5,
            "content": "Exploring ethical considerations and best practices in AI development and deployment."
        },
        {
            "id": "doc6",
            "title": "Reinforcement Learning Fundamentals",
            "bm25_score": 11.7,
            "keywords": ["reinforcement", "learning", "q-learning", "policy", "gradient"],
            "matched_count": 4,
            "content": "Core concepts and algorithms in reinforcement learning, from basic principles to advanced techniques."
        },
        {
            "id": "doc7",
            "title": "AI in Healthcare: Current Applications",
            "bm25_score": 11.2,
            "keywords": ["ai", "healthcare", "medical", "diagnosis", "treatment"],
            "matched_count": 5,
            "content": "Overview of artificial intelligence applications in healthcare, from diagnosis to treatment planning."
        },
        {
            "id": "doc8",
            "title": "Neural Network Architectures",
            "bm25_score": 10.8,
            "keywords": ["neural", "networks", "architecture", "cnn", "rnn"],
            "matched_count": 4,
            "content": "Comprehensive guide to different neural network architectures and their specific use cases."
        }
    ]
    
    # Convert to KeywordSearchResult objects
    results = [KeywordSearchResult(**item) for item in raw_results]
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000
    
    # Create and return response
    return KeywordSearchResponse(
        results=results,
        total=len(results),
        processing_time_ms=processing_time
    )
