import os
import re
from typing import Any, Tuple

# Import the global state store
from app.state import JOB_STORE
from app.models import DownloadStatus 

# --- Global Configuration ---
DOWNLOAD_DIR = "downloaded_content"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# --- Helper Functions (Private) ---

def _handle_instagram_download(url: str, job_id: str) -> Tuple[str, dict]:
    """Uses Instaloader to download public Instagram content and returns thumbnail info."""
    import instaloader 
    
    L = instaloader.Instaloader(
        dirname_pattern=os.path.join(DOWNLOAD_DIR, job_id),
        max_connection_attempts=1,
        save_metadata=False,
        post_metadata_txt_fmt=''
    )
    
    match = re.search(r"/(p|tv|reel)/([a-zA-Z0-9_-]+)", url)
    if not match:
        raise ValueError("Invalid Instagram post URL format.")
    
    shortcode = match.group(2)
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    
    # Capture thumbnail URL before downloading
    metadata = {"thumbnail": post.url} 
    
    L.download_post(post, target=job_id)
    
    # Find the downloaded file path
    downloaded_files = [
        os.path.join(DOWNLOAD_DIR, job_id, f) 
        for f in os.listdir(os.path.join(DOWNLOAD_DIR, job_id)) 
        if f.endswith(('.mp4', '.jpg', '.jpeg', '.webp'))
    ]
    
    if not downloaded_files:
        raise FileNotFoundError("Instaloader downloaded metadata but not the media file.")
        
    return downloaded_files[0], metadata


def _handle_yt_dlp_download(url: str, job_id: str) -> Tuple[str, dict]:
    """Uses yt-dlp to download content and extracts thumbnail from info_dict."""
    import yt_dlp      

    output_template = os.path.join(DOWNLOAD_DIR, job_id, '%(title)s.%(ext)s')
    
    ydl_opts = {
        'outtmpl': output_template,
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'simulate': False,
        'forcefilename': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        final_filename = ydl.prepare_filename(info_dict)
        
        if not final_filename:
            final_filename = os.path.join(DOWNLOAD_DIR, job_id, os.path.basename(info_dict.get('filepath', 'video.mp4')))
                 
        return os.path.normpath(final_filename), info_dict


# --- Main Worker Function (Public) ---

def run_download_job(job_id: str, url: str):
    """Executes the download and populates the metadata (including thumbnails)."""
    
    status_obj: DownloadStatus = JOB_STORE.get(job_id)
    if not status_obj: return 

    status_obj.status = "IN_PROGRESS"
    status_obj.message = "Analyzing URL and starting download..."
    
    try:
        if re.search(r"instagram\.com", url):
            # Updated to receive both path and info
            download_path, info_data = _handle_instagram_download(url, job_id)
            source_type = "Instagram"
        elif re.search(r"facebook\.com|fb\.watch", url):
            download_path, info_data = _handle_yt_dlp_download(url, job_id)
            source_type = "Facebook"
        else:
            raise ValueError(f"URL domain not supported: {url}")
            
        # Finalize the job
        status_obj.status = "COMPLETED"
        status_obj.progress = 100
        status_obj.message = "Download successful."
        status_obj.download_path = download_path
        
        # 💥 ENHANCED METADATA: Adding thumbnail and source info
        status_obj.metadata = {
            "source": source_type, 
            "url": url, 
            "filename": os.path.basename(download_path), 
            "size_bytes": os.path.getsize(download_path),
            "thumbnail": info_data.get("thumbnail") # Works for both yt-dlp and our Insta helper
        }
        
    except Exception as e:
        status_obj.status = "FAILED"
        status_obj.message = f"Download failed: {type(e).__name__}: {str(e)[:100]}"
        status_obj.progress = 0
