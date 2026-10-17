"""
Abstract Base Scraper providing safe HTTP session management, rate limiting, and headers.
"""

import time
import requests
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class BaseScraper(ABC):
    def __init__(self, name: str, rate_limit_sec: float = 1.0, timeout_sec: int = 15):
        self.name = name
        self.rate_limit_sec = rate_limit_sec
        self.timeout_sec = timeout_sec
        self.last_request_time = 0.0

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "VideoGameDatabaseExplorer/1.0 (University DSA Project CS200; Contact: student@university.edu)"
        })

    def _wait_rate_limit(self):
        """Enforces polite rate limiting between successive requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_sec:
            time.sleep(self.rate_limit_sec - elapsed)
        self.last_request_time = time.time()

    def get_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Performs a rate-limited GET request expecting JSON."""
        self._wait_rate_limit()
        resp = self.session.get(url, params=params, timeout=self.timeout_sec)
        resp.raise_for_status()
        return resp.json()

    def get_html(self, url: str, params: Optional[Dict[str, Any]] = None, cookies: Optional[Dict[str, str]] = None) -> str:
        """Performs a rate-limited GET request returning HTML text."""
        self._wait_rate_limit()
        resp = self.session.get(url, params=params, cookies=cookies, timeout=self.timeout_sec)
        resp.raise_for_status()
        return resp.text

