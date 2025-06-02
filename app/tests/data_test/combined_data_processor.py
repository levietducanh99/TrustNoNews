import pandas as pd
import numpy as np
import re
import ast
import os
from sentence_transformers import SentenceTransformer
import pymongo

# File paths
VECTORS_CSV = "vectors.csv"
CLEAN_CSV = "vectors_clean.csv"
VECTORS_NPY = "vectors.npy"

def generate_vectors(output_csv_path, model_name='all-MiniLM-L6-v2'):
    # Connect to MongoDB
    connection_string = "mongodb+srv://trung7cyv:Pwrl2KClurSIANRy@cluster0.wwa6we5.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(connection_string)
    
    # Explicitly specify the database name
    db = client["news_scraper"]
    
    # Assuming the collection name is "articles" - adjust if needed
    collection = db["articles"]
    
    # Check if we already have processed documents
    existing_df = None
    existing_mongo_ids = set()
    max_existing_id = 0
    
    if os.path.exists(output_csv_path):
        print(f"📂 Tìm thấy file vectors hiện có: {output_csv_path}")
        existing_df = pd.read_csv(output_csv_path)
        
        if 'mongo_id' in existing_df.columns:
            # Extract existing MongoDB IDs to avoid reprocessing
            existing_mongo_ids = set(existing_df['mongo_id'].astype(str))
            print(f"✅ Đã tìm thấy {len(existing_mongo_ids)} documents đã xử lý trước đó")
            
            # Find the maximum existing ID to continue sequential numbering
            if 'id' in existing_df.columns and not existing_df['id'].empty:
                max_existing_id = existing_df['id'].max()
                print(f"✅ ID hiện tại lớn nhất: {max_existing_id}")
    
    # Retrieve all documents from MongoDB
    print("📊 Đang kết nối và lấy dữ liệu từ MongoDB...")
    all_documents = list(collection.find({}))
    print(f"✅ Đã lấy {len(all_documents)} documents từ MongoDB")
    
    # Filter out documents that have already been processed
    new_documents = [doc for doc in all_documents if str(doc.get("_id", "")) not in existing_mongo_ids]
    print(f"🔍 Tìm thấy {len(new_documents)} documents mới cần xử lý")
    
    if not new_documents:
        print("✅ Không có documents mới, giữ nguyên file hiện tại")
        return existing_df
    
    # Create dataframe with required fields and assign sequential integer IDs
    data = []
    for i, doc in enumerate(new_documents, max_existing_id + 1):  # Continue numbering from max ID
        # Extract fields, use empty string if not present
        mongo_id = str(doc.get("_id", ""))
        title = doc.get("title", "")
        content = doc.get("content", "")
        
        data.append({
            "id": i,
            "mongo_id": mongo_id,
            "title": title, 
            "content": content
        })
    
    new_df = pd.DataFrame(data)
    
    # Load model
    print("🔄 Đang tải mô hình embedding...")
    model = SentenceTransformer(model_name)
    
    # Ensure title and content columns exist before combining
    if 'title' not in new_df.columns or 'content' not in new_df.columns:
        print("WARNING: Required columns not found in data")
        # Create missing columns with empty strings if they don't exist
        if 'title' not in new_df.columns:
            new_df['title'] = ''
        if 'content' not in new_df.columns:
            new_df['content'] = ''
    
    # Combine title and content
    new_df['text'] = new_df['title']
    
    # Generate embeddings
    print(f"🔄 Đang tạo embedding cho {len(new_df)} documents mới, vui lòng chờ...")
    embeddings = model.encode(new_df['text'].tolist(), show_progress_bar=True)
    
    # Create output dataframe with id and vector
    new_output_df = pd.DataFrame({
        'id': new_df['id'],
        'mongo_id': new_df['mongo_id'],  # Include MongoDB ID for reference
        'vector': [list(vec) for vec in embeddings]  # Convert numpy array to list
    })
    
    # Combine existing and new data if needed
    if existing_df is not None:
        combined_df = pd.concat([existing_df, new_output_df], ignore_index=False)
        print(f"✅ Đã kết hợp {len(existing_df)} documents cũ và {len(new_output_df)} documents mới")
    else:
        combined_df = new_output_df
    
    # Save combined dataframe
    combined_df.to_csv(output_csv_path, index=False)
    print(f"✅ Đã lưu file vector tại: {output_csv_path}")
    
    return combined_df

def parse_np_float32_string(vec_str):
    # Trích xuất tất cả số thực từ định dạng np.float32(...)
    numbers = re.findall(r'np\.float32\(([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\)', vec_str)
    return [float(num) for num in numbers]

def clean_vectors(input_csv, output_csv, output_npy):
    print("Đang đọc file gốc...")
    df = pd.read_csv(input_csv)

    print("Đang ép kiểu ID về số nguyên...")
    df = df.dropna(subset=['id'])  # Bỏ hàng thiếu ID nếu có
    df['id'] = df['id'].astype(int)

    print("Đang xử lý vector...")
    # Check if the vector needs parsing (string with np.float32) or is already in list format
    first_vec = df["vector"].iloc[0] if not df.empty else ""
    
    if isinstance(first_vec, str) and "np.float32" in first_vec:
        print("Phát hiện định dạng np.float32, đang chuyển đổi...")
        df["vector_clean"] = df["vector"].apply(parse_np_float32_string)
    else:
        print("Phát hiện định dạng list, sử dụng trực tiếp...")
        df["vector_clean"] = df["vector"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    print(f"Lưu file CSV sạch vào {output_csv}...")
    # Include mongo_id in the output if it exists
    if 'mongo_id' in df.columns:
        df_out = df[["id", "mongo_id", "vector_clean"]].rename(columns={"vector_clean": "vector"})
    else:
        df_out = df[["id", "vector_clean"]].rename(columns={"vector_clean": "vector"})
    
    df_out.to_csv(output_csv, index=False)

    print(f"Lưu file nhị phân .npy vào {output_npy}...")
    np_vectors = np.array(df_out["vector"].apply(lambda x: np.array(x)).tolist(), dtype=np.float32)
    np.save(output_npy, np_vectors)

    print("✅ Hoàn tất quá trình làm sạch vector!")

def main():
    print("🚀 Bắt đầu quy trình xử lý dữ liệu...")
    
    # Step 1: Generate vectors from MongoDB data (only for new documents)
    print("\n=== PHASE 1: GENERATING VECTORS FROM MONGODB (INCREMENTAL) ===")
    generate_vectors(VECTORS_CSV)
    
    # Step 2: Clean the vectors and save in the required formats
    print("\n=== PHASE 2: CLEANING AND PROCESSING VECTORS ===")
    clean_vectors(VECTORS_CSV, CLEAN_CSV, VECTORS_NPY)
    
    print("\n✅ TOÀN BỘ QUY TRÌNH ĐÃ HOÀN TẤT!")

if __name__ == "__main__":
    main()
