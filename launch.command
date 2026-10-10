#!/usr/bin/env bash
set -e

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=========================================="
echo " Starting Local YouTube Downloader..."
echo "=========================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if not already installed
if ! python -c "import flask, yt_dlp" 2>/dev/null; then
    echo "Installing required dependencies (Flask, yt-dlp)..."
    pip install Flask yt-dlp
fi

# Check for local FFmpeg and download static build if missing
if [ ! -f "bin/ffmpeg" ]; then
    echo "FFmpeg not found locally. Downloading static build for macOS..."
    mkdir -p bin
    cd bin
    curl -sL https://evermeet.cx/ffmpeg/getrelease/zip -o ffmpeg.zip
    unzip -q -o ffmpeg.zip
    rm ffmpeg.zip
    chmod +x ffmpeg
    cd ..
    echo "FFmpeg downloaded successfully! Full high-quality merging is now enabled."
fi

# Kill existing instance if running
if [ -f "server.pid" ]; then
    old_pid=$(cat server.pid)
    if ps -p $old_pid > /dev/null; then
        kill $old_pid || true
    fi
    rm server.pid
fi

echo "Starting server..."

# The Python app will automatically open the web browser.
# We use nohup so it stays alive if the terminal closes.
nohup python app/app.py > server.log 2>&1 &
echo $! > server.pid
echo "Server started! A browser window should open shortly."
echo "You can safely close this terminal window. Use the 'Quit App' button on the website to stop the server."
sleep 1
