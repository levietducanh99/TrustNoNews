import ollama

def summarize_text(text: str, max_length: int = 400, min_length: int = 100) -> str:
    """Summarize the given text using Ollama."""
    try:
        # Use Ollama to summarize the text
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": f"Tóm tắt nội dung: {text}"}],
            stream=False
        )
        summary = response.get("message", {}).get("content", "").strip()
        return summary
    except Exception as e:
        raise RuntimeError(f"Lỗi khi gọi API Ollama để tóm tắt: {str(e)}")
