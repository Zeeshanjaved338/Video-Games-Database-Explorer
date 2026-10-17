"""
Database schema definition and SQLite initialization for Video Game Database Explorer.
"""

import sqlite3
import os
from typing import Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "games.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS games (
    game_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    release_date TEXT,
    developer TEXT,
    publisher TEXT,
    genres TEXT,
    platforms TEXT,
    rating REAL,
    rating_count INTEGER,
    price REAL,
    metacritic_score INTEGER,
    multiplayer INTEGER,
    source TEXT NOT NULL,
    source_url TEXT,
    description TEXT,
    external_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_games_title ON games(title);
CREATE INDEX IF NOT EXISTS idx_games_rating ON games(rating);
CREATE INDEX IF NOT EXISTS idx_games_price ON games(price);
CREATE INDEX IF NOT EXISTS idx_games_release_date ON games(release_date);
CREATE INDEX IF NOT EXISTS idx_games_metacritic ON games(metacritic_score);
CREATE INDEX IF NOT EXISTS idx_games_source ON games(source);
CREATE UNIQUE INDEX IF NOT EXISTS idx_games_source_extid ON games(source, external_id) WHERE external_id IS NOT NULL;
"""


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates and returns a connection to the SQLite database with row factory."""
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high concurrency between reader threads and scraper thread
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn


def init_database(db_path: Optional[str] = None) -> None:
    """Initialize database tables and indexes."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript(SCHEMA_SQL)
    finally:
        conn.close()

