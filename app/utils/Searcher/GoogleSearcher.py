from googlesearch import search
# from newspaper import Article  # Uncomment if using article parsing

def search_articles(title):
    """
    Search for articles based on the given title and return a list of dictionaries
    containing the article title and summary.
    """
    domains = ["vnexpress.vn", "skysports.com"]  # Specify allowed domains

    # Append domain filters to the query
    domain_filters = " OR ".join([f"site:{domain}" for domain in domains])
    query = f"{title} ({domain_filters})"

    results = search(query, num_results=100, advanced=True)  # Limit to 10 results for simplicity
    articles = []

    for result in results:
        article_title = result.title
        article_url = result.url
        # Simulated summary for demonstration purposes
        article_summary = result.description if result.description else "No description available"

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
            "summary": article_summary
        })

    return articles

if __name__ == "__main__":
    # Example usage for testing
    test_title = "messi won wc 2022"
    print(f"Searching for articles with title: '{test_title}'")
    results = search_articles(test_title)
    print(results)


