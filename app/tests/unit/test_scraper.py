import unittest
from app.utils.Scraper.scraper import scrape

class TestScraper(unittest.TestCase):
    def setUp(self):
        # URL for testing
        self.test_url = "https://bongdaplus.vn/goc-check-var/tuyen-thu-quoc-gia-giau-ao-mua-trong-tat-4642632504.html"

    def test_scrape(self):
        try:
            result = scrape(self.test_url)
            self.assertIn("title", result)
            self.assertIn("content", result)
            self.assertIn("summary", result)
            self.assertIn("keywords", result)
            self.assertIn("url", result)
            self.assertIn("method", result)
            print("Scraper Result:", result)
        except Exception as e:
            self.fail(f"scrape raised an exception: {e}")

if __name__ == "__main__":
    unittest.main()
