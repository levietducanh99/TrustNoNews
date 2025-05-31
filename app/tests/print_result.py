import time  # Import time module
from tests.vectorize import vectorize_texts, calculate_cosine_similarity
import pandas as pd
import numpy as np
import ast
from sentence_transformers import SentenceTransformer


embedder = SentenceTransformer("all-MiniLM-L6-v2")

def compare_with_csv(input_text, csv_file):
    start_time = time.time()  # Start timing

    # Vector hóa chuỗi đầu vào
    input_vector = embedder.encode(input_text, convert_to_tensor=True)


    # Đọc file CSV
    df = pd.read_csv(csv_file)

    # Danh sách lưu kết quả
    similarities = []

    # Duyệt qua từng dòng trong CSV
    for index, row in df.iterrows():
        # Chuyển chuỗi vector về mảng NumPy
        vector = np.array(ast.literal_eval(row['vector']))

        # Tính cosine similarity
        similarity = calculate_cosine_similarity(input_vector, vector)

        # Lưu id và độ tương đồng
        similarities.append({'id': row['id'], 'similarity': similarity})

    # Sắp xếp theo độ tương đồng (giảm dần)
    similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)

    end_time = time.time()  # End timing
    print(f"Execution time: {end_time - start_time:.4f} seconds")  # Print execution time

    return similarities


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


# Ví dụ sử dụng
if __name__ == "__main__":
    data_csv = "data_test/WebScrapData_rows.csv"
    input_text = "NRA TV Host Chides Mark Hamill: What If Galactic Republic Outlawed Lightsabers?"
    csv_file_path = "data_test/database.csv"

    # In kết quả
    # Bước 1: So sánh vector và lấy top 5 ID
    similarities = compare_with_csv(input_text, csv_file_path)

    if similarities:
        print("Top similar vectors:")
        ids = [result['id'] for result in similarities]
        for result in similarities[:5]:
            print(f"ID: {result['id']}, Similarity: {result['similarity']:.4f}")

        # Bước 2: Truy vấn Supabase với danh sách ID
        results = query_csv_by_ids(data_csv, ids[:5])  # Lấy top 5 ID
        if results:
            print("\nSupabase query results:")
            for row in results:
                print(f"ID: {row['id']}, Headline: {row['headline']}, Short Description: {row['short_description']}")
    else:
        print("No similar vectors found.")
