# 🔥 GlowUp AI — AI Photo Enhancement Demo

> Upload a photo → 5 AI agents enhance it → Download stunning results

## Architecture

```
📸 Photo Scout ──→ ✍️ Prompt Architect ──→ 🎨 Image Enhancer
     │                    │                       │
     │ (searches web      │ (writes the           │ (Nano Banana Pro
     │  for similar       │  perfect prompt       │  generates the
     │  pro photos)       │  using all inputs)    │  enhanced image)
     │                    │                       │
     ▼                    ▼                       ▼
 Web Search MCP     Prompt Library MCP     🔍 Quality Inspector
                                                  │
                                           (PASS? → 🖌️ Post-Production)
                                           (FAIL? → retry with fixed prompt)
```

## Quick Start

### 1. Get API Keys

| Service | URL | Time |
|---|---|---|
| **Gemini API** | [aistudio.google.com](https://aistudio.google.com) | 2 min |
| **Unsplash API** | [unsplash.com/developers](https://unsplash.com/developers) | 5 min |
| **Pexels API** | [pexels.com/api](https://www.pexels.com/api/) | 5 min |

### 2. Setup

```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux
pip install -r requirements.txt

# Create your .env file
copy ..\.env.example ..\.env
# Then edit ..\.env and paste your API keys

# Frontend
cd ../frontend
npm install
```

### 3. Run

```bash
# Terminal 1: Backend
cd backend
python main.py
# → http://localhost:8000/docs

# Terminal 2: Frontend
cd frontend
npm run dev
# → http://localhost:3000
```

### 4. Test with curl

```bash
# Enhance a photo (2 variations)
curl -X POST http://localhost:8000/api/enhance \
  -F "file=@your_photo.jpg" \
  -F "num_variations=2"

# Enhance with a vibe
curl -X POST http://localhost:8000/api/enhance \
  -F "file=@your_photo.jpg" \
  -F "vibe=coffee_shop" \
  -F "num_variations=2"
```

## Project Structure

```
backend/
├── main.py                 # FastAPI server
├── pipeline.py             # Orchestrator (runs all 5 agents)
├── config.py               # Config + .env loader
├── agents/
│   ├── photo_scout.py      # 📸 Finds reference photos from web
│   ├── prompt_architect.py # ✍️ Writes optimal enhancement prompts
│   ├── image_enhancer.py   # 🎨 Generates images via Nano Banana Pro
│   ├── quality_inspector.py# 🔍 Evaluates quality with separate model
│   └── post_production.py  # 🖌️ Applies realism post-processing
├── mcp_servers/
│   ├── web_search.py       # Unsplash + Pexels APIs
│   ├── image_analysis.py   # Gemini vision analysis
│   ├── prompt_library.py   # Local JSON prompt store
│   └── storage.py          # Local filesystem storage
├── outputs/                # Generated images saved here
└── requirements.txt

frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx        # Main page: upload → enhance → download
│   │   ├── layout.tsx      # Root layout with metadata
│   │   └── globals.css     # Design system + animations
│   └── components/
│       ├── PhotoUploader.tsx    # Drag & drop upload
│       ├── VibeSelector.tsx     # Optional vibe picker
│       ├── ProgressDisplay.tsx  # Pipeline stage animation
│       └── ResultGallery.tsx    # Results + download buttons
├── next.config.ts          # API proxy to backend
└── package.json
```

## How It Works

1. **Photo Scout** analyzes your photo (face, pose, setting, lighting) using Gemini, then searches Unsplash/Pexels for similar professional photos
2. **Prompt Architect** studies your photo + the scouted references + past successful prompts, then writes a highly specific enhancement prompt
3. **Image Enhancer** sends everything to Nano Banana Pro to generate the enhanced image
4. **Quality Inspector** evaluates the result using a SEPARATE Gemini model (catches artifacts the generator misses)
   - If FAIL → sends issues back to Prompt Architect for prompt rewriting → retry
   - If PASS → continues to Post-Production
5. **Post-Production** applies realism layers: vignette, sensor noise, color shift, JPEG compression, iPhone EXIF data

## Status

- [x] Backend: All agents + MCP servers + pipeline
- [x] Frontend: Next.js + Tailwind CSS UI
- [ ] End-to-end testing with live API keys
