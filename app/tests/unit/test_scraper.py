from app.utils.Scraper.scraper import scrape

def main():
    # URL to test the scrape function
    url = "https://www.huffpost.com/entry/clickbait_n_3473825"

    # Call the scrape function
    result = scrape(url)

    # Print the result
    print("Scrape Result:")
    print(result)

if __name__ == "__main__":
    main()

