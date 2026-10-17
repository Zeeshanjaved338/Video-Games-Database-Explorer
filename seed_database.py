"""
Database Seeder Script for Video Game Database Explorer.

Collects and populates at least 15,000 distinct video game records from legitimate
sources (SteamSpy, FreeToGame, and CheapShark) into the persistent SQLite database.
"""

import sys
import os
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.repository import GameRepository
from scraper.steamspy_scraper import SteamSpyScraper
from scraper.freetogame_scraper import FreeToGameScraper
from scraper.cheapshark_scraper import CheapSharkScraper


def seed_database(target_records: int = 15000, db_path: str = None):
    print(f"=== Video Game Database Explorer: Data Seeder ===")
    repo = GameRepository(db_path)
    current_count = repo.get_total_count()
    print(f"Initial unique records in database: {current_count:,}")

    if current_count >= target_records:
        print(f"[✓] Database already contains {current_count:,} records (>= target of {target_records:,}). Seeding skipped.")
        return current_count

    total_added = 0
    total_dupes = 0
    start_time = time.time()

    # 1. FreeToGame
    print("\n[1/3] Fetching curated titles from FreeToGame API...")
    try:
        ftg = FreeToGameScraper(rate_limit_sec=0.2)
        ftg_games = ftg.fetch_all()
        added, dupes = repo.insert_games_batch(ftg_games)
        total_added += added
        total_dupes += dupes
        print(f"      + Added: {added:,} games (Duplicates skipped: {dupes:,})")
    except Exception as e:
        print(f"      [!] FreeToGame notice: {e}")

    # 2. CheapShark
    print("\n[2/3] Fetching deals from CheapShark API...")
    try:
        cs = CheapSharkScraper(rate_limit_sec=0.2)
        for page in range(5):
            cs_games = cs.fetch_page(page_num=page, page_size=60)
            if not cs_games:
                break
            added, dupes = repo.insert_games_batch(cs_games)
            total_added += added
            total_dupes += dupes
            print(f"      Page {page + 1}: +{added} games")
    except Exception as e:
        print(f"      [!] CheapShark notice: {e}")

    # 3. SteamSpy
    print(f"\n[3/3] Fetching 1,000-game pages from SteamSpy API to reach target of {target_records:,}...")
    spy = SteamSpyScraper(rate_limit_sec=0.4)
    page = 0
    while repo.get_total_count() < target_records and page < 30:
        try:
            print(f"      Requesting SteamSpy page {page}... ", end="", flush=True)
            t0 = time.time()
            spy_games = spy.fetch_page(page)
            t_fetch = round(time.time() - t0, 2)
            if not spy_games:
                print("0 records returned.")
                break

            added, dupes = repo.insert_games_batch(spy_games)
            total_added += added
            total_dupes += dupes
            cur = repo.get_total_count()
            print(f"fetched {len(spy_games)} in {t_fetch}s -> +{added} new (Total in DB: {cur:,})")
            page += 1
        except Exception as e:
            print(f"Error on page {page}: {e}")
            page += 1
            time.sleep(1)

    elapsed = round(time.time() - start_time, 2)
    final_count = repo.get_total_count()
    print(f"\n=======================================================")
    print(f"Seeding Complete in {elapsed}s!")
    print(f"Total Unique Games in Database: {final_count:,}")
    print(f"Newly Added: {total_added:,}")
    print(f"Duplicates Filtered Out: {total_dupes:,}")
    print(f"=======================================================")
    return final_count


if __name__ == "__main__":
    target = 15000
    if len(sys.argv) > 1:
        try:
            target = int(sys.argv[1])
        except ValueError:
            pass
    seed_database(target)

