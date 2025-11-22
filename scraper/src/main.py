import argparse
import sys
import json
import os
from typing import Set, List
from collections import deque
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


# Import modules
from .fetcher import fetch_page, USER_AGENT
from .parser import parse_book_page, extract_category_from_page
from .pagination import get_next_page_url
from .robots import RobotsChecker
from .data_structures import BookItem, ScraperArgs

# Output paths
OUTPUT_PRIMARY = Path(__file__).resolve().parent.parent / "data" / "items.jsonl"
OUTPUT_UI = Path(__file__).resolve().parent.parent.parent / "ui" / "public" / "data" / "items.jsonl"


# Save items to BOTH scraper/data and ui/public/data
def save_items_to_jsonl(items: List[BookItem], saved_item_keys: Set[str]):
    newly_saved_count = 0

    os.makedirs(os.path.dirname(OUTPUT_PRIMARY), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_UI), exist_ok=True)

    primary_exists = os.path.exists(OUTPUT_PRIMARY)

    with open(OUTPUT_PRIMARY, 'a', encoding='utf-8') as f1, \
         open(OUTPUT_UI, 'a', encoding='utf-8') as f2:

        for item in items:
            key = item.url
            if key not in saved_item_keys:
                line = json.dumps(item.to_jsonl(), ensure_ascii=False) + "\n"
                f1.write(line)
                f2.write(line)
                saved_item_keys.add(key)
                newly_saved_count += 1

    if newly_saved_count > 0:
        if primary_exists:
            print(f"-> Saved {newly_saved_count} NEW unique items to {OUTPUT_PRIMARY} (and UI mirror)")
        else:
            print(f"-> Created and saved {newly_saved_count} unique items to {OUTPUT_PRIMARY} (and UI mirror)")


# Extract category URLs
def extract_all_category_urls(html: str, base_url: str):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.select('ul.nav-list ul li a')
    urls = []
    for a in links:
        rel = a.get('href')
        if rel:
            urls.append(urljoin(base_url, rel))
    return urls


# Main scraper 
def run_scraper(args: ScraperArgs):

    crawled_urls: Set[str] = set()
    url_queue: deque[str] = deque()

    # Homepage → load category URLs
    if args.start.rstrip('/') in ["http://books.toscrape.com", "https://books.toscrape.com"]:
        print("Start URL is homepage. Loading categories...")

        homepage_html = fetch_page(args.start, args.delay_ms)
        if homepage_html:
            categories = extract_all_category_urls(homepage_html, args.start)
            print(f"Discovered {len(categories)} categories.")
            for c in categories:
                url_queue.append(c)

        crawled_urls.update([
            "http://books.toscrape.com", "http://books.toscrape.com/",
            "https://books.toscrape.com", "https://books.toscrape.com/"
        ])
    else:
        url_queue.append(args.start)

    # Dedup items
    saved_item_keys: Set[str] = set()
    if os.path.exists(OUTPUT_PRIMARY):
        try:
            with open(OUTPUT_PRIMARY, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        item = json.loads(line)
                        if "url" in item:
                            saved_item_keys.add(item["url"])
            print(f"Loaded {len(saved_item_keys)} existing items.")
        except Exception as e:
            print(f"WARNING: Could not load existing items: {e}")

    robots_checker = RobotsChecker(USER_AGENT)
    pages_crawled = 0

    concurrency = max(1, args.concurrency)
    print(f"Using concurrency = {concurrency}")

    # ThreadPool concurrency
    with ThreadPoolExecutor(max_workers=concurrency) as executor:

        while url_queue and pages_crawled < args.max_pages:

            batch = []
            while url_queue and len(batch) < concurrency:
                url = url_queue.popleft()

                if url in crawled_urls:
                    continue
                if not robots_checker.is_url_allowed(url):
                    continue

                future = executor.submit(fetch_page, url, args.delay_ms)
                batch.append((url, future))

            if not batch:
                break

            # Process completed fetch results
            for url, future in batch:

                html_content = future.result()
                crawled_urls.add(url)

                print(f"Crawling: {url}")

                if html_content is None:
                    print(f"Fetch failed for {url}, skipping.")
                    continue

                soup = BeautifulSoup(html_content, 'html.parser')
                category = extract_category_from_page(soup)
                print(f"-> Category: {category}")

                items = parse_book_page(html_content, url, category)
                if not args.dry_run and items:
                    save_items_to_jsonl(items, saved_item_keys)

                next_page = get_next_page_url(html_content, url)
                if next_page and next_page not in crawled_urls:
                    url_queue.append(next_page)

                pages_crawled += 1
                if pages_crawled >= args.max_pages:
                    break

    # End-of-run summary
    print("\n--- SCRAPER FINISHED ---")
    print(f"Pages Crawled: {pages_crawled}")
    print(f"Unique Items Saved: {len(saved_item_keys)}")


# CLI argument parsing
def parse_arguments() -> ScraperArgs:
    parser = argparse.ArgumentParser(
        description="Concurrent book scraper for books.toscrape.com.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('-s', '--start', type=str, default='http://books.toscrape.com/')
    parser.add_argument('-m', '--max-pages', type=int, default=5)
    parser.add_argument('-d', '--delay-ms', type=int, default=1000)
    parser.add_argument('--dry-run', action='store_true')

    parser.add_argument(
        '-c', '--concurrency',
        type=int,
        default=1,
        help="Number of concurrent workers."
    )

    try:
        args = parser.parse_args()

        return ScraperArgs(
            start=args.start,
            max_pages=args.max_pages,
            delay_ms=args.delay_ms,
            dry_run=args.dry_run,
            concurrency=args.concurrency,
        )

    except SystemExit:
        sys.exit(0)


# Main
def main():
    args = parse_arguments()

    print("Starting scraper with:")
    print(f"  Start: {args.start}")
    print(f"  Pages: {args.max_pages}")
    print(f"  Delay: {args.delay_ms} ms")
    print(f"  Concurrency: {args.concurrency}")
    print(f"  Dry Run: {args.dry_run}")

    run_scraper(args)


if __name__ == "__main__":
    main()
