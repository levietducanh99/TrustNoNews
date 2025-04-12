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
from langdetect import detect, LangDetectException

# Đảm bảo dữ liệu NLTK cần thiết đã được tải
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)  # Thêm stopwords cho nhiều ngôn ngữ

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
        print(f"\n✅ Đã lưu kết quả vào: {filepath}")
        return filepath
    except Exception as e:
        print(f"\n❌ Không thể lưu kết quả: {e}")
        return None

def extract_publish_date(url):
    """
    Trích xuất ngày xuất bản từ meta tags của trang web.
    Được sử dụng bởi cả hai phương pháp scraping.
    """
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Danh sách các meta tag phổ biến chứa ngày xuất bản trong nhiều ngôn ngữ
        meta_properties = [
            'article:published_time', 'og:published_time', 'article:modified_time',
            'og:modified_time', 'datePublished', 'dateModified', 'pubdate',
            'publishdate', 'publication_date', 'release_date'
        ]

        # Tìm kiếm trong thuộc tính property
        for meta in soup.find_all('meta'):
            if 'property' in meta.attrs and meta.attrs['property'].lower() in meta_properties:
                return meta.attrs['content']

            # Tìm kiếm trong thuộc tính name
            if 'name' in meta.attrs and meta.attrs['name'].lower() in meta_properties:
                return meta.attrs['content']

            # Tìm kiếm trong thuộc tính itemprop
            if 'itemprop' in meta.attrs and meta.attrs['itemprop'].lower() in meta_properties:
                return meta.attrs['content']

        # Tìm schema.org markup
        for script in soup.find_all('script', {'type': 'application/ld+json'}):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'datePublished' in data:
                    return data['datePublished']
            except:
                pass

        return "Không xác định"
    except Exception as e:
        return f"Lỗi khi trích xuất ngày xuất bản: {str(e)}"

def detect_language(url, text=None):
    """
    Phát hiện ngôn ngữ của trang web từ URL hoặc nội dung văn bản
    """
    try:
        if text:
            return detect(text)
        else:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            return detect(response.text)
    except LangDetectException:
        # Nếu không phát hiện được ngôn ngữ, mặc định là tiếng Anh
        return 'en'
    except Exception as e:
        print(f"Lỗi khi phát hiện ngôn ngữ: {e}")
        return 'en'  # Mặc định là tiếng Anh

def scrape(url, language=None):
    """
    Scrape trang web, ưu tiên sử dụng newspaper3k, nếu thất bại sẽ sử dụng readability-lxml.
    Tự động phát hiện ngôn ngữ nếu không được chỉ định.
    """
    try:
        # Tự động phát hiện ngôn ngữ nếu không được chỉ định
        if not language:
            try:
                language = detect_language(url)
                print(f"Đã phát hiện ngôn ngữ: {language}")
            except Exception as e:
                print(f"Không thể phát hiện ngôn ngữ, sử dụng 'auto': {e}")
                language = 'auto'

        # Thử scrape bằng newspaper3k
        article = Article(url, language=language)
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
            "language": language,
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
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)

            # Phát hiện ngôn ngữ từ nội dung trang
            try:
                detected_language = detect(response.text[:5000])  # Sử dụng 5000 ký tự đầu tiên để phát hiện
                print(f"Đã phát hiện ngôn ngữ từ nội dung: {detected_language}")
            except:
                detected_language = language if language else 'auto'

            doc = Document(response.text)
            html = doc.summary()
            soup = BeautifulSoup(html, 'html.parser')
            paragraphs = soup.find_all('p')
            content = '\n'.join([p.get_text() for p in paragraphs])
            publish_date = extract_publish_date(url)

            # Lấy domain cho kết quả
            domain = urlparse(url).netloc

            # Lấy keywords từ meta tags nếu có
            keywords = []
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and 'content' in meta_keywords.attrs:
                keywords = [kw.strip() for kw in meta_keywords['content'].split(',')]

            result = {
                "title": doc.title(),
                "time": publish_date,
                "content": content,
                "summary": doc.short_title(),  # Sử dụng tiêu đề ngắn làm tóm tắt
                "keywords": keywords,
                "url": url,
                "original_domain": domain,
                "language": detected_language,
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

