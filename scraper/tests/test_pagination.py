import unittest
from scraper.src.pagination import get_next_page_url

class TestPagination(unittest.TestCase):

    def test_next_page_simple(self):
        html = """
        <ul class="pager">
            <li class="next"><a href="page-2.html">next</a></li>
        </ul>
        """
        result = get_next_page_url(html, "https://books.toscrape.com/catalogue/page-1.html")
        self.assertEqual(
            result,
            "https://books.toscrape.com/catalogue/page-2.html"
        )

    def test_no_next_page(self):
        html = """
        <ul class="pager">
            <li class="previous"><a href="#">previous</a></li>
        </ul>
        """
        result = get_next_page_url(html, "https://books.toscrape.com/catalogue/page-2.html")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
