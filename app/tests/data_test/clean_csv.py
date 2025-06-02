import pandas as pd
import re
import numpy as np
import ast

INPUT_CSV = "vectors.csv"
OUTPUT_CSV = "vectors_clean.csv"
OUTPUT_NPY = "vectors.npy"

def parse_np_float32_string(vec_str):
    # Trích xuất tất cả số thực từ định dạng np.float32(...)
    numbers = re.findall(r'np\.float32\(([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\)', vec_str)
    return [float(num) for num in numbers]

def main():
    print("Đang đọc file gốc...")
    df = pd.read_csv(INPUT_CSV)

    print("Đang ép kiểu ID về số nguyên...")
    df = df.dropna(subset=['id'])  # Bỏ hàng thiếu ID nếu có
    df['id'] = df['id'].astype(int)

    print("Đang xử lý vector...")
    df["vector_clean"] = df["vector"].apply(parse_np_float32_string)

    print(f"Lưu file CSV sạch vào {OUTPUT_CSV}...")
    # Include mongo_id in the output if it exists
    if 'mongo_id' in df.columns:
        df_out = df[["id", "mongo_id", "vector_clean"]].rename(columns={"vector_clean": "vector"})
    else:
        df_out = df[["id", "vector_clean"]].rename(columns={"vector_clean": "vector"})
    
    df_out.to_csv(OUTPUT_CSV, index=False)

    print(f"Lưu file nhị phân .npy vào {OUTPUT_NPY}...")
    np_vectors = np.array(df_out["vector"].apply(lambda x: np.array(x)).tolist(), dtype=np.float32)
    np.save(OUTPUT_NPY, np_vectors)

    print("✅ Hoàn tất!")

if __name__ == "__main__":
    main()
