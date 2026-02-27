import json

# Curated aesthetic styles from Awesome Nano Banana Pro
# Each style defines the core instruction to inject into the prompt
# and specific tags/keywords the model recognizes for that aesthetic.

STYLE_PRESETS = {
    "1990s_camera_flash": {
        "name": "1990s Camera Flash",
        "description": "Raw, nostalgic point-and-shoot camera feel",
        "instruction": "Captured with a 1990s-style camera using a direct front flash. The 35mm lens flash creates a nostalgic glow.",
        "keywords": ["1990s-style camera", "direct front flash", "35mm lens flash", "nostalgic glow", "raw aesthetic"],
    },
    "professional_headshot": {
        "name": "Professional Studio Headshot",
        "description": "Clean, corporate/LinkedIn ready portrait",
        "instruction": "Place the subject against a clean, solid dark gray studio photography backdrop with a subtle gradient (vignette effect). Shot on a Sony A7III with an 85mm f/1.4 lens. Use a classic three-point lighting setup. The main key light should create soft, defining shadows on the face. A subtle rim light should separate the subject's shoulders and hair from the dark background.",
        "keywords": ["professional studio headshot", "dark gray studio backdrop", "Sony A7III", "85mm f/1.4 lens", "three-point lighting setup", "key light", "rim light", "ultra-realistic", "8k"],
    },
    "emotional_film": {
        "name": "Emotional Film Photography",
        "description": "Cinematic, soft, golden hour film look",
        "instruction": "A cinematic, emotional portrait shot on Kodak Portra 400 film. Warm, nostalgic lighting hitting the side of the face. Apply a subtle film grain and soft focus to create a dreamy, storytelling vibe. High quality, depth of field.",
        "keywords": ["cinematic", "emotional portrait", "Kodak Portra 400 film", "warm nostalgic lighting", "film grain", "soft focus", "storytelling vibe"],
    },
    "2000s_mirror_selfie": {
        "name": "2000s Mirror Selfie",
        "description": "Y2K aesthetic with harsh flash and retro highlights",
        "instruction": "Captured as an early-2000s mirror selfie aesthetic. Use harsh super-flash with bright blown-out highlights. Subtle grain, retro highlights, V6 realism, crisp details.",
        "keywords": ["early-2000s digital camera aesthetic", "harsh super-flash", "mirror selfie", "subtle grain", "retro highlights"],
    },
    "hyper_realistic_crowd": {
        "name": "Hyper-Realistic Cinematic",
        "description": "Ultra-sharp, 8k cinematic lighting",
        "instruction": "A hyper-realistic, ultra-sharp, full-color large-format cinematic frame. The image must look like a perfectly photographed editorial cover with impeccable lighting. Photorealistic, 8k, shallow depth of field, soft natural fill light + strong golden rim light. High dynamic range, calibrated color grading.",
        "keywords": ["hyper-realistic", "ultra-sharp", "large-format image", "cinematic frame", "editorial cover", "impeccable lighting", "8k", "shallow depth of field", "natural fill light", "golden rim light"],
    },
    "casual_iphone": {
        "name": "Casual iPhone Snapshot",
        "description": "Candid, UGC (User-Generated Content) style, natural",
        "instruction": "Captured as a casual iPhone photo, NOT professional. Quality should be iPhone camera - good but not studio, realistic social media quality. Natural, slightly grainy iPhone look, not over-processed.",
        "keywords": ["casual iPhone selfie", "NOT professional", "realistic social media quality", "slightly grainy iPhone look", "not over-processed"],
    }
}

from typing import Optional

class StyleLibraryMCP:
    """MCP interface for retrieving specific aesthetic styles."""

    async def get_all_styles(self) -> dict:
        """Get the full mapping of available styles."""
        return STYLE_PRESETS

    async def get_style_by_id(self, style_id: str) -> Optional[dict]:
        """Get a specific style preset by its internal ID."""
        return STYLE_PRESETS.get(style_id)

    async def get_style_instructions(self) -> str:
        """Format the styles for the Image Analyzer to pick from."""
        options = []
        for sid, data in STYLE_PRESETS.items():
            options.append(f"- ID: {sid} | Name: {data['name']} | Desc: {data['description']}")
        return "\n".join(options)
