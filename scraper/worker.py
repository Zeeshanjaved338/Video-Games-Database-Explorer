"""
Background Scraping Worker using QThread.
Coordinates all scrapers with Start, Pause, Resume, Stop, and live UI signals.
Saves data incrementally to SQLite so no work is lost on pause or interruption.
"""

import time
from PyQt5.QtCore import QThread, pyqtSignal
from typing import Optional, List
from models.game import Game
from database.repository import GameRepository
from scraper.steamspy_scraper import SteamSpyScraper
from scraper.freetogame_scraper import FreeToGameScraper
from scraper.cheapshark_scraper import CheapSharkScraper


class ScraperWorker(QThread):
    # Signals to communicate with PyQt5 UI
    progress_updated = pyqtSignal(int, int, int, int, int, str, float)  # collected, target, newly_added, duplicates, errors, source, elapsed_sec
    log_message = pyqtSignal(str)
    finished_scraping = pyqtSignal(int, int, int)  # total_added, total_duplicates, total_errors
    stopped_scraping = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, target_count: int = 15000, repo: Optional[GameRepository] = None, parent=None):
        super().__init__(parent)
        self.target_count = target_count
        self.repo = repo or GameRepository()

        # Thread control flags
        self._is_running = False
        self._is_paused = False
        self._is_stopped = False

        # Counters
        self.total_added = 0
        self.total_duplicates = 0
        self.total_errors = 0
        self.start_time = 0.0

        # Scraper instances
        self.steamspy = SteamSpyScraper(rate_limit_sec=0.8)
        self.freetogame = FreeToGameScraper(rate_limit_sec=0.5)
        self.cheapshark = CheapSharkScraper(rate_limit_sec=0.5)

    def pause(self):
        """Pauses the scraper execution."""
        self._is_paused = True
        self.log_message.emit("Scraper PAUSED by user.")

    def resume(self):
        """Resumes the scraper execution."""
        self._is_paused = False
        self.log_message.emit("Scraper RESUMED by user.")

    def stop(self):
        """Signals the scraper to stop completely."""
        self._is_stopped = True
        self._is_paused = False
        self.log_message.emit("Scraper STOP requested.")

    def _check_pause_and_stop(self) -> bool:
        """Returns True if scraper should terminate, or handles pausing."""
        while self._is_paused and not self._is_stopped:
            self.msleep(200)

        return self._is_stopped

    def run(self):
        """Main scraping loop executed on background QThread."""
        self._is_running = True
        self._is_stopped = False
        self._is_paused = False
        self.start_time = time.time()

        initial_count = self.repo.get_total_count()
        current_collected = initial_count
        self.log_message.emit(f"Starting scraper. Current unique database records: {initial_count:,}. Target: {self.target_count:,}.")

        # 1. First, scrape FreeToGame catalog (fast, ~420 rich records)
        if current_collected < self.target_count and not self._check_pause_and_stop():
            self.log_message.emit("Querying FreeToGame official catalog...")
            try:
                ftg_games = self.freetogame.fetch_all()
                added, dupes = self.repo.insert_games_batch(ftg_games)
                self.total_added += added
                self.total_duplicates += dupes
                current_collected = self.repo.get_total_count()
                elapsed = time.time() - self.start_time
                self.progress_updated.emit(current_collected, self.target_count, self.total_added, self.total_duplicates, self.total_errors, "FreeToGame", elapsed)
                self.log_message.emit(f"FreeToGame complete: {added} new games added, {dupes} duplicates.")
            except Exception as e:
                self.total_errors += 1
                self.log_message.emit(f"FreeToGame fetch error: {str(e)}")

        # 2. Second, scrape CheapShark deals (several pages of deals)
        cs_page = 0
        while current_collected < self.target_count and cs_page < 10 and not self._check_pause_and_stop():
            self.log_message.emit(f"Querying CheapShark deals (page {cs_page + 1})...")
            try:
                cs_games = self.cheapshark.fetch_page(page_num=cs_page, page_size=60)
                if not cs_games:
                    break
                added, dupes = self.repo.insert_games_batch(cs_games)
                self.total_added += added
                self.total_duplicates += dupes
                current_collected = self.repo.get_total_count()
                elapsed = time.time() - self.start_time
                self.progress_updated.emit(current_collected, self.target_count, self.total_added, self.total_duplicates, self.total_errors, f"CheapShark (pg {cs_page+1})", elapsed)
                cs_page += 1
            except Exception as e:
                self.total_errors += 1
                self.log_message.emit(f"CheapShark page {cs_page} error: {str(e)}")
                break

        # 3. Third, scrape SteamSpy API (1,000 games per page, 15+ pages)
        steamspy_page = 0
        while current_collected < self.target_count and steamspy_page < 30:
            if self._check_pause_and_stop():
                break

            self.log_message.emit(f"Querying SteamSpy public repository (page {steamspy_page})...")
            try:
                spy_games = self.steamspy.fetch_page(page_num=steamspy_page)
                if not spy_games:
                    self.log_message.emit(f"SteamSpy page {steamspy_page} returned 0 records.")
                    break

                added, dupes = self.repo.insert_games_batch(spy_games)
                self.total_added += added
                self.total_duplicates += dupes
                current_collected = self.repo.get_total_count()
                elapsed = time.time() - self.start_time

                self.progress_updated.emit(current_collected, self.target_count, self.total_added, self.total_duplicates, self.total_errors, f"SteamSpy (pg {steamspy_page})", elapsed)
                self.log_message.emit(f"SteamSpy page {steamspy_page}: +{added} added, {dupes} duplicates. Total in DB: {current_collected:,}.")

                steamspy_page += 1
            except Exception as e:
                self.total_errors += 1
                self.log_message.emit(f"SteamSpy error on page {steamspy_page}: {str(e)}")
                steamspy_page += 1
                self.msleep(1000)

        # Finished or stopped
        if self._is_stopped:
            self.log_message.emit("Scraping operation stopped.")
            self.stopped_scraping.emit()
        else:
            self.log_message.emit(f"Scraping completed! Newly added: {self.total_added:,}, Duplicates skipped: {self.total_duplicates:,}, Total unique in DB: {self.repo.get_total_count():,}.")
            self.finished_scraping.emit(self.total_added, self.total_duplicates, self.total_errors)

        self._is_running = False

