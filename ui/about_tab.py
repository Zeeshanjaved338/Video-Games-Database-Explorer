"""
About Tab: University CS200 Data Structures & Algorithms viva presentation guide,
algorithm theory, complexity reference, and architecture overview.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextBrowser
from PyQt5.QtCore import Qt


class AboutTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 4px; padding: 12px;")

        html = """
        <div style='font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; color: #0f172a; line-height: 1.5; font-size: 11px;'>
            <div style='border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 12px;'>
                <div style='font-size: 14px; font-weight: 700; color: #0f172a;'>
                    Video Game Database Explorer — CS200 DSA Project 1
                </div>
                <div style='color: #64748b; font-size: 11px; margin-top: 3px;'>
                    Desktop engineering demonstration featuring eight from-scratch sorting algorithms, multi-key resolution, composite filtering, web scraping, and empirical benchmarking across 15,000+ video game records.
                </div>
            </div>

            <div style='font-size: 12px; font-weight: 700; color: #0f172a; margin-top: 14px; margin-bottom: 6px;'>
                1. Algorithm Complexity &amp; Stability Reference
            </div>
            <table width='100%' border='1' cellpadding='5' style='border-collapse: collapse; border: 1px solid #e2e8f0; font-size: 11px;'>
                <tr style='background-color: #f8fafc; color: #475569; font-weight: 600; text-align: left;'>
                    <th style='padding: 6px 8px; border: 1px solid #e2e8f0;'>Algorithm</th>
                    <th style='padding: 6px 8px; border: 1px solid #e2e8f0;'>Best Time</th>
                    <th style='padding: 6px 8px; border: 1px solid #e2e8f0;'>Avg Time</th>
                    <th style='padding: 6px 8px; border: 1px solid #e2e8f0;'>Worst Time</th>
                    <th style='padding: 6px 8px; border: 1px solid #e2e8f0;'>Aux Space</th>
                    <th style='padding: 6px 8px; border: 1px solid #e2e8f0;'>Stability</th>
                    <th style='padding: 6px 8px; border: 1px solid #e2e8f0;'>Key Characteristics</th>
                </tr>
                <tr>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'><b>Insertion Sort</b></td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>O(1)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>Stable</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>Efficient for small or nearly sorted datasets. Online incremental processing.</td>
                </tr>
                <tr style='background-color: #fafbfc;'>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'><b>Selection Sort</b></td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>O(1)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#d97706; font-weight:600;'>Unstable</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>Always performs n(n-1)/2 comparisons; minimal memory writes (at most n-1 swaps).</td>
                </tr>
                <tr>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'><b>Merge Sort</b></td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#2563eb; font-weight:600;'>O(n log n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#2563eb; font-weight:600;'>O(n log n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#2563eb; font-weight:600;'>O(n log n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>O(n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>Stable</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>Divide-and-conquer; guaranteed O(n log n) worst-case. Stable merge with tie retention.</td>
                </tr>
                <tr style='background-color: #fafbfc;'>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'><b>Bubble Sort</b></td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>O(1)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>Stable</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>Early-exit swapped flag detects already-sorted sequences in a single linear pass.</td>
                </tr>
                <tr>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'><b>Quick Sort</b></td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#2563eb; font-weight:600;'>O(n log n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#2563eb; font-weight:600;'>O(n log n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>O(log n)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#d97706; font-weight:600;'>Unstable</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>Median-of-three pivot selection protects against degradation; iterative stack avoids recursion overflow.</td>
                </tr>
                <tr style='background-color: #fafbfc;'>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'><b>Counting Sort</b></td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(n + k)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(n + k)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(n + k)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>O(n + k)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>Stable</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>Non-comparison integer algorithm. Negative values offset to min=0. Reverse scan maintains stability.</td>
                </tr>
                <tr>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'><b>Bucket Sort</b></td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(n + k)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(n + k)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#dc2626; font-weight:600;'>O(n²)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>O(n + k)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>Stable</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>Normalized distribution into k buckets; buckets internally sorted with stable Insertion Sort.</td>
                </tr>
                <tr style='background-color: #fafbfc;'>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'><b>Radix Sort (LSD)</b></td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(d(n + b))</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(d(n + b))</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>O(d(n + b))</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>O(n + b)</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0; color:#059669; font-weight:600;'>Stable</td>
                    <td style='padding: 5px 8px; border: 1px solid #e2e8f0;'>Processes least-to-most significant digits (base 10) via stable counting passes. Offsets negative values.</td>
                </tr>
            </table>

            <div style='font-size: 12px; font-weight: 700; color: #0f172a; margin-top: 16px; margin-bottom: 6px;'>
                2. University Viva &amp; Demonstration Guide
            </div>
            <ol style='color: #334155; padding-left: 18px; margin-top: 4px;'>
                <li style='margin-bottom: 8px;'>
                    <b>Q: How did you implement multi-level sorting (e.g. Rating DESC &rarr; Release Date DESC &rarr; Title ASC)?</b><br/>
                    <span style='color:#1e293b;'>A:</span> For stable algorithms (Merge, Insertion, Bubble, Counting, Radix), we use the <b>Radix Multi-Pass Principle</b>:
                    we sort successively from the lowest-priority key to the highest-priority key. Because each pass is stable,
                    whenever items tie on the primary key, their relative order established by the secondary key pass is strictly preserved.
                    For unstable algorithms (Quick Sort), we utilize a composite multi-attribute comparator during partitioning.
                </li>
                <li style='margin-bottom: 8px;'>
                    <b>Q: Why do Counting Sort and Radix Sort break the theoretical O(n log n) comparison lower bound?</b><br/>
                    <span style='color:#1e293b;'>A:</span> The &Omega;(n log n) lower bound applies strictly to <i>comparison-based</i> sorting models (decision trees with n! leaves).
                    Counting Sort and Radix Sort are <i>non-comparison</i> algorithms that inspect the algebraic properties and digit representation of integer keys directly,
                    achieving linear O(n + k) or O(d(n + b)) complexity.
                </li>
                <li style='margin-bottom: 8px;'>
                    <b>Q: How are missing / null values handled across all algorithms?</b><br/>
                    <span style='color:#1e293b;'>A:</span> Missing values (None) are normalized. By university convention, None values are placed at the very end of ascending sorts
                    (and the start of descending sorts), preventing Python's <code>TypeError: '&lt;' not supported between instances of 'NoneType' and 'int'</code>.
                </li>
                <li style='margin-bottom: 8px;'>
                    <b>Q: How does the application avoid UI freezing when sorting 15,000 records or scraping?</b><br/>
                    <span style='color:#1e293b;'>A:</span> All long-running tasks (scraping and benchmarking) execute on separate background <code>QThread</code> workers.
                    The main UI thread remains completely responsive, receiving updates through thread-safe PyQt signals and slots.
                </li>
                <li style='margin-bottom: 8px;'>
                    <b>Q: How does the Bonus URL Scraper protect against SSRF (Server-Side Request Forgery)?</b><br/>
                    <span style='color:#1e293b;'>A:</span> Before making any HTTP request, the URL's hostname is resolved to an IP address and checked against
                    private, loopback, link-local, and reserved IP ranges (e.g. 127.0.0.1, 192.168.x.x, 10.x.x.x, 169.254.x.x, ::1).
                    Any request targeting local or private infrastructure is immediately blocked.
                </li>
            </ol>

            <div style='font-size: 12px; font-weight: 700; color: #0f172a; margin-top: 16px; margin-bottom: 6px;'>
                3. Architecture &amp; Data Model
            </div>
            <ul style='color: #334155; padding-left: 18px; margin-top: 4px;'>
                <li><b>models/</b>: Typed definitions for Game entities, FilterCondition, FilterGroup, SortLevel, SortResult.</li>
                <li><b>algorithms/sorting.py</b>: Pure from-scratch implementations of all 8 sorting algorithms with operation counters.</li>
                <li><b>algorithms/searching.py</b>: Text, numeric, and date filter operators joined by AND, OR, and NOT.</li>
                <li><b>database/</b>: SQLite database with indexes, WAL mode, transaction-safe batch inserts, and deduplication.</li>
                <li><b>scraper/</b>: Multi-source adapters (SteamSpy, FreeToGame, CheapShark) and SSRF-safe URL scraper with QThread worker.</li>
                <li><b>services/</b>: High-level orchestration for sorting, benchmarking, CSV exporting, and data caching.</li>
                <li><b>ui/</b>: Modern PyQt5 graphical interface with tables, visual query builder, and Matplotlib integration.</li>
            </ul>
        </div>
        """
        browser.setHtml(html)
        layout.addWidget(browser)
