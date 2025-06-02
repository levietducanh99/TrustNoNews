import pandas as pd
from sentence_transformers import SentenceTransformer
import pymongo

def generate_vectors(output_csv_path, model_name='all-MiniLM-L6-v2'):
    # Connect to MongoDB
    connection_string = "mongodb+srv://trung7cyv:Pwrl2KClurSIANRy@cluster0.wwa6we5.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(connection_string)
    
    # Explicitly specify the database name
    db = client["news_scraper"]
    
    # Assuming the collection name is "articles" - adjust if needed
    collection = db["articles"]
    
    # Retrieve documents from MongoDB
    print("📊 Đang kết nối và lấy dữ liệu từ MongoDB...")
    documents = list(collection.find({}))
    print(f"✅ Đã lấy {len(documents)} documents từ MongoDB")
    
    # Debug: Print first document structure if available
    if documents:
        print("Sample document structure:", list(documents[0].keys()))
    else:
        print("WARNING: No documents found in the database!")
        return
    
    # Create dataframe with required fields and assign sequential integer IDs
    data = []
    for i, doc in enumerate(documents, 1):  # Start numbering from 1
        # Extract fields, use empty string if not present
        mongo_id = str(doc.get("_id", ""))
        title = doc.get("title", "")
        content = doc.get("content", "")
        
        # Print debug info for first document
        if i == 1:
            print(f"First document title: {title[:30]}..." if title else "No title field")
            print(f"First document content: {content[:30]}..." if content else "No content field")
        
        data.append({
            "id": i,
            "mongo_id": mongo_id,
            "title": title, 
            "content": content
        })
    
    df = pd.DataFrame(data)
    
    # Debug: Print DataFrame columns
    print("DataFrame columns:", df.columns.tolist())
    
    # Load model
    print("🔄 Đang tải mô hình embedding...")
    model = SentenceTransformer(model_name)
    
    # Ensure title and content columns exist before combining
    if 'title' not in df.columns or 'content' not in df.columns:
        print("WARNING: Required columns not found in data")
        # Create missing columns with empty strings if they don't exist
        if 'title' not in df.columns:
            df['title'] = ''
        if 'content' not in df.columns:
            df['content'] = ''
    
    # Combine title and content
    df['text'] = df['title']
    
    # Generate embeddings
    print("🔄 Đang tạo embedding, vui lòng chờ...")
    embeddings = model.encode(df['text'].tolist(), show_progress_bar=True)
    
    # Create output dataframe with id and vector
    output_df = pd.DataFrame({
        'id': df['id'],
        'mongo_id': df['mongo_id'],  # Include MongoDB ID for reference
        'vector': [list(vec) for vec in embeddings]  # Convert numpy array to list
    })
    
    output_df.to_csv(output_csv_path, index=False)
    print(f"✅ Đã lưu file vector tại: {output_csv_path}")

# Example usage
if __name__ == "__main__":
    output_csv_path = "vectors.csv"
    generate_vectors(output_csv_path)
