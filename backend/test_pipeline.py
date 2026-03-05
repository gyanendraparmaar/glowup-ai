import os
import asyncio
import json
import urllib.request
from PIL import Image, ImageDraw, ImageFont

# 1. GENERATE MOCK SCREENSHOTS
os.makedirs("test_images", exist_ok=True)

# Unsplash generic portraits
urls = [
    "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=800&q=80",
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=800&q=80",
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80"
]

texts = [
    "Alex, 28\nSoftware Engineer\nNew York",
    "I go crazy for...\nA good cup of coffee and long hikes on the weekend.",
    "Together, we could...\nBuild the ultimate Lego Star Wars set."
]

saved_paths = []
print("Downloading and generating mock Hinge screenshots...")
for i, url in enumerate(urls):
    filename = f"test_images/screenshot_{i+1}.jpg"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filename, 'wb') as out_file:
            out_file.write(response.read())

        # Overlay text to simulate Hinge prompt
        img = Image.open(filename)
        draw = ImageDraw.Draw(img)
        
        # Try a basic system font, fallback to default
        try:
             font = ImageFont.truetype("arial", 40)
        except IOError:
             font = ImageFont.load_default()

        # Draw a semi-transparent black rectangle background for text readability
        draw.rectangle(((20, img.height - 200), (img.width - 20, img.height - 20)), fill=(0, 0, 0, 150))
        draw.text((40, img.height - 180), texts[i], fill=(255, 255, 255), font=font)
        
        # Add basic UI element
        draw.ellipse((img.width - 80, img.height - 250, img.width - 20, img.height - 190), fill=(255, 255, 255))
        
        img.save(filename)
        saved_paths.append(os.path.abspath(filename))
        print(f"✅ Created: {filename}")
    except Exception as e:
        print(f"Failed to generate {filename}: {e}")

# 2. RUN PIPELINE
from dotenv import load_dotenv
load_dotenv()
from pipeline import run_review_pipeline

async def test_backend():
    print(f"\nRunning backend pipeline with {len(saved_paths)} images...")
    try:
        review_data = await run_review_pipeline(saved_paths)
        print("\n🎉 PIPELINE SUCCESSFUL. Final Output:")
        print(json.dumps(review_data, indent=2))
        
        # Validate critical keys exist
        assert "overall_score" in review_data, "Missing overall_score"
        assert "actionable_advice" in review_data, "Missing actionable_advice"
        print("\n✅ All JSON keys validated.")
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_backend())
