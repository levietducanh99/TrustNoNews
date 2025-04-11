# utils/Scraper/scraper.py
import requests
from newspaper import Article
from readability.readability import Document
from bs4 import BeautifulSoup
import nltk
import os
import json
from datetime import datetime
from urllib.parse import urlparse

# Đảm bảo dữ liệu NLTK cần thiết đã được tải
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

# Xác định đường dẫn chính xác đến thư mục data có sẵn trong dự án
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # utils/Scraper/
UTILS_DIR = os.path.dirname(CURRENT_DIR)  # utils/
APP_DIR = os.path.dirname(UTILS_DIR)  # app/
DATA_DIR = os.path.join(APP_DIR, 'data')  # app/data/

def save_to_file(data, url):
    """
    Lưu dữ liệu vào file JSON với timestamp trong thư mục data
    """
    # Tạo thư mục results nếu chưa tồn tại
    results_dir = os.path.join(DATA_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)

    # Lấy domain từ URL
    try:
        domain = urlparse(url).netloc
    except:
        domain = "unknown"

    # Tạo tên file với timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{domain}.json"
    filepath = os.path.join(results_dir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n Đã lưu kết quả vào: {filepath}")
        return filepath
    except Exception as e:
        print(f"\n Không thể lưu kết quả: {e}")
        return None

def extract_publish_date(url):
    """
    Trích xuất ngày xuất bản từ meta tags của trang web.
    Được sử dụng bởi cả hai phương pháp scraping.
    """
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        for meta in soup.find_all('meta'):
            if 'property' in meta.attrs and meta.attrs['property'].lower() in ['article:published_time', 'og:published_time']:
                return meta.attrs['content']
            if 'name' in meta.attrs and meta.attrs['name'].lower() in ['pubdate', 'publishdate', 'timestamp']:
                return meta.attrs['content']
        return "Không xác định"
    except Exception as e:
        return f"Lỗi khi trích xuất ngày xuất bản: {str(e)}"

def scrape(url):
    """
    Scrape trang web, ưu tiên sử dụng newspaper3k, nếu thất bại sẽ sử dụng readability-lxml.
    """
    try:
        # Thử scrape bằng newspaper3k
        article = Article(url, language="vi")
        article.download()
        article.parse()
        article.nlp()  # Thực hiện NLP để trích xuất từ khóa, tóm tắt, v.v.
        publish_date = article.publish_date if article.publish_date else extract_publish_date(url)

        # Lấy domain cho kết quả
        domain = urlparse(url).netloc

        result = {
            "title": article.title,
            "time": str(publish_date) if publish_date else "Không xác định",
            "content": article.text,
            "summary": article.summary,
            "keywords": article.keywords,
            "url": url,
            "original_domain": domain,
            "method": "newspaper"
        }

        # Lưu kết quả vào file
        saved_path = save_to_file(result, url)
        result["saved_path"] = saved_path
        return result

    except Exception as e_newspaper:
        print(f"Newspaper scraping failed: {str(e_newspaper)}")
        # Nếu newspaper3k thất bại, thử scrape bằng readability-lxml
        try:
            response = requests.get(url, timeout=10)
            doc = Document(response.text)
            html = doc.summary()
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text() for p in paragraphs])
            publish_date = extract_publish_date(url)

            # Lấy domain cho kết quả
            domain = urlparse(url).netloc

            result = {
                "title": doc.title(),
                "time": publish_date,
                "content": content,
                "summary": doc.short_title(),  # Sử dụng tiêu đề ngắn làm tóm tắt
                "keywords": [meta['content'] for meta in soup.find_all('meta', attrs={'name': 'keywords'})],
                "url": url,
                "original_domain": domain,
                "method": "readability"
            }

            # Lưu kết quả vào file
            saved_path = save_to_file(result, url)
            result["saved_path"] = saved_path
            return result

        except Exception as e_readability:
            print(f"Readability scraping failed: {str(e_readability)}")
            # Trả về lỗi nếu cả hai phương pháp đều thất bại
            error_msg = {
                "error": f"Không thể scrape trang web. Newspaper lỗi: {str(e_newspaper)}. Readability lỗi: {str(e_readability)}",
                "url": url,
                "original_domain": urlparse(url).netloc if url else "unknown",
                "method": "error"
            }
            save_to_file(error_msg, url)
            return error_msg

# def main():
#     # Ví dụ sử dụng
#     url = "https://vnexpress.net/tong-bi-thu-chu-tich-trung-quoc-tap-can-binh-sap-tham-viet-nam-4872223.html"
#     result = scrape(url)
#     print(result)
#
# if __name__ == "__main__":
#     main()