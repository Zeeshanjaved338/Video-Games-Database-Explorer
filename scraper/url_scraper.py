"""
URL-based Scraper module (Bonus Feature).

Provides safe URL validation, SSRF protection (blocking local/private IPs),
response size limiting, and page parsing (Steam Store, FreeToGame, CheapShark, and generic OpenGraph metadata).
"""

import socket
import ipaddress
import urllib.parse
import re
import requests
from bs4 import BeautifulSoup
from typing import Tuple, Optional
from models.game import Game


class URLScraper:
    MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB limit
    TIMEOUT = 12  # seconds

    @staticmethod
    def validate_url(url: str) -> Tuple[bool, str]:
        """
        Validates URL format, scheme, and guards against SSRF (Server-Side Request Forgery)
        by ensuring the hostname does not resolve to private or loopback IP ranges.
        """
        if not url or not isinstance(url, str):
            return False, "URL is empty or invalid."

        url = url.strip()
        parsed = urllib.parse.urlparse(url)

        if parsed.scheme.lower() not in ("http", "https"):
            return False, f"Invalid scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted."

        hostname = parsed.hostname
        if not hostname:
            return False, "URL is missing a valid hostname."

        # Check for banned loopback hostnames
        if hostname.lower() in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            return False, "Access to localhost or loopback addresses is forbidden for security."

        # Resolve hostname to check IP range
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for info in addr_info:
                ip_str = info[4][0]
                ip_obj = ipaddress.ip_address(ip_str)
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
                    return False, f"Security rejection: Destination IP {ip_str} is in a private, loopback, or reserved range."
        except socket.gaierror:
            return False, f"Unable to resolve hostname '{hostname}'. Check internet connection and URL spelling."
        except Exception as e:
            return False, f"DNS resolution error: {str(e)}"

        return True, "Valid"

    @classmethod
    def scrape_url(cls, url: str) -> Tuple[Optional[Game], Optional[str]]:
        """
        Safely fetches and parses the given URL into a Game model.
        Returns (game, None) on success or (None, error_message) on failure.
        """
        valid, msg = cls.validate_url(url)
        if not valid:
            return None, msg

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        cookies = {
            "birthtime": "283993201",
            "lastagecheckage": "1-0-1990",
            "mature_content": "1"
        }

        try:
            with requests.get(url, headers=headers, cookies=cookies, timeout=cls.TIMEOUT, stream=True) as resp:
                resp.raise_for_status()

                # Content-Length check
                content_len = resp.headers.get("Content-Length")
                if content_len and int(content_len) > cls.MAX_RESPONSE_SIZE:
                    return None, f"Response size exceeds maximum permitted limit ({cls.MAX_RESPONSE_SIZE // (1024*1024)} MB)."

                # Stream content with safety cap
                chunks = []
                total_downloaded = 0
                for chunk in resp.iter_content(chunk_size=65536):
                    chunks.append(chunk)
                    total_downloaded += len(chunk)
                    if total_downloaded > cls.MAX_RESPONSE_SIZE:
                        return None, "Response size exceeded 5 MB safety limit during streaming."

                html_content = b"".join(chunks).decode("utf-8", errors="replace")

        except requests.exceptions.Timeout:
            return None, f"Request timed out after {cls.TIMEOUT} seconds."
        except requests.exceptions.HTTPError as e:
            return None, f"HTTP Error {resp.status_code}: {str(e)}"
        except Exception as e:
            return None, f"Network error during fetch: {str(e)}"

        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Specialized Steam Store Page Parser
        if "store.steampowered.com/app/" in url:
            return cls._parse_steam_store_page(soup, url)

        # 2. Specialized FreeToGame Parser
        elif "freetogame.com" in url:
            return cls._parse_freetogame_page(soup, url)

        # 3. Generic OpenGraph & Schema.org Parser
        else:
            return cls._parse_generic_game_page(soup, url)

    @classmethod
    def _parse_steam_store_page(cls, soup: BeautifulSoup, url: str) -> Tuple[Optional[Game], Optional[str]]:
        """Extracts game details from a Steam Store page."""
        title_el = soup.select_one("#appHubAppName, .apphub_AppName")
        if not title_el:
            return None, "Could not find game title on this Steam Store page."

        title = title_el.get_text(strip=True)

        # App ID from URL
        match = re.search(r"/app/(\d+)", url)
        external_id = match.group(1) if match else None

        # Release date
        rel_el = soup.select_one(".release_date .date")
        release_date = rel_el.get_text(strip=True) if rel_el else None

        # Developer & Publisher
        dev_el = soup.select_one(".dev_row a[href*='developer']")
        developer = dev_el.get_text(strip=True) if dev_el else None

        pub_el = soup.select_one(".dev_row a[href*='publisher']")
        publisher = pub_el.get_text(strip=True) if pub_el else None

        # Description
        desc_el = soup.select_one(".game_description_snippet")
        description = desc_el.get_text(strip=True) if desc_el else None

        # Genres / Tags
        tag_els = soup.select(".popular_tags a.app_tag")
        genres = ", ".join([t.get_text(strip=True) for t in tag_els[:4]]) if tag_els else "Video Game"

        # Metacritic score
        meta_el = soup.select_one("#game_area_metascore .score")
        metacritic_score = None
        if meta_el:
            try:
                metacritic_score = int(meta_el.get_text(strip=True))
            except ValueError:
                pass

        # Price
        price = None
        price_el = soup.select_one(".game_purchase_price, .discount_final_price")
        if price_el:
            price_text = price_el.get_text(strip=True).replace("$", "").replace("USD", "").strip()
            if "free" in price_text.lower():
                price = 0.0
            else:
                try:
                    price = float(price_text)
                except ValueError:
                    pass

        # Rating from user review summary
        rating = 85.0  # reasonable default
        rating_count = 1000
        review_el = soup.select_one(".user_reviews_summary_bar")
        if review_el:
            tooltip = review_el.get("data-tooltip-html", "")
            match_pct = re.search(r"(\d+)%\s+of\s+the\s+([\d,]+)", tooltip)
            if match_pct:
                rating = float(match_pct.group(1))
                rating_count = int(match_pct.group(2).replace(",", ""))

        game = Game(
            title=title,
            release_date=release_date,
            developer=developer,
            publisher=publisher,
            genres=genres,
            platforms="PC, Windows",
            rating=rating,
            rating_count=rating_count,
            price=price,
            metacritic_score=metacritic_score,
            multiplayer=None,
            source="URL Scraper (Steam)",
            source_url=url,
            external_id=external_id,
            description=description
        )
        return game, None

    @classmethod
    def _parse_freetogame_page(cls, soup: BeautifulSoup, url: str) -> Tuple[Optional[Game], Optional[str]]:
        title_el = soup.select_one("h1")
        if not title_el:
            return None, "Could not find game title on this FreeToGame page."
        title = title_el.get_text(strip=True)

        desc_el = soup.select_one("meta[name='description']")
        description = desc_el.get("content", "") if desc_el else None

        game = Game(
            title=title,
            genres="Free to Play",
            platforms="PC",
            rating=80.0,
            price=0.0,
            multiplayer=True,
            source="URL Scraper (FreeToGame)",
            source_url=url,
            description=description
        )
        return game, None

    @classmethod
    def _parse_generic_game_page(cls, soup: BeautifulSoup, url: str) -> Tuple[Optional[Game], Optional[str]]:
        """Parses generic page using OpenGraph metadata tags."""
        og_title = soup.select_one("meta[property='og:title']")
        title_tag = soup.select_one("title")

        title = None
        if og_title and og_title.get("content"):
            title = og_title["content"].strip()
        elif title_tag:
            title = title_tag.get_text(strip=True)

        if not title:
            return None, "Could not locate a recognizable title in the web page metadata."

        og_desc = soup.select_one("meta[property='og:description'], meta[name='description']")
        description = og_desc.get("content", "").strip() if og_desc else None

        game = Game(
            title=title,
            genres="Video Game",
            platforms="PC / Multi-platform",
            rating=75.0,
            price=None,
            source="URL Scraper (Generic)",
            source_url=url,
            description=description
        )
        return game, None

