# app/state.py
from typing import Dict
from app.models import DownloadStatus

# Global store with zero dependencies on external download libs
JOB_STORE: Dict[str, DownloadStatus] = {}
