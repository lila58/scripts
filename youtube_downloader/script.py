import os
import yt_dlp

def download_youtube_playlist(playlist_url, download_folder="./downloads"):
    """
    Download a complete YouTube playlist
    
    Args:
        playlist_url: YouTube playlist URL
        download_folder: Output folder
    """
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)
    
    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(playlist_index)s - %(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'ignoreerrors': True,
        'noplaylist': False,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
        
        'progress_hooks': [progress_hook],
        
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        
        'writethumbnail': True,
        'writedescription': True,
        'writesubtitles': False,
        
        # rate limiting (optionnel)
        # 'ratelimit': 1000000,  # 1MB/s
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("Retrieving playlist information...")
            info = ydl.extract_info(playlist_url, download=False)
            
            if 'entries' in info:
                print(f"Playlist: {info.get('title', 'No Title')}")
                print(f"Number of videos: {len(info['entries'])}\n")
            
            print("Download starting...\n")
            ydl.download([playlist_url])
            
        print("\nDownload completed successfully!")
        return True
        
    except yt_dlp.utils.DownloadError as e:
        print(f"\nDownloading Error: {e}")
        return False
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        return False

def progress_hook(d):
    """Displays download progress"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"\rProgression: {percent} | Speed: {speed} | ETA: {eta}", end='')
    elif d['status'] == 'finished':
        print(f"\nDownload complete: {d['filename']}")

if __name__ == "__main__":
    # Configuration
    playlist_url = "https://youtube.com/playlist?list=PlaylistURL"
    download_folder = "./downloads"
    
    download_youtube_playlist(playlist_url, download_folder)