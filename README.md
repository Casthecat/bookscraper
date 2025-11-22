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

