"""
Main Window for Video Game Database Explorer.
Integrates all tabs, header controls, status bar, and service events.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QStatusBar, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from ui.styles import APP_STYLESHEET
from ui.dashboard_tab import DashboardTab
from ui.library_tab import LibraryTab
from ui.scraper_tab import ScraperTab
from ui.filter_tab import FilterTab
from ui.sorting_tab import SortingTab
from ui.benchmark_tab import BenchmarkTab
from ui.about_tab import AboutTab
from services.data_service import DataService


class MainWindow(QMainWindow):
    def __init__(self, data_service: DataService):
        super().__init__()
        self.data_service = data_service

        self.setWindowTitle("Video Game Database Explorer — CS200 Data Structures & Algorithms Project 1")
        self.resize(1280, 820)
        self.setMinimumSize(1000, 650)

        self.setStyleSheet(APP_STYLESHEET)
        self.init_ui()
        self.refresh_all_views()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(6)

        # Top Header Bar
        header = QHBoxLayout()
        header_title_box = QVBoxLayout()
        header_title_box.setSpacing(2)
        header_title = QLabel("Video Game Database Explorer")
        header_title.setStyleSheet("font-size: 15px; font-weight: 700; color: #0f172a; letter-spacing: -0.2px;")
        header_sub = QLabel("University CS200 DSA Project 1 • Custom Sorting, Searching, Scraping & Benchmarking")
        header_sub.setStyleSheet("color: #64748b; font-size: 11px;")
        header_title_box.addWidget(header_title)
        header_title_box.addWidget(header_sub)
        header.addLayout(header_title_box)

        header.addStretch()

        # Database counter pill badge
        self.lbl_db_badge = QLabel("Database: 0 games")
        self.lbl_db_badge.setStyleSheet("""
            background-color: #f8fafc;
            color: #334155;
            border: 1px solid #cbd5e1;
            border-radius: 4px;
            padding: 4px 10px;
            font-weight: 600;
            font-size: 11px;
        """)
        header.addWidget(self.lbl_db_badge)

        main_layout.addLayout(header)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Instantiate Tabs
        self.dashboard_tab = DashboardTab(self.data_service)
        self.library_tab = LibraryTab(self.data_service)
        self.scraper_tab = ScraperTab(self.data_service)
        self.filter_tab = FilterTab(self.data_service)
        self.sorting_tab = SortingTab(self.data_service)
        self.benchmark_tab = BenchmarkTab(self.data_service)
        self.about_tab = AboutTab()

        # Add Tabs
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.library_tab, "Game Library")
        self.tabs.addTab(self.scraper_tab, "Data Scraper")
        self.tabs.addTab(self.filter_tab, "Search & Filters")
        self.tabs.addTab(self.sorting_tab, "Sorting & Multi-Level")
        self.tabs.addTab(self.benchmark_tab, "Algorithm Benchmarks")
        self.tabs.addTab(self.about_tab, "Documentation & Viva")

        main_layout.addWidget(self.tabs)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. System initialized.")

        # Wire Signals
        self._connect_signals()

    def _connect_signals(self):
        # Navigation from Dashboard / Actions
        self.dashboard_tab.navigate_to_tab.connect(self.tabs.setCurrentIndex)
        self.filter_tab.navigate_to_tab.connect(self.tabs.setCurrentIndex)
        self.sorting_tab.navigate_to_tab.connect(self.tabs.setCurrentIndex)

        # Scraper updates
        self.scraper_tab.data_updated.connect(self._on_scraper_data_updated)

        # Filter updates -> propagate to Library, Sorting, and Benchmark
        self.filter_tab.filters_applied.connect(self._on_filters_applied)

        # Sort updates -> propagate to Library
        self.sorting_tab.data_sorted.connect(self._on_data_sorted)

    def refresh_all_views(self):
        """Refreshes all tabs with latest database data."""
        total = self.data_service.get_total_count()
        self.lbl_db_badge.setText(f"Database: {total:,} games")

        self.dashboard_tab.refresh_stats()
        self.library_tab.reload_data()
        self.scraper_tab.update_db_counter()

        all_games = self.data_service.get_all_games()
        self.sorting_tab.set_filtered_context(all_games)
        self.benchmark_tab.set_filtered_context(all_games)

    def _on_scraper_data_updated(self):
        total = self.data_service.get_total_count()
        self.lbl_db_badge.setText(f"Database: {total:,} games")
        self.dashboard_tab.refresh_stats()
        self.library_tab.reload_data()

    def _on_filters_applied(self, filtered_records: list, filter_group: object):
        self.library_tab.load_records(filtered_records)
        self.sorting_tab.set_filtered_context(filtered_records)
        self.benchmark_tab.set_filtered_context(filtered_records)
        self.status_bar.showMessage(f"Filters applied: {len(filtered_records):,} matching records.")

    def _on_data_sorted(self, sorted_data: list, sort_result: object):
        self.library_tab.load_records(sorted_data)
        self.status_bar.showMessage(f"Sorted {len(sorted_data):,} records using {sort_result.algorithm_name} in {sort_result.elapsed_ms:.2f} ms.")

