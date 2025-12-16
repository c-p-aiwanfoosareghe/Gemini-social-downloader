# app/api/router.py

import uuid
import os # Necessary for os.path.exists() and os.path.basename()
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse # Necessary for serving files

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
    background_tasks.add_task(run_download_job, job_id, url_str)
    
    return new_status

@router.get("/download/status/{job_id}", response_model=DownloadStatus)
async def get_job_status(job_id: str):
    """Returns the current status (PENDING, IN_PROGRESS, COMPLETED, FAILED) of a job."""
    
    status_obj = JOB_STORE.get(job_id)
    
    if not status_obj:
        raise HTTPException(status_code=404, detail="Job ID not found.")
        
    return status_obj

@router.get("/download/file/{job_id}")
async def get_downloaded_file(job_id: str):
    """
    Retrieves the downloaded file if the job is COMPLETED.
    This endpoint uses temporary local storage.
    """
    status_obj = JOB_STORE.get(job_id)
    
    if not status_obj:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    
    # 1. Check if the download is complete
    if status_obj.status != "COMPLETED":
        raise HTTPException(
            status_code=409, 
            detail=f"Download not yet complete. Current status: {status_obj.status}"
        )
    
    file_path = status_obj.download_path
    
    # 2. Check if path was saved
    if not file_path:
         raise HTTPException(status_code=500, detail="Job completed, but no file path was saved.")
         
    # 3. Check if the file still exists (The key check on Render's ephemeral storage)
    if not os.path.exists(file_path):
         # Raise 410 (Gone) to signal file loss due to temporary storage/server restart
         raise HTTPException(
             status_code=410, 
             detail="File was downloaded, but has been deleted from the temporary server storage."
         )

    # 4. Serve the file
    filename = status_obj.metadata.get("filename", os.path.basename(file_path))
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )
