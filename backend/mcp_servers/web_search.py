from __future__ import annotations
"""Web Search MCP Server — searches Unsplash and Pexels for reference photos."""

import hashlib
import logging
import os
import httpx
from config import config

logger = logging.getLogger("glowup.web_search")


class WebSearchMCP:
    """MCP-style tool server for searching and downloading reference images."""

    def __init__(self):
        self.unsplash_key = config.UNSPLASH_API_KEY
        self.pexels_key = config.PEXELS_API_KEY
        self.cache_dir = os.path.join(config.OUTPUT_DIR, "_ref_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

    def _evict_cache_if_needed(self):
        """Remove oldest cached files when cache exceeds max entries."""
        try:
            cached_files = []
            for f in os.listdir(self.cache_dir):
                fpath = os.path.join(self.cache_dir, f)
                if os.path.isfile(fpath):
                    cached_files.append((fpath, os.path.getmtime(fpath)))

            if len(cached_files) <= config.REF_CACHE_MAX_ENTRIES:
                return

            # Sort by modification time (oldest first) and remove excess
            cached_files.sort(key=lambda x: x[1])
            to_remove = len(cached_files) - config.REF_CACHE_MAX_ENTRIES
            for fpath, _ in cached_files[:to_remove]:
                os.remove(fpath)

            logger.info("cache.eviction removed=%d remaining=%d", to_remove, config.REF_CACHE_MAX_ENTRIES)
        except Exception as e:
            logger.warning("cache.eviction_failed error=%s", str(e))

    async def search_images(
        self,
        query: str,
        count: int = 5,
        orientation: str = "portrait",
    ) -> list[dict]:
        """Search for professional photos matching a description.

        Tries Unsplash first, falls back to Pexels.
        Returns list of {url, thumbnail, description, source, photographer}.
        """
        results = []

        # --- Unsplash ---
        if self.unsplash_key:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        "https://api.unsplash.com/search/photos",
                        params={
                            "query": query,
                            "per_page": count,
                            "orientation": orientation,
                        },
                        headers={
                            "Authorization": f"Client-ID {self.unsplash_key}"
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    for photo in data.get("results", []):
                        results.append({
                            "url": photo["urls"]["regular"],
                            "thumbnail": photo["urls"]["thumb"],
                            "description": photo.get("alt_description", ""),
                            "source": "unsplash",
                            "photographer": photo["user"]["name"],
                        })
                    logger.info("unsplash.search query=%s results=%d", query[:50], len(results))
            except Exception as e:
                logger.warning("unsplash.search_failed query=%s error=%s", query[:50], str(e))

        # --- Pexels (fallback / supplement) ---
        if self.pexels_key and len(results) < count:
            needed = count - len(results)
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    resp = await client.get(
                        "https://api.pexels.com/v1/search",
                        params={
                            "query": query,
                            "per_page": needed,
                            "orientation": orientation,
                        },
                        headers={"Authorization": self.pexels_key},
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    pexels_count = 0
                    for photo in data.get("photos", []):
                        results.append({
                            "url": photo["src"]["large"],
                            "thumbnail": photo["src"]["small"],
                            "description": photo.get("alt", ""),
                            "source": "pexels",
                            "photographer": photo.get("photographer", ""),
                        })
                        pexels_count += 1
                    logger.info("pexels.search query=%s results=%d", query[:50], pexels_count)
            except Exception as e:
                logger.warning("pexels.search_failed query=%s error=%s", query[:50], str(e))

        return results[:count]

    async def download_image(self, url: str) -> str | None:
        """Download an image from URL to local cache. Returns local file path."""
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        local_path = os.path.join(self.cache_dir, f"ref_{url_hash}.jpg")

        if os.path.exists(local_path):
            return local_path

        # Evict old entries before adding new ones
        self._evict_cache_if_needed()

        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                return local_path
        except Exception as e:
            logger.warning("download_failed url=%s error=%s", url[:60], str(e))
            return None
