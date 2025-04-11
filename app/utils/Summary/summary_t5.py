from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from pathlib import Path

# Initialize model and tokenizer globally for reuse
MODEL_NAME = "mrm8488/t5-base-finetuned-summarize-news"
MODEL_PATH = Path("../../models/summary")
MODEL_PATH.mkdir(parents=True, exist_ok=True)

try:
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_NAME,
        cache_dir=str(MODEL_PATH)
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME,
        cache_dir=str(MODEL_PATH)
    )
except Exception as e:
    raise RuntimeError(f"Failed to load model or tokenizer: {e}")

if not any(MODEL_PATH.iterdir()):
    raise FileNotFoundError(f"Model files not found in {MODEL_PATH}. Ensure the model is downloaded correctly.")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model.to(DEVICE)

def summarize_text(text: str, max_length: int = 400, min_length: int = 100) -> str:
    """Summarize the given text using the T5 model."""
    # Truncate text to avoid exceeding model limits
    max_input_length = tokenizer.model_max_length
    formatted_text = "vietnews: " + text[:max_input_length - 10] + " </s>"

    encoding = tokenizer(
        formatted_text, return_tensors="pt", truncation=True
    )
    input_ids = encoding["input_ids"].to(DEVICE)
    attention_mask = encoding["attention_mask"].to(DEVICE)

    outputs = model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
        max_length=max_length,
        min_length=min_length,
        num_beams=4,
        length_penalty=1.0,
        early_stopping=True
    )

    summary = tokenizer.decode(outputs[0], skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return summary
