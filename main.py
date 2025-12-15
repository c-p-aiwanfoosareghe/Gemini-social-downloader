import uuid
import time
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
# Import libraries for actual downloading (e.g., instaloader, yt_dlp)
# import instaloader 
# import yt_dlp

# --- 1. Data Models (Pydantic) ---

class DownloadRequest(BaseModel):
    """Schema for the POST request body."""
    url: HttpUrl

class DownloadStatus(BaseModel):
    """Schema for the GET /status response."""
    job_id: str
    status: str
    message: str
    progress: Optional[int] = None
    download_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# --- 2. Global Job Store (In-Memory Database Mock) ---

# Stores job_id: DownloadStatus object
JOB_STORE: Dict[str, DownloadStatus] = {}
# Simulate a queue/worker system for simplicity
DOWNLOAD_QUEUE = []

# --- 3. FastAPI App Initialization ---

app = FastAPI(title="Public Content Downloader API", version="1.0.0")

# --- 4. Mock Download/Worker Function ---

def run_download_job(job_id: str, url: str):
    """
    SIMULATED ASYNCHRONOUS WORKER FUNCTION (Replace with Celery/actual download logic).
    
    In a real app, this would run in a separate thread/process (e.g., Celery).
    We're mocking the progress update here.
    """
    print(f"Starting simulated download for Job ID: {job_id}")
    
    # Update status to IN_PROGRESS
    status_obj = JOB_STORE[job_id]
    status_obj.status = "IN_PROGRESS"
    
    # Mock download stages
    for i in range(1, 4):
        time.sleep(1) # Simulate delay
        status_obj.progress = i * 25
        status_obj.message = f"Downloading stage {i}..."
    
    # Finalize the job
    time.sleep(1)
    status_obj.status = "COMPLETED"
    status_obj.progress = 100
    status_obj.message = "Download complete and content saved."
    status_obj.download_path = f"/storage/content/{job_id}.mp4"
    status_obj.metadata = {"source": "Instagram", "date": time.ctime()}
    
    print(f"Job ID: {job_id} completed.")

# --- 5. API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Public Content Downloader API is running."}

@app.post("/api/v1/download/submit", response_model=DownloadStatus, status_code=202)
async def submit_download_job(request: DownloadRequest):
    """Submits a URL for asynchronous download and returns a Job ID."""
    job_id = str(uuid.uuid4())
    url_str = str(request.url)

    new_status = DownloadStatus(
        job_id=job_id,
        status="PENDING",
        message="Job accepted and queued.",
        progress=0
    )
    
    JOB_STORE[job_id] = new_status
    
    # In a real app, you would send this to a Celery worker:
    # run_download_job.delay(job_id, url_str) 
    
    # For this simple deployment, we'll just queue it locally and assume a worker picks it up
    DOWNLOAD_QUEUE.append((job_id, url_str)) 
    
    # **NOTE:** Since Render needs a simple setup, you'll need a *real* queue 
    # (like Celery/Redis) to handle the long task or you must run the task synchronously 
    # (which will time out the request for long downloads). 
    # For now, we rely on the client to check the status.
    # To run this mock job immediately in memory, uncomment the line below:
    # run_download_job(job_id, url_str) 
    
    return new_status

@app.get("/api/v1/download/status/{job_id}", response_model=DownloadStatus)
async def get_job_status(job_id: str):
    """Returns the current status of the download job."""
    if job_id not in JOB_STORE:
        raise HTTPException(status_code=404, detail="Job ID not found.")
        
    # **Critical Mock Fix:** To ensure the mock job actually runs when polled, 
    # we'll check the queue and run it synchronously the first time the status is checked 
    # (This is bad practice for production, but necessary for a single-process Render demo)
    if JOB_STORE[job_id].status == "PENDING" and (job_id, JOB_STORE[job_id].metadata) in [(j[0], None) for j in DOWNLOAD_QUEUE]:
        # Simple hack: find the job in the queue and run it
        try:
            url_to_run = [url for j_id, url in DOWNLOAD_QUEUE if j_id == job_id][0]
            run_download_job(job_id, url_to_run)
            DOWNLOAD_QUEUE.pop(DOWNLOAD_QUEUE.index((job_id, url_to_run)))
        except IndexError:
            pass # Job was somehow already removed
            
    return JOB_STORE[job_id]

# The /file and /metadata endpoints are implicitly handled by the DownloadStatus 
# response model once the status is COMPLETED.
