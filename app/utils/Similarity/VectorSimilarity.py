import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
# Lấy đường dẫn tương đối đến thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODELS_DIR = BASE_DIR / "models"

# Thiết lập biến môi trường để lưu trữ mô hình
os.environ['HF_HOME'] = str(MODELS_DIR)
os.environ['TRANSFORMERS_CACHE'] = str(MODELS_DIR)

# Define the local model path
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_PATH = MODELS_DIR / "sbert"
MODEL_PATH.mkdir(parents=True, exist_ok=True)

try:
    # Load the SBERT model
    model = SentenceTransformer(
        MODEL_NAME,
        cache_folder=str(MODEL_PATH)  # Specify cache directory
    )
except Exception as e:
    raise RuntimeError(f"Failed to load SBERT model: {e}")

# Kiểm tra xem file mô hình có tồn tại trong thư mục không
if not any(MODEL_PATH.iterdir()):
    raise FileNotFoundError(f"Model files not found in {MODEL_PATH}. Ensure the model is downloaded correctly.")

def vectorize_texts(texts):
    """Vector hóa văn bản bằng SBERT, trả về vector 384 chiều."""
    return model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

def calculate_cosine_similarity(vec1, vec2):
    """Tính độ tương đồng cosine giữa hai vector."""
    return cosine_similarity([vec1], [vec2])[0][0]

def create_faiss_index(vectors, n_dimensions=384):
    """Tạo chỉ mục FAISS với kích thước 384 chiều."""
    assert vectors.shape[1] == n_dimensions, f"Vector dimensions must be {n_dimensions} but got {vectors.shape[1]}"
    index = faiss.IndexFlatL2(n_dimensions)
    faiss.normalize_L2(vectors)
    index.add(vectors.astype(np.float32))
    return index

def get_similarity(text1: str, text2: str):
    vec1 = vectorize_texts([text1])[0]  # Shape: (384,)
    vec2 = vectorize_texts([text2])[0]  # Shape: (384,)
    similarity = calculate_cosine_similarity(vec1, vec2)
    return similarity

def main():
    # Ví dụ sử dụng
    text1 = "This Secret Recipe Will Change Your Dinner Forever"
    text2 = "Despite the enticing headline, the article doesn’t include any recipes, cooking tips, or food hacks. Instead, it dives into a detailed analysis of recent government policy changes affecting agricultural subsidies and food import taxes. It discusses how these political shifts could impact food prices and availability in the coming months — especially for low-income households.tone is formal and heavily focused on economics and legislation. There are charts, expert interviews, and no mention of any “secret recipe.” The only connection to food is in the broader policy implications, not the personal or culinary tone the headline suggests."
    similarity_score = get_similarity(text1, text2)
    print(f"Độ tương đồng giữa hai văn bản: {similarity_score:.4f}")

if __name__ == "__main__":
    main()
