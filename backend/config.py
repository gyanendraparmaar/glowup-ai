"""Configuration loader for GlowUp AI Demo."""

import os
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    raw_keys = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
    GEMINI_API_KEYS: list[str] = [k.strip() for k in raw_keys.split(",") if k.strip()]
    
    @property
    def GEMINI_API_KEY(self) -> str:
        """Returns a random Gemini API key for basic load balancing to avoid limits."""
        import random
        return random.choice(self.GEMINI_API_KEYS) if self.GEMINI_API_KEYS else ""

    # Photo Scout APIs
    UNSPLASH_API_KEY: str = os.getenv("UNSPLASH_API_KEY", "")
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")

    # Pipeline settings
    QUALITY_THRESHOLD: int = int(os.getenv("QUALITY_THRESHOLD", "7"))
    AI_DETECTION_MAX: int = int(os.getenv("AI_DETECTION_MAX", "3"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    NUM_VARIATIONS: int = int(os.getenv("NUM_VARIATIONS", "1"))
    NUM_SCOUT_REFS: int = int(os.getenv("NUM_SCOUT_REFS", "3"))

    # Paths
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    PROMPT_LIBRARY_PATH: str = os.getenv("PROMPT_LIBRARY_PATH", "prompt_library.json")


    # Models
    PROMPT_MODEL: str = "gemini-2.0-flash"
    IMAGE_MODEL: str = "gemini-2.0-flash-preview-image-generation"
    QUALITY_MODEL: str = "gemini-2.0-flash"


config = Config()
