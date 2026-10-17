"""
Data Service managing game records, in-memory filtering/sorting cache, and repository access.
"""

from typing import List, Dict, Any, Optional
from database.repository import GameRepository
from models.game import Game
from models.filter_sort import FilterGroup
from algorithms.searching import apply_composite_filters


class DataService:
    def __init__(self, repo: Optional[GameRepository] = None):
        self.repo = repo or GameRepository()
        self._cached_games: Optional[List[Dict[str, Any]]] = None

    def get_all_games(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Returns all game records, caching in memory for fast UI interaction."""
        if self._cached_games is None or force_refresh:
            self._cached_games = self.repo.get_all_games()
        return self._cached_games

    def invalidate_cache(self):
        """Invalidates in-memory cache after new games are scraped or added."""
        self._cached_games = None

    def get_total_count(self) -> int:
        return self.repo.get_total_count()

    def get_summary_statistics(self) -> Dict[str, Any]:
        return self.repo.get_summary_statistics()

    def get_source_statistics(self) -> Dict[str, int]:
        return self.repo.get_source_statistics()

    def filter_games(self, filter_group: FilterGroup) -> List[Dict[str, Any]]:
        """Filters all games using the in-memory composite filter engine."""
        games = self.get_all_games()
        return apply_composite_filters(games, filter_group)

    def insert_single_game(self, game: Game) -> Optional[int]:
        res = self.repo.insert_game(game)
        if res:
            self.invalidate_cache()
        return res

    def delete_game(self, game_id: int) -> bool:
        res = self.repo.delete_game(game_id)
        if res:
            self.invalidate_cache()
        return res

    def clear_all(self):
        self.repo.clear_all()
        self.invalidate_cache()

