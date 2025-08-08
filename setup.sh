#!/bin/bash
# Update package list
sudo apt-get update

# Install ffmpeg
sudo apt-get install -y ffmpeg

# Install Python dependencies
pip install --upgrade pip
pip install streamlit pydub pytubefix moviepy requests python-dotenv
