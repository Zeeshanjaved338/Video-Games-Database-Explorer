"""
Scraper package for Video Game Database Explorer.
"""
from scraper.base import BaseScraper
from scraper.steamspy_scraper import SteamSpyScraper
from scraper.freetogame_scraper import FreeToGameScraper
from scraper.cheapshark_scraper import CheapSharkScraper
from scraper.url_scraper import URLScraper
from scraper.worker import ScraperWorker

__all__ = [
    "BaseScraper",
    "SteamSpyScraper",
    "FreeToGameScraper",
    "CheapSharkScraper",
    "URLScraper",
    "ScraperWorker"
]

