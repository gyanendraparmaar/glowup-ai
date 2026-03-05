from __future__ import annotations
"""Prompt Library MCP Server — stores and retrieves successful prompt patterns.

Uses SQLite for thread-safe, ACID-compliant storage.
"""

import hashlib
import logging
import sqlite3
import threading
from config import config

logger = logging.getLogger("glowup.prompt_library")


class PromptLibraryMCP:
    """MCP-style tool server for managing prompt patterns.

    Uses a local SQLite database for thread-safe storage.
    Stores prompts that produced PASS results so the pipeline improves over time.
    """

    _lock = threading.Lock()

    def __init__(self):
        self.db_path = config.PROMPT_LIBRARY_PATH
        self._ensure_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _ensure_db(self):
        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS prompts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        prompt TEXT NOT NULL,
                        score REAL NOT NULL,
                        scenario TEXT DEFAULT '',
                        photo_description TEXT DEFAULT '',
                        prompt_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_prompts_scenario ON prompts(scenario)
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_prompts_score ON prompts(score DESC)
                """)
                conn.commit()
            finally:
                conn.close()

    async def get_successful_prompts(
        self, scenario: str = "", limit: int = 3
    ) -> list[dict]:
        """Retrieve prompts that previously produced PASS results.

        Args:
            scenario: e.g. "outdoor_enhance", "coffee_shop_vibe"
            limit: max number to return
        """
        with self._lock:
            conn = self._get_conn()
            try:
                if scenario:
                    rows = conn.execute(
                        """SELECT prompt, score, scenario, photo_description
                           FROM prompts
                           WHERE score >= ? AND scenario LIKE ?
                           ORDER BY score DESC
                           LIMIT ?""",
                        (config.QUALITY_THRESHOLD, f"%{scenario.lower()}%", limit),
                    ).fetchall()
                else:
                    rows = conn.execute(
                        """SELECT prompt, score, scenario, photo_description
                           FROM prompts
                           WHERE score >= ?
                           ORDER BY score DESC
                           LIMIT ?""",
                        (config.QUALITY_THRESHOLD, limit),
                    ).fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()

    async def save_prompt_result(
        self,
        prompt: str,
        score: float,
        scenario: str = "",
        photo_description: str = "",
    ):
        """Save a prompt and its quality score for future learning."""
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]

        with self._lock:
            conn = self._get_conn()
            try:
                conn.execute(
                    """INSERT INTO prompts (prompt, score, scenario, photo_description, prompt_hash)
                       VALUES (?, ?, ?, ?, ?)""",
                    (prompt, score, scenario, photo_description, prompt_hash),
                )

                # Keep only the top 100 prompts
                conn.execute("""
                    DELETE FROM prompts WHERE id NOT IN (
                        SELECT id FROM prompts ORDER BY score DESC LIMIT 100
                    )
                """)

                conn.commit()
                logger.info("prompt_library.saved hash=%s score=%.1f scenario=%s", prompt_hash, score, scenario)
            finally:
                conn.close()

    async def get_enhancement_patterns(
        self, lighting_issue: str = "", pose_type: str = ""
    ) -> list[str]:
        """Return proven prompt fragments for specific issues."""
        patterns = {
            "harsh_lighting": "Soft diffused natural window light, avoid harsh shadows",
            "flat_lighting": "Add directional key light with subtle fill, create depth",
            "backlit": "Fill flash to balance subject against bright background",
            "standing": "Full body with natural posture, weight shifted slightly",
            "sitting": "Relaxed seated pose with natural hand placement",
            "close-up": "Tight framing on face with shallow depth of field",
        }

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
