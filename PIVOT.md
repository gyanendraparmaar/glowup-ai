# GlowUp AI ──→ Hinge Assistant (Project Pivot)

## 📌 Executive Summary
This project was originally conceptualized as **GlowUp AI**, an AI Image Enhancement Demo. The goal was to take user-uploaded dating profile photos and pass them through 5 AI agents (including *Nano Banana Pro*) to generate highly realistic, "glowed up" deepfakes of the user.

However, during development, the core value proposition shifted significantly. The project has undergone a complete **pivot**. 

The new application is **Hinge Assistant — AI Profile Analyst**.

## 🔄 What Changed?

### 1. From Image Generation to Dating Analysis
Instead of generating *fake* images that make a user look better, the app now acts as a brutal, elite dating coach that reviews the user's *actual* profile.
- Users upload screenshots of their Hinge profile.
- The AI extracts data (bio, age, job, prompts, photo descriptions).
- The AI critiques the photos, roasts bad prompts, and generates better, custom-tailored prompts/openers based on the user's overall "vibe".

### 2. Architecture & Agent Overhaul
The old architecture consisting of 5 agents (Photo Scout, Prompt Architect, Image Enhancer, Quality Inspector, Post-Production) has been entirely scrapped.
The new architecture relies on two powerful Vision-capable agents:
1. **Screenshot Scout (`screenshot_scout.py`)**: Uses `gemini-2.5-flash`'s vision capabilities to meticulously parse multiple profile screenshots into a structured JSON representation (detecting text, prompts, and deep-analyzing photo composition).
2. **Profile Reviewer (`profile_reviewer.py`)**: Uses `gemini-2.5-flash` with a strict "expert dating coach for 2024/2025" system prompt to synthesize the data into a brutal but actionable review, complete with scores and specific prompt rewrites.

### 3. Fixing API & Infrastructure Bottlenecks
During the pivot, we also resolved significant technical blockers:
- **Async Deadlocks**: Moved away from broken asynchronous image generation flows.
- **Vision Model Access**: Dropped Groq's `llama-3.2-90b-vision` due to API key restrictions (model decommissioned on free tiers).
- **Gemini Rate Limits (429)**: Standard `gemini-2.5-pro` keys frequently hit the 50 RPM limit. We introduced multi-key rotation and defaulted to the highly capable `gemini-2.5-flash` to guarantee high availability.
- **Payload Limits (413)**: Implemented strict client-side/server-side image compression (downscaling and JPEG conversion via Pillow) to ensure raw iPhone screenshots don't exceed HTTP payload limits.

## 📁 Updated Files
All relevant project files have been updated to reflect the new **Hinge Assistant** identity, including:
- `README.md`
- `AGENT_HANDOFF_LOG.md`
- Next.js Metadata (`layout.tsx`)
- Internal documentation & agent prompts.
