# Web Scraper — Blueberry AI SWE Intern Assessment

This folder contains the Python-based web scraper used to collect structured book data from **books.toscrape.com**.  
The scraper is engineered for reliability, extensibility, and real-world production scraping constraints.

It features concurrency, resume crawl, schema versioning, robots.txt awareness, and automatic data mirroring for use by downstream systems.


##  Features

### **1. Category-Aware Book Scraping**
- Extracts full book listings across all 50 categories.
- Resolves pagination reliably.
- Uses breadcrumb navigation to determine book category.

### **2. Concurrency Support**
Fetch multiple pages in parallel:

--concurrency N

Implemented using `ThreadPoolExecutor`, with polite delays and robots.txt compliance.

### **3. Resume Crawl & De-duplication**
- Automatically loads previous results from `data/items.jsonl`
- Avoids duplicate entries using URL-based keys
- Enables safe incremental scraping (stop + restart)

### **4. Dual Output Storage**
Every successful item is written to two locations:

scraper/data/items.jsonl (primary storage)
../ui/public/data/items.jsonl (UI mirror)

No manual copying required.

### **5. Schema Versioning (v1)**
All output rows include a version field:

"schema_version": 1

This enables safe schema evolution in future versions.

### **6. robots.txt Compliance**
Scraper checks:

- Disallowed paths  
- Allowed paths  
- Fetcher throttle settings  

using a custom `RobotsChecker`.


##  File Structure

```
scraper/
│
├── src/
│ ├── main.py # Main scraper entrypoint
│ ├── fetcher.py # HTTP fetching with retries & delay
│ ├── parser.py # HTML parsing and item extraction
│ ├── pagination.py # Next-page URL resolution
│ ├── robots.py # robots.txt handling
│ └── data_structures.py # BookItem + ScraperArgs
│
└── data/
  └── items.jsonl # Scraped output (auto-generated)
```

##  Installation
pip install -r requirements.txt

##  Running the Scraper

### Default Argument Values

The scraper provides several CLI arguments. Their default values are:
```
--start       (default: http://books.toscrape.com/)
--max-pages   (default: 5)
--delay-ms    (default: 1000)
--dry-run     (default: False)
```

### **Basic run**

python -m src.main

### **Limit number of pages**

python -m src.main --max-pages 20

### **Concurrent workers**

python -m src.main --concurrency 3

### **Start from a specific category**

python -m src.main --start https://books.toscrape.com/catalogue/category/books/mystery_3/index.html

### **Dry run**

python -m src.main --dry-run

### **Example**

python -m src.main --start https://books.toscrape.com/ --max-pages 10 --concurrency 3



##  Schema Versioning & Migration Notes

Each item includes:

"schema_version": 1


### Why?

- Allows future schema upgrades  
- Keeps UI & other consumers backwards-compatible  
- Prevents breaking changes when adding/renaming fields  

### Migration Strategy

When schema changes:

1. Increment `SCHEMA_VERSION` in `data_structures.py`  
2. Document differences between versions  
3. Optionally write a migration script converting old records  



##  Example Output (JSONL)

{"title": "The Past Never Ends",
"price": 56.5,
"availability": "In stock",
"rating": 4,
"category": "Mystery",
"url": "https://books.toscrape.com/catalogue/the-past-never-ends_942/index.html
",
"schema_version": 1}



##  Design Principles

- Stateless scraping, safe to restart anytime  
- Clear separation of concerns (fetch / parse / pagination / robots / save)  
- Efficient concurrency without overwhelming the server  
- Portable codebase that can be adapted to other sites  


