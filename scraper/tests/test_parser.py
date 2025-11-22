import unittest
from scraper.src.parser import parse_book_page
from scraper.src.parser import extract_category_from_page
from bs4 import BeautifulSoup

MOCK_HTML_CONTENT = """
<html>
<body>

<ul class="breadcrumb">
    <li><a href="index.html">Home</a></li>
    <li><a href="books.html">Books</a></li>
    <li class="active">Travel</li>
</ul>

<section>
    <!-- BOOK 1 -->
    <article class="product_pod">
        <h3>
            <a href="book1.html" title="A Light in the Attic">A Light in the Attic</a>
        </h3>
        <p class="price_color">£51.77</p>
        <p class="star-rating Three"></p>
        <p class="instock availability">
            In stock
        </p>
    </article>

    <!-- BOOK 2 -->
    <article class="product_pod">
        <h3>
            <a href="book2.html" title="Test Title">Test Title</a>
        </h3>
        <p class="price_color">£22.00</p>
        <p class="star-rating Five"></p>
        <p class="instock availability">
            In stock
        </p>
    </article>

    <!-- BOOK 3 -->
    <article class="product_pod">
        <h3>
            <a href="book3.html" title="Another Book">Another Book</a>
        </h3>
        <p class="price_color">£10.99</p>
        <p class="star-rating One"></p>
        <p class="instock availability">
            Out of stock
        </p>
    </article>

</section>

</body>
</html>
"""


class TestParser(unittest.TestCase):

    def setUp(self):
        self.base_url = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
        # ADD category param
        self.items = parse_book_page(MOCK_HTML_CONTENT, self.base_url, "Travel")

    def test_item_count(self):
        self.assertEqual(len(self.items), 3)

    def test_title_and_category(self):
        self.assertEqual(self.items[0].title, "A Light in the Attic")
        self.assertEqual(self.items[0].category, "Travel")

    def test_price_and_type(self):
        self.assertEqual(self.items[0].price, 51.77)
        self.assertIsInstance(self.items[0].price, float)

    def test_rating_and_type(self):
        self.assertEqual(self.items[0].rating, 3)

    def test_availability(self):
        self.assertEqual(self.items[0].availability, "In stock")

    def test_url_joining(self):
        self.assertIn("book1.html", self.items[0].url)
