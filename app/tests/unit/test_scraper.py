from app.utils.Scraper.scraper import scrape

def main():
    # URL to test the scrape function
    url = "https://e.vnexpress.net/news/tech/enterprises/tech-giant-fpt-partners-with-chelsea-fc-for-global-digital-transformation-4872335.html?fbclid=IwY2xjawJleDdleHRuA2FlbQIxMAABHkA70XlV78dbh5HziH6E9kqDl7liblVqbf7_NGna_lkB7TyM_S10kFGkx5Hn_aem_qFDxmN08Y8CR61GEJsgCIg"

    # Call the scrape function
    result = scrape(url)

    # Print the result
    print("Scrape Result:")
    print(result)

if __name__ == "__main__":
    main()

