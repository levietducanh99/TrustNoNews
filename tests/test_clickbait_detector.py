import sys
import os
# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.clickbait_detector import predict_clickbait, check_clickbait
import time

def test_predict_clickbait():
    """Test the model-only prediction function"""
    test_titles = [
        "10 Shocking Facts About Sleep You Never Knew!",  # Likely clickbait
        "Study Shows Link Between Sleep Duration and Heart Health",  # Likely not clickbait
        "You Won't BELIEVE What This Celebrity Did Next!",  # Likely clickbait
        "New Research Suggests Regular Exercise May Help Prevent Cognitive Decline",  # Likely not clickbait
    ]
    
    for title in test_titles:
        start_time = time.time()
        result = predict_clickbait(title)
        elapsed = time.time() - start_time
        
        print(f"\nTitle: '{title}'")
        print(f"Prediction: {'Clickbait' if result['is_clickbait'] else 'Not clickbait'}")
        print(f"Probability: {result['probability']:.2f}")
        print(f"Clickbait words: {', '.join(result['clickbait_words']) if result['clickbait_words'] else 'None'}")
        print(f"Processing time: {elapsed:.2f} seconds")

def test_full_clickbait_check():
    """Test the full clickbait check with sample content"""
    test_cases = [
        {
            "title": "10 Shocking Facts About Sleep You Never Knew!",
            "content": """Sleep is an essential part of human health. Adults typically need between 7-9 hours of sleep per night.
            REM sleep is when most dreaming occurs. The body repairs itself during deep sleep. 
            Lack of sleep can lead to decreased cognitive function. Some people naturally require less sleep than others.
            Sleep quality is as important as quantity. Sleep disorders affect millions of people worldwide.
            Too much sleep can be associated with health problems. Consistent sleep schedules help maintain circadian rhythm."""
        },
        {
            "title": "Study Shows Link Between Sleep Duration and Heart Health",
            "content": """A recent study published in the Journal of Sleep Research has found significant correlations between sleep duration and cardiovascular health markers.
            Researchers tracked 2,500 participants over a five-year period, measuring sleep patterns against various health metrics.
            The study found that individuals consistently sleeping less than 6 hours or more than 9 hours had higher rates of heart disease and hypertension.
            "Our findings reinforce the importance of quality sleep as a modifiable risk factor for heart health," said lead researcher Dr. Maria Hernandez.
            The research controlled for factors such as age, weight, exercise habits, and diet, suggesting sleep itself plays an independent role in heart health.
            Participants with optimal sleep duration of 7-8 hours showed the lowest risk profiles across all cardiovascular measures."""
        }
    ]
    
    for case in test_cases:
        print(f"\n--- Testing full clickbait check ---")
        print(f"Title: '{case['title']}'")
        
        start_time = time.time()
        result = check_clickbait(case['title'], case['content'])
        elapsed = time.time() - start_time
        
        print(f"Overall result: {'Clickbait' if result['is_clickbait'] else 'Not clickbait'}")
        print(f"Model prediction: {'Clickbait' if result['model_prediction']['is_clickbait'] else 'Not clickbait'}")
        print(f"Similarity score: {result['similarity_score']:.2f}")
        print(f"Explanation: {result['explanation']}")
        print(f"Processing time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    print("Testing clickbait prediction model:")
    test_predict_clickbait()
    
    print("\n\nTesting full clickbait detection:")
    test_full_clickbait_check()
