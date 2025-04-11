from app.utils.Scraper.scraper import scrape

def main():
    # URL to test the scrape function
    url = "https://www.dailymail.co.uk/tvshowbiz/article-14588373/White-Lotus-friendships-Aimee-Lou-Wood-Walton-Goggins-feud.html"

    # Call the scrape function
    result = scrape(url)

    # Print the result
    print("Scrape Result:")
    print(result)

if __name__ == "__main__":
    main()

