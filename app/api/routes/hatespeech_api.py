from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
from bs4 import BeautifulSoup
from app.utils.Scraper.scraper import scrape  # Import scrape function
from app.services.check_hatespeech import check_hatespeech  # Import check_hatespeech function

# Khởi tạo FastAPI
app = FastAPI(title="Hate Speech Detection API", description="API to detect hate speech from URL content using unitary/toxic-bert")

# Load mô hình và tokenizer
try:
    tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")
    model = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")
except Exception as e:
    print(f"Error loading model: {e}")
    raise Exception("Failed to load model or tokenizer")

# Danh sách nhãn của mô hình toxic-bert
labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

# Mô tả chi tiết cho từng nhãn
criteria_descriptions = {
    "toxic": "Ngôn ngữ thù địch hoặc tiêu cực tổng quát",
    "severe_toxic": "Ngôn ngữ thù địch nghiêm trọng, cực kỳ độc hại",
    "obscene": "Ngôn ngữ tục tĩu, thô tục",
    "threat": "Lời đe dọa, gây nguy hiểm",
    "insult": "Sự xúc phạm cá nhân",
    "identity_hate": "Kỳ thị dựa trên danh tính (vùng miền, giới tính, v.v.)"
}

# Model để nhận dữ liệu đầu vào từ client
class URLInput(BaseModel):
    url: str
    threshold: float = 0.5  # Ngưỡng mặc định

# Hàm lấy nội dung từ URL
def fetch_content_from_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        text = ' '.join([p.get_text() for p in soup.find_all(['p', 'div', 'span', 'article'])])
        return text.strip()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")

# Hàm kiểm tra ngôn ngữ thù địch
def check_hatespeech_from_content(text: str, threshold: float = 0.5) -> dict:
    if not text:
        return {"error": "No content to analyze"}

    # Token hóa văn bản
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Dự đoán với mô hình
    with torch.no_grad():
        outputs = model(**inputs)

    # Áp dụng sigmoid để lấy xác suất
    probabilities = torch.sigmoid(outputs.logits).squeeze().tolist()

    # Tạo dictionary kết quả
    results = {label: prob for label, prob in zip(labels, probabilities)}
    detected_labels = [(label, prob) for label, prob in results.items() if prob > threshold]

    # Chuẩn bị response
    response = {
        "content_snippet": text[:200] + "..." if len(text) > 200 else text,
        "criteria": [
            {"label": label, "description": criteria_descriptions[label], "probability": prob}
            for label, prob in results.items()
        ],
        "detected": bool(detected_labels)
    }

    if detected_labels:
        max_prob = max(prob for _, prob in detected_labels)
        max_label = [label for label, prob in detected_labels if prob == max_prob][0]
        response.update({
            "conclusion": "Content contains hate speech",
            "main_label": max_label,
            "confidence": max_prob,
            "detected_labels": [
                {"label": label, "probability": prob}
                for label, prob in detected_labels
            ]
        })
    else:
        max_prob = max(probabilities)
        response.update({
            "conclusion": "Content does not contain hate speech",
            "confidence": max(1 - max_prob, 0)
        })

    return response

# Endpoint để kiểm tra hate speech từ URL
@app.post("/check-hatespeech")
async def check_hatespeech(input_data: URLInput):
    try:
        # Lấy nội dung từ URL
        content = fetch_content_from_url(input_data.url)
        # Phân tích nội dung
        result = check_hatespeech_from_content(content, input_data.threshold)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Endpoint để scrape và kiểm tra hate speech
@app.post("/scrape-and-check-hatespeech")
async def scrape_and_check_hatespeech(input_data: URLInput):
    try:
        # Gọi hàm scrape để lấy dữ liệu từ URL
        scrape_result = scrape(input_data.url)
        if "error" in scrape_result:
            raise HTTPException(status_code=400, detail=f"Scraping failed: {scrape_result['error']}")

        # Lấy tiêu đề và nội dung từ kết quả scrape
        title = scrape_result.get("title", "No title available")
        content = scrape_result.get("content", "")

        if not content:
            raise HTTPException(status_code=400, detail="Scraped content is empty")

        # Phân tích nội dung
        result = check_hatespeech_from_content(content, input_data.threshold)
        result["title"] = title  # Thêm tiêu đề vào kết quả
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
