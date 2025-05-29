try:
    from src.elasticsearch.category_classifier import CategoryClassifier
    TORCH_AVAILABLE = True
    TENSORFLOW_AVAILABLE = True
except ImportError as e:
    if "torch" in str(e):
        TORCH_AVAILABLE = False
    elif "tensorflow" in str(e):
        TENSORFLOW_AVAILABLE = False

def test_category_classification():
    if not TORCH_AVAILABLE:
        print("PyTorch is not installed. Please install it to run this test.")
        return
    if not TENSORFLOW_AVAILABLE:
        print("TensorFlow is not installed. Please install it to run this test.")
        return
    classifier = CategoryClassifier()
    query = input("🔎 Nhập truy vấn để phân loại category: ")
    result = classifier.classify(query)
    print(f"\n📝 Query: {query}")
    print(f"📂 Dự đoán category: {result['category']} ({result['confidence'] * 100:.2f}%)")

if __name__ == "__main__":
    test_category_classification()
