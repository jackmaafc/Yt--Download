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

The easiest way to start the app is to use the provided launch script, which handles everything automatically:

```bash
# 1. Open Terminal and navigate to the folder where you downloaded this code
cd path/to/youtube_downloader

# 2. Make the launcher executable (if not already):
chmod +x launch.command

# 3. Run it:
./launch.command
```
*(Alternatively, you can just double-click the included `YouTubeDownloader.app` icon).*

The script will automatically:
1. Create a Python virtual environment.
2. Install the required dependencies (`Flask`, `yt-dlp`).
3. Download a local, static build of FFmpeg (required for video processing).
4. Start the local server and open your default web browser.

## Setup & Running (Windows)

Because the automated launcher is written for Mac/Linux, Windows users just need to run a few manual commands to set it up:

1. **Install Python:** Ensure you have Python 3.8 or newer installed from [python.org](https://python.org).
2. **Install FFmpeg:** Download [FFmpeg](https://ffmpeg.org/download.html), extract it, and add it to your Windows System PATH.
3. **Open Command Prompt / PowerShell** in the project folder and run:
   ```cmd
   # Create a virtual environment
   python -m venv venv
   
   # Activate it
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   python app/app.py
   ```

## Security Notes
- Output file paths are strictly bounded. The application ensures downloads are only written safely to your user directory (defaulting to the `Downloads` folder) and actively blocks arbitrary directory traversal or writes to sensitive hidden system folders.
- The server binds strictly to `127.0.0.1` and incorporates CSRF Origin/Referer protections to prevent malicious external websites from interacting with your local downloader.
