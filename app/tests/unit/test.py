from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Khởi tạo mô hình SBERT
model = SentenceTransformer('all-MiniLM-L6-v2')

# Hai câu ví dụ
sentence_a = "Messi giành Quả bóng vàng 2023."
sentence_b = "Biến đổi khí hậu đe dọa sự sống ở Bắc Cực."

# Vector hóa
embedding_a = model.encode([sentence_a])
embedding_b = model.encode([sentence_b])

# Tính cosine similarity
similarity = cosine_similarity(embedding_a, embedding_b)[0][0]
print(f"Cosine similarity giữa hai câu: {similarity:.4f}")
