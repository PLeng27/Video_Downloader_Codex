# Video Downloader (Flask + yt-dlp)

A small cross-platform web app for downloading publicly accessible videos (or audio) from supported sources.

## Features
- Paste a video URL and fetch metadata (title, thumbnail, duration).
- List selectable formats and download chosen format.
- Download progress indicator.
- Audio-only mode (MP3 extraction).
- Download history persisted locally.
- Dark mode toggle.
- Save to default `Downloads` folder or a custom path.
- URL validation and graceful error handling for invalid/unsupported/private content.

## Supported sources (public content only)
- YouTube public videos
- Vimeo public videos
- Internet Archive
- Pexels

> **Disclaimer:** Use this tool only for content you are legally allowed to download. Respect copyright, platform terms, and local laws. This app does not bypass DRM, authentication, or access restrictions.

## Project structure
- `app.py` - Flask API + web routes.
- `services/platforms.py` - pluggable platform definitions.
- `services/validation.py` - URL validation.
- `services/download_manager.py` - metadata extraction and download workers.
- `services/history_store.py` - local download history storage.
- `templates/index.html`, `static/styles.css`, `static/app.js` - frontend.

## Setup
1. Ensure Python 3.10+ is installed.
2. (Recommended) Install `ffmpeg` for MP3 extraction and media merging.
3. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Run:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000`.

## Usage
1. Paste a supported public video URL.
2. Click **Fetch Metadata**.
3. Choose a format (or enable **Audio only (MP3)**).
4. (Optional) Provide a custom save path.
5. Click **Download** and monitor progress.

## Notes on file saving / OS compatibility
- Default save location is your OS user `Downloads` folder (fallback to home directory if absent).
- You may provide an absolute custom save path.
- Works on Windows/macOS/Linux when run locally with Python + ffmpeg.

## Legal test URLs (public domain/open)
- Internet Archive: `https://archive.org/details/BigBuckBunny_328`
- Vimeo Staff Pick/public sample: `https://vimeo.com/76979871`
- Pexels sample: `https://www.pexels.com/video/aerial-shot-of-seashore-855564/`

(Availability may vary by region/time.)
