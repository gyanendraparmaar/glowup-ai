"""Image Analysis MCP Server — uses Gemini for deep photo analysis."""

from io import BytesIO
from PIL import Image
import google.genai as genai
import json
from tenacity import retry, stop_after_attempt, wait_exponential
from config import config


class ImageAnalysisMCP:
    """MCP-style tool server for analyzing photos using Gemini vision."""

    @retry(stop=stop_after_attempt(12), wait=wait_exponential(multiplier=2, min=15, max=120))
    def _call_api(self, model: str, contents: list):
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        return client.models.generate_content(
            model=model,
            contents=contents,
        )

    async def analyze_photo(self, image_path: str) -> dict:
        """Deep analysis of a photo: face, pose, lighting, setting, clothing, issues.

        Returns a structured dict with analysis results, including a matching
        Awesome Nano Banana Pro style category.
        """
        img = Image.open(image_path)

        # Fetch available styles to inject into prompt
        from mcp_servers.style_library import StyleLibraryMCP
        library = StyleLibraryMCP()
        style_instructions = await library.get_style_instructions()

        prompt_text = f"""Analyze this photo in detail. Return ONLY valid JSON with these fields:

        {{
            "gender": "male/female/unknown",
            "age_range": "20s/30s/etc",
            "pose": "standing/sitting/close-up/etc",
            "setting": "outdoor park/indoor cafe/street/studio/etc",
            "lighting": {{
                "quality": "good/harsh/flat/backlit/dim",
                "direction": "front/side/overhead/natural/mixed",
                "color_temp": "warm/neutral/cool"
            }},
            "clothing": "brief description of what they're wearing",
            "expression": "smiling/neutral/serious/laughing/etc",
            "background": "brief description",
            "issues": ["list of quality issues: e.g. overexposed, blurry, harsh shadows"],
            "strengths": ["list of what's already good about the photo"],
            "search_query": "search query to find similar professional photos on stock sites",
            "style_category": "ID of the best matching aesthetic style from the list below"
        }}

        Be specific and accurate. The search_query should describe the type of
        professional photo that would serve as a good lighting/composition reference.

        AVAILABLE AESTHETIC STYLES TO CHOOSE FROM:
        {style_instructions}

        Choose the ONE style ID that best matches the natural vibe, setting, or potential
        of this photo. (e.g., if it's a mirror selfie, choose '2000s_mirror_selfie'. If
        it has strong flash, choose '1990s_camera_flash').
        """

        response = self._call_api(
            model=config.PROMPT_MODEL,
            contents=[img, prompt_text],
        )

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return {
                "gender": "unknown",
                "pose": "unknown",
                "setting": "unknown",
                "lighting": {"quality": "unknown", "direction": "unknown", "color_temp": "unknown"},
                "clothing": "unknown",
                "expression": "unknown",
                "background": "unknown",
                "issues": [],
                "strengths": [],
                "search_query": "professional portrait photography",
                "style_category": "casual_iphone",
            }

    async def compare_photos(
        self, original_path: str, generated_bytes: bytes
    ) -> dict:
        """Compare original and generated photo for identity match & quality."""
        original = Image.open(original_path)
        generated = Image.open(BytesIO(generated_bytes))

        response = self._call_api(
            model=config.QUALITY_MODEL,
            contents=[
                generated,
                original,
                """You are an expert photo forensics analyst. Image 1 is potentially
                AI-generated. Image 2 is the original real photo of the same person.

                Evaluate Image 1 on these criteria (1-10 each):

                1. REALISM: Does it look like a real phone photo?
                2. IDENTITY_MATCH: Same person as Image 2? (face, features, skin tone)
                3. NATURALNESS: Does the pose/expression feel candid and natural?
                4. ATTRACTIVENESS: Is it dating-app worthy?
                5. AI_DETECTION_RISK: How likely would someone suspect AI?
                   (1 = definitely looks real, 10 = obviously AI)
                6. ENHANCEMENT_QUALITY: Is it clearly better than the original?

                Also list SPECIFIC issues if any (e.g., "left hand has 6 fingers",
                "skin too smooth on forehead", "eyes lack reflections").

                Return ONLY valid JSON:
                {
                    "realism": X,
                    "identity_match": X,
                    "naturalness": X,
                    "attractiveness": X,
                    "ai_detection_risk": X,
                    "enhancement_quality": X,
                    "overall": X,
                    "issues": ["issue1", "issue2"],
                    "verdict": "PASS" or "FAIL",
                    "fix_suggestions": ["suggestion1", "suggestion2"]
                }

                PASS requires: overall >= 7 AND ai_detection_risk <= 3
                """,
            ],
        )

        try:
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(text)
        except (json.JSONDecodeError, IndexError):
            return {
                "realism": 0, "identity_match": 0, "naturalness": 0,
                "attractiveness": 0, "ai_detection_risk": 10,
                "enhancement_quality": 0, "overall": 0,
                "issues": ["Quality check response was not valid JSON"],
                "verdict": "FAIL",
                "fix_suggestions": ["Re-generate with stronger realism instructions"],
            }
