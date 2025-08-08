import os
import random
import time
import requests
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from pathlib import Path

load_dotenv(Path("/workspace/mm/.env"))

TENOR_API_KEY = os.getenv("TENOR_API_KEY", "YOUR_TENOR_API_KEY")

def fetch_random_tenor_media(tag='lofi', limit=25, contentfilter='high'):
    """
    Fetch a random media from Tenor preferring MP4 formats to avoid GIF frame read warnings.
    Downloads the media locally and returns the path.
    """
    try:
        url = "https://tenor.googleapis.com/v2/search"
        params = {
            "q": tag,
            "key": TENOR_API_KEY,
            "limit": limit,
            "random": "true",
            "contentfilter": contentfilter,
            "media_filter": "mp4,tinymp4,gif,tinygif"  # MP4 prioritized
        }
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            st.warning("No Tenor results found.")
            return None

        choice = random.choice(results)
        formats = choice.get("media_formats", {})

        media_url, out_name = None, None
        # Prefer MP4 formats first
        for key in ["mp4", "tinymp4"]:
            if key in formats and "url" in formats[key]:
                media_url = formats[key]["url"]
                out_name = f"temp_{int(time.time())}.mp4"
                break

        # If no MP4 found, fallback to GIF formats
        if not media_url:
            for key in ["gif", "tinygif"]:
                if key in formats and "url" in formats[key]:
                    media_url = formats[key]["url"]
                    out_name = f"temp_{int(time.time())}.gif"
                    break

        if not media_url:
            st.warning("No suitable media format found on Tenor.")
            return None

        media_resp = requests.get(media_url, timeout=30)
        media_resp.raise_for_status()
        with open(out_name, "wb") as f:
            f.write(media_resp.content)

        return out_name

    except Exception as e:
        st.error(f"Tenor fetch error: {e}")
        return None
