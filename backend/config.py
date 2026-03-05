from __future__ import annotations
"""Configuration loader for GlowUp AI Demo."""

import os
import logging
from dotenv import load_dotenv

load_dotenv(override=True)

# ── Logging Setup ──────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("glowup")


class Config:
    # ── API Keys ───────────────────────────────────────────────────
    raw_keys = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
    GEMINI_API_KEYS: list[str] = [k.strip() for k in raw_keys.split(",") if k.strip()]
    _key_index: int = 0

    @property
    def GEMINI_API_KEY(self) -> str:
        """Returns the next Gemini API key using round-robin rotation."""
        if not self.GEMINI_API_KEYS:
            return ""
        key = self.GEMINI_API_KEYS[self._key_index % len(self.GEMINI_API_KEYS)]
        Config._key_index += 1
        return key

    # Photo Scout APIs
    UNSPLASH_API_KEY: str = os.getenv("UNSPLASH_API_KEY", "")
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")

    # ── Pipeline Settings ──────────────────────────────────────────
    QUALITY_THRESHOLD: int = int(os.getenv("QUALITY_THRESHOLD", "7"))
    AI_DETECTION_MAX: int = int(os.getenv("AI_DETECTION_MAX", "3"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    NUM_VARIATIONS: int = int(os.getenv("NUM_VARIATIONS", "1"))
    NUM_SCOUT_REFS: int = int(os.getenv("NUM_SCOUT_REFS", "3"))

    # ── Upload Limits ──────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_SIZE_MB", "20"))
    MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024
    MAX_PHOTOS_PER_REQUEST: int = 5
    ALLOWED_IMAGE_TYPES: set[str] = {"image/jpeg", "image/png", "image/webp"}

    # ── Rate Limiting ──────────────────────────────────────────────
    RATE_LIMIT: str = os.getenv("RATE_LIMIT", "5/minute")

    # ── CORS ───────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        o.strip()
        for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
        if o.strip()
    ]

    # ── Paths ──────────────────────────────────────────────────────
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    PROMPT_LIBRARY_PATH: str = os.getenv("PROMPT_LIBRARY_PATH", "prompt_library.db")

    # ── Models ─────────────────────────────────────────────────────
    PROMPT_MODEL: str = "gemini-2.0-flash"
    IMAGE_MODEL: str = "gemini-2.0-flash-preview-image-generation"
    QUALITY_MODEL: str = "gemini-2.0-flash"

    # ── Generation Constants ───────────────────────────────────────
    BASE_TEMPERATURE: float = 0.75
    TEMPERATURE_INCREMENT: float = 0.05
    RETRY_MAX_ATTEMPTS: int = 12
    RETRY_MULTIPLIER: int = 2
    RETRY_MIN_WAIT: int = 15
    RETRY_MAX_WAIT: int = 120

    # ── Post-Production Constants ──────────────────────────────────
    VIGNETTE_STRENGTH: float = 0.15
    SENSOR_NOISE_INTENSITY: int = 3
    COLOR_SHIFT_MIN: float = 0.97
    COLOR_SHIFT_MAX: float = 1.03
    WARMTH_SHIFT_MIN: float = 1.0
    WARMTH_SHIFT_MAX: float = 1.02
    LENS_BLUR_RADIUS: float = 0.3
    JPEG_QUALITY_MIN: int = 87
    JPEG_QUALITY_MAX: int = 93

    # ── Cache Settings ─────────────────────────────────────────────
    REF_CACHE_MAX_ENTRIES: int = int(os.getenv("REF_CACHE_MAX_ENTRIES", "200"))


config = Config()
