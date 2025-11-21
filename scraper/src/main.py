import argparse
import sys
import json
import os
from typing import NamedTuple, Set, List
from collections import deque # Used for the URL queue (FIFO)

# Import all modules from the src folder
from .fetcher import fetch_page, USER_AGENT # Need USER_AGENT for robots.txt
# *** Import the new category discovery function ***
from .parser import parse_book_page, find_category_urls 
from .pagination import get_next_page_url, get_base_url
from .robots import RobotsChecker
from .data_structures import BookItem, ScraperArgs 

# --- Configuration ---
OUTPUT_FILE_PATH = 'data/items.jsonl'

# --- Utility Functions ---

def save_items_to_jsonl(items: List[BookItem], saved_item_keys: Set[str]):
    """
    Saves new BookItems to the items.jsonl file and updates the set of saved keys.
    """
    newly_saved_count = 0
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE_PATH), exist_ok=True)
    
    with open(OUTPUT_FILE_PATH, 'a', encoding='utf-8') as f:
        for item in items:
            # Use URL as the unique key to prevent duplicates
            item_key = item.url
            if item_key not in saved_item_keys:
                # Convert BookItem to a dictionary suitable for JSONL
                item_dict = item.to_jsonl()
                # Write the item as a single line JSON
                f.write(json.dumps(item_dict, ensure_ascii=False) + '\n')
                # Update the tracking set
                saved_item_keys.add(item_key)
                newly_saved_count += 1

    print(f"File Save: Saved {newly_saved_count} new items. Total unique items: {len(saved_item_keys)}")


def parse_arguments() -> ScraperArgs:
    """
    Parses command-line arguments and returns them in a structured NamedTuple.
    """
    parser = argparse.ArgumentParser(
        description='A simple web scraper for books.toscrape.com, with politeness and error handling.'
    )
    # Start URL: Default is the main index page
    parser.add_argument(
        '--start',
        type=str,
        default='http://books.toscrape.com/index.html',
        help='The starting URL for the scrape.'
    )
    # Max Pages: Control how many pages to crawl
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Maximum number of pages to crawl (includes the start page). Default is 10.'
    )
    # Delay Time: Politeness delay in milliseconds
    parser.add_argument(
        '--delay-ms',
        type=int,
        default=500,
        help='Minimum delay between requests in milliseconds. Default is 500ms.'
    )
    # Dry Run: For debugging and testing
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='If set, the scraper will run the main loop but skip saving items to file.'
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.delay_ms < 100:
        print("Warning: Delay time is very short. Setting minimum to 100ms.")
        args.delay_ms = 100
        
    return ScraperArgs(
        start=args.start,
        max_pages=args.max_pages,
        delay_ms=args.delay_ms,
        dry_run=args.dry_run
    )


def run_scraper(args: ScraperArgs):
    """
    Executes the main crawling loop, implementing the category-first strategy.
    """
    # 1. Initialize Scrape State
    # Deque for FIFO queue
    url_queue: deque[str] = deque([args.start]) 
    crawled_urls: Set[str] = set()              # Set to track visited URLs
    saved_item_keys: Set[str] = set()           # Set to track saved items by URL key
    pages_crawled = 0
    robots_checker = RobotsChecker(USER_AGENT)
    
    # --- Category Discovery Logic ---
    # Fetch the initial page to find all specific category URLs first.
    print(f"--- Stage 1: Discovering Categories from {args.start} ---")
    initial_page_html = fetch_page(args.start, args.delay_ms)
    
    if initial_page_html is not None:
        # Use the new function to extract all category links from the left sidebar
        category_urls = find_category_urls(initial_page_html, args.start)
        
        # If specific categories are found, switch the crawl strategy: replace the queue
        if category_urls:
            print(f"Strategy changed to Category-First. Found {len(category_urls)} categories. The main index page will be skipped.")
            url_queue.clear() # Clear the initial queue containing only the index page
            
            # Add all found category URLs to the queue. Each category URL is a new starting point.
            for url in category_urls:
                url_queue.append(url)
                
            # Crucial: Mark the original start page (All Products) as crawled
            # to prevent it from being processed later in the main loop.
            crawled_urls.add(args.start)
        else:
            print("No specific categories found. Continuing with standard crawl.")
            
    # --- End Category Discovery Logic ---

    # 2. Main Crawl Loop
    print(f"\n--- Stage 2: Starting Main Crawl Loop ---")
    while url_queue and pages_crawled < args.max_pages:
        # 3. Get the next URL from the queue
        current_url = url_queue.popleft()
        
        # Ensure URL is absolute (simple check)
        if not current_url.startswith('http'):
             print(f"Skipping malformed URL: {current_url}")
             continue

        # Check if already crawled (This will skip the 'All Products' page if categories were found)
        if current_url in crawled_urls:
            continue

        # 4. Robots.txt Check
        if not robots_checker.is_url_allowed(current_url):
            print(f"Skipping {current_url} due to robots.txt restrictions.")
            crawled_urls.add(current_url) # Mark as checked/skipped
            continue
            
        # 5. Fetch the page
        print(f"\nCrawling Page {pages_crawled + 1}/{args.max_pages}: {current_url}")
        html_content = fetch_page(current_url, args.delay_ms)
        
        if html_content is None:
            # If fetching failed, skip to the next URL
            crawled_urls.add(current_url)
            continue
            
        # 6. Parse Page Content
        new_items = parse_book_page(html_content, current_url)
        
        # 7. Save Data
        if not args.dry_run:
            save_items_to_jsonl(new_items, saved_item_keys)
        else:
            print(f"Dry Run: Skipping file save for {len(new_items)} items.")

        # 8. Handle Pagination (Find the next page)
        next_page_url = get_next_page_url(html_content, current_url)
        if next_page_url:
            # Add the next page URL to the queue if not already processed
            if next_page_url not in crawled_urls and next_page_url not in url_queue:
                url_queue.append(next_page_url)
                print(f"Pagination found: Next page resolved to {next_page_url}")
            
        # 9. Update status and counter
        crawled_urls.add(current_url)
        pages_crawled += 1

    print(f"\n--- SCRAPER FINISHED ---")
    print(f"Total Pages Crawled: {pages_crawled}")
    print(f"Total Unique Items Saved: {len(saved_item_keys)}")
    if pages_crawled >= args.max_pages:
        print(f"Reason: Graceful stop - Max pages limit reached (max: {args.max_pages}).")
    elif not url_queue:
        print("Reason: Pagination exhausted - All category pages and their subsequent pages have been crawled.")


def main():
    """Main function to run the scraper."""
    print("Starting the web scraper with the following parameters:")
    
    # ScraperArgs NamedTuple ensures robust argument handling
    args = parse_arguments() 

    # Print parsed arguments
    print(f"Start URL: {args.start}")
    print(f"Max Pages: {args.max_pages}")
    print(f"Delay Time: {args.delay_ms} milliseconds")
    if args.dry_run:
        print("Mode: Dry Run (Data will NOT be saved to file).")
    else:
        print("Mode: Live Run (Data WILL be saved to data/items.jsonl).")
    print("-" * 30)

    try:
        run_scraper(args)
    except Exception as e:
        print(f"A fatal error occurred during the scrape: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    # This is the essential entry point for execution.
    main()