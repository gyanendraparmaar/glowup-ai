from __future__ import annotations
"""Web Search MCP Server — searches Unsplash and Pexels for reference photos."""

import httpx
import os
import hashlib
from config import config


class WebSearchMCP:
    """MCP-style tool server for searching and downloading reference images."""

    def __init__(self):
        self.unsplash_key = config.UNSPLASH_API_KEY
        self.pexels_key = config.PEXELS_API_KEY
        self.cache_dir = os.path.join(config.OUTPUT_DIR, "_ref_cache")
        os.makedirs(self.cache_dir, exist_ok=True)

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
            except Exception as e:
                print(f"  ⚠️ Unsplash search failed: {e}")

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
                    for photo in data.get("photos", []):
                        results.append({
                            "url": photo["src"]["large"],
                            "thumbnail": photo["src"]["small"],
                            "description": photo.get("alt", ""),
                            "source": "pexels",
                            "photographer": photo.get("photographer", ""),
                        })
            except Exception as e:
                print(f"  ⚠️ Pexels search failed: {e}")

        return results[:count]

    async def download_image(self, url: str) -> str | None:
        """Download an image from URL to local cache. Returns local file path."""
        # Use URL hash as filename to avoid re-downloading
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        local_path = os.path.join(self.cache_dir, f"ref_{url_hash}.jpg")

        if os.path.exists(local_path):
            return local_path

        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(resp.content)
                return local_path
        except Exception as e:
            print(f"  ⚠️ Download failed for {url[:60]}...: {e}")
            return None
