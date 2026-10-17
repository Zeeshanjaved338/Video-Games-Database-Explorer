"""
Database package for Video Game Database Explorer.
"""
from database.schema import init_database, get_connection, DEFAULT_DB_PATH
from database.repository import GameRepository

__all__ = ["init_database", "get_connection", "DEFAULT_DB_PATH", "GameRepository"]

