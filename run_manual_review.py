import asyncio
import json
import sys
import os

# Add backend dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

from backend.agents.profile_reviewer import ProfileReviewerAgent
from dotenv import load_dotenv

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/.env")))

extracted_data = {
  "photos": [
    {
      "id": 1,
      "description": "User standing on a boat in a printed short-sleeve shirt and blue shorts. Clear blue sky and a mountain island in the background. Good lighting.",
      "type": "full_body"
    },
    {
      "id": 2,
      "description": "User standing on a wide street or plaza with historic stone buildings in the background. Wearing a green textured sweater, khaki cargo pants, and sunglasses.",
      "type": "full_body"
    },
    {
      "id": 3,
      "description": "User in a snowy mountain landscape wearing a green winter jacket, beanie, sunglasses, and gloves. Mountains and snow in the background.",
      "type": "activity"
    },
    {
      "id": 4,
      "description": "Bathroom mirror selfie. User is wearing a maroon polo shirt and khaki shorts, looking at the phone screen.",
      "type": "other"
    },
    {
      "id": 5,
      "description": "Public restroom mirror selfie. User is wearing a white sleeveless graphic tee, khaki cargo pants, and lime green sneakers. Holding phone to face.",
      "type": "full_body"
    },
    {
      "id": 6,
      "description": "Nighttime concert or festival setting. User is with a friend. Both are wearing glasses and making a playful pose with their hands near their chins.",
      "type": "group"
    }
  ],
  "prompts": [
    {
      "question": "Most exotic place I've been",
      "answer": "[No text answer, just the boat photo attached to this prompt]"
    },
    {
      "question": "My submission to National Geographic",
      "answer": "[No text answer, just the snowy mountains photo attached to this prompt]"
    },
    {
      "question": "My simple pleasures",
      "answer": "Cardio after every workout. Coz I want to feel like Milkha Singh once a day."
    },
    {
      "question": "Don't judge me",
      "answer": "[No text answer, just the concert photo attached to this prompt]"
    },
    {
      "question": "Dating me is like",
      "answer": "Software updates, it might take a while but you’ll end up in a place you haven’t been"
    }
  ],
  "bio": {
    "name": "Unknown",
    "age": "22",
    "job": "SDE at Bangalore",
    "location": "Bangalore"
  }
}

async def run():
    reviewer = ProfileReviewerAgent()
    review = await reviewer.generate_review(extracted_data)
    with open("review_output.json", "w") as f:
        json.dump(review, f, indent=2)
    print("Done")

if __name__ == "__main__":
    asyncio.run(run())
