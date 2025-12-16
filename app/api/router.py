# app/api/router.py

import uuid
import os
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

@router.get("/download/file/{job_id}")
async def get_downloaded_file(job_id: str):
    """
    Retrieves the downloaded file if the job is COMPLETED.
    """
    status_obj = JOB_STORE.get(job_id)
    
    if not status_obj:
        raise HTTPException(status_code=404, detail="Job ID not found.")
    
    # Check if the download is complete
    if status_obj.status != "COMPLETED":
        raise HTTPException(
            status_code=409, 
            detail=f"Download not yet complete. Current status: {status_obj.status}"
        )
    
    file_path = status_obj.download_path
    
    # Sanity check: Ensure the path is safe and the file exists
    if not file_path or not os.path.exists(file_path):
         # This case indicates a system issue or a deleted file
         raise HTTPException(status_code=500, detail="File path not found on server.")

    # Extract the file name from the metadata for the response header
    filename = status_obj.metadata.get("filename", os.path.basename(file_path))
    
    # 💥 CRITICAL: Use FileResponse to stream the file to the client.
    # The media_type is inferred, but setting filename ensures the browser downloads it.
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream' # Generic type for forcing download
    )

  # app/api/router.py (Inside get_downloaded_file)
# app/api/router.py (Inside get_downloaded_file)

# ...
    file_path = status_obj.download_path
    
    if not file_path:
         # Internal error: status said COMPLETED but path wasn't saved.
         raise HTTPException(status_code=500, detail="Job completed, but no file path was saved.")
         
    if not os.path.exists(file_path):
         # 💥 CRITICAL FIX: Raise 404 or 410 (Gone) to signal temporary loss
         raise HTTPException(
             # Use 410 (Gone) to show the file was once there but is no longer available.
             status_code=410, 
             detail="File was downloaded, but has been deleted from the temporary server storage."
         )

    # If the file exists, it will proceed to FileResponse
# ...
