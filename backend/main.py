"""GlowUp AI Demo — FastAPI Backend Server."""

import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import config

# Ensure output directory exists
os.makedirs(config.OUTPUT_DIR, exist_ok=True)

app = FastAPI(
    title="Hinge Profile Reviewer",
    description="AI-powered profile critiques using Groq Vision and Gemini",
    version="0.2.0",
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
        "message": "Hinge Profile Reviewer API",
        "docs": "/docs",
        "endpoints": {
            "POST /api/review": "Upload profile screenshots for critique",
        },
    }


from typing import List

@app.post("/api/review")
async def review_profile(
    files: List[UploadFile] = File(..., description="The screenshots of the Hinge profile to review"),
):
    """Upload Hinge profile screenshots, run the 2-agent review pipeline.

    This is the main endpoint. It:
    1. Saves the uploaded screenshots locally
    2. Runs the pipeline (Scout -> Reviewer)
    3. Returns the structured JSON review from Gemini
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
        
    num_files = len(files)
    if num_files > 6:
        raise HTTPException(status_code=400, detail="Maximum 6 screenshots allowed")

    job_id = str(uuid.uuid4())[:8]
    print(f"\n[NEW JOB] New profile review job: {job_id} with {num_files} files")

    saved_paths = []
    
    # Save uploaded files
    for i, file in enumerate(files):
        if not file.content_type or not file.content_type.startswith("image/"):
             raise HTTPException(status_code=400, detail=f"File {file.filename} must be an image")

        ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        upload_path = os.path.join(config.OUTPUT_DIR, f"{job_id}_screenshot_{i}.{ext}")
        
        with open(upload_path, "wb") as f:
            content = await file.read()
            f.write(content)
        saved_paths.append(upload_path)

    try:
        # Run the full agent pipeline
        from pipeline import run_review_pipeline
        review_data = await run_review_pipeline(
            image_paths=saved_paths
        )

        return {
            "job_id": job_id,
            "status": "done",
            "review": review_data
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[ERROR] Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=f"Review failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
