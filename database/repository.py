"""
Repository layer for game data storage, deduplication, queries, and statistics.
"""

import sqlite3
import datetime
from typing import List, Optional, Dict, Any, Tuple
from models.game import Game
from database.schema import get_connection, init_database, DEFAULT_DB_PATH


class GameRepository:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        init_database(self.db_path)

    def insert_game(self, game: Game) -> Optional[int]:
        """
        Inserts a single game with duplicate checks.
        Returns game_id if inserted, or None if skipped as duplicate.
        """
        conn = get_connection(self.db_path)
        try:
            with conn:
                # 1. Check external_id + source duplicate
                if game.external_id:
                    cursor = conn.execute(
                        "SELECT game_id FROM games WHERE source = ? AND external_id = ?",
                        (game.source, str(game.external_id))
                    )
                    row = cursor.fetchone()
                    if row:
                        return None

                # 2. Check title + developer duplicate fallback
                cursor = conn.execute(
                    "SELECT game_id FROM games WHERE LOWER(title) = LOWER(?) AND (LOWER(developer) = LOWER(?) OR (developer IS NULL AND ? IS NULL))",
                    (game.title, game.developer or "", game.developer)
                )
                if cursor.fetchone():
                    return None

                # Insert
                multiplayer_val = None
                if game.multiplayer is not None:
                    multiplayer_val = 1 if game.multiplayer else 0

                created_at_val = game.created_at or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                cur = conn.execute(
                    """
                    INSERT INTO games (
                        title, release_date, developer, publisher, genres, platforms,
                        rating, rating_count, price, metacritic_score, multiplayer,
                        source, source_url, description, external_id, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        game.title, game.release_date, game.developer, game.publisher,
                        game.genres, game.platforms, game.rating, game.rating_count,
                        game.price, game.metacritic_score, multiplayer_val,
                        game.source, game.source_url, game.description, game.external_id,
                        created_at_val
                    )
                )
                return cur.lastrowid
        finally:
            conn.close()

    def insert_games_batch(self, games: List[Game]) -> Tuple[int, int]:
        """
        Batch inserts games in a single transaction for maximum speed.
        Returns (inserted_count, duplicate_count).
        """
        conn = get_connection(self.db_path)
        inserted = 0
        duplicates = 0
        try:
            with conn:
                for game in games:
                    # Quick duplicate check
                    if game.external_id:
                        cur = conn.execute(
                            "SELECT 1 FROM games WHERE source = ? AND external_id = ? LIMIT 1",
                            (game.source, str(game.external_id))
                        )
                        if cur.fetchone():
                            duplicates += 1
                            continue

                    cur = conn.execute(
                        "SELECT 1 FROM games WHERE LOWER(title) = LOWER(?) LIMIT 1",
                        (game.title,)
                    )
                    if cur.fetchone():
                        duplicates += 1
                        continue

                    multiplayer_val = 1 if game.multiplayer else (0 if game.multiplayer is False else None)
                    created_at_val = game.created_at or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    conn.execute(
                        """
                        INSERT INTO games (
                            title, release_date, developer, publisher, genres, platforms,
                            rating, rating_count, price, metacritic_score, multiplayer,
                            source, source_url, description, external_id, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            game.title, game.release_date, game.developer, game.publisher,
                            game.genres, game.platforms, game.rating, game.rating_count,
                            game.price, game.metacritic_score, multiplayer_val,
                            game.source, game.source_url, game.description, game.external_id,
                            created_at_val
                        )
                    )
                    inserted += 1
            return inserted, duplicates
        finally:
            conn.close()

    def get_game_by_id(self, game_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single game by internal game_id."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.execute("SELECT * FROM games WHERE game_id = ?", (game_id,))
            row = cur.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all_games(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """Retrieve all games as a list of dictionaries."""
        conn = get_connection(self.db_path)
        try:
            if limit is not None:
                cur = conn.execute(
                    "SELECT * FROM games ORDER BY game_id ASC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            else:
                cur = conn.execute("SELECT * FROM games ORDER BY game_id ASC")
            return [dict(row) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_total_count(self) -> int:
        """Returns the total number of distinct games in the database."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.execute("SELECT COUNT(*) FROM games")
            return cur.fetchone()[0]
        finally:
            conn.close()

    def get_source_statistics(self) -> Dict[str, int]:
        """Returns count of games grouped by data source."""
        conn = get_connection(self.db_path)
        try:
            cur = conn.execute("SELECT source, COUNT(*) as cnt FROM games GROUP BY source ORDER BY cnt DESC")
            return {row["source"]: row["cnt"] for row in cur.fetchall()}
        finally:
            conn.close()

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Computes key analytics: total games, averages, ranges, and genre counts."""
        conn = get_connection(self.db_path)
        try:
            stats: Dict[str, Any] = {}
            cur = conn.execute("""
                SELECT 
                    COUNT(*) as total,
                    ROUND(AVG(rating), 2) as avg_rating,
                    ROUND(AVG(price), 2) as avg_price,
                    ROUND(AVG(metacritic_score), 2) as avg_metacritic,
                    MAX(rating) as max_rating,
                    MIN(price) as min_price,
                    MAX(price) as max_price
                FROM games
            """)
            row = dict(cur.fetchone())
            stats.update(row)

            # Top genres breakdown
            cur_genres = conn.execute("SELECT genres FROM games WHERE genres IS NOT NULL AND genres != ''")
            genre_counts: Dict[str, int] = {}
            for g_row in cur_genres.fetchall():
                parts = [p.strip() for p in g_row[0].replace("/", ",").split(",") if p.strip()]
                for p in parts:
                    genre_counts[p] = genre_counts.get(p, 0) + 1

            # Sort top 8 genres
            sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:8]
            stats["top_genres"] = sorted_genres

            # Release years breakdown
            cur_years = conn.execute("""
                SELECT SUBSTR(release_date, 1, 4) as r_year, COUNT(*) as cnt
                FROM games
                WHERE release_date IS NOT NULL AND LENGTH(release_date) >= 4 AND r_year GLOB '[1-2][0-9][0-9][0-9]'
                GROUP BY r_year
                ORDER BY r_year DESC
                LIMIT 10
            """)
            stats["year_distribution"] = {r["r_year"]: r["cnt"] for r in cur_years.fetchall()}

            return stats
        finally:
            conn.close()

    def delete_game(self, game_id: int) -> bool:
        """Deletes a game by ID."""
        conn = get_connection(self.db_path)
        try:
            with conn:
                cur = conn.execute("DELETE FROM games WHERE game_id = ?", (game_id,))
                return cur.rowcount > 0
        finally:
            conn.close()

    def clear_all(self) -> None:
        """Clears all records from the games table."""
        conn = get_connection(self.db_path)
        try:
            with conn:
                conn.execute("DELETE FROM games")
                conn.execute("DELETE FROM sqlite_sequence WHERE name='games'")
        finally:
            conn.close()
