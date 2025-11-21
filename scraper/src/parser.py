from bs4 import BeautifulSoup, Tag
from typing import List, Optional
from urllib.parse import urljoin, urlparse
import re

# Import the data structure defined in types.py
# Assuming the correct path to types.py relative to the current file
from .data_structures import BookItem

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
    Example: 'star-rating Three' -> 3
    """
    # Look for the rating word (e.g., 'Three') present in the class list
    for word, rating_int in RATING_MAP.items():
        if word in rating_class:
            return rating_int
    return 0 # Return 0 if rating cannot be determined

def extract_category_from_page(soup: BeautifulSoup) -> str:
    """
    Extracts the category name from the page's breadcrumb.
    This works best when crawling a specific category's list page.
    """
    # Target the active item in the breadcrumb which usually holds the category name
    # Selector: ul.breadcrumb li.active
    category_tag = soup.select_one('ul.breadcrumb li.active')
    if category_tag:
        # The category name is the text content of the active breadcrumb item
        return category_tag.text.strip()
    
    # Default value, which should ideally be replaced by a specific category when 
    # using the "category-first" scraping strategy.
    return "All products"

def find_category_urls(html_content: str, current_url: str) -> List[str]:
    """
    Finds all specific category URLs from the left sidebar of the main index page.
    These URLs will be used to start the category-first crawl.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    category_links = []
    
    # Target: Locate the nested <ul> list containing the specific category links.
    # Selector: .side_categories ul.nav-list ul.nav-list
    # The first <ul> is 'All products', the inner <ul> contains specific categories.
    inner_list = soup.select_one('.side_categories ul.nav-list ul.nav-list')
    
    if inner_list:
        # Find all <a> tags within the nested list
        for a_tag in inner_list.find_all('a'):
            href = a_tag.get('href')
            if href:
                # Convert relative links to absolute URLs
                absolute_url = urljoin(current_url, href)
                category_links.append(absolute_url)

    print(f"Found {len(category_links)} specific category URLs.")
    return category_links


def parse_book_page(html_content: str, current_url: str) -> List[BookItem]:
    """
    Parses the HTML content of a book listing page to extract book details.
    
    Args:
        html_content: The HTML source code of the page.
        current_url: The URL of the current page (used for resolving relative links).
        
    Returns:
        A list of BookItem objects found on the page.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    book_items: List[BookItem] = []
    
    # Extract the category for the entire current page (e.g., 'Travel', 'Mystery')
    category = extract_category_from_page(soup)

    # Main product list is typically within <article> tags with class 'product_pod'
    product_pods = soup.select('li.col-xs-6.col-sm-4.col-md-3.col-lg-3 > article.product_pod')

    for product in product_pods:
        try:
            # Extract Title
            title_tag = product.select_one('h3 a')
            if not title_tag or not title_tag.get('title'):
                raise ValueError("Product title not found.")
            title = title_tag['title'].strip()
            
            # Extract URL
            relative_url = title_tag['href']
            full_url = urljoin(current_url, relative_url)

            # Extract Price (using robust regex to handle currency symbols/mangled text)
            price_tag = product.select_one('p.price_color')
            if not price_tag:
                 raise ValueError("Price tag not found.")
                 
            price_text = price_tag.text.strip()
            
            # Use regex to strip all characters that are not digits or a decimal point
            cleaned_price_text = re.sub(r'[^\d.]', '', price_text) 
            
            if not cleaned_price_text:
                raise ValueError(f"Price text '{price_text}' could not be cleaned into a valid number.")

            # Convert the cleaned price string to a float
            price = float(cleaned_price_text) 

            # Extract Rating
            # Rating is in the class attribute, e.g., <p class="star-rating Three">
            rating_tag = product.select_one('p.star-rating')
            if not rating_tag or not rating_tag.get('class'):
                raise ValueError("Rating tag or class not found.")
                
            rating_classes = rating_tag['class']
            rating = parse_rating(' '.join(rating_classes)) 

            # Extract Availability
            # Availability text is typically in a p tag with classes 'instock' and 'availability'
            availability_tag = product.select_one('p.instock.availability')
            if not availability_tag:
                 raise ValueError("Availability tag not found.")
                 
            availability = availability_tag.text.strip()
            # Clean up the string (e.g., remove multiple spaces/newlines)
            availability = ' '.join(availability.split()) 
            
            # Create and append the BookItem object
            book_item = BookItem(
                title=title,
                price=price,
                availability=availability,
                rating=rating,
                category=category, # *** This now holds the correct category name ***
                url=full_url
            )
            book_items.append(book_item)
            
        except Exception as e:
            # Log any parsing errors for a specific item, but continue with the rest
            print(f"ERROR: Failed to parse a product on the page. Skipping item. Error: {e}")
            continue

    print(f"Successfully parsed {len(book_items)} items from the page. Category: {category}")
    return book_items