import os
import sys
import instaloader


def download_instagram(username, media_type="all", output_folder="./downloads", login_user=None):
    """
    Download Instagram user media with optional login

    Args:
        username: target username
        media_type: videos | photos | all
        output_folder: output directory
        login_user: Instagram login username (optional)
    """

    L = instaloader.Instaloader(dirname_pattern=os.path.join(output_folder, "{target}"))

    if login_user:
        try:
            print(f"Logging in as {login_user}...")
            L.load_session_from_file(login_user)
            print("Session loaded successfully!\n")
            L.context._session.headers.update({
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            })
        except FileNotFoundError:
            print("No saved session found. Logging in manually...")
            L.login(login_user, input("Enter your Instagram password: "))
            L.save_session_to_file()
            print("Session saved!\n")

    print(f"Downloading @{username} ({media_type})...\n")

    profile = instaloader.Profile.from_username(L.context, username)

    for post in profile.get_posts():
        if media_type == "videos" and not post.is_video:
            continue
        if media_type == "photos" and post.is_video:
            continue

        L.download_post(post, target=username)

    print("\nDownload complete!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <username> [media_type] [output_folder] [login_user]")
        print("media_type: videos | photos | all")
        print("Example: python script.py natgeo videos ./downloads my_username")
        sys.exit(1)

    username = sys.argv[1]
    media_type = sys.argv[2] if len(sys.argv) > 2 else "all"
    output_folder = sys.argv[3] if len(sys.argv) > 3 else "./downloads"
    login_user = sys.argv[4] if len(sys.argv) > 4 else None

    download_instagram(username, media_type, output_folder, login_user)