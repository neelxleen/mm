#!/bin/bash
set -e

sudo apt-get update
sudo apt-get install -y ffmpeg

pip install --upgrade pip
pip install streamlit pydub pytubefix moviepy requests python-dotenv
echo "Setup complete."
