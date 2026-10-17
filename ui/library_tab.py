"""
Library Tab: Main game records explorer with pagination, search, column visibility,
selection detail drawer, and CSV export.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QComboBox, QSplitter, QTextBrowser, QFileDialog, QMessageBox,
    QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any, Optional
from services.export_service import ExportService


class LibraryTab(QWidget):
    def __init__(self, data_service, parent=None):
        super().__init__(parent)
        self.data_service = data_service

        # State
        self.current_records: List[Dict[str, Any]] = []
        self.page_number = 1
        self.page_size = 50
        self.total_pages = 1

        self.columns = [
            ("game_id", "ID", 60),
            ("title", "Title", 220),
            ("rating", "Rating", 80),
            ("rating_count", "Reviews", 90),
            ("price", "Price ($)", 80),
            ("metacritic_score", "Metacritic", 90),
            ("genres", "Genres", 150),
            ("release_date", "Release Date", 100),
            ("developer", "Developer", 140),
            ("publisher", "Publisher", 140),
            ("source", "Source", 100),
        ]

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(6)

        # Top Control Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(6)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search title, developer, publisher, or genre...")
        self.search_input.textChanged.connect(self._on_search_changed)
        top_bar.addWidget(self.search_input, stretch=3)

        self.reset_btn = QPushButton("Reset Filter")
        self.reset_btn.setObjectName("secondaryBtn")
        self.reset_btn.clicked.connect(self.reload_data)
        top_bar.addWidget(self.reset_btn)

        self.export_btn = QPushButton("Export CSV")
        self.export_btn.setObjectName("secondaryBtn")
        self.export_btn.clicked.connect(self._export_csv)
        top_bar.addWidget(self.export_btn)

        main_layout.addLayout(top_bar)

        # Splitter: Main Table + Details Panel
        splitter = QSplitter(Qt.Horizontal)

        # Left: Table + Pagination
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels([col[1] for col in self.columns])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)

        for idx, col in enumerate(self.columns):
            self.table.setColumnWidth(idx, col[2])

        self.table.itemSelectionChanged.connect(self._on_row_selected)
        left_layout.addWidget(self.table)

        # Pagination Controls
        pag_bar = QHBoxLayout()
        pag_bar.setSpacing(4)

        self.btn_first = QPushButton("First")
        self.btn_first.setObjectName("secondaryBtn")
        self.btn_first.clicked.connect(self._go_first_page)
        pag_bar.addWidget(self.btn_first)

        self.btn_prev = QPushButton("Previous")
        self.btn_prev.setObjectName("secondaryBtn")
        self.btn_prev.clicked.connect(self._go_prev_page)
        pag_bar.addWidget(self.btn_prev)

        self.lbl_page = QLabel("Page 1 of 1")
        self.lbl_page.setStyleSheet("color: #0f172a; font-weight: 600; font-size: 11px; padding: 0 8px;")
        pag_bar.addWidget(self.lbl_page)

        self.btn_next = QPushButton("Next")
        self.btn_next.setObjectName("secondaryBtn")
        self.btn_next.clicked.connect(self._go_next_page)
        pag_bar.addWidget(self.btn_next)

        self.btn_last = QPushButton("Last")
        self.btn_last.setObjectName("secondaryBtn")
        self.btn_last.clicked.connect(self._go_last_page)
        pag_bar.addWidget(self.btn_last)

        pag_bar.addSpacing(12)
        lbl_rpp = QLabel("Per page:")
        lbl_rpp.setStyleSheet("color: #64748b; font-size: 11px;")
        pag_bar.addWidget(lbl_rpp)

        self.combo_page_size = QComboBox()
        self.combo_page_size.addItems(["25", "50", "100", "250", "500"])
        self.combo_page_size.setCurrentText("50")
        self.combo_page_size.currentIndexChanged.connect(self._on_page_size_changed)
        pag_bar.addWidget(self.combo_page_size)

        self.lbl_total_records = QLabel("Showing 0 of 0 games")
        self.lbl_total_records.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 8px;")
        pag_bar.addWidget(self.lbl_total_records)
        pag_bar.addStretch()

        left_layout.addLayout(pag_bar)
        splitter.addWidget(left_widget)

        # Right: Detail Drawer
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(6, 0, 0, 0)
        right_layout.setSpacing(4)

        detail_title = QLabel("Selected Game Details")
        detail_title.setStyleSheet("font-weight: 700; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #475569;")
        right_layout.addWidget(detail_title)

        self.detail_browser = QTextBrowser()
        self.detail_browser.setOpenExternalLinks(True)
        self.detail_browser.setStyleSheet("background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 5px; padding: 10px;")
        self.detail_browser.setHtml("<p style='color:#64748b; font-size:11px;'>Select a row to inspect attributes, metadata, and description.</p>")
        right_layout.addWidget(self.detail_browser)

        splitter.addWidget(right_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def load_records(self, records: List[Dict[str, Any]]):
        """Loads records into the library view, resetting to page 1."""
        self.current_records = records
        self.page_number = 1
        self._render_current_page()

    def reload_data(self):
        """Reloads the entire dataset from the data service."""
        games = self.data_service.get_all_games(force_refresh=True)
        self.search_input.clear()
        self.load_records(games)

    def _render_current_page(self):
        """Renders the current slice of records according to page_number and page_size."""
        total_items = len(self.current_records)
        self.total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)

        if self.page_number > self.total_pages:
            self.page_number = self.total_pages
        if self.page_number < 1:
            self.page_number = 1

        start_idx = (self.page_number - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_items)
        page_slice = self.current_records[start_idx:end_idx]

        self.table.setRowCount(len(page_slice))
        for row_idx, item in enumerate(page_slice):
            for col_idx, (col_key, _, _) in enumerate(self.columns):
                raw_val = item.get(col_key)
                if raw_val is None or raw_val == "":
                    display_text = "—"
                elif col_key == "rating":
                    display_text = f"{raw_val:.1f}%"
                elif col_key == "price":
                    display_text = f"${raw_val:.2f}" if float(raw_val) > 0 else "Free"
                elif col_key == "rating_count":
                    display_text = f"{int(raw_val):,}"
                else:
                    display_text = str(raw_val)

                table_item = QTableWidgetItem(display_text)
                if col_key in ("game_id", "rating", "rating_count", "price", "metacritic_score"):
                    table_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    table_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                self.table.setItem(row_idx, col_idx, table_item)

        # Update labels and pagination buttons
        self.lbl_page.setText(f"Page {self.page_number} of {self.total_pages}")
        self.lbl_total_records.setText(f"Showing {start_idx + 1 if total_items > 0 else 0} - {end_idx} of {total_items:,} games")

        self.btn_first.setEnabled(self.page_number > 1)
        self.btn_prev.setEnabled(self.page_number > 1)
        self.btn_next.setEnabled(self.page_number < self.total_pages)
        self.btn_last.setEnabled(self.page_number < self.total_pages)

    def _on_row_selected(self):
        """Displays rich details of selected game in right panel."""
        selected_rows = self.table.selectedIndexes()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        start_idx = (self.page_number - 1) * self.page_size
        actual_idx = start_idx + row
        if actual_idx >= len(self.current_records):
            return

        item = self.current_records[actual_idx]

        # Build HTML detail view
        url = item.get('source_url') or '#'
        url_link = f"<a href='{url}' style='color:#2563eb; text-decoration:none;'>{url}</a>" if item.get('source_url') else "None"

        html = f"""
        <div style='font-family:Segoe UI, -apple-system, sans-serif; color:#0f172a;'>
            <div style='font-size:13px; font-weight:700; color:#0f172a; margin-bottom:4px;'>{item.get('title', 'Unknown')}</div>
            <hr style='border: none; border-top: 1px solid #e2e8f0; margin:4px 0;'/>
            <table cellpadding='2' width='100%' style='font-size:11px;'>
                <tr><td style='color:#64748b; width:38%;'>ID:</td><td style='font-weight:600;'>{item.get('game_id')}</td></tr>
                <tr><td style='color:#64748b;'>External ID:</td><td>{item.get('external_id') or 'N/A'}</td></tr>
                <tr><td style='color:#64748b;'>Source:</td><td><span style='background-color:#f1f5f9; color:#334155; border:1px solid #e2e8f0; padding:1px 5px; border-radius:3px; font-size:10px;'>{item.get('source')}</span></td></tr>
                <tr><td style='color:#64748b;'>Release Date:</td><td>{item.get('release_date') or 'N/A'}</td></tr>
                <tr><td style='color:#64748b;'>Developer:</td><td style='font-weight:600;'>{item.get('developer') or 'Unknown'}</td></tr>
                <tr><td style='color:#64748b;'>Publisher:</td><td>{item.get('publisher') or 'Unknown'}</td></tr>
                <tr><td style='color:#64748b;'>Genres:</td><td>{item.get('genres') or 'N/A'}</td></tr>
                <tr><td style='color:#64748b;'>Platforms:</td><td>{item.get('platforms') or 'PC'}</td></tr>
                <tr><td style='color:#64748b;'>Rating:</td><td><b>{item.get('rating')}%</b> <span style='color:#64748b;'>({item.get('rating_count', 0):,} rev)</span></td></tr>
                <tr><td style='color:#64748b;'>Price:</td><td style='font-weight:600;'>${item.get('price'):.2f}</td></tr>
                <tr><td style='color:#64748b;'>Metacritic:</td><td style='font-weight:600;'>{item.get('metacritic_score') or 'N/A'} / 100</td></tr>
                <tr><td style='color:#64748b;'>Store Link:</td><td>{url_link}</td></tr>
            </table>
            <div style='font-size:10px; font-weight:700; text-transform:uppercase; color:#64748b; letter-spacing:0.5px; margin-top:8px; margin-bottom:2px;'>Description</div>
            <p style='color:#334155; line-height:1.4; font-size:11px; margin:0;'>
                {item.get('description') or 'No description available for this record.'}
            </p>
        </div>
        """
        self.detail_browser.setHtml(html)

    def _on_search_changed(self, text: str):
        text = text.strip().lower()
        if not text:
            self.load_records(self.data_service.get_all_games())
            return

        all_games = self.data_service.get_all_games()
        matched = []
        for g in all_games:
            title = str(g.get("title", "")).lower()
            dev = str(g.get("developer", "")).lower()
            pub = str(g.get("publisher", "")).lower()
            gen = str(g.get("genres", "")).lower()
            if text in title or text in dev or text in pub or text in gen:
                matched.append(g)

        self.load_records(matched)

    def _go_first_page(self):
        self.page_number = 1
        self._render_current_page()

    def _go_prev_page(self):
        if self.page_number > 1:
            self.page_number -= 1
            self._render_current_page()

    def _go_next_page(self):
        if self.page_number < self.total_pages:
            self.page_number += 1
            self._render_current_page()

    def _go_last_page(self):
        self.page_number = self.total_pages
        self._render_current_page()

    def _on_page_size_changed(self, idx):
        self.page_size = int(self.combo_page_size.currentText())
        self.page_number = 1
        self._render_current_page()

    def _export_csv(self):
        if not self.current_records:
            QMessageBox.warning(self, "Export CSV", "No records available to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Games to CSV", "games_export.csv", "CSV Files (*.csv)")
        if path:
            success = ExportService.export_games_to_csv(self.current_records, path)
            if success:
                QMessageBox.information(self, "Export Successful", f"Successfully exported {len(self.current_records):,} games to:\n{path}")
            else:
                QMessageBox.critical(self, "Export Failed", "Could not export records to CSV.")

