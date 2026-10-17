"""
Data model for video game entities.
Contains the Game dataclass with serialization and normalization helpers.
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any
import datetime


@dataclass
class Game:
    game_id: Optional[int] = None
    title: str = ""
    release_date: Optional[str] = None
    developer: Optional[str] = None
    publisher: Optional[str] = None
    genres: Optional[str] = None
    platforms: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    price: Optional[float] = None
    metacritic_score: Optional[int] = None
    multiplayer: Optional[bool] = None
    source: str = "Unknown"
    source_url: Optional[str] = None
    description: Optional[str] = None
    external_id: Optional[str] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert game entity to a clean dictionary."""
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Game":
        """Instantiate a Game from a dictionary, safely casting data types."""
        # Clean and normalize fields
        game_id = data.get("game_id")
        if game_id is not None:
            try:
                game_id = int(game_id)
            except (ValueError, TypeError):
                game_id = None

        title = str(data.get("title", "")).strip() or "Untitled Game"

        release_date = data.get("release_date")
        if release_date:
            release_date = str(release_date).strip()
            # If timestamp integer in milliseconds or seconds
            if release_date.isdigit():
                try:
                    ts = int(release_date)
                    if ts > 10000000000:
                        ts = ts / 1000
                    release_date = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                except Exception:
                    pass

        developer = data.get("developer")
        if developer:
            developer = str(developer).strip() or None

        publisher = data.get("publisher")
        if publisher:
            publisher = str(publisher).strip() or None

        genres = data.get("genres")
        if genres:
            genres = str(genres).strip() or None

        platforms = data.get("platforms")
        if platforms:
            platforms = str(platforms).strip() or None

        rating = data.get("rating")
        if rating is not None and str(rating).strip() != "":
            try:
                rating = round(float(rating), 2)
            except (ValueError, TypeError):
                rating = None
        else:
            rating = None

        rating_count = data.get("rating_count")
        if rating_count is not None and str(rating_count).strip() != "":
            try:
                rating_count = int(float(rating_count))
            except (ValueError, TypeError):
                rating_count = None
        else:
            rating_count = None

        price = data.get("price")
        if price is not None and str(price).strip() != "":
            try:
                price = round(float(price), 2)
            except (ValueError, TypeError):
                price = None
        else:
            price = None

        metacritic_score = data.get("metacritic_score")
        if metacritic_score is not None and str(metacritic_score).strip() != "":
            try:
                metacritic_score = int(float(metacritic_score))
            except (ValueError, TypeError):
                metacritic_score = None
        else:
            metacritic_score = None

        multiplayer = data.get("multiplayer")
        if multiplayer is not None:
            if isinstance(multiplayer, bool):
                pass
            elif str(multiplayer).lower() in ("1", "true", "yes"):
                multiplayer = True
            elif str(multiplayer).lower() in ("0", "false", "no"):
                multiplayer = False
            else:
                multiplayer = None

        source = str(data.get("source", "Unknown")).strip()
        source_url = data.get("source_url")
        if source_url:
            source_url = str(source_url).strip() or None

        description = data.get("description")
        if description:
            description = str(description).strip() or None

        external_id = data.get("external_id")
        if external_id is not None:
            external_id = str(external_id).strip() or None

        created_at = data.get("created_at")
        if not created_at:
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return cls(
            game_id=game_id,
            title=title,
            release_date=release_date,
            developer=developer,
            publisher=publisher,
            genres=genres,
            platforms=platforms,
            rating=rating,
            rating_count=rating_count,
            price=price,
            metacritic_score=metacritic_score,
            multiplayer=multiplayer,
            source=source,
            source_url=source_url,
            description=description,
            external_id=external_id,
            created_at=created_at,
        )

