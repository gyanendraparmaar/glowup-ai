"""Configuration loader for GlowUp AI Demo."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Photo Scout APIs
    UNSPLASH_API_KEY: str = os.getenv("UNSPLASH_API_KEY", "")
    PEXELS_API_KEY: str = os.getenv("PEXELS_API_KEY", "")

    # Pipeline settings
    QUALITY_THRESHOLD: int = int(os.getenv("QUALITY_THRESHOLD", "7"))
    AI_DETECTION_MAX: int = int(os.getenv("AI_DETECTION_MAX", "3"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    NUM_VARIATIONS: int = int(os.getenv("NUM_VARIATIONS", "4"))
    NUM_SCOUT_REFS: int = int(os.getenv("NUM_SCOUT_REFS", "3"))

    # Paths
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "outputs")
    PROMPT_LIBRARY_PATH: str = os.getenv("PROMPT_LIBRARY_PATH", "prompt_library.json")


    # Models
    PROMPT_MODEL: str = "gemini-2.5-flash"
    IMAGE_MODEL: str = "gemini-2.0-flash-exp"  # Nano Banana Pro / image generation model
    QUALITY_MODEL: str = "gemini-2.5-pro"


config = Config()
