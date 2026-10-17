# Video Game Database Explorer
### An Interactive Game Data Scraping, Searching, Sorting, and Benchmarking Desktop Application
**Course**: CS200 Data Structures & Algorithms — Project 1  
**Technology Stack**: Python 3.14+, PyQt5, SQLite3, Requests, BeautifulSoup4, Pandas, Matplotlib

---

## 🎮 Overview

**Video Game Database Explorer** is a high-performance desktop application engineered for university CS200 Data Structures and Algorithms. The application collects, explores, filters, multi-level sorts, and benchmarks **over 15,000 distinct video game records** gathered from legitimate gaming APIs and stores.

All eight sorting algorithms and composite filtering engines are implemented from scratch in pure Python without relying on built-in `sorted()`, `list.sort()`, Pandas `sort_values()`, or SQL `ORDER BY`.

---

## 🌟 Key Features

1. **Eight Custom-Implemented Sorting Algorithms**:
   - **Insertion Sort**: Shift-based insertion with $O(n)$ best-case and $O(n^2)$ worst-case; stable.
   - **Selection Sort**: Unstable minimum-selection sort with guaranteed $O(1)$ auxiliary space.
   - **Merge Sort**: Stable divide-and-conquer $O(n \log n)$ sort with auxiliary memory movements tracking.
   - **Bubble Sort**: Adjacent-swap sort with an early-exit optimization achieving $O(n)$ best-case.
   - **Quick Sort**: Partition-based algorithm utilizing median-of-three pivot selection and an iterative call stack to prevent recursion depth exceptions on 15,000+ items.
   - **Counting Sort**: Non-comparison $O(n + k)$ integer sorting with negative range offset technique and stable cumulative accumulation.
   - **Bucket Sort**: Normalized range distribution into buckets sorted individually via Insertion Sort.
   - **Radix Sort (LSD)**: Least Significant Digit base-10 digit-by-digit sorting with offset handling for negative values.

2. **Benchmark Engine & Charts**:
   - "Benchmark All 8 Algorithms" button runs all algorithms on equivalent deep copies of the exact same input.
   - Verifies sorted correctness.
   - Collects execution time in milliseconds, comparison count, swap count, and movement count.
   - Interactive Matplotlib charts comparing runtimes and operations.
   - CSV export of benchmark comparison reports.

3. **Multi-Level Sorting & Tie Resolution**:
   - Dynamic priority levels (e.g., Level 1: `rating` DESC $\rightarrow$ Level 2: `release_date` DESC $\rightarrow$ Level 3: `title` ASC).
   - Utilizes the Radix Multi-Pass Principle for stable algorithms to resolve ties consistently.

4. **Composite Search & Filter Engine**:
   - Text filters (`contains`, `not_contains`, `starts_with`, `ends_with`, `equals`, `not_equals`).
   - Numeric filters (`>`, `<`, `>=`, `<=`, `==`, `!=`, `between [v1, v2]`).
   - Date range filters (`before`, `after`, `between`, `exact`).
   - Boolean condition filters (`multiplayer`).
   - Logical `AND` / `OR` joins and condition-level `NOT` inversion.
   - Pre-configured filter presets for rapid inspection.

5. **Multi-Source Scraping Subsystem**:
   - Collects 15,000+ verified records across SteamSpy, FreeToGame, and CheapShark.
   - Background `QThread` execution with **Start, Pause, Resume, and Stop** controls.
   - Live progress bar, percentage, elapsed time, current page, and error count.
   - Incremental saving to SQLite so stopping never discards progress.
   - Automatic duplicate detection and filtering based on external IDs and title normalization.

6. **Bonus Feature: Single-Game URL Scraper**:
   - Dedicated URL input field to scrape game pages (e.g. Steam Store, FreeToGame, or OpenGraph).
   - SSRF (Server-Side Request Forgery) protection: resolves hostnames and blocks private, loopback, or link-local IP addresses (e.g. `127.0.0.1`, `10.x`, `192.168.x`).
   - Response size caps (5MB) and timeouts.
   - One-click persistence to SQLite database.

---

## 📂 Project Directory Structure

```
Project_1/
├── algorithms/
│   ├── __init__.py
│   ├── sorting.py              # 8 custom sorting algorithms + metrics tracker
│   └── searching.py            # Search filters, operators, composite query engine
├── database/
│   ├── __init__.py
│   ├── schema.py               # Table schema, indexes, connection factory
│   └── repository.py           # CRUD operations, batch inserts, stats, deduplication
├── models/
│   ├── __init__.py
│   ├── game.py                 # Game entity dataclass and normalizers
│   └── filter_sort.py          # FilterCondition, FilterGroup, SortLevel, SortResult
├── scraper/
│   ├── __init__.py
│   ├── base.py                 # Abstract base scraper with polite rate limiting
│   ├── steamspy_scraper.py     # SteamSpy paginated API scraper (1,000 games/page)
│   ├── freetogame_scraper.py   # FreeToGame catalog scraper
│   ├── cheapshark_scraper.py   # CheapShark deals and ratings scraper
│   ├── url_scraper.py          # Bonus URL scraper (SSRF protection, BeautifulSoup)
│   └── worker.py               # QThread background scraper with Start/Pause/Resume/Stop
├── services/
│   ├── __init__.py
│   ├── data_service.py         # In-memory dataset caching and repository coordinator
│   ├── sort_service.py         # Single and multi-level sorting orchestration
│   ├── benchmark_service.py    # Benchmark runner across all 8 algorithms
│   └── export_service.py       # CSV exporter for data and benchmark reports
├── ui/
│   ├── __init__.py
│   ├── main_window.py          # PyQt5 main application window with tabs and status bar
│   ├── dashboard_tab.py        # Analytics dashboard, statistics cards, genre chart
│   ├── library_tab.py          # Game table, pagination, detail drawer, quick search
│   ├── scraper_tab.py          # Scraper controls, live progress, stats, bonus URL scraper
│   ├── filter_tab.py           # Composite visual filter builder (AND, OR, NOT, presets)
│   ├── sorting_tab.py          # Single/Multi-level sort, algorithm details, complexity card
│   ├── benchmark_tab.py        # Benchmark runner, results table, matplotlib comparison charts
│   ├── about_tab.py            # University Viva guide, DSA algorithm reference
│   └── styles.py               # Modern dark theme stylesheet
├── tests/
│   ├── __init__.py
│   ├── test_sorting.py         # Unit tests for all 8 sorting algorithms
│   ├── test_searching.py       # Unit tests for search operators and composite filtering
│   ├── test_multilevel.py      # Unit tests for multi-level sorting and tie resolution
│   └── test_scraper.py         # Unit tests for URL validation, SSRF, and deduplication
├── data/
│   └── games.db                # Persistent SQLite database with 15,128+ records
├── main.py                     # Application launcher
├── seed_database.py            # Database seeder script
├── requirements.txt            # Python dependencies
├── VIVA_GUIDE.md               # University viva demonstration guide
└── README.md                   # This documentation
```

---

## 🚀 Installation & Setup

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Pip package manager

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `PyQt5`: Desktop graphical interface
- `requests`: HTTP client for web scraping
- `beautifulsoup4`: HTML parsing for web pages
- `pandas`: Tabular export helpers
- `matplotlib`: Performance comparison charts

### 3. Database Population (Seed)
The project comes with a seeder script that collects 15,000+ distinct video game records:
```bash
python seed_database.py 15000
```
*Note: If `data/games.db` already exists with $\ge 15,000$ records, seeding is skipped automatically.*

### 4. Running the Application
```bash
python main.py
```

### 5. Running Automated Tests
To run all 18 unit tests covering all 8 sorting algorithms, composite filters, multi-level sorting, and SSRF security:
```bash
python -m unittest discover tests
```

---

## 📊 Summary of Implemented Algorithms

| Algorithm | Best Time | Average Time | Worst Time | Aux Space | Stability | Compatible Column Types |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Insertion Sort** | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Stable | All columns (text, dates, numbers) |
| **Selection Sort** | $O(n^2)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Unstable | All columns (text, dates, numbers) |
| **Merge Sort** | $O(n \log n)$ | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | Stable | All columns (text, dates, numbers) |
| **Bubble Sort** | $O(n)$ | $O(n^2)$ | $O(n^2)$ | $O(1)$ | Stable | All columns (text, dates, numbers) |
| **Quick Sort** | $O(n \log n)$ | $O(n \log n)$ | $O(n^2)$ | $O(\log n)$ | Unstable | All columns (text, dates, numbers) |
| **Counting Sort** | $O(n + k)$ | $O(n + k)$ | $O(n + k)$ | $O(n + k)$ | Stable | Bounded integer / numeric keys |
| **Bucket Sort** | $O(n + k)$ | $O(n + k)$ | $O(n^2)$ | $O(n + k)$ | Stable | Numeric columns (rating, price, etc.) |
| **Radix Sort (LSD)** | $O(d(n + b))$ | $O(d(n + b))$ | $O(d(n + b))$ | $O(n + b)$ | Stable | Integer / scaled numeric keys |

---

## 🔒 Security & Polite Scraping Practices

- **SSRF Protection**: Resolves domain names to IP addresses and rejects `127.0.0.1`, `localhost`, `10.x.x.x`, `192.168.x.x`, `169.254.x.x`, and IPv6 `::1` before any socket connection is opened.
- **Safety Caps**: Limits downloads to 5 MB per request to prevent memory exhaustion and zip-bomb style attacks.
- **Polite Rate Limiting**: Enforces minimum sleep delays between requests and uses descriptive User-Agent headers.
- **Legitimate Sources**: Gathers data exclusively from permitted public APIs (SteamSpy, FreeToGame, CheapShark) and public store pages without bypassing authentication or CAPTCHAs.

