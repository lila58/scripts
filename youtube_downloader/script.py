import os
import sys
import yt_dlp
import shutil


def get_js_runtime():
    """Find the best available JavaScript runtime"""
    deno_path = shutil.which('deno')
    if deno_path:
        return 'deno', deno_path

    node_path = shutil.which('node')
    if node_path:
        return 'node', node_path

    return None, None


def download_youtube_playlist(playlist_url, download_folder="./downloads", cookies_file="./cookies.txt"):
    """
    Download a complete YouTube playlist

    Args:
        playlist_url: YouTube playlist URL
        download_folder: Output folder
        cookies_file: Path to cookies.txt file (optional)
    """
    os.makedirs(download_folder, exist_ok=True)

    runtime_name, runtime_path = get_js_runtime()

    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(playlist_index)s - %(title)s.%(ext)s'),

        'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best',

        'ignoreerrors': False,
        'noplaylist': False,
        'quiet': False,
        'no_warnings': False,

        'progress_hooks': [progress_hook],

        'writethumbnail': False,
        'writedescription': False,
        'writesubtitles': False,
        # 'verbose': True,
    }

    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file
        print(f"Using cookies from: {cookies_file}")

    if runtime_path:
        print(f"Using {runtime_name} runtime: {runtime_path}\n")

        ydl_opts['js_runtimes'] = {
            runtime_name: {
                'path': runtime_path
            }
        }

        ydl_opts['remote_components'] = ['ejs:github']
        ydl_opts['ffmpeg_location'] = shutil.which('ffmpeg')
        
        ydl_opts['extractor_args'] = {
            'youtube': {
                'player_client': ['web']
            }
        }

    else:
        print("WARNING: No JavaScript runtime found (node or deno required).")
        print("Install Deno: curl -fsSL https://deno.land/install.sh | sh")
        print("Or install Node.js: sudo apt install nodejs\n")

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
    if len(sys.argv) < 2:
        print("Usage: python youtube_playlist_downloader.py <playlist_url> [output_folder] [cookies_file]")
        print("Example: python youtube_playlist_downloader.py \"https://youtube.com/playlist?list=...\"")
        print("With cookies: python youtube_playlist_downloader.py \"url\" ./downloads cookies.txt\n")

        print("To export cookies:")
        print("  Chrome/Edge: Get cookies.txt LOCALLY")
        print("  Firefox: cookies.txt extension")

        sys.exit(1)

    playlist_url = sys.argv[1]
    download_folder = sys.argv[2] if len(sys.argv) > 2 else "./downloads"
    cookies_file = sys.argv[3] if len(sys.argv) > 3 else None

    download_youtube_playlist(playlist_url, download_folder, cookies_file)