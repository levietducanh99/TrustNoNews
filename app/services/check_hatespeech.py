from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load mô hình và tokenizer
tokenizer = AutoTokenizer.from_pretrained("unitary/toxic-bert")
model = AutoModelForSequenceClassification.from_pretrained("unitary/toxic-bert")

# Danh sách nhãn của mô hình toxic-bert
labels = ["toxic", "severe_toxic", "obscene", "threat", "insult", "identity_hate"]

def check_hatespeech(title, content):
    # Gộp title và content để kiểm tra
    text_to_check = f"{title}\n{content}" if title and content else title or content

    if not text_to_check.strip():
        return {"result": "No data to check", "probabilities": {}}

    # Token hóa văn bản
    inputs = tokenizer(text_to_check, return_tensors="pt", padding=True, truncation=True, max_length=512)

    # Dự đoán với mô hình
    with torch.no_grad():
        outputs = model(**inputs)

    # Áp dụng sigmoid để lấy xác suất cho từng nhãn
    probabilities = torch.sigmoid(outputs.logits).squeeze().tolist()
    prob_dict = {label: round(prob, 2) for label, prob in zip(labels, probabilities)}

    # In thông tin chi tiết (giữ lại để debug)
    print(f"Title: {title}")
    print(f"Content: {content}")
    for label, prob in zip(labels, probabilities):
        print(f"{label}: {prob:.2f}")

    # Kiểm tra xem có nhãn nào vượt ngưỡng không
    toxic_detected = any(prob > 0.5 for prob in probabilities)

    if toxic_detected:
        max_prob = max(probabilities)
        max_label = labels[probabilities.index(max_prob)]
        result = f"Text contains hate speech (Label: {max_label}, Confidence: {max_prob:.2f})"
    else:
        result = f"Text does not contain hate speech (Confidence: {max(1 - max(probabilities), 0):.2f})"

    return {"result": result, "probabilities": prob_dict}

def test_hatespeech():
    test_data = [
        {
            "title": "This is a hateful article",
            "content": "All those idiots should just disappear, they’re worthless trash."
        },
        {
            "title": "What a wonderful day",
            "content": "Everyone is so kind and the weather is perfect, let’s enjoy it!"
        },
        {
            "title": "Nobody likes you",
            "content": "You’re a total loser, go away and never come back."
        },
        {
            "title": "Negative opinion",
            "content": "People like that are a plague on society. They do nothing but complain, cause trouble, and drag everyone down."
        },
    ]

    for data in test_data:
        result = check_hatespeech(data["title"], data["content"])
        print(f"Result: {result['result']}\n")