# Local YouTube Downloader

A lightweight, local-only web application for downloading YouTube videos and audio. It features a clean UI, queue management, background processing, and quality selection—all running safely on your own machine.

## Features
- **Video & Audio Downloads:** Download full videos or extract audio instantly (M4A) or with conversion (MP3).
- **Playlist Support:** Queue entire playlists effortlessly.
- **Local-Only:** Binds only to `localhost` (`127.0.0.1`) for maximum privacy.
- **Background Queue:** Downloads are processed in a background thread so the UI never freezes.
- **Auto FFmpeg Setup (macOS):** Automatically provisions the required FFmpeg dependencies to handle high-quality video merging.

## Prerequisites
- **Python 3.8+** installed on your system.

## Setup & Running (macOS / Linux)

The easiest way to start the app is to use the provided launch script:

```bash
# From the project root, make the launcher executable (if not already):
chmod +x launch.command

# Run it:
./launch.command
```
*(Alternatively, on macOS you can double-click `YouTubeDownloader.app` if you prefer an icon).*

The script will automatically:
1. Create a Python virtual environment.
2. Install the required dependencies.
3. Download a local, static build of FFmpeg (required for processing).
4. Start the local server and open your default web browser.

## Setup & Running (Windows / Manual Setup)

1. Create a virtual environment and activate it:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```cmd
   pip install -r requirements.txt
   ```
3. **Important for Windows:** You must install [FFmpeg](https://ffmpeg.org/download.html) and ensure it is available in your system's `PATH`.
4. Run the application:
   ```cmd
   python app/app.py
   ```

## Security Notes
- The server binds strictly to `127.0.0.1` and incorporates CSRF Origin/Referer protections to prevent malicious external websites from interacting with your local downloader.
- Output file paths are strictly bounded to prevent arbitrary directory traversal.
