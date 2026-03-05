import os
from typing import Dict, Any
import google.generativeai as genai
import json

class ProfileReviewerAgent:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            # Fallback to multiple keys logic if needed
            keys = os.getenv("GEMINI_API_KEYS", "").split(",")
            if keys and keys[0]:
                self.api_key = keys[0]
            else:
                 raise ValueError("GEMINI_API_KEY environment variable is required.")
        
        self.model = "gemini-2.5-flash"

    async def generate_review(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the structured text/photo descriptions from Groq/Gemini Vision and passes it to Gemini
        for deeper strategic analysis and advice generation based on 2024 Hinge meta.
        """
        print("🤔 [ProfileReviewer] Strategizing feedback based on 2024/2025 Hinge meta...")
        
        system_instruction = (
            "You are an elite dating coach and profile analyst specializing in Hinge in 2024/2025. "
            "A \"ScreenshotScout\" vision AI has already extracted the text and photo descriptions from the user's Hinge profile. "
            "Your job is to read this extracted raw data and provide a harsh but constructive, actionable review.\n\n"
            "BEST PRACTICES & TRENDS (2024/2025):\n"
            "- Prompts: Best performing prompts invoke conversation (e.g., 'Together, we could', 'I go crazy for'). "
            "Answers must be specific, playful, and NOT generic. 'I love tacos and dogs' is an instant fail.\n"
            "- Photos: 1st photo MUST be a clear headshot, smiling, eye contact. You need a full body shot. "
            "You need an activity/hobby shot. Avoid excessive mirror selfies, group photos where the user is hidden, and sunglasses.\n"
            "- Opening lines: Need to be personalized. No 'Hey'.\n\n"
            "Output your review as a highly structured JSON document with the following keys:\n"
            "{\n"
            "  \"photo_review\": [{ \"id\": 1, \"critique\": \"Harsh but helpful critique\", \"is_keeper\": bool }],\n"
            "  \"prompt_review\": [{ \"question\": \"q\", \"critique\": \"critique\", \"suggested_rewrite\": \"rewrite\" }],\n"
            "  \"overall_score\": int (1-10),\n"
            "  \"actionable_advice\": [\"3 to 5 bullet points of crucial changes\"],\n"
            "  \"suggested_openers\": [\"3 completely custom opening lines they could use on others based on their profile vibe\"],\n"
            "  \"suggested_prompts\": [{ \"prompt_name\": \"e.g., Dating me is like...\", \"suggested_answer\": \"Tailored, clever answer based on their profile\" }]\n"
            "}"
        )

        user_content = f"Here is the raw extracted profile data:\n```json\n{json.dumps(extracted_data, indent=2)}\n```"

        # Setup round-robin keys
        keys_to_try = [self.api_key]
        env_keys = os.getenv("GEMINI_API_KEYS", "").split(",")
        keys_to_try.extend([k for k in env_keys if k and k != self.api_key])
        
        max_retries = len(keys_to_try)

        for attempt in range(max_retries):
            try:
                current_key = keys_to_try[attempt]
                genai.configure(api_key=current_key)
                
                # Standard generativeai call
                model = genai.GenerativeModel(
                    model_name=self.model,
                    system_instruction=system_instruction
                )
                
                response = model.generate_content(
                    user_content,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        response_mime_type="application/json",
                    )
                )
                
                return json.loads(response.text)
            
            except Exception as e:
                import asyncio
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"⚠️ [ProfileReviewer] Rate limited (429). Rotating API key (attempt {attempt + 1}/{max_retries})...")
                    import time
                    time.sleep(2) # Sync sleep since this method isn't currently using run_in_executor
                    continue
                else:
                    print(f"❌ [ProfileReviewer] Error during review generation (attempt {attempt + 1}): {e}")
                    raise
        raise Exception("All API keys failed or rate limit exceeded max retries.")
