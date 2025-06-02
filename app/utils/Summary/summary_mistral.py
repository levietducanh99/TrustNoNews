import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Configure Google Gemini
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def summarize_text(text: str, max_length: int = 400, min_length: int = 100) -> str:
    """Summarize the given text using Gemini."""
    try:
        # Use Gemini to summarize the text
        summary_prompt = f"Summarize the following text concisely in about {max_length} characters, but not less than {min_length} characters:\n\n{text}"
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=summary_prompt
        )
        summary = response.text.strip()
        return summary
    except Exception as e:
        raise RuntimeError(f"Lỗi khi gọi API Gemini để tóm tắt: {str(e)}")
