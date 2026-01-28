import os
import subprocess
import sys

def download_tiktok_videos(tiktok_url, output_folder="./downloads"):
    """
    Download TikTok videos using yt-dlp
    
    Args:
        tiktok_url: TikTok profile URL or video URL
        output_folder: Directory to save downloaded videos
    """
    os.makedirs(output_folder, exist_ok=True)
    
    command = [
        "yt-dlp",
        "-o", f"{output_folder}/%(uploader)s/%(title)s.%(ext)s",
        "--no-warnings",  
        "--progress", 
        tiktok_url
    ]
    
    print(f"Downloading TikTok videos from: {tiktok_url}")
    print(f"Saving to: {output_folder}\n")
    
    try:
        result = subprocess.run(command, check=True)
        print("\nDownload complete!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nError during download: {e}")
        return False
    except FileNotFoundError:
        print("Error: yt-dlp is not installed or not found in PATH")
        print("Install it with: pip install yt-dlp")
        return False

if __name__ == "__main__":
    # Example usage - replace with real TikTok URL
    tiktok_url = "https://www.tiktok.com/@username"
    output_folder = "./downloads"
    
    if len(sys.argv) > 1:
        tiktok_url = sys.argv[1]
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    
    download_tiktok_videos(tiktok_url, output_folder)