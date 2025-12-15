# app/services/download_manager.py
import uuid
import os
import re
from typing import Dict, Any

from app.models import DownloadStatus

# app/services/download_manager.py (Mock version)
import time # Ensure time is imported

def run_download_job(job_id: str, url: str):
    status_obj = JOB_STORE.get(job_id)
    if not status_obj: return 

    status_obj.status = "IN_PROGRESS"
    status_obj.message = "Simulating download..."

    # MOCK LOGIC: Remove all yt-dlp/instaloader code
    time.sleep(5) 

    status_obj.status = "COMPLETED"
    status_obj.message = "Mock download successful."
    status_obj.download_path = "/mock/path"
    status_obj.metadata = {"source": "MOCK", "url": url}

    # END MOCK LOGIC

