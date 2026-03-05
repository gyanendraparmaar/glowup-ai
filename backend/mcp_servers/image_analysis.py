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
    async def _call_api(self, model: str, contents: list):
        from groq import AsyncGroq
        import base64
        from io import BytesIO
        
        client = AsyncGroq(api_key=config.GROQ_API_KEY)
        
        groq_content = []
        for item in contents:
            if isinstance(item, str):
                groq_content.append({"type": "text", "text": item})
            else:
                # Resize to fit Groq limits and convert to base64
                if max(item.size) > 1024:
                    item.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                buffered = BytesIO()
                if item.mode != 'RGB':
                    item = item.convert('RGB')
                item.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                groq_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}
                })
                
        print(f"       [?] Sending Groq request to model: {model}...")
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": groq_content}],
                temperature=0.2
            )
            print(f"       [✓] Groq response received.")
            
            class MockResponse:
                @property
                def text(self):
                    return response.choices[0].message.content
                    
            return MockResponse()
        except Exception as e:
            print(f"       [X] Groq Error: {e}")
            raise

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

        response = await self._call_api(
            model=config.GROQ_VISION_MODEL,
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
        self, 
        original_path: str, 
        generated_bytes: bytes,
        mode: str = "enhance",
        vibe: str | None = None
    ) -> dict:
        """Compare original and generated photo for identity match, quality & context."""
        original = Image.open(original_path)
        generated = Image.open(BytesIO(generated_bytes))
        
        # Contextual constraint string
        if mode == "vibe" and vibe:
            bg_instruction = f"Is the background/setting broadly appropriate for the requested '{vibe}' vibe? (true/false)"
        else:
            bg_instruction = "Are they in the exact same setting/background? (true/false. True if it's the exact same place, just better lit/framed)."

        response = await self._call_api(
            model=config.GROQ_VISION_MODEL,
            contents=[
                generated,
                original,
                f"""You are an expert photo forensics analyst. Image 1 is potentially
                AI-generated. Image 2 is the original real photo of the same person.

                Evaluate Image 1 on these criteria (1-10 each):

                1. REALISM: Does it look like a real phone photo?
                2. IDENTITY_MATCH: Same person as Image 2? (face, features, skin tone)
                3. NATURALNESS: Does the pose/expression feel candid and natural?
                4. ATTRACTIVENESS: Is it dating-app worthy?
                5. AI_DETECTION_RISK: How likely would someone suspect AI?
                   (1 = definitely looks real, 10 = obviously AI)
                6. ENHANCEMENT_QUALITY: Is it clearly better than the original?
                
                Also evaluate these STRICT PRESERVATION BOOLEANS (true/false):
                7. BACKGROUND_PRESERVED: {bg_instruction}
                8. CLOTHING_PRESERVED: Are they wearing the EXACT same clothing? (true/false)
                9. COMPANIONS_PRESERVED: If there are other people in Image 2, are they all STILL PRESENT in Image 1? (true/false. Also true if ONLY one person is in Image 2).

                Also list SPECIFIC issues if any (e.g., "left hand has 6 fingers",
                "skin too smooth on forehead", "eyes lack reflections").

                Return ONLY valid JSON:
                {{
                    "realism": 0,
                    "identity_match": 0,
                    "naturalness": 0,
                    "attractiveness": 0,
                    "ai_detection_risk": 0,
                    "enhancement_quality": 0,
                    "overall": 0,
                    "background_preserved": true,
                    "clothing_preserved": true,
                    "companions_preserved": true,
                    "issues": ["issue1", "issue2"],
                    "verdict": "PASS",
                    "fix_suggestions": ["suggestion1"]
                }}

                PASS requires: overall >= 7 AND ai_detection_risk <= 3 AND all booleans are true.
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
                "background_preserved": False,
                "clothing_preserved": False,
                "companions_preserved": False,
                "issues": ["Quality check response was not valid JSON"],
                "verdict": "FAIL",
                "fix_suggestions": ["Re-generate with stronger realism instructions"],
            }
