import yt_dlp
import os
from fastapi import HTTPException

def download_youtube_video(url: str) -> str:
    """Download a YouTube video and return the path to the downloaded file."""
    ydl_opts = {
        'format': 'best[ext=mp4]/best',  # Simplified format selection
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': False,  # Show output for debugging
        'no_warnings': False,
        'ignoreerrors': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading YouTube video: {url}")
            info = ydl.extract_info(url, download=True)
            if info is None:
                # First attempt failed, try with a different format
                logger.warning("First attempt failed, trying with a different format")
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                    info = ydl2.extract_info(url, download=True)
                    
            if info is None:
                # Second attempt failed, try with an even more basic format
                logger.warning("Second attempt failed, trying with basic format")
                ydl_opts['format'] = 'mp4'
                with yt_dlp.YoutubeDL(ydl_opts) as ydl3:
                    info = ydl3.extract_info(url, download=True)
            
            if info is None:
                raise Exception("Failed to extract video info after multiple attempts")
                
            video_id = info['id']
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                # If the file doesn't exist with the expected name, look for it with different extensions
                potential_files = [f"{video_id}.{ext}" for ext in ['mp4', 'webm', 'mkv']]
                for file in potential_files:
                    if os.path.exists(file):
                        filename = file
                        break
                else:
                    raise Exception(f"Downloaded file not found: {filename}")
                        
            return filename
    except Exception as e:
        logger.error(f"Error downloading YouTube video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to download YouTube video: {str(e)}") 