# app/models.py
from typing import Dict, Any, Optional
from pydantic import BaseModel, HttpUrl

class DownloadRequest(BaseModel):
    url: HttpUrl

class DownloadStatus(BaseModel):
    job_id: str
    status: str
    message: str
    progress: Optional[int] = None
    download_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
