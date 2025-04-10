# utils/scraper.py
import requests
from newspaper import Article
from readability.readability import Document
from bs4 import BeautifulSoup
import nltk

# Đảm bảo dữ liệu NLTK cần thiết đã được tải
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)

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

def scrape_with_newspaper(url):
    """
    Scrape trang web bằng thư viện newspaper3k.
    """
    try:
        article = Article(url, language="vi")
        article.download()
        article.parse()
        article.nlp()  # Thực hiện NLP để trích xuất từ khóa, tóm tắt, v.v.
        publish_date = article.publish_date if article.publish_date else extract_publish_date(url)
        return {
            "title": article.title,
            "time": str(publish_date) if publish_date else "Không xác định",
            "content": article.text,
            "summary": article.summary,
            "keywords": article.keywords
        }
    except Exception as e:
        raise Exception(f"Không thể scrape bằng newspaper3k: {str(e)}")

def scrape_with_readability(url):
    """
    Scrape trang web bằng thư viện readability-lxml.
    """
    try:
        response = requests.get(url, timeout=10)
        doc = Document(response.text)
        html = doc.summary()
        soup = BeautifulSoup(html, 'html.parser')
        paragraphs = soup.find_all('p')
        content = '\n'.join([p.get_text() for p in paragraphs])
        publish_date = extract_publish_date(url)
        return {
            "title": doc.title(),
            "time": publish_date,
            "content": content,
            "summary": doc.short_title(),  # Sử dụng tiêu đề ngắn làm tóm tắt
            "keywords": [meta['content'] for meta in soup.find_all('meta', attrs={'name': 'keywords'})]
        }
    except Exception as e:
        raise Exception(f"Không thể scrape bằng readability: {str(e)}")