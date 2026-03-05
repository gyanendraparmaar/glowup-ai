import asyncio
import os
import io
from PIL import Image
from agents.prompt_architect import PromptArchitectAgent

async def main():
    architect = PromptArchitectAgent()
    
    # Load user's concert photo
    img_path = r"C:\Users\Gyanendra Parmaar\.gemini\antigravity\brain\3e82d804-ca4e-4791-b3d4-138ae9fc2e1e\media__1772306389224.png"
    img = Image.open(img_path)
    
    # Prepare gemini content format
    contents = [img]
    
    # Generate prompt
    try:
        prompt = await architect.generate_prompt(
            original_path=img_path, 
            reference_paths=[], 
            mode="vibe", 
            vibe="Professional Headshot"
        )
        with open("user_prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt)
        print("Successfully generated user_prompt.txt")
    except Exception as e:
        print("Error generating prompt:", e)

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
