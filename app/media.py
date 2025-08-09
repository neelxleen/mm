import os
import random
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path("/workspace/mm/.env"))

TENOR_API_KEY = os.getenv("TENOR_API_KEY", "YOUR_TENOR_API_KEY")

def fetch_random_tenor_media(tag="anime sad lofi", limit=30, contentfilter="high"):
    try:
        url = "https://tenor.googleapis.com/v2/search"
        params = {
            "q": tag,
            "key": TENOR_API_KEY,
            "limit": limit,
            "random": "true",
            "contentfilter": contentfilter,
            "media_filter": "mp4,tinymp4,gif,tinygif"
        }
        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        results = data.get("results", [])
        if not results:
            return None

        choice = random.choice(results)
        fmts = choice.get("media_formats", {})

        if "mp4" in fmts and "url" in fmts["mp4"]:
            media_url = fmts["mp4"]["url"]
            out = f"temp_{int(time.time())}.mp4"
        elif "tinymp4" in fmts and "url" in fmts["tinymp4"]:
            media_url = fmts["tinymp4"]["url"]
            out = f"temp_{int(time.time())}.mp4"
        elif "gif" in fmts and "url" in fmts["gif"]:
            media_url = fmts["gif"]["url"]
            out = f"temp_{int(time.time())}.gif"
        elif "tinygif" in fmts and "url" in fmts["tinygif"]:
            media_url = fmts["tinygif"]["url"]
            out = f"temp_{int(time.time())}.gif"
        else:
            return None

        mr = requests.get(media_url, timeout=40)
        mr.raise_for_status()
        with open(out, "wb") as f:
            f.write(mr.content)
        return out
    except Exception:
        return None
