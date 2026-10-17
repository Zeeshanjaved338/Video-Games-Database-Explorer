"""
Unit tests for searching and composite filtering.
Tests text operators, numeric comparisons, date filtering, AND/OR logic, and NOT negation.
"""

import unittest
from algorithms.searching import apply_composite_filters, evaluate_condition, BUILTIN_PRESETS
from models.filter_sort import FilterCondition, FilterGroup


class TestSearchingAndFiltering(unittest.TestCase):
    def setUp(self):
        self.games = [
            {"game_id": 1, "title": "The Witcher 3: Wild Hunt", "genres": "RPG, Action", "rating": 96.0, "price": 39.99, "release_date": "2015-05-19", "multiplayer": False},
            {"game_id": 2, "title": "Grand Theft Auto V", "genres": "Action, Adventure", "rating": 95.0, "price": 29.99, "release_date": "2013-09-17", "multiplayer": True},
            {"game_id": 3, "title": "Cyberpunk 2077", "genres": "RPG, Sci-Fi", "rating": 82.0, "price": 59.99, "release_date": "2020-12-10", "multiplayer": False},
            {"game_id": 4, "title": "Apex Legends", "genres": "Action, Shooter", "rating": 80.0, "price": 0.0, "release_date": "2019-02-04", "multiplayer": True},
            {"game_id": 5, "title": "Portal", "genres": "Puzzle", "rating": 90.0, "price": 9.99, "release_date": "2007-10-10", "multiplayer": False},
            {"game_id": 6, "title": "Unknown Title", "genres": None, "rating": None, "price": None, "release_date": None, "multiplayer": None},
        ]

    def test_text_operators(self):
        """Test contains, not_contains, starts_with, ends_with, equals."""
        # contains
        cond1 = FilterCondition(column="title", operator="contains", value="Witcher")
        res1 = apply_composite_filters(self.games, FilterGroup("AND", [cond1]))
        self.assertEqual(len(res1), 1)
        self.assertEqual(res1[0]["game_id"], 1)

        # starts_with
        cond2 = FilterCondition(column="title", operator="starts_with", value="Grand")
        res2 = apply_composite_filters(self.games, FilterGroup("AND", [cond2]))
        self.assertEqual(len(res2), 1)
        self.assertEqual(res2[0]["game_id"], 2)

        # ends_with
        cond3 = FilterCondition(column="title", operator="ends_with", value="2077")
        res3 = apply_composite_filters(self.games, FilterGroup("AND", [cond3]))
        self.assertEqual(len(res3), 1)
        self.assertEqual(res3[0]["game_id"], 3)

        # not_contains
        cond4 = FilterCondition(column="genres", operator="not_contains", value="RPG")
        res4 = apply_composite_filters(self.games, FilterGroup("AND", [cond4]))
        titles = [g["title"] for g in res4]
        self.assertNotIn("The Witcher 3: Wild Hunt", titles)
        self.assertNotIn("Cyberpunk 2077", titles)

    def test_numeric_operators(self):
        """Test equals, gt, lt, gte, lte, between."""
        # gt
        cond1 = FilterCondition(column="rating", operator="gt", value=92.0)
        res1 = apply_composite_filters(self.games, FilterGroup("AND", [cond1]))
        self.assertEqual([g["game_id"] for g in res1], [1, 2])

        # lte
        cond2 = FilterCondition(column="price", operator="lte", value=10.0)
        res2 = apply_composite_filters(self.games, FilterGroup("AND", [cond2]))
        # Apex Legends (0.0) and Portal (9.99)
        self.assertEqual(set(g["game_id"] for g in res2), {4, 5})

        # between
        cond3 = FilterCondition(column="price", operator="between", value=20.0, value2=40.0)
        res3 = apply_composite_filters(self.games, FilterGroup("AND", [cond3]))
        # The Witcher 3 ($39.99) and GTA V ($29.99)
        self.assertEqual(set(g["game_id"] for g in res3), {1, 2})

    def test_date_operators(self):
        """Test before, after, between date filters."""
        # after
        cond1 = FilterCondition(column="release_date", operator="after", value="2018-01-01")
        res1 = apply_composite_filters(self.games, FilterGroup("AND", [cond1]))
        # Cyberpunk (2020) and Apex Legends (2019)
        self.assertEqual(set(g["game_id"] for g in res1), {3, 4})

        # before
        cond2 = FilterCondition(column="release_date", operator="before", value="2010-01-01")
        res2 = apply_composite_filters(self.games, FilterGroup("AND", [cond2]))
        # Portal (2007)
        self.assertEqual([g["game_id"] for g in res2], [5])

    def test_composite_and_or_not(self):
        """Test composite AND, OR, and condition-level NOT negation."""
        # AND: rating >= 90 AND price <= 10.0
        c1 = FilterCondition(column="rating", operator="gte", value=90.0)
        c2 = FilterCondition(column="price", operator="lte", value=10.0)
        group_and = FilterGroup(logical_op="AND", conditions=[c1, c2])
        res_and = apply_composite_filters(self.games, group_and)
        # Portal (90.0, $9.99)
        self.assertEqual([g["game_id"] for g in res_and], [5])

        # OR: genres contains "RPG" OR multiplayer is True
        c3 = FilterCondition(column="genres", operator="contains", value="RPG")
        c4 = FilterCondition(column="multiplayer", operator="equals", value=True)
        group_or = FilterGroup(logical_op="OR", conditions=[c3, c4])
        res_or = apply_composite_filters(self.games, group_or)
        # Witcher 3 (RPG), Cyberpunk (RPG), GTA V (multiplayer), Apex Legends (multiplayer)
        self.assertEqual(set(g["game_id"] for g in res_or), {1, 2, 3, 4})

        # NOT negation: NOT (genres contains "Action")
        c5 = FilterCondition(column="genres", operator="contains", value="Action", is_negated=True)
        group_not = FilterGroup(logical_op="AND", conditions=[c5])
        res_not = apply_composite_filters(self.games, group_not)
        titles = [g["title"] for g in res_not]
        self.assertIn("Cyberpunk 2077", titles)
        self.assertIn("Portal", titles)
        self.assertNotIn("The Witcher 3: Wild Hunt", titles)
        self.assertNotIn("Grand Theft Auto V", titles)


if __name__ == "__main__":
    unittest.main()

