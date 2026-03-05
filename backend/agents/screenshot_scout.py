import os
from typing import List, Dict, Any
from google import genai
from google.genai import types
import json

class ScreenshotScoutAgent:
    def __init__(self, api_key: str = None):
        # We will use Gemini for vision since the Groq key lacks vision access
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            keys = os.getenv("GEMINI_API_KEYS", "").split(",")
            if keys and keys[0]:
                self.api_key = keys[0]
            else:
                 raise ValueError("GEMINI_API_KEY environment variable is required.")
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-2.5-flash"

    async def analyze_screenshots(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Takes a list of screenshot paths and uses Gemini Vision to extract text and describe the user's photos.
        """
        print(f"🕵️‍♂️ [ScreenshotScout] Analyzing {len(image_paths)} screenshots via Gemini Vision...")
        
        system_instruction = (
            "You are an expert dating profile analyst. The user has uploaded screenshots of their Hinge profile. "
            "Your job is to extract all the information from these screenshots with extreme detail.\n\n"
            "Please provide your analysis in the following structured JSON format:\n"
            "{\n"
            "  \"photos\": [\n"
            "    {\n"
            "      \"id\": 1,\n"
            "      \"description\": \"Detailed description of the photo (lighting, angle, setting, user's expression, what they are doing).\",\n"
            "      \"type\": \"headshot | full_body | group | activity | other\"\n"
            "    }\n"
            "  ],\n"
            "  \"prompts\": [\n"
            "    {\n"
            "      \"question\": \"The Hinge prompt question visible\",\n"
            "      \"answer\": \"The user's answer to the prompt\"\n"
            "    }\n"
            "  ],\n"
            "  \"bio\": {\n"
            "     \"name\": \"user's name if visible\",\n"
            "     \"age\": \"user's age if visible\",\n"
            "     \"job\": \"user's job if visible\",\n"
            "     \"location\": \"user's location if visible\"\n"
            "  }\n"
            "}\n\n"
            "Focus ONLY on returning this strict JSON format. Do not include markdown formatting or extra text."
        )

        from PIL import Image
        import io

        # We need to pass the images to Gemini
        contents = ["Extract the profile information from these screenshots."]
        for path in image_paths:
             # Compress slightly to avoid massive payloads, though Gemini handles large files better
             with Image.open(path) as img:
                 if img.mode in ("RGBA", "P"):
                     img = img.convert("RGB")
                 img.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
                 buffer = io.BytesIO()
                 img.save(buffer, format="JPEG", quality=85)
                 contents.append(
                     types.Part.from_bytes(
                         data=buffer.getvalue(),
                         mime_type="image/jpeg",
                     )
                 )

        import asyncio
        loop = asyncio.get_event_loop()
        
        # Support multiple keys for round-robin if rate limited
        keys_to_try = [self.api_key]
        env_keys = os.getenv("GEMINI_API_KEYS", "").split(",")
        keys_to_try.extend([k for k in env_keys if k and k != self.api_key])
        
        max_retries = len(keys_to_try)
        
        for attempt in range(max_retries):
            try:
                # Update client with the current key to try
                current_key = keys_to_try[attempt]
                self.client = genai.Client(api_key=current_key)
                
                response = await loop.run_in_executor(
                        None,
                        lambda: self.client.models.generate_content(
                            model=self.model,
                            contents=contents,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                                temperature=0.2,
                                response_mime_type="application/json"
                            )
                        )
                    )
                
                result_text = response.text
                return json.loads(result_text.strip())

            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"⚠️ [ScreenshotScout] Rate limited (429). Rotating API key (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(2) # brief pause before switching key
                    continue
                else:
                    print(f"❌ [ScreenshotScout] Error during extraction (attempt {attempt + 1}): {e}")
                    raise

