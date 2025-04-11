# test_scraper.py
import unittest
from app.utils.Scraper.scraper import scrape_with_newspaper, scrape_with_readability

class TestScraper(unittest.TestCase):
    def setUp(self):
        # URL for testing
        self.test_url = "https://bongdaplus.vn/goc-check-var/tuyen-thu-quoc-gia-giau-ao-mua-trong-tat-4642632504.html"

    def test_scrape_with_newspaper(self):
        try:
            result = scrape_with_newspaper(self.test_url)
            self.assertIn("title", result)
            self.assertIn("content", result)
            self.assertIn("summary", result)
            self.assertIn("keywords", result)
            print("Newspaper Scraper Result:", result)
        except Exception as e:
            self.fail(f"scrape_with_newspaper raised an exception: {e}")

    def test_scrape_with_readability(self):
        try:
            result = scrape_with_readability(self.test_url)
            self.assertIn("title", result)
            self.assertIn("content", result)
            self.assertIn("summary", result)
            self.assertIn("time", result)
            print("Readability Scraper Result:", result)
        except Exception as e:
            self.fail(f"scrape_with_readability raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()