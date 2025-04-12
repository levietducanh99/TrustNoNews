# from googlesearch import search #remove this
from duckduckgo_search import DDGS
# from newspaper import Article  # Uncomment if using article parsing

def search_articles(title):
    """
    Search for articles based on the given title and return a list of dictionaries
    containing the article title and summary.
    """
    domains = ["e.vnexpress.net", "skysports.com"]  # Specify allowed domains

    # Append domain filters to the query
    domain_filters = " OR ".join([f"site:{domain}" for domain in domains])
    query = f"{title} ({domain_filters})"

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=10)

    articles = []

    for result in results:
        article_title = result['title']
        article_url = result['href']
        # Simulated summary for demonstration purposes
        article_summary = result['body'] if 'body' in result else "No description available"

        # Uncomment the following block if you want to fetch and parse the article content
        # try:
        #     article = Article(article_url)
        #     article.download()
        #     article.parse()
        #     article.nlp()
        #     article_summary = article.summary
        # except Exception as e:
        #     article_summary = f"Error fetching or parsing article: {e}"

        articles.append({
            "title": article_title,
            "summary": article_summary,
            "url": article_url,
        })

    return articles

def main():
    # Example usage for testing
    test_title = "Tổng Bí thư, Chủ tịch Trung Quốc Tập Cận Bình sắp thăm Việt Nam"
    print(f"Searching for articles with title: '{test_title}'")
    results = search_articles(test_title)
    print(results)

if __name__ == "__main__":
    main()