from __future__ import annotations
"""Photo Scout Agent — finds professional reference photos from the web."""

from mcp_servers.web_search import WebSearchMCP
from mcp_servers.image_analysis import ImageAnalysisMCP
from config import config


class PhotoScoutAgent:
    """Agent that analyzes the user's photo and finds similar professional
    photos from the web to use as composition/lighting references.

    MCP servers used:
        - Image Analysis MCP (analyze the user's photo)
        - Web Search MCP (search + download references)
    """

    def __init__(self):
        self.search = WebSearchMCP()
        self.analysis = ImageAnalysisMCP()

    async def find_references(
        self,
        user_photo_path: str,
        vibe: str | None = None,
        count: int | None = None,
    ) -> list[str]:
        """Analyze the user's photo and find matching professional references.

        Args:
            user_photo_path: Path to the user's uploaded photo
            vibe: Optional vibe/scene (e.g. "coffee_shop", "outdoors")
            count: Number of references to find (defaults to config)

        Returns:
            List of local file paths to downloaded reference images
        """
        count = count or config.NUM_SCOUT_REFS

        # Step 1: Analyze the user's photo to understand what to search for
        print("     📸 Analyzing photo characteristics...")
        analysis = await self.analysis.analyze_photo(user_photo_path)

        # Step 2: Build search query
        if vibe:
            # Vibe mode: search for the specific vibe/setting
            query = f"professional portrait {vibe} {analysis.get('gender', '')} photography"
        else:
            # Enhance mode: use the AI-generated search query
            query = analysis.get(
                "search_query",
                f"professional portrait {analysis.get('setting', '')} photography"
            )

        print(f"     🔍 Searching: \"{query}\"")

        # Step 3: Search for matching photos
        search_results = await self.search.search_images(
            query=query, count=count + 2  # fetch extras in case some fail to download
        )

        if not search_results:
            print("     ⚠️ No search results found, using photo as-is")
            return []

        # Step 4: Download the top matches
        downloaded = []
        for result in search_results:
            if len(downloaded) >= count:
                break
            path = await self.search.download_image(result["url"])
            if path:
                downloaded.append(path)
                src = result.get("source", "web")
                photographer = result.get("photographer", "unknown")
                print(f"     ✅ Ref {len(downloaded)}: {src} by {photographer}")

        # Also store the analysis for the Prompt Architect to use
        self._last_analysis = analysis

        return downloaded

    @property
    def last_analysis(self) -> dict:
        """Get the analysis from the most recent find_references call."""
        return getattr(self, "_last_analysis", {})
