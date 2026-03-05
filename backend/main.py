from __future__ import annotations
"""GlowUp AI Demo — FastAPI Backend Server."""

import asyncio
import logging
import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pipeline import run_enhancement_pipeline
from config import config

logger = logging.getLogger("glowup.server")

# Ensure output directory exists
os.makedirs(config.OUTPUT_DIR, exist_ok=True)

app = FastAPI(
    title="GlowUp AI Demo",
    description="AI-powered photo enhancement — 5 agents make your photos stunning",
    version="0.2.0",
)

# ── CORS — restricted to configured origins ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ── Rate Limiting ──────────────────────────────────────────────────
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded

    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    HAS_RATE_LIMITER = True
    logger.info("Rate limiting enabled: %s", config.RATE_LIMIT)
except ImportError:
    HAS_RATE_LIMITER = False
    logger.warning("slowapi not installed — rate limiting disabled")

    # No-op decorator fallback
    class _NoOpLimiter:
        def limit(self, _rule):
            def decorator(func):
                return func
            return decorator
    limiter = _NoOpLimiter()

# Serve generated images
app.mount("/outputs", StaticFiles(directory=config.OUTPUT_DIR), name="outputs")


# ── In-memory job store (async pipeline) ───────────────────────────
_jobs: dict[str, dict] = {}


def _validate_image_bytes(content: bytes) -> bool:
    """Validate that file content starts with a recognized image magic byte sequence."""
    # JPEG: FF D8 FF
    # PNG: 89 50 4E 47
    # WEBP: 52 49 46 46 ... 57 45 42 50
    if content[:3] == b"\xff\xd8\xff":
        return True
    if content[:4] == b"\x89PNG":
        return True
    if content[:4] == b"RIFF" and content[8:12] == b"WEBP":
        return True
    return False


@app.get("/")
async def root():
    return {
        "message": "GlowUp AI Demo API",
        "docs": "/docs",
        "endpoints": {
            "POST /api/enhance": "Upload a photo and start enhancement (returns job_id)",
            "GET /api/status/{job_id}": "Check enhancement job status",
            "GET /api/download/{filename}": "Download an enhanced image",
        },
    }


@app.post("/api/enhance")
@limiter.limit(config.RATE_LIMIT)
async def enhance_photo(
    request: Request,
    file: UploadFile = File(..., description="The photo to enhance"),
    vibe: str = Form(default=None, description="Optional vibe: coffee_shop, outdoors, formal, etc."),
    num_variations: int = Form(default=2, description="Number of variations (1-4)"),
):
    """Upload a photo and start the 5-agent enhancement pipeline.

    Returns a job_id immediately. Poll /api/status/{job_id} for progress.
    """
    # ── Content-type validation ────────────────────────────────────
    if not file.content_type or file.content_type not in config.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(config.ALLOWED_IMAGE_TYPES)}",
        )

    # ── Read and validate file size ────────────────────────────────
    content = await file.read()

    if len(content) > config.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {config.MAX_UPLOAD_SIZE_MB}MB",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    # ── Magic byte validation ──────────────────────────────────────
    if not _validate_image_bytes(content):
        raise HTTPException(
            status_code=400,
            detail="File content does not match a supported image format",
        )

    # Clamp variations
    num_variations = max(1, min(4, num_variations))

    # Save uploaded file
    job_id = str(uuid.uuid4())[:8]
    upload_path = os.path.join(config.OUTPUT_DIR, f"{job_id}_original.jpg")
    with open(upload_path, "wb") as f:
        f.write(content)

    logger.info(
        "job.created job_id=%s mode=%s variations=%d size_kb=%d",
        job_id,
        f"vibe({vibe})" if vibe else "enhance",
        num_variations,
        len(content) // 1024,
    )

    # ── Launch pipeline as background task ─────────────────────────
    _jobs[job_id] = {"status": "processing", "stage": 0, "images": [], "error": None}

    asyncio.create_task(_run_job(job_id, upload_path, vibe, num_variations))

    return {
        "job_id": job_id,
        "status": "processing",
        "poll_url": f"/api/status/{job_id}",
    }


async def _run_job(job_id: str, upload_path: str, vibe: str | None, num_variations: int):
    """Run the pipeline in the background and update job status."""
    try:
        result_paths = await run_enhancement_pipeline(
            original_path=upload_path,
            mode="vibe" if vibe else "enhance",
            vibe=vibe,
            output_dir=config.OUTPUT_DIR,
            job_id=job_id,
            num_variations=num_variations,
        )

        _jobs[job_id] = {
            "status": "done",
            "stage": 5,
            "original": f"/outputs/{job_id}_original.jpg",
            "images": [f"/outputs/{os.path.basename(p)}" for p in result_paths],
            "count": len(result_paths),
            "error": None,
        }
        logger.info("job.done job_id=%s images=%d", job_id, len(result_paths))

    except Exception as e:
        logger.error("job.failed job_id=%s error=%s", job_id, str(e))
        _jobs[job_id] = {
            "status": "error",
            "stage": 0,
            "images": [],
            "error": "Enhancement failed. Please try again.",
        }


@app.get("/api/status/{job_id}")
async def job_status(job_id: str):
    """Check the status of an enhancement job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **job}


@app.get("/api/download/{filename}")
async def download_image(filename: str):
    """Download a single enhanced image as JPEG."""
    # Prevent path traversal
    safe_name = os.path.basename(filename)
    path = os.path.join(config.OUTPUT_DIR, safe_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=safe_name,
        headers={"Content-Disposition": f'attachment; filename="glowup_{safe_name}"'},
    )


# ── Backwards-compatible synchronous endpoint ─────────────────────
@app.post("/api/enhance/sync")
@limiter.limit(config.RATE_LIMIT)
async def enhance_photo_sync(
    request: Request,
    file: UploadFile = File(..., description="The photo to enhance"),
    vibe: str = Form(default=None, description="Optional vibe: coffee_shop, outdoors, formal, etc."),
    num_variations: int = Form(default=2, description="Number of variations (1-4)"),
):
    """Synchronous version — blocks until pipeline completes. Used by the frontend."""
    # ── Content-type validation ────────────────────────────────────
    if not file.content_type or file.content_type not in config.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(config.ALLOWED_IMAGE_TYPES)}",
        )

    content = await file.read()

    if len(content) > config.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {config.MAX_UPLOAD_SIZE_MB}MB",
        )

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if not _validate_image_bytes(content):
        raise HTTPException(
            status_code=400,
            detail="File content does not match a supported image format",
        )

    num_variations = max(1, min(4, num_variations))

    job_id = str(uuid.uuid4())[:8]
    upload_path = os.path.join(config.OUTPUT_DIR, f"{job_id}_original.jpg")
    with open(upload_path, "wb") as f:
        f.write(content)

    logger.info(
        "job.sync job_id=%s mode=%s variations=%d",
        job_id,
        f"vibe({vibe})" if vibe else "enhance",
        num_variations,
    )

    try:
        result_paths = await run_enhancement_pipeline(
            original_path=upload_path,
            mode="vibe" if vibe else "enhance",
            vibe=vibe,
            output_dir=config.OUTPUT_DIR,
            job_id=job_id,
            num_variations=num_variations,
        )

        return {
            "job_id": job_id,
            "status": "done",
            "original": f"/outputs/{job_id}_original.jpg",
            "images": [f"/outputs/{os.path.basename(p)}" for p in result_paths],
            "count": len(result_paths),
        }

    except Exception as e:
        logger.error("job.sync.failed job_id=%s error=%s", job_id, str(e))
        raise HTTPException(
            status_code=500,
            detail="Enhancement failed. Please try again.",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
