"""
FreeToGame API Scraper.
Collects curated free-to-play games with full metadata (genres, platforms, developers, release dates).
"""

from typing import List
from scraper.base import BaseScraper
from models.game import Game


class FreeToGameScraper(BaseScraper):
    def __init__(self, rate_limit_sec: float = 0.5):
        super().__init__(name="FreeToGame", rate_limit_sec=rate_limit_sec, timeout_sec=15)
        self.endpoint = "https://www.freetogame.com/api/games"

    def fetch_all(self) -> List[Game]:
        """Fetches all free-to-play games."""
        data = self.get_json(self.endpoint)
        if not isinstance(data, list):
            return []

        games: List[Game] = []
        for item in data:
            title = str(item.get("title", "")).strip()
            if not title:
                continue

            game = Game(
                title=title,
                release_date=item.get("release_date"),
                developer=item.get("developer"),
                publisher=item.get("publisher"),
                genres=item.get("genre"),
                platforms=item.get("platform"),
                rating=85.0,  # Default rating baseline for curated list
                price=0.0,    # Free to Play
                multiplayer=True,
                source="FreeToGame",
                source_url=item.get("freetogame_profile_url") or item.get("game_url"),
                external_id=str(item.get("id")),
                description=item.get("short_description")
            )
            games.append(game)

        return games

