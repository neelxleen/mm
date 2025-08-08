import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
load_dotenv(Path("/workspace/mm/.env"))

# --- API and File Configuration ---

# Get your free API key from https://tenor.com/gifapi/documentation
# It is recommended to set this as an environment variable for security.
TENOR_API_KEY = os.getenv("TENOR_API_KEY", "YOUR_TENOR_API_KEY_HERE")

# --- Default Settings ---
TENOR_DEFAULT_TAG = "lofi anime"
TENOR_CONTENT_FILTER = "high"  # Options: "off", "low", "medium", "high"
TENOR_SEARCH_LIMIT = 50

# --- File Paths ---
TEMP_AUDIO_PATH = "temp_audio.mp3"
LOFI_AUDIO_PATH = "lofi_audio.mp3"
OUTPUT_VIDEO_PATH = "lofi_video.mp4"

# --- Video & Audio Processing Settings ---
VIDEO_RESOLUTION = (1920, 1080)
VIDEO_FPS = 30
VIDEO_BITRATE = "5000k"
AUDIO_SAMPLE_RATE = 22050
AUDIO_LOW_PASS_FREQ = 3000
