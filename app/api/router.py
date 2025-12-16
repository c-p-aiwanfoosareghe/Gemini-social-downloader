# app/api/router.py

import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks

# Import all necessary models and service components
from app.models import DownloadRequest, DownloadStatus 
from app.state import JOB_STORE
from app.services.download_manager import run_download_job 

router = APIRouter(prefix="/api/v1", tags=["Download Jobs"])

@router.post("/download/submit", response_model=DownloadStatus, status_code=202)
async def submit_download_job(request: DownloadRequest, background_tasks: BackgroundTasks):
    """
    Submits a URL for download and starts the process in the background.
    Returns a Job ID for status tracking.
    """
    job_id = str(uuid.uuid4())
    url_str = str(request.url)

    new_status = DownloadStatus(
        job_id=job_id,
        status="PENDING",
        message="Job accepted and submitted to background process.",
        progress=0
    )
    
    # Store the new job status object
    JOB_STORE[job_id] = new_status
    
    # Add the long-running task to FastAPI's BackgroundTasks queue
    # This allows the API to return 202 immediately.
    background_tasks.add_task(run_download_job, job_id, url_str)
    
    return new_status

@router.get("/download/status/{job_id}", response_model=DownloadStatus)
async def get_job_status(job_id: str):
    """Returns the current status (PENDING, IN_PROGRESS, COMPLETED, FAILED) of a job."""
    
    status_obj = JOB_STORE.get(job_id)
    
    if not status_obj:
        raise HTTPException(status_code=404, detail="Job ID not found.")
        
    return status_obj
