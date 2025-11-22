# Book Scraper + React Dashboard  
_A Data Collection & Visualization Project (Blueberry AI SWE Intern Assessment)_

This repository contains a complete end-to-end system for scraping structured book data from **books.toscrape.com** and visualizing it using a **React-based dashboard**.

It demonstrates real-world software engineering, including:

- Reliable web scraping with concurrency  
- Data schema versioning  
- Incremental resume crawl with deduplication  
- robots.txt compliance  
- UI data mirroring  
- Interactive dashboard for browsing / searching / visualizing books  


#  Project Overview

The system consists of two major parts:

### **1. Python Scraper (`/scraper`)**
- Fetches and parses book data  
- Extracts categories, solves pagination  
- Supports concurrency  
- Writes results to JSONL  
- Automatically syncs results to UI folder  

### **2. React Dashboard (`/ui`)**
- Loads the scraper's output  
- Provides filtering, sorting, and charts  
- Displays 300+ scraped books interactively  
- Runs fully client-side  

Together, they form a mini-pipeline:

```
Scraper (Python) → JSONL dataset → UI (React)
```


#  Demo

Demo video available on Google Drive: https://drive.google.com/file/d/1DgDoEmEWN7az825BpgC4ngSWGniD3zsf/view?usp=sharing


#  Repository Structure

```
project-root/
│
├── scraper/                     # Python web scraper
│   ├── src/                     # Scraper source code
│   ├── data/items.jsonl         # Primary scraped data
│   └── README.md                # Scraper-specific documentation
│
├── ui/                          # React dashboard
│   ├── public/data/items.jsonl  # UI mirror of scraper output
│   ├── src/                     # React code
│   └── README.md                # UI documentation
│
└── README.md                    # (this file)
```


#  Technologies Used

### **Backend / Scraper**
- Python 3  
- requests / BeautifulSoup  
- ThreadPoolExecutor (concurrency)  
- JSONL structured output  
- robots.txt parsing  

### **Frontend / UI**
- React + TypeScript  
- Vite  
- Custom JSONL loader  
- Data visualization with custom chart component  

#  Installation & Setup

## 1. Clone the repository

```
git clone https://github.com/Casthecat/bookscraper
cd bookscraper
```


#  Scraper (Python)

### Install dependencies

```
pip install -r scraper/requirements.txt
```

### Run scraper

```
python -m scraper.src.main
```

### Options

```
--max-pages N        Limit scraping
--concurrency N      Enable parallel fetching
--dry-run            Test run without writing
--start URL          Start at category or page
```

Example:

```
python -m scraper.src.main --max-pages 50 --concurrency 3
```

Scraped data is saved to:

```
scraper/data/items.jsonl
ui/public/data/items.jsonl
```

#  UI Dashboard (React)

### Install

```
cd ui
npm install
```

### Run dev server

```
npm run dev
```

Dashboard opens at:

```
http://localhost:5173
```

### Build production version

```
npm run build
```

#  Dashboard Features

- Search by title / category  
- Filter by category  
- Filter by minimum rating  
- Sort table columns  
- Visual chart: book counts by rating  
- 300+ scraped books displayed  

Example components:

- `Filters.tsx`
- `Table.tsx`
- `Chart.tsx`
- `loadData.ts` (JSONL loader)


#  Schema Versioning (v1)

Each scraped item includes:

```
"schema_version": 1
```

### Purpose
- Allows future schema upgrades  
- Prevents UI or pipeline breakage  
- Makes backward compatibility explicit  

### Migration Strategy
Documented in:

```
scraper/README.md
```


#  Key Engineering Features

###  Concurrency support  
Multi-threaded page fetching with polite delay compliance.

###  Deduplicated resume crawl  
Restarts safely without rewriting existing items.

###  Data mirroring  
Scraper writes to **two** JSONL files automatically:
- local scraper data  
- UI's `public/data` folder  

###  Robust HTML parsing  
Category extraction from breadcrumbs guarantees correct classification.

###  Clean code structure  
Separate modules for fetching, parsing, robots, pagination, storage.

###  Real-world production practices  
- schema versioning  
- modular architecture  
- concurrency  
- robust error handling  


#   Screenshot of the dashboard

![alt text](image.png)


#   Design Decisions

The scraper is organized around small, single-purpose modules so that each part of the pipeline remains easy to understand, maintain, and test independently.
fetcher.py handles networking, retry logic, and polite delays;
parser.py focuses strictly on translating HTML into structured Python objects;
pagination.py isolates the logic of detecting the next page; and
robots.py is responsible for validating crawler permissions.

This modular layout keeps responsibilities narrow and makes failures easier to diagnose—network issues are separated from parsing issues, and parsing issues are separated from navigation issues.

I chose synchronous requests paired with a configurable worker-pool instead of a fully asynchronous design. While an asyncio-based scraper could maximize throughput, the worker-pool model strikes a practical balance between performance, debuggability, and clarity. The concurrency level is configurable from the command line, allowing the scraper to adapt across different environments without introducing unnecessary complexity.

The frontend follows the same philosophy: predictable rendering, minimal global state, and explicit boundaries. Since the UI operates entirely on a static JSON dataset, no server coordination or data fetching complexity is required. All types are defined in types.ts, ensuring a clear and self-documenting contract between the Python scraper and the React UI.


#   More nice-to-haves

With additional time, I would extend the scraper beyond the current “snapshot” model and support incremental crawling. This would include storing checksums or last-modified timestamps to detect which items have changed between runs, avoiding unnecessary re-fetching.
Domain-aware throttling could also be added—reading crawl-delay or applying heuristics based on response times to dynamically adjust pacing.

A more robust storage layer (e.g., SQLite or DuckDB) would allow the scraper to scale to tens of thousands of records while keeping queries fast and efficient. For robustness, I would also consider adding rotating user agents, proxy pools, and automated retry scheduling.

On the frontend, I would expand interactions to include richer filtering (e.g., availability, price range), a debounced full-text search, and more flexible sorting. Pagination or virtualized tables would improve performance with large datasets. I would also introduce unit tests for UI components and possibly auto-generate TypeScript types directly from the Python schema to ensure perfect type alignment.
With more time, the static JSON file could be replaced by a small backend API that supports server-side queries, enabling the UI to scale smoothly with larger datasets.


#   Known Limitations

The scraper performs reliably for the Books to Scrape domain, but several assumptions limit its generality. The parser depends on stable HTML structures—such as the presence of classes like product_pod, price_color, and star-rating. If the site changes its templates or introduces dynamically rendered components, the parser would require updates.
The category extraction logic also assumes a simple breadcrumb layout and is not yet robust against deeper or unconventional category structures.

The networking layer intentionally avoids advanced anti-bot measures. While retries and delays provide basic politeness, the scraper does not currently support proxy rotation, user-agent cycling, rate-limit detection, or CAPTCHA handling. These would be required for large-scale or production-grade scraping.

On the frontend, the entire dataset is loaded into memory. This is sufficient for a few hundred items but will not scale efficiently to tens of thousands. All search, filtering, and pagination operations are client-side and would eventually need server support for optimal performance.
Finally, the overall pipeline is built for manual batch runs rather than scheduled or continuous crawling, and therefore lacks incremental update logic and historical tracking.


#  Credits

Created by **Zhuoning (Lynde) Li**  
As part of the **Blueberry AI SWE Intern Assessment**  
Featuring both backend + frontend engineering.

#  Summary

This project demonstrates:

- A reliable, production-style scraper  
- A modern React visualization frontend  
- Engineering principles like concurrency, schema migration, and modular design  
- Full end-to-end data pipeline from collection → processing → visualization  

