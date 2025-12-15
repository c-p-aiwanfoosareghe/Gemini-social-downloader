# app/services/download_manager.py
import uuid
import os
import re
from typing import Dict, Any

from app.models import DownloadStatus

# Global Job Store and Download Dir setup here
JOB_STORE: Dict[str, DownloadStatus] = {}
DOWNLOAD_DIR = "downloaded_content"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# The run_download_job function, handle_instagram_download, 
# and handle_yt_dlp_download all go here.
# (The functions you saw in the last response)
