# 💘 Hinge Assistant - Agent Handoff Log

This document serves as a comprehensive reference guide for future AI agents working on the Hinge Assistant codebase. It details the architectural decisions, the project pivot, critical bug fixes, API idiosyncrasies, and prompt engineering discoveries.

## 1. Project Pivot & Architecture
**Original Objective (GlowUp AI):** An AI image generator aiming to create realistic deepfakes of users to look more attractive using Nano Banana Pro. This direction was scrapped.
**Current Objective (Hinge Assistant):** A multi-agent web application that extracts data from user-uploaded Hinge profile screenshots and uses an elite dating coach prompt to synthesize actionable feedback, grade photos, rewrite prompt answers, and generate new pickup lines format.

**Tech Stack:**
*   **Frontend:** Next.js 14, React, Tailwind CSS, TypeScript. Features a modern UI with drag-and-drop file support, floating UI cards for photo/prompt review, and animated transitions.
*   **Backend:** Python 3.9+, FastAPI, Uvicorn.
*   **Vision Engine:** Google Gemini (`gemini-2.5-flash`). Used for extracting text and meticulously describing photos (`ScreenshotScoutAgent`).
*   **Reasoning Engine:** Google Gemini (`gemini-2.5-flash`). Used to apply 2024/2025 dating meta to the extracted data and provide a highly structured JSON critique (`ProfileReviewerAgent`).

## 2. API Limitations & Fixes

### A. Groq Vision Limitations (Model Decommissioned)
**The Issue:** The project originally utilized Groq's `llama-3.2-90b-vision-preview`. However, free-tier Groq API keys either faced `model_decommissioned` errors or total lack of access to any Vision models.
**The Fix:** Pivoted the `ScreenshotScoutAgent` to use `gemini-2.5-flash` for high-accuracy VLM capabilities.

### B. Gemini API Free-Tier Rate Limits (`429 RESOURCE_EXHAUSTED`)
**The Issue:** The Gemini API free tier has extremely strict RPM/RPD limits, specifically on Pro models (`gemini-2.5-pro` allows only 50 requests per day).
**The Fix:**
*   Switched the core backbone of both agents to `gemini-2.5-flash` which has a much larger free tier quota (1500 per day).
*   Implemented API Key rotation in the backend. If a `429` error is hit, the agent loops through a comma-separated list of keys in `GEMINI_API_KEYS`.
*   Moved from the modern (`google.genai`) SDK back to `google.generativeai` due to `NOT_FOUND` errors on the new experimental SDK for valid `1.5-flash` endpoints on Windows.

### C. 413 Payload Too Large (FastAPI & Vision APIs)
**The Issue:** Uploading high-res screenshots (e.g., iPhone 15 Pro Max) generated Base64 strings so massive that they triggered `413 Request Entity Too Large` errors when piped into early LLM iterations.
**The Fix:**
*   The `ScreenshotScoutAgent` implements an active compression step using `Pillow (PIL)`.
*   Images are stripped of alpha channels (`RGBA` to `RGB`), downscaled using `LANCZOS` resampling to a bounding box of 1600x1600, and converted to JPEG at 85% quality before Base64 encoding.

## 3. High-End Prompt Engineering Discoveries

### A. Structured JSON Enforcement
**The Issue:** Extracting actionable feedback requires strict JSON constraints, otherwise the frontend errors out trying to map generic markdown.
**The Fix:** The `ProfileReviewerAgent` embeds a raw skeletal JSON schema in the system prompt alongside the `response_mime_type="application/json"` config. It is specifically directed to analyze photos (via standard integer IDs), critique existing prompts, and offer dynamically generated prompt suggestions.

### B. Current Hinge Meta Injecting
**The Issue:** LLMs tend to be overly supportive or use outdated 2018 Tinder logic.
**The Fix:** The system prompt explicitly enforces harsh, constructive 2024/2025 meta (e.g., specific rules on the first photo being a clear smiling headshot, banning generic responses like "I love tacos and dogs", and restricting opening lines from being just "Hey").

## 4. Current State & Next Steps
*   The system successfully runs end-to-end processing 3+ screenshots concurrently in the frontend -> backend -> Gemini -> frontend flow.
*   The user's current testing was successful after fixing the server reload issue.
*   **Next step:** The core features are complete. Future work could involve expanding the types of supported dating apps (Bumble/Tinder), or adding an automated cropper feature.
