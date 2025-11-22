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

I structured the scraper around small, single-purpose modules so each part of the pipeline remains easy to understand and independently testable. fetcher.py is responsible only for networking, retry logic, and polite delays; parser.py focuses purely on translating HTML into structured data; pagination.py isolates the logic of discovering the “next page”; and robots.py handles crawler permissions. This modularization keeps the codebase maintainable and makes failures easier to diagnose since each component has a narrow responsibility.

I chose to use synchronous requests with a configurable worker pool rather than switching entirely to asyncio. While asyncio would provide maximal throughput, a worker-pool model strikes a practical balance between performance and readability. The goal was to build a scraper that is reliable and transparent rather than overly clever, and the concurrency level is adjustable from the command line so different environments can tune performance according to their constraints.

The UI mirrors the same philosophy: minimal state, predictable rendering, and clear boundaries. Instead of introducing global state managers or server-driven queries, the UI simply treats the scraped JSON as a static dataset. This keeps the frontend lightweight and reduces implicit complexity. Types are defined explicitly in types.ts to provide a self-documenting contract between the scraper and the UI.


#   More nice-to-haves

Given more time, I would expand the scraper beyond the “snapshot” model and add incremental crawling. That would include checksums or last-modified timestamps to detect which books have changed between runs, preventing unnecessary re-downloads. I would also introduce domain-aware throttling—reading crawl-delay or custom site heuristics to adaptively adjust request pacing. Another improvement would be moving the storage layer to SQLite or another embedded database so the tool can scale to tens of thousands of items while keeping query speeds fast.

For the frontend, I would add richer interactions—filtering by availability, and a debounced full-text search across titles. Pagination or virtual scrolling would also improve rendering performance for large datasets. Additionally, I would implement unit tests for UI components and possibly auto-generate TypeScript types directly from the scraper schema to ensure type parity across both layers. With more time, a small backend API could replace the static JSON and provide live querying, allowing the UI to handle far larger datasets smoothly.


#   Known Limitations

This scraper works reliably for the Books to Scrape domain, but it does make a few assumptions that would need refinement for broader use. The HTML parser expects the site to follow a fairly stable structure—for example, it looks for specific CSS classes like product_pod, price_color, and star-rating. If the site changes its layout or introduces dynamic content, the parser would require adjustments. Similarly, the breadcrumb-based category extraction works well for this dataset, but it is not yet robust against unusual or deeply nested category structures.

The networking layer is intentionally simple. While retries and delays help avoid disruptive patterns, the scraper does not yet account for more complex anti-bot mechanisms such as rotating user agents, proxy pools, IP rate limits, or CAPTCHAs. For large-scale or production scraping, those would need to be added. Error handling is conservative—when an item cannot be parsed, the scraper skips it rather than attempting a partial extraction. This keeps the output clean, but it may fail silently on pages that deviate from the expected structure.

On the frontend side, the UI loads the entire dataset into memory. This is perfectly fine for a few hundred entries, but it would not scale gracefully to tens of thousands of records. Features like search, filtering, and pagination are done client-side and would need optimization or a backend API if the dataset grows significantly. Finally, the pipeline is designed for batch runs rather than continuous or scheduled crawling, so incremental updates or historical tracking are not yet supported.


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

