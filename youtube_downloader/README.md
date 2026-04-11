# Youtube Downloader

Simple Python script to download Youtube playlist videos !

## Installation

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependancies
pip install -r requirements.txt
```

## Usage

```bash
# Basic usage
python script.py "<playlist_url>"

# Specify output folder
python script.py "<playlist_url>" ./downloads

# Use Cookies (Recommanded)
python script.py "<playlist_url>" ./downloads cookies.txt
```

Videos will be saved in `./downloads/` by default.

## Using Cookies (IMPORTANT)

Due to recent YouTube restrictions, using cookies is highly recommended.

### Step 1: Export cookies

Use a browser extension:

- Chrome / Edge → Get cookies.txt LOCALLY
- Firefox → cookies.txt

### Step 2: Save as

cookies.txt

### Step 3: Run with cookies

```bash
python script.py "<playlist_url>" ./downloads cookies.txt
```

## Notes

Always wrap URLs in quotes:

```bash
python script.py "https://youtube.com/playlist?list=..."
```

Some videos may not download without cookies due to:

- YouTube SABR streaming
- PO Token protection
- Age restriction`

Ensure ffmpeg is installed
