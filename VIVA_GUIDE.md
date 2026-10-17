# CS200 University DSA Viva & Demonstration Guide

This guide is designed to help you ace your university examination/viva presentation for **Project 1: Video Game Database Explorer**. It covers live demonstration workflows, core algorithm theoretical questions, and defense of implementation decisions.

---

## 🎙️ 1. Five-Minute Live Demonstration Workflow

### Step 1: Launch and Overview (30 seconds)
1. Launch the application:
   ```bash
   python main.py
   ```
2. Point out the top header badge: **"Database: 15,128 games"**.
3. Show the **Dashboard**: Highlight summary statistics (Average Rating, Average Price, Top Metacritic score), the data source breakdown (SteamSpy, FreeToGame, CheapShark), and top genres.

### Step 2: Game Library & Detail Inspector (45 seconds)
1. Switch to **Tab 2: Game Library**.
2. Demonstrate pagination: Notice how smoothly 15,128 records load and page through (50 records per page).
3. Use the quick search bar: Type `"Witcher"` or `"Valve"`. Show instantaneous filtering.
4. Click on any game row: Show the right-hand **Detail Inspector** displaying full game metadata, external IDs, price, and clickable source URL.

### Step 3: Bonus URL-Based Scraper Demonstration (60 seconds)
1. Switch to **Tab 3: Live Scraper**.
2. Show the live scraper controls (**Start, Pause, Resume, Stop**, Target SpinBox, and real-time activity log).
3. Demonstrate the **Bonus Feature: URL Scraper**:
   - Paste a legitimate Steam Store URL: `https://store.steampowered.com/app/570/Dota_2/`
   - Click **"🌐 Scrape URL"**.
   - Show how it securely validates against SSRF, parses the title, developer, rating, price, and description, and displays a success notification.
   - Click **"💾 Save to Database"** to demonstrate immediate persistence into SQLite.
   - *Bonus Defense*: Demonstrate entering an unsafe URL like `http://127.0.0.1:8080` and show how the application security layer intercepts and rejects it with a clear SSRF protection alert!

### Step 4: Composite Boolean Filter Builder (60 seconds)
1. Switch to **Tab 4: Search & Filters**.
2. Select a preset: e.g. **"Budget Games (Price <= $10)"**.
3. Add a condition row:
   - Set **Column**: `genres` | **Operator**: `contains` | **Value**: `Action`
   - Toggle **NOT** on one condition to show inversion.
4. Change logical join mode: Demonstrate **ALL (AND)** vs **ANY (OR)**.
5. Click **"🔍 Apply Composite Filters"**: Point out the updated matching count (e.g. `Matched 2,410 of 15,128 records`).
6. Click **"⚡ Sort Filtered Results"** to transition seamlessly into sorting the filtered subset!

### Step 5: Sorting & Multi-Level Sorting (60 seconds)
1. Switch to **Tab 5: Sorting & Multi-Level**.
2. Select **Scope**: "Currently Filtered Results" or "Full Database".
3. **Single Sort**:
   - Select Column: `rating`
   - Select Algorithm: `Merge Sort`
   - Click **"⚡ Execute Selected Algorithm"**.
   - Review the **Algorithm Performance & Complexity Card**: Note exact milliseconds, comparison count, element movements, stability (`Stable`), and time/space complexity.
4. **Multi-Level Sort**:
   - Level 1: `rating` (Descending)
   - Level 2: `price` (Ascending)
   - Level 3: `title` (Ascending)
   - Choose Primary Algorithm: `Merge Sort`
   - Click **"⚡ Execute Multi-Level Sort"**.
   - Explain how ties are resolved: Games with the same rating are strictly ordered by price, and ties on price are ordered by title!

### Step 6: Benchmarking All 8 Algorithms & Charts (45 seconds)
1. Switch to **Tab 6: Benchmarks & Charts**.
2. Scope: Select "Fast Viva Demo (1,000 records)" or "Full Database".
3. Click **"⚡ Benchmark All 8 Algorithms"**.
4. Show that the UI does NOT freeze (it runs on a background `QThread` with live progress).
5. Examine the resulting comparison table:
   - Review runtime (ms), comparisons, swaps, movements, stability, and status.
   - Show the interactive **Matplotlib Bar Charts** rendering execution time and comparison counts.
6. Click **"⬇ Export CSV Report"** to export the benchmark results to a spreadsheet.

---

## 🧠 2. Expected Viva Questions & Expert Answers

### Q1: Why did you implement your own algorithms instead of using Python's `sort()`?
**Answer:**
> "Python's `list.sort()` and `sorted()` use **Timsort** (a hybrid of Merge Sort and Insertion Sort implemented in C). In this university project, our primary learning objective is to understand, implement, and measure the fundamental mechanics of individual data structures and algorithms—including exact comparison counts, swaps, shifts, and memory complexity. Relying on built-in C functions would conceal these operations and prevent fair empirical analysis."

### Q2: How does your Multi-Level Sort resolve ties?
**Answer:**
> "For our stable algorithms (Merge Sort, Insertion Sort, Bubble Sort, Counting Sort, Radix Sort), we implemented the **Radix Multi-Pass Principle**: we sort backwards from the lowest-priority key (e.g., Level 3: Title) up to the primary key (Level 1: Rating). Because each algorithm is provably **stable**, equal keys in the primary pass retain the exact relative order established by the secondary pass! For unstable algorithms (such as Quick Sort), we use a multi-key composite comparator inside our iterative partitioning function."

### Q3: Why do Counting Sort and Radix Sort achieve $O(n)$ time when Merge Sort is $O(n \log n)$?
**Answer:**
> "The theoretical lower bound of $\Omega(n \log n)$ applies strictly to **comparison-based** sorting algorithms, where the output permutation is deduced by pairwise comparisons (modeled as a decision tree with $n!$ leaves and height $\ge \log_2(n!) = \Omega(n \log n)$).  
> **Counting Sort and Radix Sort are non-comparison sorts**. They do not compare two elements against each other; instead, they inspect the algebraic and positional digit values of the integer keys directly, calculating array indices in $O(n + k)$ or $O(d(n + b))$ time."

### Q4: How did you prevent Quick Sort from hitting Python's `RecursionError` on 15,000 items?
**Answer:**
> "Standard recursive Quicksort has a worst-case recursion depth of $O(n)$, which triggers Python's default recursion limit (1,000 frames) on large or nearly sorted datasets.  
> We resolved this by:
> 1. Implementing an **iterative stack-based Quicksort** using an explicit stack rather than the Python call stack.
> 2. Using **median-of-three pivot selection** (taking the median of the low, middle, and high elements), which drastically reduces the probability of encountering the $O(n^2)$ unbalanced partition on already sorted or reverse-sorted data.
> 3. Always pushing the larger partition onto the stack and processing the smaller partition first, bounding auxiliary space to $O(\log n)$."

### Q5: How did you handle missing (`None`) values in your sorting and filtering algorithms?
**Answer:**
> "In Python, attempting to compare `None < 5` raises an unhandled `TypeError`. In our custom comparator `compare_keys()`, we normalize missing values:
> By university convention, `None` values are defined as greater than any regular value during ascending sorts (placing them safely at the end of the list), and conversely during descending sorts. For non-comparison algorithms like Counting and Radix Sort, records with `None` keys are partitioned into an auxiliary list and concatenated at the end, preserving stability and data integrity."

### Q6: What security measures did you implement for the bonus URL scraper?
**Answer:**
> "We implemented strict **SSRF (Server-Side Request Forgery) protection**:
> 1. We inspect the URL scheme and permit only `http` and `https`.
> 2. We resolve the hostname using `socket.getaddrinfo()` and parse the IP address with Python's `ipaddress` module.
> 3. We verify that the destination IP is not private (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`, `::1`), link-local (`169.254.0.0/16`), or reserved.
> 4. We enforce streaming response limits (max 5 MB) and network timeouts to prevent denial-of-service."

---

## 📋 3. Requirement-to-Module Traceability Matrix

| Requirement | Description | Implementation Module | UI Control | Test Suite |
| :--- | :--- | :--- | :--- | :--- |
| **Req 1** | Insertion Sort | `algorithms/sorting.py` | Sorting Tab & Benchmark Tab | `test_sorting.py::test_numeric_sorting_correctness` |
| **Req 1** | Selection Sort | `algorithms/sorting.py` | Sorting Tab & Benchmark Tab | `test_sorting.py::test_numeric_sorting_correctness` |
| **Req 1** | Merge Sort | `algorithms/sorting.py` | Sorting Tab & Benchmark Tab | `test_sorting.py::test_stability_preservation` |
| **Req 1** | Bubble Sort (Early Exit) | `algorithms/sorting.py` | Sorting Tab & Benchmark Tab | `test_sorting.py::test_bubble_sort_early_exit` |
| **Req 1** | Quick Sort (Iterative) | `algorithms/sorting.py` | Sorting Tab & Benchmark Tab | `test_sorting.py::test_numeric_sorting_correctness` |
| **Req 1** | Counting Sort (Negative Offset) | `algorithms/sorting.py` | Sorting Tab & Benchmark Tab | `test_sorting.py::test_negative_numbers_and_zeroes` |
| **Req 1** | Bucket Sort (Insertion Inside) | `algorithms/sorting.py` | Sorting Tab & Benchmark Tab | `test_sorting.py::test_negative_numbers_and_zeroes` |
| **Req 1** | Radix Sort (LSD Base-10) | `algorithms/sorting.py` | Sorting Tab & Benchmark Tab | `test_sorting.py::test_negative_numbers_and_zeroes` |
| **Req 2** | Column-based Search | `algorithms/searching.py` | Library Tab search & Filter Tab | `test_searching.py::test_text_operators` |
| **Req 3** | Composite AND, OR, NOT Filters | `algorithms/searching.py` | Filter Tab Query Builder | `test_searching.py::test_composite_and_or_not` |
| **Req 4** | Multi-Level Sorting | `services/sort_service.py` | Sorting Tab Multi-Level Builder | `test_multilevel.py::test_multilevel_stable_merge_sort` |
| **Req 5** | 15,000+ Unique Records & DB | `database/repository.py` | Dashboard Tab & Library Tab | `test_scraper.py::test_incremental_deduplication` |
| **Req 5** | Live Scraper Controls | `scraper/worker.py` | Scraper Tab (Start/Pause/Resume/Stop) | Verified via `worker.py` and `test_scraper.py` |
| **Bonus** | SSRF-Safe URL-based Scraper | `scraper/url_scraper.py` | Scraper Tab URL Section | `test_scraper.py::test_ssrf_protection_private_and_loopback` |
| **Charts** | Matplotlib Comparison Charts | `ui/benchmark_tab.py` | Benchmark Tab Charts | Verified in UI |
| **Export** | CSV Data & Report Export | `services/export_service.py` | Library Tab & Benchmark Tab | Verified via ExportService |

