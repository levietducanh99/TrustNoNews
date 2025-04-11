from app.utils.Scraper.scraper import scrape
from app.utils.Similarity.VectorSimilarity import vectorize_texts, create_faiss_index
import pandas as pd
import time
import faiss
import numpy as np

def combine_vectors(title_vecs, summary_vecs, title_weight=0.7):
    """Gộp hai vector 768 chiều thành một vector 768 chiều bằng trung bình có trọng số."""
    return title_weight * title_vecs + (1 - title_weight) * summary_vecs

def search_articles(query, articles, index, k=15):
    # Vector hóa truy vấn trực tiếp thành 768 chiều
    query_vec = vectorize_texts([query])  # Shape: (1, 768)
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
        # Gọi hàm scrape từ scraper.py
        result = scrape(url)

        # Kiểm tra xem scrape có thành công không
        if "error" in result:
            raise ValueError(f"Không thể trích xuất dữ liệu từ URL: {result['error']}")

        title = result.get('title', '')
        summary = result.get('summary', '')

        # Kiểm tra nếu title hoặc summary rỗng
        if not title.strip() and not summary.strip():
            raise ValueError("Không trích xuất được title hoặc summary từ URL")

        # Kết hợp title và summary thành một truy vấn
        if title.strip() and summary.strip():
            query = f"{title}. {summary}"
        elif title.strip():
            query = title
        else:
            query = summary

        return query
    except Exception as e:
        raise RuntimeError(f"Lỗi khi xử lý URL {url}: {str(e)}")

def create_dummy_data():
    """Tạo dữ liệu giả gồm 10 bài báo với title và summary."""
    dummy_data = [
        {"title": "Công nghệ AI thay đổi thế giới",
         "summary": "Trí tuệ nhân tạo đang thúc đẩy các ngành công nghiệp với những tiến bộ vượt bậc."},
        {"title": "Khám phá vũ trụ với kính viễn vọng mới",
         "summary": "Kính viễn vọng không gian mới cung cấp hình ảnh chi tiết về các thiên hà xa xôi."},
        {"title": "Biến đổi khí hậu ảnh hưởng nông nghiệp",
         "summary": "Nông dân đối mặt với thách thức từ thời tiết cực đoan và nhiệt độ tăng cao."},
        {"title": "Xe điện dẫn đầu xu hướng giao thông",
         "summary": "Các hãng xe lớn đầu tư mạnh vào công nghệ xe điện để giảm khí thải."},
        {"title": "Ứng dụng blockchain trong tài chính",
         "summary": "Blockchain mang lại sự minh bạch và an toàn cho các giao dịch tài chính."},
        {"title": "Sức khỏe tâm lý trong thời đại số",
         "summary": "Công nghệ số đặt ra nhiều thách thức mới cho sức khỏe tinh thần."},
        {"title": "Robot hỗ trợ y tế tiên tiến",
         "summary": "Robot được sử dụng trong phẫu thuật và chăm sóc bệnh nhân với độ chính xác cao."},
        {"title": "Du lịch bền vững ngày càng phổ biến",
         "summary": "Du khách chọn các điểm đến thân thiện với môi trường để bảo vệ hành tinh."},
        {"title": "Học máy cải thiện dự báo thời tiết",
         "summary": "Mô hình học máy giúp dự báo thời tiết chính xác hơn bao giờ hết."},
        {"title": "Thực tế ảo trong giáo dục",
         "summary": "Công nghệ VR mang đến trải nghiệm học tập sống động và tương tác."},
        {"title": "Tổng Bí thư, Chủ tịch Trung Quốc Tập Cận Bình sắp thăm Việt Nam",
         "summary": "Đây là chuyến thăm cấp nhà nước lần thứ tư của ông Tập Cận Bình đến Việt Nam trên cương vị Tổng Bí thư, Chủ tịch Trung Quốc, diễn ra chưa đầy một năm sau chuyến thăm cấp nhà nước đến Trung Quốc của Tổng Bí thư Tô Lâm.\nTổng Bí thư, Chủ tịch Trung Quốc Tập Cận Bình.\nẢnh: AFPTrung Quốc là nước đầu tiên thiết lập quan hệ ngoại giao với Việt Nam vào ngày 18/1/1950.\nViệt Nam là đối tác thương mại lớn nhất của Trung Quốc trong ASEAN và là đối tác thương mại lớn thứ năm của Trung Quốc trên thế giới.\nSố lượng lưu học sinh Việt Nam tại Trung Quốc trong năm 2024 ở mức kỷ lục, gần 23.000 người, tăng gấp đôi so với năm 2019.",
         }
    ]
    return pd.DataFrame(dummy_data)

def show_list_similarity(url):
    # Tạo dữ liệu giả thay vì đọc từ file
    articles = create_dummy_data()

    # Kiểm tra dữ liệu đầu vào
    if articles['title'].isnull().any() or articles['summary'].isnull().any():
        raise ValueError("Articles contain missing titles or summaries")

    titles = articles['title'].tolist()
    summaries = articles['summary'].tolist()

    title_vecs = vectorize_texts(titles)  # Shape: (N, 768)
    summary_vecs = vectorize_texts(summaries)  # Shape: (N, 768)
    combined_vecs = combine_vectors(title_vecs, summary_vecs)  # Shape: (N, 768)

    index = create_faiss_index(combined_vecs, n_dimensions=768)  # Sử dụng 768 chiều cho BGE

    try:
        # Trích xuất truy vấn từ URL
        query = process_url(url)
        print(f"Truy vấn được trích xuất: {query}")

        start_time = time.time()

        results = search_articles(query, articles, index, k=15)

        end_time = time.time()
        print(f"\nThời gian tìm kiếm: {end_time - start_time:.4f} giây")

    except Exception as e:
        print(f"Lỗi: {str(e)}")
        results = []  # Trả về danh sách rỗng nếu có lỗi
        
    return results

# def main():
#     url = "https://vnexpress.net/tong-bi-thu-chu-tich-trung-quoc-tap-can-binh-sap-tham-viet-nam-4872223.html"
#     show_list_similarity(url)
# 
# if __name__ == "__main__":
#     main()
