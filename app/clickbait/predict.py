import numpy as np
import joblib
from tensorflow.keras.models import load_model
import re
from colorama import Fore, Style, init

# Initialize colorama for colored console output
init()

# Define clickbait words
CLICKBAIT_WORDS = ['shocking', 'wow', 'unbelievable', 'amazing',
                   'you won\'t believe', 'mind-blowing', 'outrageous',
                   'secret', 'never seen before', 'warning', 'urgent',
                   'conspiracy', 'exposed', 'miracle', 'this is why',
                   'banned', 'controversial', 'breaking', 'things', 'NOT']


def preprocess_text(text):
    """Clean and normalize text data"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def predict_clickbait(model, tokenizer, headline, maxlen=500):
    """Predict if a headline is clickbait"""
    clean_headline = preprocess_text(headline)
    token_text = pad_sequences(tokenizer.texts_to_sequences([clean_headline]), maxlen=maxlen)
    probability = model.predict(token_text, verbose=0)[0][0]
    prediction = round(probability)

    clickbait_words_found = [word for word in CLICKBAIT_WORDS
                             if word.lower() in clean_headline.lower()]

    return {
        'is_clickbait': bool(prediction),
        'probability': float(probability),
        'clickbait_words': clickbait_words_found
    }


def load_model_and_tokenizer(model_path='clickbait_model.h5', tokenizer_path='tokenizer.pkl'):
    """Load the trained model and tokenizer"""
    try:
        model = load_model(model_path)
        tokenizer = joblib.load(tokenizer_path)
        print(f"{Fore.GREEN}Model and tokenizer loaded successfully!{Style.RESET_ALL}")
        return model, tokenizer
    except Exception as e:
        print(f"{Fore.RED}Error loading model or tokenizer: {str(e)}{Style.RESET_ALL}")
        return None, None


def main():
    """Main function to test clickbait detection model"""
    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer()

    if model is None or tokenizer is None:
        print(f"{Fore.RED}Cannot proceed without model and tokenizer.{Style.RESET_ALL}")
        return

    print("\nClickbait Detection Tester")
    print("-------------------------")
    print("Enter headlines to test (type 'quit' to exit)\n")

    while True:
        headline = input("Enter a headline: ")

        if headline.lower() == 'quit':
            print(f"{Fore.YELLOW}Exiting program...{Style.RESET_ALL}")
            break

        if not headline.strip():
            print(f"{Fore.YELLOW}Please enter a valid headline.{Style.RESET_ALL}")
            continue

        # Get prediction
        result = predict_clickbait(model, tokenizer, headline)

        # Display results
        label = "Clickbait" if result['is_clickbait'] else "Not Clickbait"
        color = Fore.RED if result['is_clickbait'] else Fore.GREEN

        print(f"\nResult for: {headline}")
        print(f"Prediction: {color}{label}{Style.RESET_ALL}")
        print(f"Clickbait Probability: {result['probability']:.2%}")

        if result['clickbait_words']:
            print("Clickbait words found:", ", ".join(result['clickbait_words']))
        else:
            print("No clickbait words detected")
        print()


if __name__ == "__main__":
    from tensorflow.keras.preprocessing.sequence import pad_sequences

    main()