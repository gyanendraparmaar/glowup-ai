import os
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv(override=True)

# Parse API Keys
raw_keys = os.getenv("GEMINI_API_KEYS", os.getenv("GEMINI_API_KEY", ""))
GEMINI_API_KEYS = [k.strip() for k in raw_keys.split(",") if k.strip()]
print(f"Loaded {len(GEMINI_API_KEYS)} Gemini keys.")

def test_sync_gemini():
    print("Testing pure sync Gemini image generation...")
    import random
    key = random.choice(GEMINI_API_KEYS)
    genai.configure(api_key=key)
    print(f"Using key: {key[:10]}...")
    
    model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")
    
    # Send a tiny image instead of the huge original for a quick network test
    img = Image.new('RGB', (100, 100), color='red')
    
    print("Sending request...")
    response = model.generate_content(
        [img, "Turn this red image into a realistic photo of a red apple on a table. High quality."],
        generation_config=genai.types.GenerationConfig(temperature=0.7)
    )
    print("Response received!")
    print(response)

if __name__ == "__main__":
    test_sync_gemini()
