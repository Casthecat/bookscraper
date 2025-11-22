from bs4 import BeautifulSoup, Tag
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import re

# Import the data structure defined in types.py
from .data_structures import BookItem  # Changed to relative import

# Define a mapping for string ratings to integers (e.g., 'Three' -> 3)
RATING_MAP = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}

def parse_rating(rating_class: str) -> int:
    """
    Extracts the star rating integer from the HTML class string.
    e.g., 'star-rating Three' -> 3
    """
    for word, rating_int in RATING_MAP.items():
        if word in rating_class:
            return rating_int
    return 0  # Return 0 if rating cannot be determined


def extract_category_from_page(soup: BeautifulSoup) -> str:
    """
    Extracts the category name from the breadcrumb.
    On category listing pages, breadcrumb looks like:
        Home > Books > CategoryName
    """
    links = soup.select("ul.breadcrumb a")

    # Example: Home > Books > Poetry
    if len(links) >= 3:
        name = links[2].text.strip()
        if name and name.lower() != "books":
            return name

    # Fallback: <li class="active">Category</li>
    active = soup.select_one("ul.breadcrumb li.active")
    if active:
        txt = active.text.strip()
        if txt not in ["Home", "Books"]:
            return txt

    return "Uncategorized"


def parse_book_page(html_content: str, current_url: str, category: str) -> List[BookItem]:
    """
    Parses the HTML content of a book list page to extract book items.

    Args:
        html_content: Raw HTML content.
        current_url: URL of the page being parsed.
        category: Breadcrumb-derived category.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    book_items: List[BookItem] = []

    products = soup.select('article.product_pod')
    print(f"Found {len(products)} potential products on the page.")

    for product in products:
        try:
            a_tag = product.select_one('h3 a')
            relative_url = a_tag.get('href')
            full_url = urljoin(current_url, relative_url)

            title = a_tag.get('title')
            if not title:
                title = a_tag.text.strip()

            # Extract Price
            price_text = product.select_one('p.price_color').text.replace('£', '').strip()
            price = float(price_text)

            # Extract Rating
            rating_classes = product.select_one('p.star-rating')['class']
            rating = parse_rating(' '.join(rating_classes))

            # Extract Availability
            availability = product.select_one('p.instock.availability').text.strip()
            availability = ' '.join(availability.split())

            # Create BookItem
            book_item = BookItem(
                title=title,
                price=price,
                availability=availability,
                rating=rating,
                category=category,
                url=full_url
            )

            book_items.append(book_item)

        except Exception as e:
            print(f"ERROR: Failed to parse a product on the page. Skipping item. Error: {e}")
            continue

    return book_items
