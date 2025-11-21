import argparse
import sys
import json
import os
from typing import NamedTuple, Set, List
from collections import deque # Used for the URL queue (FIFO)
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# Import all modules from the src folder
from .fetcher import fetch_page, USER_AGENT # Need USER_AGENT for robots.txt
from .parser import parse_book_page, extract_category_from_page # <-- IMPORT THE CATEGORY EXTRACTOR
from .pagination import get_next_page_url, get_base_url
from .robots import RobotsChecker
from .data_structures import BookItem, ScraperArgs 

# --- Configuration ---
OUTPUT_FILE_PATH = 'data/items.jsonl'

# --- Utility Functions (Place save_items_to_jsonl function here) ---
def save_items_to_jsonl(items: List[BookItem], saved_item_keys: Set[str]):
    """
    Saves new BookItems to the items.jsonl file and updates the set of saved keys.
    """
    newly_saved_count = 0
    # Ensure data directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE_PATH), exist_ok=True)
    
    # Check if file exists to decide on logging message
    file_exists = os.path.exists(OUTPUT_FILE_PATH)
    
    with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as f:
        for item in items:
            # Generate a unique key for the item (e.g., based on URL)
            item_key = item.url 
            
            if item_key not in saved_item_keys:
                # Save item to file
                f.write(json.dumps(item.to_jsonl(), ensure_ascii=False) + '\n')
                # Update the set of saved keys
                saved_item_keys.add(item_key)
                newly_saved_count += 1
                
    if newly_saved_count > 0:
        if file_exists:
            print(f"-> Saved {newly_saved_count} NEW unique items to {OUTPUT_FILE_PATH}")
        else:
            print(f"-> Created and saved {newly_saved_count} unique items to {OUTPUT_FILE_PATH}")
    # No logging needed if newly_saved_count is 0

# --- Main Scraper Loop ---
def run_scraper(args: ScraperArgs):
    """
    The main logic loop for the web scraper.
    """
    
    # State tracking
    crawled_urls: Set[str] = set()
    url_queue: deque[str] = deque()

    if args.start.rstrip('/') in ["http://books.toscrape.com", "https://books.toscrape.com"]:
        print("Start URL is homepage. Loading all category URLs...")
        homepage_html = fetch_page(args.start, args.delay_ms)
        if homepage_html:
            categories = extract_all_category_urls(homepage_html, args.start)
            print(f"Discovered {len(categories)} categories.")
            for url in categories:
                url_queue.append(url)

        # Prevent homepage from being scraped or paginated
        crawled_urls.add("http://books.toscrape.com")
        crawled_urls.add("http://books.toscrape.com/")
        crawled_urls.add("https://books.toscrape.com/")
        crawled_urls.add("https://books.toscrape.com")
    else:
        url_queue.append(args.start)


    saved_item_keys: Set[str] = set()
    pages_crawled = 0
    
    # Initialize tools
    # Using USER_AGENT imported from fetcher.py
    robots_checker = RobotsChecker(USER_AGENT) 
    
    # Try to load existing items to prevent duplicates if the file already exists
    if os.path.exists(OUTPUT_FILE_PATH):
        try:
            with open(OUTPUT_FILE_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if 'url' in item:
                            saved_item_keys.add(item['url'])
            print(f"Loaded {len(saved_item_keys)} existing items from previous runs.")
        except Exception as e:
            print(f"WARNING: Could not load existing items from {OUTPUT_FILE_PATH}. Starting fresh. Error: {e}")

    # Main Loop: Continue as long as there are URLs to crawl and the max page limit isn't reached
    while url_queue and pages_crawled < args.max_pages:
        current_url = url_queue.popleft() # Get the next URL from the queue

        # 1. Check if already crawled (redundancy check for safety)
        if current_url in crawled_urls:
            print(f"Skipping {current_url} (already crawled).")
            continue
            
        # 2. Check robots.txt permission
        if not robots_checker.is_url_allowed(current_url):
            # The RobotsChecker handles logging the denial
            continue

        # 3. Fetch the page content
        print(f"Crawling Page {pages_crawled + 1}/{args.max_pages}: {current_url}")
        html_content = fetch_page(current_url, args.delay_ms)
        
        if html_content is None:
            # Fetcher already logged the error, skip to next URL
            crawled_urls.add(current_url)
            continue
            
        # 4. Extract Category FIRST
        soup = BeautifulSoup(html_content, 'html.parser')
        category_name = extract_category_from_page(soup)
        print(f"-> Page Category determined as: {category_name}")
            
        # 5. Parse the page for book items, passing the extracted category
        book_items = parse_book_page(html_content, current_url, category_name) # <-- PASS CATEGORY HERE
            
        # 6. Save unique items
        if not args.dry_run and book_items:
            save_items_to_jsonl(book_items, saved_item_keys)
            
        # 7. Handle Pagination (Find the next page)
        next_page_url = get_next_page_url(html_content, current_url)
        if next_page_url:
            # Add the next page URL to the queue for the next loop iteration
            url_queue.append(next_page_url)
            
        # 8. Update status and counter
        crawled_urls.add(current_url)
        pages_crawled += 1

    print(f"\n--- SCRAPER FINISHED ---")
    print(f"Total Pages Crawled: {pages_crawled}")
    print(f"Total Unique Items Saved: {len(saved_item_keys)}")
    if pages_crawled >= args.max_pages:
        print("Reason: Graceful stop - Max pages limit reached.")
    elif not url_queue:
        print("Reason: Pagination exhausted - Last page reached.")

def extract_all_category_urls(html: str, base_url: str):
    """Extracts all category URLs from the left sidebar."""
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.select('ul.nav-list ul li a')
    urls = []
    for a in links:
        rel = a.get('href')
        if rel:
            urls.append(urljoin(base_url, rel))
    return urls


def parse_arguments() -> ScraperArgs:
    """Parses command line arguments and returns them as a ScraperArgs NamedTuple."""
    parser = argparse.ArgumentParser(
        description="A simple, robust web scraper for books.toscrape.com.",
        formatter_class=argparse.RawTextHelpFormatter # Allows for newlines in help text
    )
    
    # Define arguments
    parser.add_argument(
        '-s', '--start', 
        type=str, 
        default='http://books.toscrape.com/',
        help="The URL to start scraping from (e.g., http://books.toscrape.com/ or a specific category)."
    )
    parser.add_argument(
        '-m', '--max-pages', 
        type=int, 
        default=5,
        help="The maximum number of pages to crawl."
    )
    parser.add_argument(
        '-d', '--delay-ms', 
        type=int, 
        default=1000, 
        help="Polite delay time between requests, in milliseconds (ms)."
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true', 
        help="If set, the scraper will crawl but will NOT save items to the data file."
    )
    
    # Parse and validate
    try:
        args = parser.parse_args()
        
        if args.max_pages <= 0:
            raise ValueError("Max pages must be a positive integer.")
        if args.delay_ms < 0:
            raise ValueError("Delay time must be zero or positive.")
            
        return ScraperArgs(
            start=args.start,
            max_pages=args.max_pages,
            delay_ms=args.delay_ms,
            dry_run=args.dry_run
        )

    except (ValueError, SystemExit) as e:
        if isinstance(e, SystemExit) and e.code == 0:
            # Help was requested, exit cleanly
            sys.exit(0)
        
        print(f"Argument Error: {e}", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)


def main():
    """Main function to run the scraper."""
    print("Starting the web scraper with the following parameters:")
    
    # The ScraperArgs NamedTuple ensures robust argument handling
    args = parse_arguments() 

    # Print parsed arguments
    print(f"  Start URL: {args.start}")
    print(f"  Max Pages: {args.max_pages}")
    print(f"  Delay Time: {args.delay_ms} milliseconds")
    print(f"  Dry Run: {'Yes' if args.dry_run else 'No'}")
    
    # Run the core scraping logic
    run_scraper(args)


if __name__ == '__main__':
    main()