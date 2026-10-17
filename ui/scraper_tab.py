"""
Scraper Tab: Live scraping subsystem with Start, Pause, Resume, Stop controls,
real-time progress tracking, activity logs, and the Bonus URL-based scraping feature.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QProgressBar, QGroupBox, QSpinBox, QPlainTextEdit,
    QGridLayout, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Optional
from scraper.worker import ScraperWorker
from scraper.url_scraper import URLScraper
from models.game import Game


class ScraperTab(QWidget):
    data_updated = pyqtSignal()  # Signal to trigger dashboard and library refresh

    def __init__(self, data_service, parent=None):
        super().__init__(parent)
        self.data_service = data_service
        self.worker: Optional[ScraperWorker] = None
        self.extracted_url_game: Optional[Game] = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        # -------------------------------------------------------------
        # Section 1: Live Scraping Subsystem
        # -------------------------------------------------------------
        scraper_group = QGroupBox("Automated Multi-Source Scraper")
        scraper_layout = QVBoxLayout(scraper_group)
        scraper_layout.setContentsMargins(8, 10, 8, 8)
        scraper_layout.setSpacing(8)

        # Controls Row
        ctrl_row = QHBoxLayout()
        ctrl_row.setSpacing(6)

        lbl_target = QLabel("Collection Target:")
        lbl_target.setStyleSheet("font-size: 11px; color: #334155; font-weight: 600;")
        ctrl_row.addWidget(lbl_target)

        self.spin_target = QSpinBox()
        self.spin_target.setRange(100, 100000)
        self.spin_target.setSingleStep(1000)
        self.spin_target.setValue(16000)
        ctrl_row.addWidget(self.spin_target)

        ctrl_row.addSpacing(10)

        self.btn_start = QPushButton("Start Scraper")
        self.btn_start.setObjectName("successBtn")
        self.btn_start.clicked.connect(self._start_scraper)
        ctrl_row.addWidget(self.btn_start)

        self.btn_pause = QPushButton("Pause")
        self.btn_pause.setObjectName("secondaryBtn")
        self.btn_pause.setEnabled(False)
        self.btn_pause.clicked.connect(self._pause_scraper)
        ctrl_row.addWidget(self.btn_pause)

        self.btn_resume = QPushButton("Resume")
        self.btn_resume.setObjectName("secondaryBtn")
        self.btn_resume.setEnabled(False)
        self.btn_resume.clicked.connect(self._resume_scraper)
        ctrl_row.addWidget(self.btn_resume)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setObjectName("dangerBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._stop_scraper)
        ctrl_row.addWidget(self.btn_stop)

        ctrl_row.addStretch()
        scraper_layout.addLayout(ctrl_row)

        # Progress Bar & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        scraper_layout.addWidget(self.progress_bar)

        # Stats Cards Grid
        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(8)
        stats_grid.setVerticalSpacing(4)
        self.lbl_stat_db = self._add_stat(stats_grid, "Database Total", "0", 0, 0, "#0f172a")
        self.lbl_stat_new = self._add_stat(stats_grid, "Newly Added", "0", 0, 1, "#059669")
        self.lbl_stat_dupes = self._add_stat(stats_grid, "Duplicates Skipped", "0", 0, 2, "#d97706")
        self.lbl_stat_errors = self._add_stat(stats_grid, "Errors / Retries", "0", 0, 3, "#dc2626")
        self.lbl_stat_source = self._add_stat(stats_grid, "Current Source", "Idle", 0, 4, "#0f172a")
        self.lbl_stat_time = self._add_stat(stats_grid, "Elapsed Time", "0.0s", 0, 5, "#475569")
        scraper_layout.addLayout(stats_grid)

        # Live Activity Log
        lbl_log = QLabel("Activity Log:")
        lbl_log.setStyleSheet("font-size: 10px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.3px;")
        scraper_layout.addWidget(lbl_log)
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(110)
        scraper_layout.addWidget(self.log_text)

        main_layout.addWidget(scraper_group)

        # -------------------------------------------------------------
        # Section 2: Bonus Requirement — URL-Based Scraping
        # -------------------------------------------------------------
        url_group = QGroupBox("Single-Game URL Scraper (SSRF-Protected)")
        url_layout = QVBoxLayout(url_group)
        url_layout.setContentsMargins(8, 10, 8, 8)
        url_layout.setSpacing(6)

        url_input_row = QHBoxLayout()
        url_input_row.setSpacing(6)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter Steam Store, FreeToGame, or game page URL...")
        url_input_row.addWidget(self.url_input, stretch=3)

        self.btn_scrape_url = QPushButton("Scrape URL")
        self.btn_scrape_url.clicked.connect(self._scrape_url)
        url_input_row.addWidget(self.btn_scrape_url)

        url_layout.addLayout(url_input_row)

        self.lbl_url_status = QLabel("Enter a supported game page URL to extract metadata.")
        self.lbl_url_status.setStyleSheet("color: #64748b; font-size: 11px;")
        url_layout.addWidget(self.lbl_url_status)

        # Preview Frame for Extracted URL Record
        self.preview_frame = QFrame()
        self.preview_frame.setStyleSheet("background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 6px;")
        preview_layout = QHBoxLayout(self.preview_frame)
        preview_layout.setContentsMargins(6, 4, 6, 4)

        self.lbl_preview_info = QLabel("No record extracted yet.")
        self.lbl_preview_info.setStyleSheet("color: #475569; font-size: 11px;")
        preview_layout.addWidget(self.lbl_preview_info, stretch=3)

        self.btn_save_url_game = QPushButton("Save to Database")
        self.btn_save_url_game.setObjectName("successBtn")
        self.btn_save_url_game.setEnabled(False)
        self.btn_save_url_game.clicked.connect(self._save_extracted_game)
        preview_layout.addWidget(self.btn_save_url_game)

        url_layout.addWidget(self.preview_frame)
        main_layout.addWidget(url_group)

        # Initialize current count
        self.update_db_counter()

    def _add_stat(self, grid: QGridLayout, title: str, val: str, r: int, c: int, color_hex: str) -> QLabel:
        frame = QFrame()
        frame.setStyleSheet("background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 4px;")
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(6, 4, 6, 4)
        vbox.setSpacing(2)

        t_lbl = QLabel(title)
        t_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;")
        v_lbl = QLabel(val)
        v_lbl.setStyleSheet(f"color: {color_hex}; font-size: 13px; font-weight: 700;")

        vbox.addWidget(t_lbl)
        vbox.addWidget(v_lbl)
        grid.addWidget(frame, r, c)
        return v_lbl

    def update_db_counter(self):
        total = self.data_service.get_total_count()
        self.lbl_stat_db.setText(f"{total:,}")

    def _start_scraper(self):
        target = self.spin_target.value()
        self.worker = ScraperWorker(target_count=target, repo=self.data_service.repo, parent=self)
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.log_message.connect(self._on_log)
        self.worker.finished_scraping.connect(self._on_finished)
        self.worker.stopped_scraping.connect(self._on_stopped)
        self.worker.error_occurred.connect(self._on_error)

        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(True)

        self.log_text.appendPlainText(">>> Scraping worker thread launched.")
        self.worker.start()

    def _pause_scraper(self):
        if self.worker:
            self.worker.pause()
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(True)

    def _resume_scraper(self):
        if self.worker:
            self.worker.resume()
            self.btn_pause.setEnabled(True)
            self.btn_resume.setEnabled(False)

    def _stop_scraper(self):
        if self.worker:
            self.worker.stop()
            self.btn_pause.setEnabled(False)
            self.btn_resume.setEnabled(False)
            self.btn_stop.setEnabled(False)

    def _on_progress(self, collected: int, target: int, added: int, dupes: int, errors: int, source: str, elapsed: float):
        pct = min(100, int((collected / target) * 100)) if target > 0 else 0
        self.progress_bar.setValue(pct)
        self.lbl_stat_db.setText(f"{collected:,}")
        self.lbl_stat_new.setText(f"{added:,}")
        self.lbl_stat_dupes.setText(f"{dupes:,}")
        self.lbl_stat_errors.setText(f"{errors}")
        self.lbl_stat_source.setText(source)
        self.lbl_stat_time.setText(f"{elapsed:.1f}s")
        self.data_updated.emit()

    def _on_log(self, msg: str):
        self.log_text.appendPlainText(msg)

    def _on_finished(self, added: int, dupes: int, errors: int):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.log_text.appendPlainText(">>> Scraping session successfully finished.")
        self.data_service.invalidate_cache()
        self.data_updated.emit()
        QMessageBox.information(self, "Scraper Finished", f"Scraping completed!\nNewly Added: {added:,}\nDuplicates Filtered: {dupes:,}\nErrors: {errors}")

    def _on_stopped(self):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.log_text.appendPlainText(">>> Scraping stopped by user.")
        self.data_service.invalidate_cache()
        self.data_updated.emit()

    def _on_error(self, err: str):
        self.log_text.appendPlainText(f"[ERROR] {err}")
        QMessageBox.critical(self, "Scraper Error", err)

    def _scrape_url(self):
        url = self.url_input.text().strip()
        if not url:
            self.lbl_url_status.setText("Please enter a valid URL.")
            return

        self.lbl_url_status.setText("Validating security and fetching page...")
        game, err = URLScraper.scrape_url(url)
        if err:
            self.lbl_url_status.setText(f"<span style='color:#f87171;'>[Failed] {err}</span>")
            self.btn_save_url_game.setEnabled(False)
            self.extracted_url_game = None
            self.lbl_preview_info.setText(f"Error: {err}")
            return

        self.extracted_url_game = game
        self.lbl_url_status.setText("<span style='color:#34d399;'>[Success] Game metadata parsed cleanly! Click 'Save to Database' to persist.</span>")
        self.lbl_preview_info.setText(
            f"<b>Title:</b> {game.title} | <b>Developer:</b> {game.developer or 'N/A'} | "
            f"<b>Rating:</b> {game.rating or 'N/A'}% | <b>Price:</b> ${game.price or 0.0:.2f} | "
            f"<b>Genres:</b> {game.genres or 'N/A'}"
        )
        self.btn_save_url_game.setEnabled(True)

    def _save_extracted_game(self):
        if not self.extracted_url_game:
            return

        game_id = self.data_service.insert_single_game(self.extracted_url_game)
        if game_id:
            QMessageBox.information(self, "Game Saved", f"Successfully saved '{self.extracted_url_game.title}' into database with Game ID: {game_id}!")
            self.btn_save_url_game.setEnabled(False)
            self.update_db_counter()
            self.data_updated.emit()
        else:
            QMessageBox.warning(self, "Duplicate Game", f"'{self.extracted_url_game.title}' is already present in the database. Skipped duplicate.")

