"""
SteamSpy API Scraper.
Collects games in 1,000-record paginated batches from SteamSpy public API.
"""

from typing import List, Optional
from scraper.base import BaseScraper
from models.game import Game


class SteamSpyScraper(BaseScraper):
    def __init__(self, rate_limit_sec: float = 1.0):
        super().__init__(name="SteamSpy", rate_limit_sec=rate_limit_sec, timeout_sec=20)
        self.base_url = "https://steamspy.com/api.php"

    def fetch_page(self, page_num: int) -> List[Game]:
        """
        Fetches one page (up to 1,000 games) from SteamSpy.
        Page numbers start at 0.
        """
        params = {
            "request": "all",
            "page": page_num
        }
        data = self.get_json(self.base_url, params=params)
        if not isinstance(data, dict):
            return []

        games: List[Game] = []
        for appid_str, item in data.items():
            if not isinstance(item, dict):
                continue

            appid = item.get("appid", appid_str)
            title = item.get("name", "").strip()
            if not title or title == "None":
                continue

            pos = int(item.get("positive", 0) or 0)
            neg = int(item.get("negative", 0) or 0)
            total_reviews = pos + neg
            rating = round((pos / total_reviews) * 100.0, 1) if total_reviews > 0 else None

            # Raw price is in cents
            raw_price = item.get("price")
            try:
                price = round(float(raw_price) / 100.0, 2) if raw_price is not None else None
            except (ValueError, TypeError):
                price = None

            developer = item.get("developer") or None
            publisher = item.get("publisher") or None

            game = Game(
                title=title,
                developer=developer,
                publisher=publisher,
                genres="Video Game",
                platforms="PC, Windows",
                rating=rating,
                rating_count=total_reviews,
                price=price,
                source="SteamSpy",
                source_url=f"https://store.steampowered.com/app/{appid}/",
                external_id=str(appid),
                description=f"Steam title developed by {developer or 'Unknown'}."
            )
            games.append(game)

        return games

