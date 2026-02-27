"""GlowUp AI Demo — FastAPI Backend Server."""

import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from pipeline import run_enhancement_pipeline
from config import config

# Ensure output directory exists
os.makedirs(config.OUTPUT_DIR, exist_ok=True)

app = FastAPI(
    title="GlowUp AI Demo",
    description="AI-powered photo enhancement — 5 agents make your photos stunning",
    version="0.1.0",
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated images
app.mount("/outputs", StaticFiles(directory=config.OUTPUT_DIR), name="outputs")


@app.get("/")
async def root():
    return {
        "message": "GlowUp AI Demo API",
        "docs": "/docs",
        "endpoints": {
            "POST /api/enhance": "Upload a photo and enhance it",
            "GET /api/download/{filename}": "Download an enhanced image",
        },
    }


@app.post("/api/enhance")
async def enhance_photo(
    file: UploadFile = File(..., description="The photo to enhance"),
    vibe: str = Form(default=None, description="Optional vibe: coffee_shop, outdoors, formal, etc."),
    num_variations: int = Form(default=2, description="Number of variations (1-4)"),
):
    """Upload a photo, run the full 5-agent enhancement pipeline.

    This is the main endpoint. It:
    1. Saves the uploaded photo locally
    2. Runs the full agent pipeline (Scout → Architect → Enhancer → Inspector → Post-Production)
    3. Returns URLs to the enhanced images

    NOTE: This runs synchronously for the demo. In production, you'd
    use Celery + WebSocket for async processing with progress updates.
    """
    # Validate file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Clamp variations
    num_variations = max(1, min(4, num_variations))

    # Save uploaded file
    job_id = str(uuid.uuid4())[:8]
    upload_path = os.path.join(config.OUTPUT_DIR, f"{job_id}_original.jpg")
    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)

    print(f"\n[NEW JOB] New enhancement job: {job_id}")
    print(f"   Mode: {'vibe (' + vibe + ')' if vibe else 'enhance'}")
    print(f"   Variations: {num_variations}")

    try:
        # Run the full agent pipeline
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
            "images": [
                f"/outputs/{os.path.basename(p)}" for p in result_paths
            ],
            "count": len(result_paths),
        }

    except Exception as e:
        print(f"[ERROR] Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")


@app.get("/api/download/{filename}")
async def download_image(filename: str):
    """Download a single enhanced image as JPEG."""
    path = os.path.join(config.OUTPUT_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(
        path,
        media_type="image/jpeg",
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="glowup_{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
