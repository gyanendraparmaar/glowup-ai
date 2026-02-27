from __future__ import annotations
"""Pipeline Orchestrator — runs the full 5-agent enhancement pipeline."""

from agents.photo_scout import PhotoScoutAgent
from agents.prompt_architect import PromptArchitectAgent
from agents.image_enhancer import ImageEnhancerAgent
from agents.quality_inspector import QualityInspectorAgent
from agents.post_production import PostProductionAgent
from config import config


async def run_enhancement_pipeline(
    original_path: str,
    mode: str = "enhance",
    vibe: str | None = None,
    output_dir: str | None = None,
    job_id: str = "demo",
    num_variations: int | None = None,
    max_retries: int | None = None,
) -> list[str]:
    """Run the full 5-agent enhancement pipeline.

    This is the Orchestrator — it coordinates all agents sequentially:
        1. Photo Scout → finds reference images from the web
        2. Prompt Architect → writes the enhancement prompt using all inputs
        3. Image Enhancer → generates enhanced images using Nano Banana Pro
        4. Quality Inspector → evaluates each image with a SEPARATE model
            → If FAIL: loops back to Prompt Architect for prompt rewrite
        5. Post-Production → applies realism post-processing

    Args:
        original_path: Path to the user's uploaded photo
        mode: "enhance" (default) or "vibe"
        vibe: Optional vibe name (e.g. "coffee_shop")
        output_dir: Where to save results (defaults to config)
        job_id: Unique job identifier
        num_variations: How many variations to generate
        max_retries: Max retry attempts per variation

    Returns:
        List of file paths to the final enhanced images
    """
    output_dir = output_dir or config.OUTPUT_DIR
    num_variations = num_variations or config.NUM_VARIATIONS
    max_retries = max_retries or config.MAX_RETRIES

    # Initialize all agents
    scout = PhotoScoutAgent()
    architect = PromptArchitectAgent()
    enhancer = ImageEnhancerAgent()
    inspector = QualityInspectorAgent()
    post_prod = PostProductionAgent()

    # ═══════════════════════════════════════════════════════════════
    # STEP 1: Photo Scout — find reference images from the web
    # ═══════════════════════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("📸 STEP 1: Photo Scout Agent")
    print("=" * 60)
    references = await scout.find_references(original_path, vibe=vibe)
    photo_analysis = scout.last_analysis
    print(f"   Found {len(references)} reference images")
    if photo_analysis:
        setting = photo_analysis.get("setting", "unknown")
        lighting = photo_analysis.get("lighting", {}).get("quality", "unknown")
        print(f"   Photo analysis: setting={setting}, lighting={lighting}")

    results = []

    for i in range(num_variations):
        print(f"\n{'─' * 60}")
        print(f"  Variation {i + 1}/{num_variations}")
        print(f"{'─' * 60}")

        # ═══════════════════════════════════════════════════════════
        # STEP 2: Prompt Architect — write the enhancement prompt
        # ═══════════════════════════════════════════════════════════
        print("\n  ✍️  STEP 2: Prompt Architect Agent")
        prompt = await architect.generate_prompt(
            original_path,
            references,
            mode=mode,
            vibe=vibe,
            photo_analysis=photo_analysis,
        )
        print(f"     Prompt generated ({len(prompt)} chars)")
        print(f"     Preview: {prompt[:120]}...")

        # ═══════════════════════════════════════════════════════════
        # STEP 3 + 4: Image Enhancer + Quality Inspector (with retries)
        # ═══════════════════════════════════════════════════════════
        enhanced_bytes = None

        for attempt in range(max_retries + 1):
            # --- Step 3: Generate ---
            print(f"\n  🎨 STEP 3: Image Enhancer Agent (attempt {attempt + 1}/{max_retries + 1})")
            enhanced_bytes = await enhancer.enhance(
                original_path,
                prompt,
                references,
                temperature=0.75 + (i * 0.05),
            )

            if not enhanced_bytes:
                print("     ⚠️ Empty result from generator")
                continue

            print(f"     Generated image: {len(enhanced_bytes):,} bytes")

            # --- Step 4: Quality Check ---
            print(f"\n  🔍 STEP 4: Quality Inspector Agent")
            score = await inspector.evaluate(enhanced_bytes, original_path)

            overall = score.get("overall", 0)
            ai_risk = score.get("ai_detection_risk", 10)
            verdict = score.get("verdict", "FAIL")
            issues = score.get("issues", [])

            print(f"     Overall: {overall}/10")
            print(f"     AI Detection Risk: {ai_risk}/10")
            print(f"     Verdict: {'✅ PASS' if verdict == 'PASS' else '❌ FAIL'}")

            if verdict == "PASS":
                # Save successful prompt to library for future learning
                scenario = f"{vibe}_vibe" if vibe else "default_enhance"
                await inspector.save_result(prompt, score, scenario)
                print("     📚 Prompt saved to library for future learning")
                break

            # Show failure reasons
            if issues:
                print(f"     Issues: {', '.join(issues[:3])}")

            # Retry: ask Prompt Architect to fix the prompt
            if attempt < max_retries:
                print(f"\n  🔄 Retrying — asking Prompt Architect to fix the prompt...")
                fix_inputs = score.get("fix_suggestions", []) + issues
                prompt = await architect.fix_prompt(
                    original_path, prompt, fix_inputs, vibe
                )
                print(f"     Prompt rewritten ({len(prompt)} chars)")

        if not enhanced_bytes:
            print(f"\n  ⚠️ Variation {i + 1} failed all attempts, skipping")
            continue

        # ═══════════════════════════════════════════════════════════
        # STEP 5: Post-Production — apply realism touches
        # ═══════════════════════════════════════════════════════════
        print(f"\n  🖌️  STEP 5: Post-Production Agent")
        final_path = f"{output_dir}/{job_id}_enhanced_{i + 1}.jpg"
        saved_path = await post_prod.process_and_save(enhanced_bytes, final_path)
        results.append(saved_path)
        print(f"     ✅ Saved: {saved_path}")

    print(f"\n{'=' * 60}")
    print(f"🎉 DONE! Generated {len(results)} enhanced images")
    print(f"{'=' * 60}\n")

    return results
