"""
Unit tests for all eight sorting algorithms.
Verifies correctness, stability, edge cases, missing value handling, and runtime metrics.
"""

import unittest
from algorithms.sorting import (
    insertion_sort,
    selection_sort,
    merge_sort,
    bubble_sort,
    quick_sort,
    counting_sort,
    bucket_sort,
    radix_sort,
    SORTING_ALGORITHMS,
    execute_sort
)


class TestSortingAlgorithms(unittest.TestCase):
    def setUp(self):
        self.sample_games = [
            {"game_id": 1, "title": "Portal 2", "rating": 95.0, "price": 9.99, "metacritic_score": 95, "rating_count": 300000},
            {"game_id": 2, "title": "Half-Life 2", "rating": 96.0, "price": 9.99, "metacritic_score": 96, "rating_count": 250000},
            {"game_id": 3, "title": "Terraria", "rating": 97.0, "price": 4.99, "metacritic_score": 83, "rating_count": 900000},
            {"game_id": 4, "title": "Cyberpunk 2077", "rating": 80.0, "price": 59.99, "metacritic_score": 86, "rating_count": 600000},
            {"game_id": 5, "title": "Stardew Valley", "rating": 98.0, "price": 14.99, "metacritic_score": 89, "rating_count": 500000},
            {"game_id": 6, "title": "Dota 2", "rating": 82.0, "price": 0.0, "metacritic_score": 90, "rating_count": 2000000},
        ]

    def test_empty_dataset(self):
        """All algorithms must gracefully handle empty input."""
        for name, algo_func in SORTING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                res = algo_func([], "rating", reverse=False)
                self.assertEqual(res.sorted_data, [])
                self.assertEqual(res.dataset_size, 0)

    def test_single_record(self):
        """All algorithms must handle a single record without errors."""
        single = [{"game_id": 1, "title": "Hades", "rating": 93.0, "price": 24.99}]
        for name, algo_func in SORTING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                res = algo_func(single, "rating", reverse=False)
                self.assertEqual(len(res.sorted_data), 1)
                self.assertEqual(res.sorted_data[0]["title"], "Hades")

    def test_already_sorted_and_reverse_sorted(self):
        """Test on already sorted and reverse-sorted arrays."""
        sorted_asc = sorted(self.sample_games, key=lambda x: x["rating"])
        sorted_desc = sorted(self.sample_games, key=lambda x: x["rating"], reverse=True)

        for name, algo_func in SORTING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                res_asc = algo_func(sorted_asc, "rating", reverse=False)
                ratings_asc = [r["rating"] for r in res_asc.sorted_data]
                self.assertEqual(ratings_asc, sorted(ratings_asc))

                res_desc = algo_func(sorted_desc, "rating", reverse=True)
                ratings_desc = [r["rating"] for r in res_desc.sorted_data]
                self.assertEqual(ratings_desc, sorted(ratings_desc, reverse=True))

    def test_numeric_sorting_correctness(self):
        """Verify that all 8 algorithms correctly sort numbers ascending and descending."""
        for name, algo_func in SORTING_ALGORITHMS.items():
            with self.subTest(algorithm=name):
                # Ascending
                res_asc = algo_func(self.sample_games, "rating", reverse=False)
                vals_asc = [r["rating"] for r in res_asc.sorted_data]
                self.assertEqual(vals_asc, [80.0, 82.0, 95.0, 96.0, 97.0, 98.0])

                # Descending
                res_desc = algo_func(self.sample_games, "rating", reverse=True)
                vals_desc = [r["rating"] for r in res_desc.sorted_data]
                self.assertEqual(vals_desc, [98.0, 97.0, 96.0, 95.0, 82.0, 80.0])

    def test_string_sorting(self):
        """Verify comparison-based algorithms sort strings alphabetically (case-insensitive)."""
        string_algos = ["Insertion Sort", "Selection Sort", "Merge Sort", "Bubble Sort", "Quick Sort"]
        for name in string_algos:
            with self.subTest(algorithm=name):
                res = execute_sort(name, self.sample_games, "title", reverse=False)
                titles = [r["title"] for r in res.sorted_data]
                expected = sorted([r["title"] for r in self.sample_games], key=lambda s: s.casefold())
                self.assertEqual(titles, expected)

    def test_missing_and_none_values(self):
        """Missing/None values must be placed at the end without throwing exceptions."""
        data_with_nulls = [
            {"game_id": 1, "title": "Game A", "rating": 90.0},
            {"game_id": 2, "title": "Game B", "rating": None},
            {"game_id": 3, "title": "Game C", "rating": 75.0},
            {"game_id": 4, "title": "Game D", "rating": None},
            {"game_id": 5, "title": "Game E", "rating": 85.0},
        ]
        for name in ["Insertion Sort", "Selection Sort", "Merge Sort", "Bubble Sort", "Quick Sort", "Counting Sort", "Bucket Sort", "Radix Sort"]:
            with self.subTest(algorithm=name):
                res = execute_sort(name, data_with_nulls, "rating", reverse=False)
                sorted_ratings = [r["rating"] for r in res.sorted_data]
                # Non-None should be [75.0, 85.0, 90.0] followed by two Nones
                self.assertEqual(sorted_ratings[:3], [75.0, 85.0, 90.0])
                self.assertIsNone(sorted_ratings[3])
                self.assertIsNone(sorted_ratings[4])

    def test_negative_numbers_and_zeroes(self):
        """Counting, Bucket, and Radix Sort must correctly handle zero and negative values."""
        data_with_negatives = [
            {"game_id": 1, "title": "A", "price": 0.0},
            {"game_id": 2, "title": "B", "price": -5.0},
            {"game_id": 3, "title": "C", "price": 10.0},
            {"game_id": 4, "title": "D", "price": -15.0},
            {"game_id": 5, "title": "E", "price": 20.0},
        ]
        for name in ["Counting Sort", "Bucket Sort", "Radix Sort", "Merge Sort", "Quick Sort"]:
            with self.subTest(algorithm=name):
                res = execute_sort(name, data_with_negatives, "price", reverse=False)
                prices = [r["price"] for r in res.sorted_data]
                self.assertEqual(prices, [-15.0, -5.0, 0.0, 10.0, 20.0])

    def test_stability_preservation(self):
        """
        Stable algorithms (Insertion, Merge, Bubble, Counting, Bucket, Radix)
        must preserve original order of records having identical keys.
        """
        stable_algorithms = ["Insertion Sort", "Merge Sort", "Bubble Sort", "Counting Sort", "Bucket Sort", "Radix Sort"]
        data_duplicates = [
            {"game_id": 1, "title": "First", "rating": 90.0},
            {"game_id": 2, "title": "Second", "rating": 90.0},
            {"game_id": 3, "title": "Third", "rating": 90.0},
            {"game_id": 4, "title": "Fourth", "rating": 80.0},
            {"game_id": 5, "title": "Fifth", "rating": 90.0},
        ]
        for name in stable_algorithms:
            with self.subTest(algorithm=name):
                res = execute_sort(name, data_duplicates, "rating", reverse=False)
                # First element should be Fourth (80.0)
                self.assertEqual(res.sorted_data[0]["title"], "Fourth")
                # Remaining 4 elements all have rating 90.0 and must preserve First -> Second -> Third -> Fifth
                remaining_titles = [r["title"] for r in res.sorted_data[1:]]
                self.assertEqual(remaining_titles, ["First", "Second", "Third", "Fifth"])

    def test_bubble_sort_early_exit(self):
        """Bubble sort should complete with n-1 comparisons and 0 swaps on already sorted data."""
        data_sorted = [{"game_id": i, "rating": float(i)} for i in range(10)]
        res = bubble_sort(data_sorted, "rating", reverse=False)
        self.assertEqual(res.swaps, 0)
        self.assertEqual(res.comparisons, 9)  # exactly one pass (10 - 1)


if __name__ == "__main__":
    unittest.main()

