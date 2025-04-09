import requests
from bs4 import BeautifulSoup
from newspaper3k import Article

API_KEY = 'AIzaSyDnyM5JJjChJx2FqB-x8A_FqupsgOjvaSY'
CSE_ID = '522da1739e1dd4262'


def fetch_article(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None


def summarize_text(text, ratio=0.2):
    try:
        article = Article('')
        article.text = text
        article.nlp()
        return article.summary
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None


def google_search(query, num_results=5):
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "key": API_KEY,
        "cx": CSE_ID,
        "num": num_results
    }
    res = requests.get(url, params=params)
    results = res.json().get("items", [])

    for item in results:
        print("Title:", item['title'])
        print("Link:", item['link'])
        print("Snippet:", item.get('snippet', ''))

        article_content = fetch_article(item['link'])
        if article_content:
            print("Content:", article_content[:500] + "..." if len(article_content) > 500 else article_content)  # Display first 500 chars
            summary = summarize_text(article_content)
            if summary:
                print("Summary:", summary)

        print('-' * 50)


# Ví dụ
google_search("Ronaldo won worldcup 2022 site:bbc.com")
