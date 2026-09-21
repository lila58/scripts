import argparse
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import instaloader


def extract_instagram_source(source):
    """Normalize an Instagram username or URL into a usable profile/post source."""
    if not source:
        raise ValueError("Instagram source is required")

    if not source.startswith(("http://", "https://")):
        return "profile", source.lstrip("@/")

    parsed = urlparse(source)
    path_parts = [part for part in parsed.path.split("/") if part]

    if len(path_parts) >= 2 and path_parts[0].lower() in {"p", "reel", "tv"}:
        return "post", path_parts[1]

    if path_parts:
        return "profile", path_parts[0].lstrip("@")

    raise ValueError("Invalid Instagram URL")


def build_loader(login_user=None):
    """Create an Instaloader configured to keep metadata and optionally reuse session."""
    loader = instaloader.Instaloader(
        dirname_pattern=os.path.join("./downloads", "{target}"),
        download_comments=True,
        save_metadata=True,
    )

    if login_user:
        try:
            print(f"Loading saved session for {login_user}...")
            loader.load_session_from_file(login_user)
        except FileNotFoundError:
            print("No saved session found. Please log in once manually.")
            loader.login(login_user, input("Enter your Instagram password: "))
            loader.save_session_to_file()

    return loader


def get_profile_posts(loader, username, max_posts=None):
    """Return profile posts, optionally limited in number."""
    profile = instaloader.Profile.from_username(loader.context, username)
    posts = []
    for post in profile.get_posts():
        posts.append(post)
        if max_posts and len(posts) >= max_posts:
            break
    return posts


def collect_profile_urls(username, output_path, max_posts=None, login_user=None):
    """Collect Instagram post URLs from a profile without downloading media."""
    loader = build_loader(login_user=login_user)
    posts = get_profile_posts(loader, username, max_posts=max_posts)

    urls = []
    for post in posts:
        urls.append(post.url)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(urls, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Collected {len(urls)} URLs from @{username}.")
    print(f"Saved to: {path}")
    return urls


def extract_metadata_for_posts(loader, username, output_path, max_posts=None):
    """Extract metadata from Instagram posts and save JSONL rows."""
    posts = get_profile_posts(loader, username, max_posts=max_posts)

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    stored = 0
    with output_file.open("w", encoding="utf-8") as handle:
        for post in posts:
            row = {
                "shortcode": post.shortcode,
                "url": post.url,
                "owner_username": post.owner_username,
                "caption": post.caption or "",
                "date_utc": post.date_utc.isoformat() if post.date_utc else None,
                "is_video": post.is_video,
                "likes": post.likes,
                "comments": post.comments,
                "typename": post.typename,
                "media_count": getattr(post, "media_count", 1),
                "hashtags": getattr(post, "hashtags", []) or [],
                "tagged_users": getattr(post, "tagged_users", []) or [],
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            stored += 1

    print(f"Saved {stored} Instagram metadata entries to: {output_file}")
    return stored


def load_urls_from_file(url_file):
    """Load Instagram URLs from a JSON list."""
    path = Path(url_file)
    if not path.exists():
        raise FileNotFoundError(f"URL file not found: {url_file}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, str):
        data = [data]

    if not isinstance(data, list):
        raise ValueError("The URL file must contain a JSON array of strings.")

    return [item for item in data if isinstance(item, str) and item.startswith(("http://", "https://"))]


def extract_metadata_for_url(loader, shortcode, output_path):
    """Extract metadata for a single Instagram post shortcode."""
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    row = {
        "shortcode": post.shortcode,
        "url": post.url,
        "owner_username": post.owner_username,
        "caption": post.caption or "",
        "date_utc": post.date_utc.isoformat() if post.date_utc else None,
        "is_video": post.is_video,
        "likes": post.likes,
        "comments": post.comments,
        "typename": post.typename,
        "media_count": getattr(post, "media_count", 1),
        "hashtags": getattr(post, "hashtags", []) or [],
        "tagged_users": getattr(post, "tagged_users", []) or [],
    }

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Saved metadata for: {post.url}")
    return row


def build_parser():
    parser = argparse.ArgumentParser(
        description="Collect Instagram URLs and metadata without downloading media."
    )
    parser.add_argument("source", nargs="?", help="Instagram username or URL")
    parser.add_argument("--output", default="instagram_urls.json", help="Where to save collected post URLs")
    parser.add_argument("--metadata-output", default="instagram_metadata.jsonl", help="Where to save metadata as JSONL")
    parser.add_argument("--max-posts", type=int, default=None, help="Maximum number of posts to inspect")
    parser.add_argument("--login-user", help="Instagram username to reuse a saved session")
    parser.add_argument("--urls-file", help="JSON file containing Instagram URLs already collected")
    parser.add_argument("--shortcode", help="Single Instagram shortcode to inspect")
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    if args.urls_file:
        urls = load_urls_from_file(args.urls_file)
        loader = build_loader(login_user=args.login_user)
        for url in urls:
            parsed = urlparse(url)
            path_parts = [part for part in parsed.path.split("/") if part]
            if len(path_parts) >= 2 and path_parts[0].lower() in {"p", "reel", "tv"}:
                shortcode = path_parts[1]
                extract_metadata_for_url(loader, shortcode, args.metadata_output)
        sys.exit(0)

    if args.shortcode:
        loader = build_loader(login_user=args.login_user)
        extract_metadata_for_url(loader, args.shortcode, args.metadata_output)
        sys.exit(0)

    if not args.source:
        parser.print_help()
        print("\nExamples:")
        print("  python script.py natgeo --max-posts 25")
        print("  python script.py https://www.instagram.com/natgeo/")
        print("  python script.py --urls-file instagram_urls.json --login-user my_user")
        sys.exit(1)

    source_type, source_value = extract_instagram_source(args.source)
    if source_type != "profile":
        loader = build_loader(login_user=args.login_user)
        extract_metadata_for_url(loader, source_value, args.metadata_output)
        sys.exit(0)

    collect_profile_urls(
        source_value,
        output_path=args.output,
        max_posts=args.max_posts,
        login_user=args.login_user,
    )
    loader = build_loader(login_user=args.login_user)
    extract_metadata_for_posts(
        loader,
        source_value,
        output_path=args.metadata_output,
        max_posts=args.max_posts,
    )
