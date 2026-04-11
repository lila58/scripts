# TikTok Downloader

Simple Python script to download TikTok videos from a creator username !

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
# Download videos from a creator
python script.py <username>

# With a personalized folder
python script.py khaby.lame /path/to/folder
```

Videos will be saved in `./downloads/` by default.

## Notes

- The `@` symbol before the username is optional.
- The videos are organized by creator
