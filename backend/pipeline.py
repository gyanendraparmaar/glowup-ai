from typing import List, Dict, Any
from agents.screenshot_scout import ScreenshotScoutAgent
from agents.profile_reviewer import ProfileReviewerAgent
import json
import uuid

async def run_review_pipeline(image_paths: List[str]) -> Dict[str, Any]:
    """
    Run the two-stage Hinge Profile Review pipeline:
      1. Screenshot Scout (Groq Llama Vision) -> Extracts text and photo details
      2. Profile Reviewer (Groq Llama 3.3 70B) -> Generates actionable strategic advice
      
    Args:
        image_paths: List of absolute paths to the uploaded screenshots
        
    Returns:
        The final strategic JSON advice.
    """
    job_id = str(uuid.uuid4())[:8]
    print(f"\n{'=' * 60}")
    print(f"🚀 Starting Hinge Review Job: {job_id}")
    print(f"{'=' * 60}")

    # Stage 1: Groq Vision Extraction
    print(f"\n[STAGE 1] Screenshot Scout Agent (Groq Llama Vision)")
    scout = ScreenshotScoutAgent()
    extracted_data = await scout.analyze_screenshots(image_paths)
    
    print(f"  ✅ Extracted {len(extracted_data.get('photos', []))} photos and {len(extracted_data.get('prompts', []))} prompts.")
    
    # Stage 2: Groq Strategy Review
    print(f"\n[STAGE 2] Profile Reviewer Agent (Groq Llama 3.3 70B)")
    reviewer = ProfileReviewerAgent()
    final_review = await reviewer.generate_review(extracted_data)
    
    print(f"  ✅ Generated strategic review. Overall Score: {final_review.get('overall_score', 'N/A')}/10")
    print(f"\n{'=' * 60}")
    print(f"🏁 Job {job_id} Complete!")
    print(f"{'=' * 60}\n")
    
    return final_review
