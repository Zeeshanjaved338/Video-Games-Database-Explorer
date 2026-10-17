"""
Unit tests for scraping, URL validation, SSRF security, and deduplication.
"""

import unittest
from scraper.url_scraper import URLScraper
from database.repository import GameRepository
from models.game import Game
import os
import tempfile


class TestScraper(unittest.TestCase):
    def test_ssrf_protection_private_and_loopback(self):
        """URLScraper must reject local, private, and loopback IP addresses for SSRF protection."""
        bad_urls = [
            "http://localhost:8080/test",
            "http://127.0.0.1/secret",
            "http://127.0.0.2:5000",
            "http://192.168.1.1/admin",
            "http://10.0.0.1/internal",
            "http://169.254.169.254/latest/meta-data/",  # AWS metadata service
            "ftp://example.com/game",  # Invalid protocol
            "javascript:alert(1)",     # XSS / non-http
            "",                        # Empty
        ]
        for url in bad_urls:
            with self.subTest(url=url):
                valid, msg = URLScraper.validate_url(url)
                self.assertFalse(valid)
                self.assertTrue(len(msg) > 0)

    def test_valid_public_urls(self):
        """URLScraper should permit valid public HTTP/HTTPS URLs."""
        valid_urls = [
            "https://store.steampowered.com/app/570/Dota_2/",
            "https://www.freetogame.com/open/overwatch-2",
            "https://www.google.com"
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                valid, msg = URLScraper.validate_url(url)
                self.assertTrue(valid)

    def test_incremental_deduplication(self):
        """Repository must detect duplicate external IDs and titles."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            temp_db_path = f.name

        try:
            repo = GameRepository(temp_db_path)
            g1 = Game(title="Cyberpunk 2077", external_id="1091500", source="SteamSpy")
            id1 = repo.insert_game(g1)
            self.assertIsNotNone(id1)

            # Insert exact duplicate external_id + source
            g2 = Game(title="Cyberpunk 2077 (Duplicate)", external_id="1091500", source="SteamSpy")
            id2 = repo.insert_game(g2)
            self.assertIsNone(id2)  # skipped as duplicate!

            # Insert duplicate title
            g3 = Game(title="Cyberpunk 2077", external_id="9999999", source="Other")
            id3 = repo.insert_game(g3)
            self.assertIsNone(id3)  # skipped as duplicate title!

            # Insert unique game
            g4 = Game(title="Witcher 3", external_id="292030", source="SteamSpy")
            id4 = repo.insert_game(g4)
            self.assertIsNotNone(id4)

            self.assertEqual(repo.get_total_count(), 2)
        finally:
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)


if __name__ == "__main__":
    unittest.main()

