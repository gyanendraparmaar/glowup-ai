# GlowUp AI - Project Analysis & Improvement Roadmap

## What It Does

GlowUp AI is a dating app photo enhancer. Users upload photos and a 5-agent AI pipeline processes them to look professionally shot and naturally realistic.

**User Flow:** Upload photo → Select optional vibe → Watch 5-stage pipeline → Download enhanced images

---

## Architecture Overview

```
frontend/          Next.js 16 + React 19 + Tailwind CSS v4
backend/
  main.py          FastAPI entry point
  pipeline.py      5-agent orchestrator
  config.py        API key management + constants
  agents/          5 specialized AI agents (sequential pipeline)
  mcp_servers/     Reusable tool abstractions (search, storage, vision)
  outputs/         Generated images (runtime)
```

### 5-Agent Pipeline

| # | Agent | Role |
|---|-------|------|
| 1 | Photo Scout | Analyzes user photo, finds reference images via Unsplash/Pexels |
| 2 | Prompt Architect | Crafts detailed generation prompt using photo + references + past patterns |
| 3 | Image Enhancer | Runs Gemini image generation with retry + exponential backoff |
| 4 | Quality Inspector | Evaluates realism, identity match, AI detection risk (pass/fail) |
| 5 | Post Production | Applies vignette, noise, color shift, JPEG compression, EXIF injection |

---

## Tech Stack

**Backend:** Python, FastAPI, Uvicorn, Google Gemini 2.0 Flash, Pillow, NumPy, piexif, httpx, tenacity
**Frontend:** Next.js 16, React 19, TypeScript 5, Tailwind CSS v4
**External APIs:** Gemini (text + image generation), Unsplash, Pexels

---

## Strengths

- Clean separation of concerns — each agent solves one problem
- Smart quality loop: quality inspector uses a separate model to avoid generator bias, and failed images retry with specific fix suggestions
- Post-production realism layer (vignette, sensor noise, color shift, real EXIF metadata)
- Polished frontend with glassmorphism design, drag-and-drop, progress stages, side-by-side comparison
- API key rotation and tenacity retry logic for surviving free-tier rate limits

---

## Issues Found

### Critical

| Issue | Location | Details |
|-------|----------|---------|
| Synchronous blocking in async context | All 5 agents | Tenacity retry waits (15-120s) block the FastAPI worker thread, causing timeouts under load |
| No file size/content validation | `main.py:65-66` | Only checks `content_type` string — no actual file validation or size cap |
| No rate limiting | `main.py` | `/api/enhance` has zero per-IP protection; trivial to spam |

### Medium

| Issue | Location | Details |
|-------|----------|---------|
| CORS wildcard | `main.py:26` | `allow_origins=["*"]` — anti-pattern for any deployed environment |
| Error messages expose internals | `main.py:105` | Raw exception strings sent to client reveal model names and retry logic |
| Prompt library not thread-safe | `mcp_servers/prompt_library.py` | JSON file storage with no locking — concurrent writes can corrupt |
| Unpinned dependencies | `requirements.txt` | Core packages like `fastapi`, `uvicorn`, `tenacity` have no version pins |

### Low

| Issue | Location | Details |
|-------|----------|---------|
| Silent JSON parse failures | `mcp_servers/image_analysis.py:72-90` | Falls back to defaults on bad Gemini JSON with no logging |
| Magic numbers scattered | Multiple agents | Retry counts, temperature ranges, JPEG quality not defined as constants |
| No docstrings | Most functions | Limited inline documentation |
| Reference photo cache unbounded | `mcp_servers/web_search.py` | MD5-keyed cache grows indefinitely with no eviction |

---

## Scopes for Improvement

### 1. Async Pipeline (High Impact)

The pipeline blocks a thread for minutes during retries. Fix: offload to a task queue.

```
Current:  POST /api/enhance → blocks worker until done (2-10 min)
Target:   POST /api/enhance → returns job_id immediately
          GET  /api/status/{job_id} → poll for progress
          WebSocket /api/ws/{job_id} → real-time stage updates
```

Tools: Celery + Redis, or Python `asyncio.run_in_executor` for a simpler approach.

---

### 2. Input Validation & Security

- Add `python-magic` or header-byte inspection to validate actual image content
- Add file size cap (e.g., 20MB) in FastAPI before processing
- Add per-IP rate limiting with `slowapi` (wraps FastAPI)
- Replace `allow_origins=["*"]` with specific allowed origins
- Sanitize error messages before returning to client

```python
# Quick win — add to main.py
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/enhance")
@limiter.limit("5/minute")
async def enhance(request: Request, ...):
    ...
```

---

### 3. Proper Storage Layer

Currently: local JSON prompt library + local `outputs/` folder.

Upgrade path:
- **Prompt library:** SQLite (via SQLAlchemy) as a drop-in replacement — adds ACID, concurrent writes, query capabilities
- **Generated images:** Object storage (S3, Cloudflare R2, or even MinIO locally) with signed URLs instead of serving from FastAPI
- **Cache:** Redis with TTL instead of in-memory dict (survives restarts, bounded size)

---

### 4. Observability

Zero logging or monitoring currently. Minimum viable setup:

```python
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In pipeline.py
logger.info("pipeline.start", extra={"job_id": job_id, "num_photos": len(files)})
logger.info("agent.complete", extra={"agent": "photo_scout", "duration_ms": elapsed})
logger.error("agent.failed", extra={"agent": "image_enhancer", "error": str(e)})
```

For production: structured JSON logs → Loki/Datadog/CloudWatch.

---

### 5. Dependency Pinning

`requirements.txt` uses unpinned or `>=` constraints. Switch to exact pins generated via `pip freeze` after testing, or at minimum use `~=` (compatible release):

```
fastapi~=0.115.0
uvicorn[standard]~=0.34.0
tenacity~=9.0.0
google-genai~=1.0.0
Pillow~=11.0.0
```

Add a `requirements-dev.txt` for testing tools.

---

### 6. Test Coverage

No tests exist. Recommended starting points:

- **Unit tests:** Mock Gemini API responses and test each agent's input/output contract
- **Integration tests:** Run the full pipeline against a local stub (no real API calls)
- **End-to-end:** Use a dedicated test Gemini key + small test image set (6 photos already in `test_photos/`)

Framework: `pytest` + `pytest-asyncio` + `respx` for httpx mocking.

---

### 7. API Key Management

Current key rotation using `random.choice()` across multiple keys is a workaround. Proper approach:

- Use a single key per environment and request a higher quota tier
- If multiple keys are needed (different billing accounts for dev/staging/prod), manage them via environment config per deployment, not random rotation in code
- Store keys in a secrets manager (AWS Secrets Manager, HashiCorp Vault, or GCP Secret Manager) instead of `.env` files

---

### 8. Frontend Improvements

- Hardcoded `localhost:8000` in `next.config.ts` — parameterize via `NEXT_PUBLIC_API_URL` environment variable
- No error boundary in React — a failed API call crashes the whole UI
- No loading skeleton on results once pipeline completes
- Image download uses `<a>` with URL — doesn't work once images move to object storage; implement a signed URL endpoint

---

### 9. Model Configuration

`NUM_VARIATIONS` is in `config.py` but not exposed in the UI. Consider:
- Expose as a user setting (currently clamped 1-4 in backend, UI shows slider but may not wire correctly)
- Add per-request override via API body so frontend can pass user choice dynamically

---

### 10. EXIF Metadata

Post-production always injects iPhone 15 Pro Max EXIF regardless of the original photo device. Consider:
- Preserving original EXIF when not changing the device context
- Or stripping EXIF entirely (privacy-friendly default) with an opt-in for metadata injection

---

## Priority Order

| Priority | Scope | Effort | Impact |
|----------|-------|--------|--------|
| 1 | Input validation + rate limiting | Low | High |
| 2 | Async task queue (non-blocking pipeline) | Medium | High |
| 3 | Dependency pinning | Very Low | Medium |
| 4 | Logging + error message sanitization | Low | Medium |
| 5 | Thread-safe storage (SQLite prompt library) | Low | Medium |
| 6 | Frontend API URL via env var | Very Low | Medium |
| 7 | Test suite (unit + integration) | High | High |
| 8 | Object storage for outputs | Medium | Medium |
| 9 | CORS origin restriction | Very Low | Low |
| 10 | API key management refactor | Low | Low |
