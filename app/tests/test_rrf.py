# test_rrf.py

from app.src.search_methods.rrf import rrf_fusion

def main():
    bm25_results = [
        {"id": 1, "title": "Ronaldo scores a hat-trick to secure Portugal's victory", "category": "football", "url": "https://example.com/ronaldo-hat-trick"},
        {"id": 2, "title": "Messi wins Ballon d'Or for the 8th time", "category": "football", "url": "https://example.com/messi-ballon-dor"},
        {"id": 3, "title": "Liverpool beats Man City in a thrilling match", "category": "football", "url": "https://example.com/liverpool-man-city"},
        {"id": 4, "title": "Mbappe officially joins Real Madrid", "category": "football", "url": "https://example.com/mbappe-real"}
    ]

    ilike_results = [
        {"id": 2, "title": "Messi wins Ballon d'Or for the 8th time", "category": "football", "url": "https://example.com/messi-ballon-dor"},
        {"id": 5, "title": "Champions League Final: Man United vs Real Madrid", "category": "football", "url": "https://example.com/champions-league-final"},
        {"id": 1, "title": "Ronaldo scores a hat-trick to secure Portugal's victory", "category": "football", "url": "https://example.com/ronaldo-hat-trick"},
        {"id": 6, "title": "Arsenal signs a talented young striker", "category": "football", "url": "https://example.com/arsenal-new-striker"}
    ]

    final_ranking = rrf_fusion([bm25_results, ilike_results])

    print("📋 Final RRF Ranking:")
    for doc, score in final_ranking:
        print(f"ID: {doc['id']} | Title: {doc['title']} | Category: {doc['category']} | Score: {score:.4f}")

if __name__ == "__main__":
    main()
