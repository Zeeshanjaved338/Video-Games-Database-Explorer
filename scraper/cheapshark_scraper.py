"""
CheapShark Deals and Games Scraper.
Collects game deals with Metacritic scores, Steam ratings, and prices.
"""

from typing import List
from scraper.base import BaseScraper
from models.game import Game
import datetime


class CheapSharkScraper(BaseScraper):
    def __init__(self, rate_limit_sec: float = 0.5):
        super().__init__(name="CheapShark", rate_limit_sec=rate_limit_sec, timeout_sec=15)
        self.endpoint = "https://www.cheapshark.com/api/1.0/deals"

    def fetch_page(self, page_num: int = 0, page_size: int = 60) -> List[Game]:
        """Fetches a page of deals from CheapShark."""
        params = {
            "pageNumber": page_num,
            "pageSize": page_size
        }
        data = self.get_json(self.endpoint, params=params)
        if not isinstance(data, list):
            return []

        games: List[Game] = []
        for item in data:
            title = str(item.get("title", "")).strip()
            if not title:
                continue

            # Parse metacritic score
            meta = item.get("metacriticScore")
            metacritic_score = int(meta) if meta and meta != "0" else None

            # Parse steam rating
            steam_pct = item.get("steamRatingPercent")
            rating = float(steam_pct) if steam_pct and steam_pct != "0" else None

            steam_cnt = item.get("steamRatingCount")
            rating_count = int(steam_cnt) if steam_cnt and steam_cnt != "0" else None

            sale_price = item.get("salePrice")
            try:
                price = float(sale_price) if sale_price is not None else None
            except (ValueError, TypeError):
                price = None

            # Release date unix timestamp
            rel_ts = item.get("releaseDate")
            release_date = None
            if rel_ts and int(rel_ts) > 0:
                try:
                    release_date = datetime.datetime.fromtimestamp(int(rel_ts)).strftime("%Y-%m-%d")
                except Exception:
                    release_date = None

            steam_appid = item.get("steamAppID")
            source_url = f"https://store.steampowered.com/app/{steam_appid}/" if steam_appid else None

            game = Game(
                title=title,
                release_date=release_date,
                rating=rating,
                rating_count=rating_count,
                price=price,
                metacritic_score=metacritic_score,
                genres="Action, Adventure",
                platforms="PC, Steam",
                source="CheapShark",
                source_url=source_url,
                external_id=item.get("dealID") or str(item.get("gameID")),
                description=f"Store deal on CheapShark with {item.get('savings', '0')}% savings."
            )
            games.append(game)

        return games

