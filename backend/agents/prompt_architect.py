"""Prompt Architect Agent — analyzes all inputs and writes the perfect prompt."""

from PIL import Image
import google.genai as genai
from mcp_servers.prompt_library import PromptLibraryMCP
from config import config


client = genai.Client(api_key=config.GEMINI_API_KEY)


class PromptArchitectAgent:
    """Agent that takes the user's photo, scouted references, and optional
    vibe selection, then writes a highly detailed enhancement prompt for
    the Image Enhancer agent.

    MCP servers used:
        - Prompt Library MCP (retrieve successful past prompts + realism rules)
    """

    def __init__(self):
        self.library = PromptLibraryMCP()

    async def generate_prompt(
        self,
        original_path: str,
        reference_paths: list[str],
        mode: str = "enhance",
        vibe: str | None = None,
        photo_analysis: dict | None = None,
    ) -> str:
        """Generate a detailed enhancement prompt by analyzing all inputs.

        Args:
            original_path: Path to user's original photo
            reference_paths: Paths to scouted reference images
            mode: "enhance" (improve as-is) or "vibe" (change setting)
            vibe: Optional vibe name if mode is "vibe"
            photo_analysis: Optional pre-computed analysis from Photo Scout

        Returns:
            Detailed enhancement prompt string
        """
        # Get realism rules and past successful patterns
        realism_rules = await self.library.get_realism_rules()
        scenario = f"{vibe}_vibe" if vibe else "default_enhance"
        past_prompts = await self.library.get_successful_prompts(scenario, limit=2)
        enhancement_patterns = await self.library.get_enhancement_patterns()

        # Build the contents list for Gemini
        contents = []

        # Add user's original photo
        user_photo = Image.open(original_path)
        contents.append(user_photo)

        # Add reference photos (up to 3, to stay within context limits)
        ref_images = []
        for ref_path in reference_paths[:3]:
            try:
                ref_img = Image.open(ref_path)
                ref_images.append(ref_img)
                contents.append(ref_img)
            except Exception:
                continue

        # Build the analysis instruction
        if mode == "vibe" and vibe:
            task = f"""You are an expert AI prompt engineer specializing in photo-realistic
            image generation. You have been given:

            - Image 1: The user's ORIGINAL photo (this person's identity must be preserved)
            - Images 2-{1 + len(ref_images)}: Professional REFERENCE photos found from the web
              (use these for composition, lighting, and setting inspiration ONLY — NOT their identity)

            TASK: Write a detailed image generation prompt that creates a NEW image of the
            person from Image 1 in a "{vibe}" setting/vibe.

            - PRESERVE: The person's face, skin tone, body type, and identity from Image 1
            - CHANGE: Setting, lighting, and composition inspired by the reference photos
            - The result must look like a REAL photo taken by a friend with an iPhone"""
        else:
            task = f"""You are an expert AI prompt engineer specializing in photo-realistic
            image enhancement. You have been given:

            - Image 1: The user's ORIGINAL photo (enhance THIS scene)
            - Images 2-{1 + len(ref_images)}: Professional REFERENCE photos found from the web
              (use these for lighting and quality inspiration ONLY)

            TASK: Write a detailed image ENHANCEMENT prompt that recreates the SAME scene
            from Image 1 but with dramatically better:
            - Lighting (fix issues, add warmth, natural golden tones)
            - Composition (better framing if needed)
            - Skin/facial quality (clearer, natural texture, NOT airbrushed)
            - Background (slightly cleaner, better bokeh)
            - Overall feel (more attractive, approachable, dating-app worthy)

            CRITICAL: Keep the SAME clothes, SAME setting, SAME pose, SAME person.
            Just make everything look much better — like a pro photographer was there.
            Study the reference photos for how professional lighting should look."""

        # Add past successful patterns if available
        past_context = ""
        if past_prompts:
            past_context = "\n\nHere are prompts that worked well for similar photos:\n"
            for p in past_prompts[:2]:
                past_context += f"- (score {p['score']}): {p['prompt'][:200]}...\n"

        # Add enhancement patterns
        patterns_text = "\n".join(f"- {p}" for p in enhancement_patterns)

        contents.append(f"""{task}

        {past_context}

        Include these proven enhancement patterns:
        {patterns_text}

        {realism_rules}

        Write the prompt in this exact format:

        SUBJECT: [describe the person — face, hair, skin tone, build, clothing from Image 1]
        SCENE: [describe the setting to recreate/create]
        LIGHTING: [specific lighting direction, quality, color temperature — inspired by references]
        CAMERA: [iPhone 15 Pro Max, f/1.78, natural depth-of-field]
        EXPRESSION: [specific expression direction]
        DETAILS: [specific details to include for maximum realism]
        AVOID: [things that would make it look AI-generated]

        Be EXTREMELY specific. Every detail matters for realism.
        The output must be indistinguishable from a real iPhone photo.
        """)

        response = client.models.generate_content(
            model=config.PROMPT_MODEL,
            contents=contents,
        )

        return response.text

    async def fix_prompt(
        self,
        original_path: str,
        original_prompt: str,
        issues: list[str],
        vibe: str | None = None,
    ) -> str:
        """Rewrite a prompt to fix specific quality issues found by the Inspector.

        Args:
            original_path: Path to user's original photo
            original_prompt: The prompt that produced the failed image
            issues: List of specific issues to fix
            vibe: Optional vibe if in vibe mode

        Returns:
            Rewritten prompt that addresses the issues
        """
        photo = Image.open(original_path)
        issues_text = "\n".join(f"- {issue}" for issue in issues)

        # Pre-compute realism rules (can't await inside f-string)
        realism_rules = await self.library.get_realism_rules()
        vibe_instruction = f"The desired vibe is: {vibe}" if vibe else "Enhance the existing scene."

        response = client.models.generate_content(
            model=config.PROMPT_MODEL,
            contents=[
                photo,
                f"""The previous enhancement prompt produced an image with these issues:
                {issues_text}

                Original prompt was:
                {original_prompt}

                Rewrite the prompt to specifically FIX these issues.
                Add EXPLICIT instructions to avoid each listed problem.
                Keep everything else the same — only fix the problems.

                {vibe_instruction}

                {realism_rules}
                """,
            ],
        )

        return response.text
