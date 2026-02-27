from __future__ import annotations
"""Prompt Library MCP Server — stores and retrieves successful prompt patterns."""

import json
import os
import hashlib
from config import config


class PromptLibraryMCP:
    """MCP-style tool server for managing prompt patterns.

    Uses a local JSON file as the store for the demo.
    Stores prompts that produced PASS results so the pipeline improves over time.
    """

    def __init__(self):
        self.db_path = config.PROMPT_LIBRARY_PATH
        self._ensure_db()

    def _ensure_db(self):
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({"prompts": [], "patterns": {}}, f, indent=2)

    def _load(self) -> dict:
        with open(self.db_path, "r") as f:
            return json.load(f)

    def _save(self, data: dict):
        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

    async def get_successful_prompts(
        self, scenario: str = "", limit: int = 3
    ) -> list[dict]:
        """Retrieve prompts that previously produced PASS results.

        Args:
            scenario: e.g. "outdoor_enhance", "coffee_shop_vibe"
            limit: max number to return
        """
        db = self._load()
        matches = [
            p for p in db["prompts"]
            if (not scenario or scenario.lower() in p.get("scenario", "").lower())
            and p.get("score", 0) >= config.QUALITY_THRESHOLD
        ]
        # Sort by score descending
        matches.sort(key=lambda x: x.get("score", 0), reverse=True)
        return matches[:limit]

    async def save_prompt_result(
        self,
        prompt: str,
        score: float,
        scenario: str = "",
        photo_description: str = "",
    ):
        """Save a prompt and its quality score for future learning."""
        db = self._load()
        db["prompts"].append({
            "prompt": prompt,
            "score": score,
            "scenario": scenario,
            "photo_description": photo_description,
            "prompt_hash": hashlib.md5(prompt.encode()).hexdigest()[:8],
        })
        # Keep only the top 100 prompts
        db["prompts"].sort(key=lambda x: x.get("score", 0), reverse=True)
        db["prompts"] = db["prompts"][:100]
        self._save(db)

    async def get_enhancement_patterns(
        self, lighting_issue: str = "", pose_type: str = ""
    ) -> list[str]:
        """Return proven prompt fragments for specific issues."""
        db = self._load()
        patterns = db.get("patterns", {})

        results = []
        if lighting_issue and lighting_issue in patterns:
            results.append(patterns[lighting_issue])
        if pose_type and pose_type in patterns:
            results.append(patterns[pose_type])

        # Default patterns if nothing specific found
        if not results:
            results = [
                "Shot on iPhone 15 Pro Max, f/1.78, natural depth-of-field bokeh",
                "Natural skin texture with visible pores, slight asymmetry in expression",
                "Warm color grading, not perfectly neutral — slightly shifted toward golden tones",
                "Include subtle environmental reflections in eyes",
            ]
        return results

    async def get_realism_rules(self) -> str:
        """Return the latest version of realism instructions for prompts."""
        return """CRITICAL REALISM RULES — the generated image MUST follow ALL of these:
- This must look like a REAL phone photo, NOT an AI render
- Include natural skin texture: visible pores, slight imperfections, natural skin variation
- Slightly asymmetric expression (real faces aren't perfectly symmetric)
- Natural eye reflections matching the environment lighting
- Realistic hair: individual strands visible, not a smooth mass
- Clothing with real fabric texture and natural wrinkles/folds
- Background with realistic depth-of-field blur (bokeh)
- Subtle warm color grading (slightly warm, not perfectly neutral)
- ABSOLUTELY NO airbrushed/plastic/waxy skin
- NO perfect symmetry in face or body
- NO unnaturally smooth textures on any surface
- Include micro-details: tiny fabric creases, slight color variations in skin, natural shadow gradients
- Camera: iPhone 15 Pro Max, f/1.78 aperture, slight lens distortion at edges"""
