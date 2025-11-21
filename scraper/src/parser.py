from bs4 import BeautifulSoup, Tag
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import re

# Import the data structure defined in types.py
from .data_structures import BookItem # Changed to relative import

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
    # Find the rating word (e.g., 'Three') in the class list
    for word, rating_int in RATING_MAP.items():
        if word in rating_class:
            return rating_int
    return 0 # Return 0 if rating cannot be determined

def extract_category_from_page(soup: BeautifulSoup) -> str:
    """
    Extracts the category name from the breadcrumb.
    On category listing pages, breadcrumb looks like:
        Home > Books > CategoryName
    On book detail pages, it's the same structure.
    Homepage does not contain a category; we avoid crawling homepage.
    """

    # All <a> inside breadcrumb
    links = soup.select("ul.breadcrumb a")

    # Case 1: Category listing pages or detail pages
    # Example structure:
    #   [0]=Home, [1]=Books, [2]=Poetry
    if len(links) >= 3:
        name = links[2].text.strip()
        if name and name.lower() != "books":
            return name

    # Case 2: Fallback - use the active breadcrumb item
    # e.g. <li class="active">Poetry</li>
    active = soup.select_one("ul.breadcrumb li.active")
    if active:
        txt = active.text.strip()
        # Exclude structural labels, keep real category text
        if txt not in ["Home", "Books"]:
            return txt

    # Should rarely happen; homepage is not crawled
    return "Uncategorized"


def parse_book_page(html_content: str, current_url: str, category: str) -> List[BookItem]:
    """
    Parses the HTML content of a book list page to extract book items.
    
    Args:
        html_content: The raw HTML content of the page.
        current_url: The URL of the page being parsed (for resolving relative links).
        category: The category name derived from the list page's breadcrumb.
        
    Returns:
        A list of BookItem objects found on the page.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    book_items: List[BookItem] = []
    
    # Selector for all product containers on the page
    products = soup.select('article.product_pod') 
    
    print(f"Found {len(products)} potential products on the page.")

    for product in products:
        try:
            # Resolve the product URL
            relative_url = product.select_one('h3 a')['href']
            # Convert to absolute URL using the current page's URL as base
            full_url = urljoin(current_url, relative_url) 
            
            # Extract Title
            title = product.select_one('h3 a')['title'].strip()

            # Extract Price
            # Price is within <p class="price_color">. Remove currency symbol.
            price_text = product.select_one('p.price_color').text.replace('£', '').strip()
            price = float(price_text) # Convert the string price to a float number

            # Extract Rating
            # The rating is in the class attribute, e.g., <p class="star-rating Three">
            rating_classes = product.select_one('p.star-rating')['class']
            rating = parse_rating(' '.join(rating_classes)) # Pass all classes to helper

            # Extract Availability
            # Availability text is typically in a p tag with classes 'instock' and 'availability'
            availability = product.select_one('p.instock.availability').text.strip()
            # Clean up the string (e.g., remove multiple spaces/newlines)
            availability = ' '.join(availability.split()) 
            
            # Create and append the BookItem object
            book_item = BookItem(
                title=title,
                price=price,
                availability=availability,
                rating=rating,
                category=category, # <-- THIS IS THE KEY FIX
                url=full_url
            )
            book_items.append(book_item)
            
        except Exception as e:
            # Log any parsing errors for a specific item, but continue with the rest
            print(f"ERROR: Failed to parse a product on the page. Skipping item. Error: {e}")
            continue

    return book_items