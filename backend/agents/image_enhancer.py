from __future__ import annotations
"""Image Enhancer Agent — generates enhanced images using Nano Banana Pro."""

from PIL import Image
import google.genai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
from config import config


client = genai.Client(api_key=config.GEMINI_API_KEY)


class ImageEnhancerAgent:
    """Agent that takes the crafted prompt + original photo + reference images
    and generates the enhanced image using Nano Banana Pro.

    This is a focused agent — it just executes the generation.
    The intelligence is in the Prompt Architect.
    """

    @retry(stop=stop_after_attempt(12), wait=wait_exponential(multiplier=2, min=15, max=120))
    def _call_api(self, contents, temperature):
        return client.models.generate_content(
            model=config.IMAGE_MODEL,
            contents=contents,
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                temperature=temperature,
            ),
        )

    async def enhance(
        self,
        original_path: str,
        prompt: str,
        reference_paths: list[str] | None = None,
        temperature: float = 0.75,
    ) -> bytes | None:
        """Generate an enhanced image.

        Args:
            original_path: Path to user's original photo
            prompt: The detailed enhancement prompt from the Prompt Architect
            reference_paths: Optional paths to reference images from Photo Scout
            temperature: Generation temperature (higher = more variation)

        Returns:
            Enhanced image as bytes, or None if generation failed
        """
        contents = []

        # Add the original photo
        original = Image.open(original_path)
        contents.append(original)

        # Add reference images (up to 2 to keep within context limits)
        if reference_paths:
            for ref_path in reference_paths[:2]:
                try:
                    ref_img = Image.open(ref_path)
                    contents.append(ref_img)
                except Exception:
                    continue

        # Add the prompt
        contents.append(prompt)

        try:
            response = self._call_api(contents, temperature)

            # Extract the image from the response
            if response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data and part.inline_data.data:
                        return part.inline_data.data

            print("     [!] No image in response")
            return None

        except Exception as e:
            print(f"     [ERROR] Generation error: {e}")
            return None
