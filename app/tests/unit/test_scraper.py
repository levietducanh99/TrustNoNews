from app.utils.Scraper.scraper import scrape

def main():
    # URL to test the scrape function
    url = "https://bongdaplus.vn/serie-a/ky-tich-tuoi-70-cua-nguoi-binh-thuong-ranieri-4646132504.html"

    # Call the scrape function
    result = scrape(url)

    # Print the result
    print("Scrape Result:")
    print(result)

if __name__ == "__main__":
    main()

