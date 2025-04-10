# BGE 8/4
import os
import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

# Lấy đường dẫn tương đối đến thư mục gốc của dự án
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # Lên 3 cấp từ src/utils/ đến thư mục gốc
MODELS_DIR = BASE_DIR / "models"  # Thư mục models trong dự án

# Thiết lập biến môi trường để lưu trữ mô hình
os.environ['HF_HOME'] = str(MODELS_DIR)
os.environ['TRANSFORMERS_CACHE'] = str(MODELS_DIR)

# Define the local model path
MODEL_NAME = "BAAI/bge-base-en"
MODEL_PATH = MODELS_DIR / "bge"  # Thư mục lưu trữ BGE
MODEL_PATH.mkdir(parents=True, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

try:
    # Load tokenizer and model from local path or download if not available
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        cache_dir=str(MODEL_PATH)  # Chỉ định thư mục cache
    )
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        cache_dir=str(MODEL_PATH)  # Chỉ định thư mục cache
    )
except Exception as e:
    raise RuntimeError(f"Failed to load model or tokenizer: {e}")

# Kiểm tra xem file mô hình có tồn tại trong thư mục không
if not any(MODEL_PATH.iterdir()):
    raise FileNotFoundError(f"Model files not found in {MODEL_PATH}. Ensure the model is downloaded correctly.")

# Move model to GPU if available
if torch.cuda.is_available():
    model.cuda()
    DEVICE = "cuda"
else:
    DEVICE = "cpu"

def vectorize_texts(texts):
    """Vector hóa văn bản bằng BGE, trả về vector 384 chiều."""
    inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
    # Chuyển input sang thiết bị phù hợp (CPU hoặc GPU)
    inputs = {key: val.to(DEVICE) for key, val in inputs.items()}
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state[:, 0, :]  # Lấy CLS token
    embeddings = embeddings.cpu().numpy()  # Chuyển về CPU và numpy
    if embeddings.shape[1] > 384:  # Giảm chiều nếu cần
        embeddings = embeddings[:, :384]  # Cắt xuống 384 chiều
    return embeddings

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

def get_similarity(text1: str, text2: str) -> float:
    vec1 = vectorize_texts(text1)
    vec2 = vectorize_texts(text2)
    similarity = cosine_similarity([vec1], [vec2])[0][0]
    return similarity  # Trả về giá trị float
