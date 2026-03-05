# 💘 Hinge Assistant — AI Profile Analyst

> Upload your Hinge screenshots → 2 AI Agents analyze the profile → Get actionable, brutal feedback & better prompts.

## The Pivot
Previously "GlowUp AI" (an AI photo generation tool), this project has successfully **pivoted** to a **Dating Profile Analysis Assistant**. Instead of generating deepfakes, we now extract real data from user screenshots using Vision Models to provide elite dating coach advice, tailored prompts, and direct feedback on how to improve the current profile.

## Architecture

```
📸 Screenshot Scout ──→ 🧠 Profile Reviewer ──→ 📊 Frontend Dashboard
     │                        │                       │
     │ (Uses Gemini Vision    │ (Acts as an Elite     │ (Displays formatted
     │  to extract text,      │  Dating Coach to      │  review, photo feedback
     │  prompts, and photo    │  critique and score)  │  and prompt suggestions)
     │  descriptions)         │                       │
     ▼                        ▼                       ▼
  Gemini 2.5 Flash         Gemini 2.5 Flash        Next.js + Tailwind
```

## Quick Start

### 1. Get API Keys
You will need a [Gemini API Key](https://aistudio.google.com/app/apikey). You can provide a comma-separated list of keys to evade rate-limiting.

### 2. Setup

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt

# Create your .env file
# GEMINI_API_KEYS=key1,key2,key3
```

```bash
# Frontend
cd frontend
npm install
```

### 3. Run

```bash
# Terminal 1: Backend
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
# → http://localhost:8000/docs

# Terminal 2: Frontend
cd frontend
npm run dev
# → http://localhost:3000
```

## How It Works

1. **Screenshot Scout** analyzes the uploaded screenshots using Gemini 2.5 Flash Vision. It parses out the bio, user properties, the exact Hinge prompts, and detailed descriptions of what the photos look like.
2. **Profile Reviewer** takes the parsed data and acts as an elite dating coach for 2024/2025. It evaluates the structure of the profile, writes custom openers, and crafts improved answers to top-tier Hinge prompts based on the user's vibe.
3. **Frontend Dashboard** dynamically renders the JSON analysis returned by the backend into a beautiful UI, outlining photo-by-photo scores and specific prompt rewrites.

## Status

- [x] Backend: ScreenshotScout + ProfileReviewer Agents
- [x] Frontend: Next.js + Tailwind CSS UI
- [x] Rate Limit Handling (Multi-API key rotation, payload compression)
- [x] End-to-end testing with Gemini Flash
