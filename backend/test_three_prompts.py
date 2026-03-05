import asyncio
import os
import io
from PIL import Image
from agents.prompt_architect import PromptArchitectAgent

async def main():
    architect = PromptArchitectAgent()
    
    # The 3 distinct original photos from the outputs dir
    img_files = ['user_test_original.jpg', '0051539e_original.jpg', '261c8c68_original.jpg']
    
    for filename in img_files:
        path = os.path.join("outputs", filename)
        if not os.path.exists(path):
            continue
            
        print(f"\n{'='*80}\n[IMAGE] {filename}\n{'='*80}")
        try:
            prompt = await architect.generate_prompt(
                path,
                reference_paths=[],
                mode="enhance",
            )
            print(prompt)
        except Exception as e:
            print(f"Error generating prompt for {filename}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
