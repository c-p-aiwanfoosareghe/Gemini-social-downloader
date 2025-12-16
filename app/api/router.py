# app/api/router.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models import DownloadRequest
# --- UPDATED IMPORTS ---
from app.state import JOB_STORE # Import JOB_STORE from its own simple file
from app.services.download_manager import run_download_job # Only need the function
# -----------------------
router = APIRouter(prefix="/api/v1")

@router.post("/download/submit", response_model=DownloadStatus, status_code=202)
async def submit_download_job(request: DownloadRequest, background_tasks: BackgroundTasks):
    # Logic to create job ID and submit to background tasks goes here, 
    # referencing the JOB_STORE and run_download_job from download_manager.py
    # ...
    pass

@router.get("/download/status/{job_id}", response_model=DownloadStatus)
async def get_job_status(job_id: str):
    # Logic to check status from JOB_STORE goes here
    # ...
    pass
