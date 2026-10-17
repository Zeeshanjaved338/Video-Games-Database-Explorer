"""
Dashboard Tab showing system overview, source breakdown, and analytics cards.
Designed with compact enterprise layout and professional typography.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout,
    QGroupBox, QPushButton, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Dict, Any


class DashboardTab(QWidget):
    navigate_to_tab = pyqtSignal(int)

    def __init__(self, data_service, parent=None):
        super().__init__(parent)
        self.data_service = data_service
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Header Title
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)

        title = QLabel("Database Analytics & Overview")
        title.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a;")
        subtitle = QLabel("Live database statistics, distribution summaries, and quick navigation")
        subtitle.setStyleSheet("color: #64748b; font-size: 11px;")

        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        self.refresh_btn = QPushButton("Refresh Data")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.clicked.connect(self.refresh_stats)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Metric Summary Cards Grid
        cards_group = QGroupBox("Key Metrics")
        cards_grid = QGridLayout(cards_group)
        cards_grid.setHorizontalSpacing(10)
        cards_grid.setVerticalSpacing(8)
        cards_grid.setContentsMargins(8, 10, 8, 8)

        self.card_total = self._create_card("Total Records", "0")
        self.card_avg_rating = self._create_card("Average Rating", "0.0%")
        self.card_avg_price = self._create_card("Average Price", "$0.00")
        self.card_metacritic = self._create_card("Average Metacritic", "0")

        cards_grid.addWidget(self.card_total, 0, 0)
        cards_grid.addWidget(self.card_avg_rating, 0, 1)
        cards_grid.addWidget(self.card_avg_price, 0, 2)
        cards_grid.addWidget(self.card_metacritic, 0, 3)

        layout.addWidget(cards_group)

        # Middle Section: Sources & Top Genres
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(10)

        # Data Sources Box
        sources_group = QGroupBox("Data Sources")
        self.sources_layout = QVBoxLayout(sources_group)
        self.sources_layout.setContentsMargins(8, 10, 8, 8)
        self.sources_label = QLabel("Loading data sources...")
        self.sources_label.setStyleSheet("color: #334155; line-height: 1.4; font-size: 11px;")
        self.sources_layout.addWidget(self.sources_label)
        middle_layout.addWidget(sources_group, stretch=1)

        # Top Genres Box
        genres_group = QGroupBox("Top Genres")
        self.genres_layout = QVBoxLayout(genres_group)
        self.genres_layout.setContentsMargins(8, 10, 8, 8)
        self.genres_label = QLabel("Loading top genres...")
        self.genres_label.setStyleSheet("color: #334155; line-height: 1.4; font-size: 11px;")
        self.genres_layout.addWidget(self.genres_label)
        middle_layout.addWidget(genres_group, stretch=1)

        layout.addLayout(middle_layout)

        # Quick Actions Box
        actions_group = QGroupBox("Navigation Shortcuts")
        actions_layout = QHBoxLayout(actions_group)
        actions_layout.setContentsMargins(8, 10, 8, 8)
        actions_layout.setSpacing(8)

        btn_lib = QPushButton("Game Library")
        btn_lib.setObjectName("secondaryBtn")
        btn_lib.clicked.connect(lambda: self.navigate_to_tab.emit(1))
        actions_layout.addWidget(btn_lib)

        btn_scrape = QPushButton("Scraper Subsystem")
        btn_scrape.setObjectName("secondaryBtn")
        btn_scrape.clicked.connect(lambda: self.navigate_to_tab.emit(2))
        actions_layout.addWidget(btn_scrape)

        btn_filter = QPushButton("Composite Filters")
        btn_filter.setObjectName("secondaryBtn")
        btn_filter.clicked.connect(lambda: self.navigate_to_tab.emit(3))
        actions_layout.addWidget(btn_filter)

        btn_sort = QPushButton("Sorting & Multi-Level")
        btn_sort.setObjectName("secondaryBtn")
        btn_sort.clicked.connect(lambda: self.navigate_to_tab.emit(4))
        actions_layout.addWidget(btn_sort)

        btn_bench = QPushButton("Run Benchmarks")
        btn_bench.clicked.connect(lambda: self.navigate_to_tab.emit(5))
        actions_layout.addWidget(btn_bench)

        layout.addWidget(actions_group)

        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _create_card(self, title: str, value: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 5px;
                padding: 6px;
            }
        """)
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(6, 4, 6, 4)
        vbox.setSpacing(2)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("cardTitle")

        lbl_val = QLabel(value)
        lbl_val.setObjectName("cardValue")

        vbox.addWidget(lbl_title)
        vbox.addWidget(lbl_val)
        frame.val_label = lbl_val
        return frame

    def refresh_stats(self):
        """Reloads summary statistics from data service and updates UI."""
        stats = self.data_service.get_summary_statistics()
        sources = self.data_service.get_source_statistics()

        total = stats.get("total", 0)
        self.card_total.val_label.setText(f"{total:,}")

        avg_r = stats.get("avg_rating")
        self.card_avg_rating.val_label.setText(f"{avg_r:.1f}%" if avg_r is not None else "N/A")

        avg_p = stats.get("avg_price")
        self.card_avg_price.val_label.setText(f"${avg_p:.2f}" if avg_p is not None else "N/A")

        avg_m = stats.get("avg_metacritic")
        self.card_metacritic.val_label.setText(f"{avg_m:.0f} / 100" if avg_m is not None else "N/A")

        # Source breakdown
        if sources:
            src_text = "<table width='100%' cellpadding='2' style='font-size:11px;'>"
            for src, count in sources.items():
                pct = (count / total * 100.0) if total > 0 else 0
                src_text += f"<tr><td style='color:#1e293b; font-weight:600;'>{src}</td><td align='right' style='color:#0f172a;'>{count:,}</td><td align='right' style='color:#64748b;'>({pct:.1f}%)</td></tr>"
            src_text += "</table>"
            self.sources_label.setText(src_text)
        else:
            self.sources_label.setText("No records found in database.")

        # Top genres
        top_genres = stats.get("top_genres", [])
        if top_genres:
            g_text = "<table width='100%' cellpadding='2' style='font-size:11px;'>"
            for genre, count in top_genres:
                g_text += f"<tr><td style='color:#1e293b; font-weight:600;'>{genre}</td><td align='right' style='color:#0f172a;'>{count:,}</td></tr>"
            g_text += "</table>"
            self.genres_label.setText(g_text)
        else:
            self.genres_label.setText("No genre data available.")
