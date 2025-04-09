# import nltk
#
# # Ensure the 'punkt' resource is downloaded
# try:
#     nltk.data.find('tokenizers/punkt')
# except LookupError:
#     print("Downloading NLTK 'punkt' resource...")
#     nltk.download('punkt')

from googlesearch import search
from newspaper import Article

query = "Messi dành được worldcuup 2022"
domains = ["bongdaplus.vn", "vnexpress.vn","skysports.com"]  # Specify allowed domains

# Append domain filters to the query
domain_filters = " OR ".join([f"site:{domain}" for domain in domains])
query = f"{query} ({domain_filters})"

print("Search results for:", query)
print("-" * 50)

# Using googlesearch to fetch results
results = search(query, num_results=100, advanced=True)


for result in results:
    title = result.title
    url = result.url
    description = result.description if result.description else "No description available"

    print(f"Title: {title}")
    print(f"URL: {url}")
    print(f"Description: {description}")

    # try:
    #     article = Article(url)
    #     article.download()
    #     article.parse()
    #     article.nlp()
    #
    #     content = article.text
    #     summary = article.summary
    #
    # except Exception as e:
    #     print(f"Error fetching or parsing article: {e}")

    print("-" * 50)

