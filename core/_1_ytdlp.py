import os,sys
import glob
import re
import subprocess
from core.utils import *

def sanitize_filename(filename):
    # Remove or replace illegal characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Ensure filename doesn't start or end with a dot or space
    filename = filename.strip('. ')
    # Use default name if filename is empty
    return filename if filename else 'video'

def update_ytdlp():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
        if 'yt_dlp' in sys.modules:
            del sys.modules['yt_dlp']
        rprint("[green]yt-dlp updated[/green]")
    except subprocess.CalledProcessError as e:
        rprint("[yellow]Warning: Failed to update yt-dlp: {e}[/yellow]")
    from yt_dlp import YoutubeDL
    return YoutubeDL

def download_video_ytdlp(url, save_path='output', resolution='1080', suffix=''):
    os.makedirs(save_path, exist_ok=True)
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best' if resolution == 'best' else f'bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]',
        'outtmpl': f'{save_path}/%(title)s{suffix}.%(ext)s',
        'noplaylist': True,
        'writethumbnail': True,
        "cookiesfrombrowser": ("firefox",),
        'proxy': 'http://127.0.0.1:7897',
        'postprocessors': [{'key': 'FFmpegThumbnailsConvertor', 'format': 'jpg'}],
    }

    # Read Youtube Cookie File
    cookies_path = load_key("youtube.cookies_path")
    if os.path.exists(cookies_path):
        ydl_opts["cookiefile"] = str(cookies_path)

    # Get YoutubeDL class after updating
    YoutubeDL = update_ytdlp()
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # Check and rename files after download
    for file in os.listdir(save_path):
        if os.path.isfile(os.path.join(save_path, file)):
            filename, ext = os.path.splitext(file)
            new_filename = sanitize_filename(filename)
            if new_filename != filename:
                os.rename(os.path.join(save_path, file), os.path.join(save_path, new_filename + ext))

def download_video_async(url, save_path='output', resolution='1080', suffix=''):
    """异步下载视频，用于并行处理"""
    import threading
    def download_thread():
        try:
            download_video_ytdlp(url, save_path, resolution, suffix)
        except Exception as e:
            print(f"Download failed for {resolution}p: {e}")
    
    thread = threading.Thread(target=download_thread)
    thread.start()
    return thread

def find_video_files(save_path='output', prefer_best=True):
    video_files = [file for file in glob.glob(save_path + "/*") if os.path.splitext(file)[1][1:].lower() in load_key("allowed_video_formats")]
    # change \\ to /, this happen on windows
    if sys.platform.startswith('win'):
        video_files = [file.replace("\\", "/") for file in video_files]
    video_files = [file for file in video_files if not file.startswith("output/output")]
    
    if len(video_files) == 0:
        raise ValueError("No video files found in the output directory.")
    
    if len(video_files) == 1:
        return video_files[0]
    
    # If multiple videos found, prioritize best quality
    if prefer_best:
        best_files = [f for f in video_files if '_best.' in f or 'best.' in f]
        if best_files:
            return best_files[0]
    
    # Otherwise return the first one
    return video_files[0]

if __name__ == '__main__':
    # Example usage
    url = input('Please enter the URL of the video you want to download: ')
    resolution = input('Please enter the desired resolution (360/480/720/1080, default 1080): ')
    resolution = int(resolution) if resolution.isdigit() else 1080
    download_video_ytdlp(url, resolution=resolution)
    print(f"🎥 Video has been downloaded to {find_video_files()}")
