import asyncio
import os
from agents.image_enhancer import ImageEnhancerAgent

# Prompts matched roughly to typical names
PROMPTS = {
    # Houseboat
    "user_test_original.jpg": "Young man with dark hair, wearing sunglasses, a light blue/white short-sleeve button-up shirt, grey shorts, and dark sneakers with bright green accents. Fully forward, hands in pockets. Tropical backwaters, large yellow traditional wooden houseboat on the water, calm water reflections, green palm trees on the horizon, pile of coconuts on the foreground bank. Golden hour sunlight, soft natural dimensional lighting, cinematic rim light on the subject, rich warm tones. Shot on 35mm lens, f/2.8, shallow depth of field, sharp subject focus, cinematic composition, high-end travel photography style. Relaxed, confident, slight natural smile, looking directly at the camera. High resolution, intricate textures on the wooden boat, crisp water ripples, vibrant realistic foliage, extremely photorealistic skin texture. No UI elements, text overlays, or icons.",
    
    # Washroom Selfie
    "0051539e_original.jpg": "Young man taking a mirror selfie, dark hair, wearing a white sleeveless graphic t-shirt, beige cargo pants, bright neon green sneakers, holding a black smartphone. Clean public washroom environment with a long mirror, row of sleek sinks, tiled beige walls, wall-mounted oscillating fan, overhead recessed lighting. Clean, bright studio-quality interior lighting, flattering soft fill light on the face and body. Mirror selfie perspective, 24mm equivalent, f/4, crisp entire scene focus, professional architectural interior photography style mixed with high-end lifestyle portraiture. Cool, confident, neutral yet strong gaze into the mirror. Ultra-realistic reflections, sharp clothing textures, pristine tile surfaces, enhanced image clarity.",

    # Historic Architecture
    "261c8c68_original.jpg": "Young man, wearing an olive green open-knit long-sleeve sweater, a thin silver chain necklace, beige cargo pants, bright neon green sneakers, and dark sunglasses. Head is turned looking to the left, hands in pockets. Grand, ornate Victorian Gothic railway station (Chhatrapati Shivaji Maharaj Terminus) in the background with intricate stonework, clock tower, domes, palm trees, wide paved square, people in the distance, clear blue sky. Late afternoon sunlight, beautiful soft golden hour glow illuminating the historic architecture, flattering dramatic side-lighting on the subject's face and sweater, cinematic contrast. 50mm lens, f/2.0, beautiful bokeh separating the subject from the bustling background, tack-sharp focus on the subject, high-end street style fashion photography. Candid, observational, confident and contemplative profile. Extremely detailed architectural masonry in the background."
}

async def main():
    enhancer = ImageEnhancerAgent()
    
    input_dir = "outputs"
    output_dir = "test_i2i_results"
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, prompt in PROMPTS.items():
        original_path = os.path.join(input_dir, filename)
        if not os.path.exists(original_path):
            print(f"File {original_path} not found.")
            continue
            
        print(f"Enhancing {filename}...")
        try:
            enhanced_bytes = await enhancer.enhance(
                original_path=original_path,
                prompt=prompt,
                temperature=0.75
            )
            
            if enhanced_bytes:
                out_path = os.path.join(output_dir, f"enhanced_{filename}")
                with open(out_path, "wb") as f:
                    f.write(enhanced_bytes)
                print(f"Saved {out_path}")
            else:
                print(f"Failed to enhance {filename}")
        except Exception as e:
            print(f"Error on {filename}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
