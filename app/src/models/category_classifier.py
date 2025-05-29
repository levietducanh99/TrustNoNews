from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F
import time
import re


class CategoryClassifier:
    def __init__(self, model_name="textattack/roberta-base-ag-news"):
        print(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.labels = ["World", "Sports", "Business", "Sci/Tech"]
        
        # Define subcategories for each main category
        self.subcategories = {
            "World": {
                "Politics": ["government", "election", "president", "minister", "parliament", "democracy", "political"],
                "International Relations": ["treaty", "diplomatic", "foreign", "embassy", "international", "global", "nations"],
                "Conflict": ["war", "military", "troops", "attack", "defense", "terrorism", "conflict", "violence"],
                "Environment": ["climate", "environment", "pollution", "sustainable", "conservation", "wildlife"],
                "Humanitarian": ["aid", "refugee", "crisis", "hunger", "poverty", "human rights", "disaster"],
            },
            "Sports": {
                "Football": ["football", "soccer", "fifa", "goal", "striker", "midfielder", "coach", "league"],
                "Basketball": ["basketball", "nba", "dunk", "court", "player", "team", "point guard"],
                "Tennis": ["tennis", "racket", "court", "grand slam", "tournament", "wimbledon", "player"],
                "Olympics": ["olympic", "medal", "athlete", "games", "competition", "champion"],
                "Soccer": ["soccer", "football", "goal", "fifa", "league", "match", "cup"],
                "Baseball": ["baseball", "mlb", "pitcher", "bat", "inning", "home run"],
                "Golf": ["golf", "pga", "tournament", "course", "swing", "hole", "club"],
            },
            "Business": {
                "Economy": ["economy", "growth", "inflation", "recession", "gdp", "economic"],
                "Finance": ["stock", "market", "investor", "share", "trading", "investment", "financial"],
                "Corporate": ["company", "ceo", "corporation", "profit", "revenue", "business", "startup"],
                "Technology Business": ["tech", "startup", "innovation", "venture", "capital", "entrepreneur"],
                "Real Estate": ["property", "real estate", "housing", "mortgage", "commercial", "residential"],
                "Employment": ["job", "employment", "hiring", "wage", "worker", "labor", "staff", "career"],
            },
            "Sci/Tech": {
                "AI & Computing": ["artificial intelligence", "ai", "machine learning", "algorithm", "computer", "programming", "software"],
                "Space": ["space", "nasa", "rocket", "satellite", "planet", "astronomy", "mars", "launch"],
                "Medicine": ["medical", "health", "drug", "treatment", "therapy", "research", "disease", "cure"],
                "Engineering": ["engineering", "design", "innovation", "robotics", "automation", "manufacturing"],
                "Physics": ["physics", "quantum", "particle", "energy", "theory", "experiment"],
                "Biology": ["biology", "gene", "species", "organism", "evolution", "dna", "protein"],
                "Environment Tech": ["climate tech", "renewable", "sustainable", "green", "clean energy", "carbon"],
            }
        }
        print("Model loaded successfully")

    def get_subcategory(self, text, main_category):
        """Determine the subcategory based on keyword matching"""
        text = text.lower()
        subcategory_scores = {}
        
        # Check each subcategory under the main category
        for subcategory, keywords in self.subcategories[main_category].items():
            score = 0
            for keyword in keywords:
                matches = re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', text)
                score += len(matches)
            subcategory_scores[subcategory] = score
        
        # Return the subcategory with the highest score or "General" if no keywords matched
        if all(score == 0 for score in subcategory_scores.values()):
            return f"General {main_category}"
        
        return max(subcategory_scores.items(), key=lambda x: x[1])[0]

    def classify(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            start_time = time.time()
            outputs = self.model(**inputs)
            probs = F.softmax(outputs.logits, dim=1)
            
            # Get probabilities for all categories
            all_probs = probs[0].tolist()
            
            # Get top category
            top_prob, top_class = torch.max(probs, dim=1)
            main_category = self.labels[top_class.item()]
            
            # Determine subcategory
            subcategory = self.get_subcategory(text, main_category)
            
            inference_time = time.time() - start_time

            # Create categories dict with all probabilities
            categories = {
                self.labels[i]: float(all_probs[i]) for i in range(len(self.labels))
            }

            return {
                "main_category": main_category,
                "subcategory": subcategory,
                "full_category": f"{main_category} > {subcategory}",
                "confidence": float(top_prob.item()),
                "all_categories": categories,
                "inference_time": inference_time
            }


if __name__ == "__main__":
    print("News Category Classification")
    print("============================")
    print("Using textattack/roberta-base-ag-news model with extended subcategories")

    # Initialize the classifier
    classifier = CategoryClassifier()

    while True:
        print("\nEnter news text to classify (or 'exit' to quit):")
        query = input("> ")

        if query.lower() == 'exit':
            break

        try:
            result = classifier.classify(query)
            print(f"\n📊 Classification Results:")
            print(f"Main Category: {result['main_category']}")
            print(f"Subcategory: {result['subcategory']}")
            print(f"Full Category: {result['full_category']}")
            print(f"Confidence: {result['confidence'] * 100:.2f}%")
            print(f"\nAll Categories:")
            for category, prob in result['all_categories'].items():
                print(f"  - {category}: {prob * 100:.2f}%")
            print(f"\nProcessing time: {result['inference_time'] * 1000:.2f}ms")
        except Exception as e:
            print(f"Error during classification: {e}")
