"""
Unit tests for multi-level sorting and tie resolution.
"""

import unittest
from services.sort_service import SortService
from models.filter_sort import SortLevel


class TestMultiLevelSorting(unittest.TestCase):
    def setUp(self):
        self.games = [
            {"game_id": 1, "title": "Game B", "rating": 90.0, "release_date": "2020-01-01", "price": 20.0},
            {"game_id": 2, "title": "Game A", "rating": 90.0, "release_date": "2021-01-01", "price": 10.0},
            {"game_id": 3, "title": "Game C", "rating": 95.0, "release_date": "2019-01-01", "price": 30.0},
            {"game_id": 4, "title": "Game D", "rating": 90.0, "release_date": "2021-01-01", "price": 5.0},
        ]

    def test_multilevel_stable_merge_sort(self):
        """
        Primary key: rating DESC
        Secondary key: release_date DESC
        Tertiary key: price ASC
        """
        levels = [
            SortLevel(column="rating", direction="desc"),
            SortLevel(column="release_date", direction="desc"),
            SortLevel(column="price", direction="asc")
        ]
        res = SortService.sort_multi_level(self.games, "Merge Sort", levels)
        data = res.sorted_data

        # 1. Game C has highest rating 95.0 -> must be first
        self.assertEqual(data[0]["title"], "Game C")

        # 2. Next three all have rating 90.0.
        # Among them, release_date DESC:
        # Game A (2021) and Game D (2021) beat Game B (2020).
        # Between Game A and Game D: price ASC -> Game D ($5.0) precedes Game A ($10.0)
        self.assertEqual(data[1]["title"], "Game D")
        self.assertEqual(data[2]["title"], "Game A")
        self.assertEqual(data[3]["title"], "Game B")

    def test_multilevel_composite_quick_sort(self):
        """Test multi-level sorting with Quick Sort using composite comparator."""
        levels = [
            SortLevel(column="rating", direction="desc"),
            SortLevel(column="price", direction="asc")
        ]
        res = SortService.sort_multi_level(self.games, "Quick Sort", levels)
        data = res.sorted_data

        # Game C has rating 95.0 -> first
        self.assertEqual(data[0]["title"], "Game C")

        # Ties on 90.0: price asc -> Game D ($5.0) < Game A ($10.0) < Game B ($20.0)
        self.assertEqual(data[1]["title"], "Game D")
        self.assertEqual(data[2]["title"], "Game A")
        self.assertEqual(data[3]["title"], "Game B")


if __name__ == "__main__":
    unittest.main()

