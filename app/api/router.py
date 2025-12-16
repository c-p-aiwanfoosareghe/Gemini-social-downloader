# app/api/router.py

import uuid
import os
from fastapi import APIRouter, HTTPException, BackgroundTasks
# Import FileResponse for serving files
from fastapi.responses import FileResponse 

from app.models import DownloadRequest, DownloadStatus 
from app.state import JOB_STORE
from app.services.download_manager import run_download_job 

router = APIRouter(prefix="/api/v1", tags=["Download Jobs"])

# ... (submit_download_job and get_job_status endpoints remain here) ...

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
