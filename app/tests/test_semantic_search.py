import pandas as pd
import numpy as np
import torch
from sentence_transformers import SentenceTransformer, util
import ast
import time

# Cấu hình
USE_NPY = True  # Đổi thành False nếu dùng vectors_clean.csv
CSV_PATH = "data_test/vectors_clean.csv"
NPY_PATH = "data_test/vectors.npy"
TOP_K = 5
MODEL_NAME = "all-MiniLM-L6-v2"

def load_from_csv(csv_path):
    print("Đang load vector từ CSV...")
    df = pd.read_csv(csv_path)
    vectors = df["vector"].apply(ast.literal_eval).tolist()
    ids = df["id"].tolist()
    embeddings = torch.tensor(vectors, dtype=torch.float32)
    return embeddings, ids

def load_from_npy(npy_path, csv_path):
    print("Đang load vector từ NPY...")
    embeddings = torch.from_numpy(np.load(npy_path))
    df = pd.read_csv(csv_path)
    ids = df["id"].tolist()
    return embeddings, ids

def semantic_search(query_texts):
    print(f"Đang load model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print("Đang encode query...")
    query_embeddings = model.encode(query_texts, convert_to_tensor=True)
    query_embeddings = util.normalize_embeddings(query_embeddings)

    if USE_NPY:
        corpus_embeddings, corpus_ids = load_from_npy(NPY_PATH, CSV_PATH)
    else:
        corpus_embeddings, corpus_ids = load_from_csv(CSV_PATH)

    corpus_embeddings = util.normalize_embeddings(corpus_embeddings)

    print("🔍 Đang thực hiện semantic search...")
    start = time.time()
    hits = util.semantic_search(query_embeddings, corpus_embeddings, top_k=TOP_K)
    duration = time.time() - start
    print(f"✅ Tìm kiếm xong trong {duration:.2f} giây")

    data_file = "data_test/WebScrapData_rows.csv"

    # Hiển thị kết quả kèm thông tin mô tả
    for idx, hit_list in enumerate(hits):
        print(f"\n🔎 Query: {query_texts[idx]}")
        hit_ids = [corpus_ids[hit['corpus_id']] for hit in hit_list]

        # Truy xuất thông tin tương ứng
        info_list = query_csv_by_ids(data_file, hit_ids)
        info_dict = {item["id"]: item for item in info_list}

        for rank, hit in enumerate(hit_list, 1):
            doc_id = corpus_ids[hit['corpus_id']]
            score = hit["score"]
            info = info_dict.get(doc_id, {})

            headline = info.get("headline", "N/A")
            desc = info.get("short_description", "N/A")
            print(f"{rank}. ID: {doc_id} | Score: {score:.4f}")
            print(f"   📰 Headline: {headline}")
            print(f"   📌 Description: {desc}\n")


def query_csv_by_ids(csv_file, ids):
    try:
        # Đọc dữ liệu từ file CSV
        df = pd.read_csv(csv_file)

        # Lọc các dòng có ID nằm trong danh sách ids
        filtered_df = df[df['id'].isin(ids)]

        # Lấy các trường cần thiết: id, headline, short_description
        results = filtered_df[['id', 'headline', 'short_description']].to_dict(orient='records')

        return results

    except Exception as e:
        print(f"Error occurred while reading CSV: {str(e)}")
        return None

if __name__ == "__main__":
    csv_file = "data_test/WebScrapData_rows.csv"
    # Ví dụ query
    queries = ["Messi leave Barcelona"]
    semantic_search(queries)
