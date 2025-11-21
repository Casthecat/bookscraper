import unittest
from scraper.src.parser import parse_book_page
from scraper.src.types import BookItem
from urllib.parse import urljoin

# 1. TEST FIXTURE
MOCK_HTML_CONTENT = """
<html>
<head><title>A Test Page</title></head>
<body>
    <ul class="breadcrumb">
        <li><a href="../../index.html">Home</a></li>
        <li><a href="../index.html">Travel</a></li>
        <li class="active">Non-Fiction</li> 
        </ul>
    <section>
        <ol class="row">
            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                <article class="product_pod">
                    <h3><a href="../a/light/index.html" title="A Light in the Attic">A Light in the Attic</a></h3>
                    <p class="star-rating Three"></p>
                    <div class="product_price">
                        <p class="price_color">£51.77</p>
                        <p class="instock availability">
                            <i class="icon-ok"></i>
                             In stock (22 available)
                        </p>
                    </div>
                </article>
            </li>

            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                <article class="product_pod">
                    <h3><a href="../tipping/index.html" title="Tipping the Velvet">Tipping the Velvet</a></h3>
                    <p class="star-rating One"></p>
                    <div class="product_price">
                        <p class="price_color">£17.00</p>
                        <p class="instock availability">
                            <i class="icon-ok"></i>
                            In stock (1 available)
                        </p>
                    </div>
                </article>
            </li>
            
            <li class="col-xs-6 col-sm-4 col-md-3 col-lg-3">
                <article class="product_pod">
                    <h3><a href="../some-other-book/index.html" title="Some Other Book">Some Other Book</a></h3>
                    <p class="star-rating Five"></p>
                    <div class="product_price">
                        <p class="price_color">£22.00</p>
                        <p class="instock availability">
                             <i class="icon-ok"></i>
                             <br>
                             In stock (5 available)
                        </p>
                    </div>
                </article>
            </li>
        </ol>
    </section>
</body>
</html>
"""

# TEST CASE 
class TestParser(unittest.TestCase):

    def setUp(self):
        """Setup runs before every test method."""
        # Define the base URL used to resolve relative links in the fixture
        self.base_url = 'http://example.com/catalogue/' 
        
        # Parse the fixture content once
        self.parsed_items = parse_book_page(MOCK_HTML_CONTENT, self.base_url)
        self.item1 = self.parsed_items[0]
        self.item2 = self.parsed_items[1]
        self.item3 = self.parsed_items[2]

    def test_item_count(self):
        """Test if the correct number of items were found."""
        self.assertEqual(len(self.parsed_items), 3, "Should find exactly 3 book items.")

    def test_title_and_category(self):
        """Test title extraction and the common category."""
        # Test Title
        self.assertEqual(self.item1.title, "A Light in the Attic")
        self.assertEqual(self.item2.title, "Tipping the Velvet")
        
        # Test Category (should be the same for all items on the page)
        self.assertEqual(self.item1.category, "Non-Fiction")
        self.assertEqual(self.item2.category, "Non-Fiction")

    def test_price_and_type(self):
        """Test price extraction and ensure it is a float."""
        self.assertIsInstance(self.item1.price, float, "Price should be a float.")
        self.assertEqual(self.item1.price, 51.77, "Price for item 1 is incorrect.")
        self.assertEqual(self.item2.price, 17.00, "Price for item 2 is incorrect.")

    def test_rating_and_type(self):
        """Test rating extraction and ensure it is an integer."""
        self.assertIsInstance(self.item1.rating, int, "Rating should be an integer.")
        self.assertEqual(self.item1.rating, 3, "Rating for item 1 should be 3 (Three Stars).")
        self.assertEqual(self.item2.rating, 1, "Rating for item 2 should be 1 (One Star).")
        self.assertEqual(self.item3.rating, 5, "Rating for item 3 should be 5 (Five Stars).")

    def test_availability(self):
        """Test availability text extraction and cleaning."""
        expected_availability_1 = "In stock (22 available)"
        expected_availability_2 = "In stock (1 available)"
        expected_availability_3 = "In stock (5 available)" 
        
        self.assertEqual(self.item1.availability, expected_availability_1)
        self.assertEqual(self.item2.availability, expected_availability_2)
        # Test cleaning logic for extra whitespace/newlines in item 3
        self.assertEqual(self.item3.availability, expected_availability_3) 

    def test_url_joining(self):
        """Test if relative URLs are correctly converted to absolute URLs."""
        # The parser should use self.base_url ('http://example.com/catalogue/')
        # and join it with the relative link ('../a/light/index.html')
        expected_url_1 = urljoin(self.base_url, "../a/light/index.html")
        expected_url_2 = urljoin(self.base_url, "../tipping/index.html")
        
        self.assertEqual(self.item1.url, expected_url_1)
        self.assertEqual(self.item2.url, expected_url_2)

# If this script is run directly, run the tests
if __name__ == '__main__':
    unittest.main()