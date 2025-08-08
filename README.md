# Lofi Music Video Generator

This Streamlit application converts an audio file (from a YouTube URL or direct upload) into a lofi version and combines it with a random, looping GIF from Tenor to create a 1920x1080 music video.

## Setup

### Prerequisites
- Python 3.8+
- **FFmpeg**: This is a critical dependency for `moviepy`. You must install it on your system and ensure it's available in your system's PATH.
  - **On macOS (using Homebrew):** `brew install ffmpeg`
  - **On Ubuntu/Debian:** `sudo apt-get install ffmpeg`
  - **On Windows:** Download from the official FFmpeg website and add the `bin` directory to your system's PATH environment variable.

### Installation

1.  **Clone or create the project directory.**

2.  **Set up your Tenor API Key:**
    - Get a free API key from the [Tenor GIF API Documentation](https://tenor.com/gifapi/documentation).
    - It's recommended to set this as an environment variable:
      ```
      export TENOR_API_KEY="YOUR_API_KEY_HERE"
      ```
    - Alternatively, you can hardcode it in `app/config.py` for local testing.

3.  **Install Python dependencies:**
    ```
    pip install -r requirements.txt
    ```

## Running the Application

Navigate to the project's root directory in your terminal and run the Streamlit app:

