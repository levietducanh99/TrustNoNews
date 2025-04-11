from app.utils.Scraper.scraper import scrape
from app.utils.Similarity.VectorSimilarity import vectorize_texts, create_faiss_index
from app.utils.Searcher.GoogleSearcher import search_articles as GoogleSearcher
import pandas as pd
import time
import faiss
import numpy as np


def combine_vectors(title_vecs, summary_vecs, title_weight=0.7):
    """Gộp hai vector 384 chiều thành một vector 384 chiều bằng trung bình có trọng số."""
    return title_weight * title_vecs + (1 - title_weight) * summary_vecs


def search_articles(query, articles, index, k=15):
    # Vector hóa truy vấn trực tiếp thành 384 chiều
    query_vec = vectorize_texts([query])  # Shape: (1, 384)
    faiss.normalize_L2(query_vec)
    D, I = index.search(query_vec.astype(np.float32), k)

    results = []
    for i in range(k):
        idx = I[0][i]
        if idx == -1:
            continue
        similarity = 1 - D[0][i] / 2  # Chuyển khoảng cách thành độ tương đồng (0-1)

        results.append({
            'title': articles.iloc[idx]['title'],
            'summary': articles.iloc[idx]['summary'],
            'similarity': similarity
        })
    return results


def process_url(url):
    """Trích xuất title và summary từ URL, kết hợp thành truy vấn."""
    try:
        result = scrape(url)
        if "error" in result:
            raise ValueError(f"Không thể trích xuất dữ liệu từ URL: {result['error']}")
        title = result.get('title', '')
        query = title
        return query
    except Exception as e:
        raise RuntimeError(f"Lỗi khi xử lý URL {url}: {str(e)}")


def create_dummy_data(url):
    """Tạo dữ liệu giả gồm 11 bài báo với title và summary."""
    scrape_url = scrape(url)
    title = scrape_url['title']
    print(title)
    dummy_data = GoogleSearcher(title)
    print(dummy_data)
    return pd.DataFrame(dummy_data)


def show_list_similarity(url):
    articles = create_dummy_data(url)
    if articles['title'].isnull().any() or articles['summary'].isnull().any():
        raise ValueError("Articles contain missing titles or summaries")

    titles = articles['title'].tolist()
    summaries = articles['summary'].tolist()

    title_vecs = vectorize_texts(titles)  # Shape: (N, 384)
    summary_vecs = vectorize_texts(summaries)  # Shape: (N, 384)
    combined_vecs = combine_vectors(title_vecs, summary_vecs)  # Shape: (N, 384)

    index = create_faiss_index(combined_vecs, n_dimensions=384)  # Sử dụng 384 chiều cho SBERT

    try:
        query = process_url(url)
        print(f"Truy vấn được trích xuất: {query}")

        start_time = time.time()

        results = search_articles(query, articles, index, k=15)
        print("Kết quả tìm kiếm:")
        for result in results:
            print(f"\ntitle: {result['title']}")
            print(f"summary: {result['summary']}")
            print(f"similarity: {result['similarity']:.4f}")

        end_time = time.time()
        print(f"\nThời gian tìm kiếm: {end_time - start_time:.4f} giây")

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        results = []

    return results


# def main():
#     url = "https://vnexpress.net/tong-bi-thu-chu-tich-trung-quoc-tap-can-binh-sap-tham-viet-nam-4872223.html"
#     data = create_dummy_data(url)
# if __name__ == "__main__":
#     main()