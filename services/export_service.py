"""
Export Service for saving datasets, filtered views, and benchmark reports to CSV.
"""

import csv
from typing import List, Dict, Any
from models.filter_sort import SortResult


class ExportService:
    @staticmethod
    def export_games_to_csv(games: List[Dict[str, Any]], filepath: str) -> bool:
        """Exports a list of game records to a CSV file."""
        if not games:
            return False

        fieldnames = [
            "game_id", "title", "release_date", "developer", "publisher",
            "genres", "platforms", "rating", "rating_count", "price",
            "metacritic_score", "multiplayer", "source", "source_url",
            "description", "external_id", "created_at"
        ]

        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for g in games:
                writer.writerow(g)
        return True

    @staticmethod
    def export_benchmark_to_csv(results: List[SortResult], filepath: str) -> bool:
        """Exports benchmark metrics for all algorithms to CSV."""
        if not results:
            return False

        fieldnames = [
            "Algorithm", "Elapsed Time (ms)", "Comparisons", "Swaps",
            "Movements / Shifts", "Stability", "Time (Best)", "Time (Avg)",
            "Time (Worst)", "Space Complexity", "Status"
        ]

        with open(filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(r.to_summary_dict())
        return True

