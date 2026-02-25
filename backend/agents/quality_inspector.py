"""Quality Inspector Agent — evaluates generated images using a SEPARATE model."""

from mcp_servers.image_analysis import ImageAnalysisMCP
from mcp_servers.prompt_library import PromptLibraryMCP
from config import config


class QualityInspectorAgent:
    """Agent that independently evaluates generated images for realism,
    identity match, naturalness, and AI detection risk.

    CRITICAL: Uses Gemini 2.5 Pro (a SEPARATE model from the generator)
    so it can catch artifacts that the generator systematically misses.

    MCP servers used:
        - Image Analysis MCP (forensic-level comparison)
        - Prompt Library MCP (save successful prompt scores)
    """

    def __init__(self):
        self.analysis = ImageAnalysisMCP()
        self.library = PromptLibraryMCP()

    async def evaluate(
        self,
        generated_bytes: bytes,
        original_path: str,
    ) -> dict:
        """Evaluate a generated image against the original.

        Args:
            generated_bytes: The generated image as bytes
            original_path: Path to the original user photo

        Returns:
            Score dict with verdict, scores, issues, and fix_suggestions
        """
        # Use the Image Analysis MCP for the comparison
        score = await self.analysis.compare_photos(original_path, generated_bytes)

        # Apply our pass/fail criteria
        overall = score.get("overall", 0)
        ai_risk = score.get("ai_detection_risk", 10)

        # Override verdict based on our thresholds
        if overall >= config.QUALITY_THRESHOLD and ai_risk <= config.AI_DETECTION_MAX:
            score["verdict"] = "PASS"
        else:
            score["verdict"] = "FAIL"

        return score

    async def save_result(
        self,
        prompt: str,
        score: dict,
        scenario: str = "",
        photo_description: str = "",
    ):
        """Save a successful prompt result to the library for future learning."""
        if score.get("verdict") == "PASS":
            await self.library.save_prompt_result(
                prompt=prompt,
                score=score.get("overall", 0),
                scenario=scenario,
                photo_description=photo_description,
            )
