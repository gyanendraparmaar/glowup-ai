import os
from typing import Dict, Any
from openai import OpenAI
import json
from pathlib import Path

class ProfileReviewerAgent:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is required.")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.3-70b-versatile"
        self.golden_dataset = self._load_golden_dataset()

    def _load_golden_dataset(self) -> dict:
        """Load the golden dataset of real best-performing Hinge profiles."""
        dataset_path = Path(__file__).parent.parent / "golden_datasets" / "hinge_top_profiles.json"
        try:
            with open(dataset_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"✅ [ProfileReviewer] Loaded golden dataset from {dataset_path.name}")
            return data
        except Exception as e:
            print(f"⚠️ [ProfileReviewer] Could not load golden dataset: {e}. Using fallback rules.")
            return {}

    def _build_golden_context(self) -> str:
        """Build a condensed context string from the golden dataset for few-shot prompting."""
        if not self.golden_dataset:
            return ""

        sections = []

        photo_rules = self.golden_dataset.get("photo_golden_rules", {})
        if photo_rules:
            rules_text = "\n".join(
                f"  - {r['rule']}: {r['detail']}" for r in photo_rules.get("rules", [])
            )
            anti_text = ", ".join(photo_rules.get("anti_patterns", []))
            sections.append(
                f"PHOTO BEST PRACTICES (sourced from real dating coaches):\n{rules_text}\n"
                f"  PHOTO ANTI-PATTERNS: {anti_text}"
            )

        prompt_rules = self.golden_dataset.get("prompt_golden_rules", {})
        if prompt_rules:
            rules_text = "\n".join(
                f"  - {r['rule']}: {r['detail']}" for r in prompt_rules.get("rules", [])
            )
            anti_text = ", ".join(prompt_rules.get("anti_patterns", []))
            sections.append(
                f"PROMPT BEST PRACTICES (sourced from real dating coaches):\n{rules_text}\n"
                f"  PROMPT ANTI-PATTERNS: {anti_text}"
            )

        examples = self.golden_dataset.get("top_performing_prompt_examples", {}).get("examples", [])
        if examples:
            ex_text = "\n".join(
                f"  - Prompt: \"{e['prompt']}\" → Answer: \"{e['answer']}\" (Why it works: {e['why_it_works']})"
                for e in examples[:6]
            )
            sections.append(f"TOP-PERFORMING PROMPT EXAMPLES FROM REAL PROFILES:\n{ex_text}")

        archetypes = self.golden_dataset.get("overall_profile_archetypes", {}).get("archetypes", [])
        if archetypes:
            arch_text = "\n".join(
                f"  - {a['name']} (Score: {a['score_range']}): Photos: {a['photo_mix']} | Vibe: {a['prompt_vibe']} | Feel: {a['overall_feel']}"
                for a in archetypes
            )
            sections.append(f"GOLDEN PROFILE ARCHETYPES (what a 9-10/10 profile looks like):\n{arch_text}")

        return "\n\n".join(sections)

    async def generate_review(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the structured text/photo descriptions from the ScreenshotScout and passes it to Groq
        for deeper strategic analysis and advice generation based on 2024 Hinge meta.
        """
        print("🤔 [ProfileReviewer] Strategizing feedback based on 2024/2025 Hinge meta...")
        
        golden_context = self._build_golden_context()
        
        system_instruction = (
            "You are an elite dating coach and profile analyst specializing in Hinge in 2024/2025. "
            "A \"ScreenshotScout\" vision AI has already extracted the text and photo descriptions from the user's Hinge profile. "
            "Your job is to compare their profile against the GOLDEN STANDARD of top-tier profiles below, and provide "
            "a harsh but constructive, actionable review.\n\n"
            "IMPORTANT: Score the profile CONTEXTUALLY by comparing it to the golden archetypes below. "
            "Don't just check a rigid checklist—feel the overall vibe of the profile and ask: "
            "'How close is this to the best profiles that get the most quality matches?' "
            "A profile can break one rule and still score well if the overall energy is strong.\n\n"
            f"{golden_context}\n\n"
            "SCORING GUIDELINES:\n"
            "- 9-10: Elite. Could be used as an example of a perfect profile. Great photos, great prompts, strong vibe.\n"
            "- 7-8: Strong. A few improvements would take it to the next level.\n"
            "- 5-6: Average. Needs meaningful changes to photos, prompts, or both.\n"
            "- 3-4: Below average. Major issues in photo quality, prompt answers, or overall presentation.\n"
            "- 1-2: Needs a full rebuild. Almost everything should be changed.\n\n"
            "Output your review as a highly structured JSON document with the following keys:\n"
            "{\n"
            "  \"photo_review\": [{ \"id\": 1, \"critique\": \"Harsh but helpful critique\", \"is_keeper\": bool }],\n"
            "  \"prompt_review\": [{ \"question\": \"q\", \"critique\": \"critique\", \"suggested_rewrite\": \"rewrite\" }],\n"
            "  \"overall_score\": int (1-10),\n"
            "  \"actionable_advice\": [\"3 to 5 bullet points of crucial changes\"],\n"
            "  \"suggested_openers\": [\"3 completely custom opening lines they could use on others based on their profile vibe\"],\n"
            "  \"suggested_prompts\": [{ \"prompt_name\": \"e.g., Dating me is like...\", \"suggested_answer\": \"Tailored, clever answer based on their profile\" }]\n"
            "}\n\n"
            "Return ONLY valid JSON. No markdown formatting, no explanation, no code fences."
        )

        user_content = f"Here is the raw extracted profile data:\n{json.dumps(extracted_data, indent=2)}"

        import asyncio
        loop = asyncio.get_event_loop()

        try:
            response = await loop.run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.7,
                    max_tokens=4096,
                    response_format={"type": "json_object"}
                )
            )

            result_text = response.choices[0].message.content
            print(f"✅ [ProfileReviewer] Review generation complete.")
            return json.loads(result_text.strip())
        
        except Exception as e:
            print(f"❌ [ProfileReviewer] Error during review generation: {e}")
            import traceback
            traceback.print_exc()
            raise
