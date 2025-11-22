import unittest
from scraper.src.main import extract_category_from_page
from bs4 import BeautifulSoup

class TestIntegration(unittest.TestCase):

    def test_extract_category(self):
        html = """
        <ul class="breadcrumb">
            <li><a href="/">Home</a></li>
            <li><a href="/books">Books</a></li>
            <li class="active">Travel</li>
        </ul>
        """
        soup = BeautifulSoup(html, "html.parser")
        category = extract_category_from_page(soup)
        self.assertEqual(category, "Travel")

if __name__ == "__main__":
    unittest.main()
