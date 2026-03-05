from __future__ import annotations
"""Pipeline Orchestrator — runs the full 5-agent enhancement pipeline."""

import logging
from agents.photo_scout import PhotoScoutAgent
from agents.prompt_architect import PromptArchitectAgent
from agents.image_enhancer import ImageEnhancerAgent
from agents.quality_inspector import QualityInspectorAgent
from agents.post_production import PostProductionAgent
from config import config

logger = logging.getLogger("glowup.pipeline")


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
        1. Photo Scout -> finds reference images from the web
        2. Prompt Architect -> writes the enhancement prompt using all inputs
        3. Image Enhancer -> generates enhanced images
        4. Quality Inspector -> evaluates each image with a SEPARATE model
            -> If FAIL: loops back to Prompt Architect for prompt rewrite
        5. Post-Production -> applies realism post-processing

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

    # ═══ STEP 1: Photo Scout ═══
    logger.info("pipeline.step1 job=%s action=photo_scout", job_id)
    references = await scout.find_references(original_path, vibe=vibe)
    photo_analysis = scout.last_analysis
    logger.info(
        "pipeline.step1.done job=%s refs=%d setting=%s lighting=%s",
        job_id, len(references),
        photo_analysis.get("setting", "unknown"),
        photo_analysis.get("lighting", {}).get("quality", "unknown"),
    )

    results = []

    for i in range(num_variations):
        logger.info("pipeline.variation job=%s variation=%d/%d", job_id, i + 1, num_variations)

        # ═══ STEP 2: Prompt Architect ═══
        logger.info("pipeline.step2 job=%s action=prompt_architect", job_id)
        prompt = await architect.generate_prompt(
            original_path,
            references,
            mode=mode,
            vibe=vibe,
            photo_analysis=photo_analysis,
        )
        logger.info("pipeline.step2.done job=%s prompt_chars=%d", job_id, len(prompt))

        # ═══ STEP 3 + 4: Image Enhancer + Quality Inspector (with retries) ═══
        enhanced_bytes = None
        temperature = config.BASE_TEMPERATURE + (i * config.TEMPERATURE_INCREMENT)

        for attempt in range(max_retries + 1):
            logger.info(
                "pipeline.step3 job=%s attempt=%d/%d temperature=%.2f",
                job_id, attempt + 1, max_retries + 1, temperature,
            )
            enhanced_bytes = await enhancer.enhance(
                original_path,
                prompt,
                references,
                temperature=temperature,
            )

            if not enhanced_bytes:
                logger.warning("pipeline.step3.empty job=%s attempt=%d", job_id, attempt + 1)
                continue

            logger.info("pipeline.step3.done job=%s size_bytes=%d", job_id, len(enhanced_bytes))

            # --- Step 4: Quality Check ---
            logger.info("pipeline.step4 job=%s action=quality_inspector", job_id)
            score = await inspector.evaluate(enhanced_bytes, original_path)

            overall = score.get("overall", 0)
            ai_risk = score.get("ai_detection_risk", 10)
            verdict = score.get("verdict", "FAIL")
            issues = score.get("issues", [])

            logger.info(
                "pipeline.step4.done job=%s overall=%s ai_risk=%s verdict=%s",
                job_id, overall, ai_risk, verdict,
            )

            if verdict == "PASS":
                scenario = f"{vibe}_vibe" if vibe else "default_enhance"
                await inspector.save_result(prompt, score, scenario)
                logger.info("pipeline.prompt_saved job=%s scenario=%s", job_id, scenario)
                break

            if issues:
                logger.info("pipeline.step4.issues job=%s issues=%s", job_id, ", ".join(issues[:3]))

            # Retry: ask Prompt Architect to fix the prompt
            if attempt < max_retries:
                logger.info("pipeline.retry job=%s attempt=%d", job_id, attempt + 1)
                fix_inputs = score.get("fix_suggestions", []) + issues
                prompt = await architect.fix_prompt(
                    original_path, prompt, fix_inputs, vibe
                )
                logger.info("pipeline.retry.rewritten job=%s prompt_chars=%d", job_id, len(prompt))

        if not enhanced_bytes:
            logger.warning("pipeline.variation.failed job=%s variation=%d", job_id, i + 1)
            continue

        # ═══ STEP 5: Post-Production ═══
        logger.info("pipeline.step5 job=%s action=post_production", job_id)
        final_path = f"{output_dir}/{job_id}_enhanced_{i + 1}.jpg"
        saved_path = await post_prod.process_and_save(
            enhanced_bytes, final_path, original_path=original_path
        )
        results.append(saved_path)
        logger.info("pipeline.step5.done job=%s saved=%s", job_id, saved_path)

    logger.info("pipeline.complete job=%s total_images=%d", job_id, len(results))
    return results
