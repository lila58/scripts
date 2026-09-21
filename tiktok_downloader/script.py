import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


DEFAULT_OUTPUT = "tiktok_urls.json"
DEFAULT_METADATA_OUTPUT = "metadata.jsonl"


def normalize_tiktok_source(source):
    """Normalise une URL TikTok, un nom d'utilisateur ou une collection."""
    if not source:
        return source

    if source.startswith(("http://", "https://")):
        return source

    username = source.lstrip("@")
    if "/" in username:
        return f"https://www.tiktok.com{username if username.startswith('/') else '/' + username}"

    return f"https://www.tiktok.com/@{username}"


def collect_video_urls_from_page(
    page,
    scroll_count=8,
    scroll_delay=2.0,
    max_urls=None,
):
    """Collecte les URLs de vidéos TikTok visibles sur une page."""
    seen = set()

    for _ in range(scroll_count):
        anchors = page.locator("a[href*='/video/']")
        for index in range(anchors.count()):
            href = anchors.nth(index).get_attribute("href")
            if not href:
                continue

            href = href.split("?")[0]
            if href.startswith("/"):
                href = f"https://www.tiktok.com{href}"

            if "/video/" in href and href.startswith("https://www.tiktok.com"):
                seen.add(href)

        if max_urls and len(seen) >= max_urls:
            break

        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(int(scroll_delay * 1000))

    return sorted(seen)


def collect_tiktok_urls(
    source,
    output_path,
    headless=True,
    scroll_count=8,
    scroll_delay=2.0,
    max_urls=None,
):
    """Ouvre TikTok dans Playwright et extrait les URLs de vidéos."""
    normalized_source = normalize_tiktok_source(source)
    print(f"Opening TikTok page: {normalized_source}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page(viewport={"width": 1440, "height": 2200})
        page.goto(normalized_source, wait_until="networkidle", timeout=120000)

        time.sleep(3)
        urls = collect_video_urls_from_page(
            page,
            scroll_count=scroll_count,
            scroll_delay=scroll_delay,
            max_urls=max_urls,
        )
        browser.close()

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(urls, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Found {len(urls)} video URLs.")
    print(f"Saved to: {output_file}")
    return urls


def load_urls_from_file(urls_file):
    """Charge les URLs depuis un JSON contenant une liste de chaînes."""
    path = Path(urls_file)
    if not path.exists():
        raise FileNotFoundError(f"URL file not found: {urls_file}")

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, str):
        data = [data]

    if not isinstance(data, list):
        raise ValueError("The URL file must contain a JSON list of strings.")

    urls = []
    for item in data:
        if not isinstance(item, str):
            continue
        if item.startswith(("http://", "https://")):
            urls.append(item)

    return urls


def extract_metadata_for_url(tiktok_url, browser_profile="chrome"):
    """Récupère les métadonnées d'une vidéo TikTok sans la télécharger."""
    command = [
        sys.executable,
        "-m",
        "yt_dlp",
        "--skip-download",
        "--dump-json",
        "--no-warnings",
        "--no-playlist",
    ]

    if browser_profile:
        command.extend(["--cookies-from-browser", browser_profile])

    command.append(tiktok_url)

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[ERROR] {tiktok_url}")
        print(result.stderr.strip() or result.stdout.strip() or "unknown yt-dlp error")
        return None

    stdout = result.stdout.strip()
    if not stdout:
        return None

    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue

        print(f"[WARN] Could not parse JSON metadata for: {tiktok_url}")
        return None


def extract_metadata_for_urls(urls, output_path, browser_profile="chrome"):
    """Extrait les métadonnées JSONL pour une liste d'URLs TikTok."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    with output_file.open("w", encoding="utf-8") as handle:
        for index, url in enumerate(urls, start=1):
            print(f"[{index}/{len(urls)}] Processing: {url}")
            metadata = extract_metadata_for_url(url, browser_profile=browser_profile)
            if metadata is None:
                continue

            row = {
                "webpage_url": metadata.get("webpage_url") or url,
                "id": metadata.get("id") or "",
                "title": metadata.get("title") or "",
                "description": metadata.get("description") or "",
                "uploader": metadata.get("uploader") or "",
                "uploader_id": metadata.get("uploader_id") or "",
                "channel_id": metadata.get("channel_id") or "",
                "duration": metadata.get("duration"),
                "tags": metadata.get("tags") or [],
                "thumbnail": metadata.get("thumbnail") or "",
                "availability": metadata.get("availability") or "",
                "extractor": metadata.get("extractor") or "",
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            total += 1

    print(f"Saved {total} metadata entries to: {output_file}")
    return total


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Collecte des URLs TikTok depuis une collection et extrait les métadonnées "
            "sans télécharger les vidéos."
        )
    )
    parser.add_argument(
        "source",
        nargs="?",
        help="URL TikTok de la collection / profil / compte, ou @username",
    )
    parser.add_argument(
        "--browser",
        default="chrome",
        help="Nom du navigateur à utiliser pour --cookies-from-browser (ex: chrome, firefox)",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Fichier JSON où enregistrer les URLs PDF / TikTok",  # kept intentionally vague to avoid incorrect naming?
    )
    parser.add_argument(
        "--metadata-output",
        default=DEFAULT_METADATA_OUTPUT,
        help="Fichier JSONL où enregistrer les métadonnées extraites",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Lance le navigateur en mode headless",
    )
    parser.add_argument(
        "--scroll-count",
        type=int,
        default=8,
        help="Nombre de scrolls à effectuer pour charger les vidéos",
    )
    parser.add_argument(
        "--scroll-delay",
        type=float,
        default=2.0,
        help="Délai entre chaque scroll, en secondes",
    )
    parser.add_argument(
        "--max-urls",
        type=int,
        default=None,
        help="Limite le nombre d'URLs collectées",
    )
    parser.add_argument(
        "--urls-file",
        help="Lecture d'un fichier JSON contenant des URLs TikTok déjà collectées",
    )
    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()

    if args.urls_file:
        urls = load_urls_from_file(args.urls_file)
        extract_metadata_for_urls(
            urls,
            output_path=args.metadata_output,
            browser_profile=args.browser,
        )
        sys.exit(0)

    if not args.source:
        parser.print_help()
        print("\nExamples:")
        print("  python script.py "
              "https://www.tiktok.com/@youraccount/collection/1234567890?is_copy_url=1")
        print("  python script.py @youraccount --output my_urls.json")
        print("  python script.py --urls-file my_urls.json --browser chrome")
        sys.exit(1)

    urls = collect_tiktok_urls(
        source=args.source,
        output_path=args.output,
        headless=args.headless,
        scroll_count=args.scroll_count,
        scroll_delay=args.scroll_delay,
        max_urls=args.max_urls,
    )

    extract_metadata_for_urls(
        urls,
        output_path=args.metadata_output,
        browser_profile=args.browser,
    )
