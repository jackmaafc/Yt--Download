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

## Setup & Running (macOS)

If you are on a Mac, setup is completely automated!

1. Download this code and extract the folder somewhere on your computer.
2. **Double-click the `YouTubeDownloader` app icon** inside the folder.
   *(Note: The very first time you open it, your Mac might show a security warning because it was downloaded from the internet. To bypass this, right-click the app icon and click **Open**).*

That's it! The app will automatically handle installing Python dependencies, downloading FFmpeg, and securely opening the downloader in your web browser. 

*(Advanced Linux/Mac users: You can run `./launch.command` in the terminal instead).*

## Setup & Running (Windows)

Because the automated 1-click launcher is built for Mac, Windows users need to do a one-time manual setup:

**Step 1: Install Python**
Download Python from [python.org](https://www.python.org/downloads/). 
*CRITICAL:* When the installer opens, you must check the box that says **"Add Python to PATH"** at the very bottom before clicking Install.

**Step 2: Install FFmpeg**
This app requires FFmpeg to combine video and audio files. 
1. Download [FFmpeg for Windows](https://github.com/BtbN/FFmpeg-Builds/releases) (look for the `ffmpeg-master-latest-win64-gpl.zip` file).
2. Extract the folder and follow a guide to "Add FFmpeg to Windows PATH" so your computer recognizes it.

**Step 3: Run the App**
1. Open the **Command Prompt** on your computer (search for `cmd` in the Start menu).
2. Type `cd ` (with a space) and then drag-and-drop the downloaded YouTube downloader folder directly into the black window to paste its path, then press Enter.
3. Finally, copy and paste these commands one by one, pressing Enter after each:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python app/app.py
   ```
The window will show a web address (like `http://127.0.0.1:50000`). Just copy and paste that into your web browser to start downloading!

## Security Notes
- Output file paths are strictly bounded. The application ensures downloads are only written safely to your user directory (defaulting to the `Downloads` folder) and actively blocks arbitrary directory traversal or writes to sensitive hidden system folders.
- The server binds strictly to `127.0.0.1` and incorporates CSRF Origin/Referer protections to prevent malicious external websites from interacting with your local downloader.
