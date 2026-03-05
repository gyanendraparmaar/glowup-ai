import os
from typing import List, Dict, Any
from openai import OpenAI
import json
import base64

class ScreenshotScoutAgent:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required.")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "meta-llama/llama-4-scout-17b-16e-instruct"

    async def analyze_screenshots(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Takes a list of screenshot paths and uses Groq Llama Vision to extract text and describe the user's photos.
        """
        print(f"🕵️‍♂️ [ScreenshotScout] Analyzing {len(image_paths)} screenshots via Groq Vision...")
        
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

        # Build message content with images as base64 data URIs
        content_parts = [
            {"type": "text", "text": "Extract the profile information from these Hinge screenshots."}
        ]
        
        for path in image_paths:
            with Image.open(path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=80)
                buffer.seek(0)
                b64_image = base64.b64encode(buffer.read()).decode("utf-8")
                content_parts.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{b64_image}"
                    }
                })

        import asyncio
        loop = asyncio.get_event_loop()

        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": content_parts}
                    ],
                    temperature=0.2,
                    max_tokens=4096
                )
            )

            result_text = response.choices[0].message.content
            # Clean up markdown fences if present
            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]
            print(f"✅ [ScreenshotScout] Extraction complete.")
            return json.loads(result_text.strip())

        except Exception as e:
            print(f"❌ [ScreenshotScout] Error during extraction: {e}")
            import traceback
            traceback.print_exc()
            raise
