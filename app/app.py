import os
import streamlit as st
from pydub import AudioSegment
from pytubefix import YouTube

import audio as audio_mod
import media
import video

st.set_page_config(page_title="Lofi Sad Anime Video Generator", page_icon="🎧", layout="centered")

st.title("🎧 Lofi Sad Anime Video Generator")
st.write(
    "Generate a 1920x1080 lofi video from YouTube or uploaded audio, "
    "with a Tenor sad anime background and adjustable lofi audio effects."
)

TEMP_AUDIO_PATH = "temp_audio_input.mp3"
LOFI_AUDIO_PATH = "lofi_audio.mp3"
OUTPUT_VIDEO_PATH = "lofi_video_1080p.mp4"

method = st.radio("Choose audio input method:", ["YouTube URL", "Upload Audio File"], horizontal=True)
gif_tag = st.text_input("Background vibe (Tenor search):", value="anime sad lofi")
content_filter = st.selectbox("Content filter", ["off", "low", "medium", "high"], index=3)

if "media_path" not in st.session_state:
    st.session_state.media_path = None

# Sidebar controls for lofi audio parameters
st.sidebar.header("Lofi Audio Controls")
slowdown_speed = st.sidebar.slider("Slowdown Speed (0.7x to 1.0x)", 0.7, 1.0, 0.9, 0.01)
delay_ms = st.sidebar.slider("Reverb Delay (ms)", 100, 400, 220, 10)
reverb_repeats = st.sidebar.slider("Reverb Repeats", 0, 3, 1, 1)
reverb_decay = st.sidebar.slider("Reverb Decay", 0.3, 0.9, 0.75, 0.05)

input_song = None
if method == "YouTube URL":
    yt_url = st.text_input("Enter YouTube URL:")
    if yt_url:
        if st.button("Download Audio"):
            try:
                st.info("Downloading audio from YouTube...")
                yt = YouTube(yt_url, use_po_token=True)
                stream = yt.streams.get_audio_only()
                stream.download(filename=TEMP_AUDIO_PATH)
                input_song = AudioSegment.from_file(TEMP_AUDIO_PATH)
                st.success("Audio downloaded!")
                st.audio(TEMP_AUDIO_PATH)
            except Exception as e:
                st.error(f"Download failed: {e}")
        elif os.path.exists(TEMP_AUDIO_PATH):
            input_song = AudioSegment.from_file(TEMP_AUDIO_PATH)
            st.audio(TEMP_AUDIO_PATH)
else:
    upload = st.file_uploader("Upload audio", type=["mp3", "wav", "ogg"])
    if upload:
        with open(TEMP_AUDIO_PATH, "wb") as f:
            f.write(upload.getbuffer())
        input_song = AudioSegment.from_file(TEMP_AUDIO_PATH)
        st.success("Audio uploaded!")
        st.audio(TEMP_AUDIO_PATH)

cols = st.columns(2)
with cols[0]:
    if st.button("🎲 Regenerate Background Media"):
        if st.session_state.media_path and os.path.exists(st.session_state.media_path):
            try:
                os.remove(st.session_state.media_path)
            except:
                pass
        st.info("Fetching new background media...")
        mp = media.fetch_random_tenor_media(tag=gif_tag, contentfilter=content_filter)
        if mp:
            st.session_state.media_path = mp
            st.success("Media fetched!")
        else:
            st.warning("No media found. Try a different tag.")

with cols[1]:
    if st.button("🧹 Clear Media"):
        if st.session_state.media_path and os.path.exists(st.session_state.media_path):
            try:
                os.remove(st.session_state.media_path)
            except:
                pass
        st.session_state.media_path = None
        st.info("Background media cleared.")

st.markdown("### Background Media Preview")
if st.session_state.media_path and os.path.exists(st.session_state.media_path):
    ext = os.path.splitext(st.session_state.media_path)[1].lower()
    if ext in ['.gif', '.png', '.jpg', '.jpeg']:
        st.image(st.session_state.media_path, use_container_width=True)
    elif ext in ['.mp4', '.mov', '.webm']:
        st.video(st.session_state.media_path)
    else:
        st.info("Preview not supported for this file type.")
else:
    st.info("Click 'Regenerate Background Media' to fetch and preview a background.")

def apply_lofi_with_params(song):
    # Apply lofi effects with user controlled parameters
    processed = audio_mod.normalize(song)
    processed = audio_mod._speed_change(processed, speed=slowdown_speed)
    processed = audio_mod.low_pass_filter(processed, 3000)
    
    processed = audio_mod._simple_reverb(processed, delay_ms=delay_ms, decay=reverb_decay, repeats=reverb_repeats)
    processed = audio_mod.apply_saturation(processed, gain_db=2)  # Optional warmth
    processed = processed + 1
    processed = audio_mod.normalize(processed)
    processed = audio_mod.low_pass_filter(processed, 7500)
    processed = processed.set_frame_rate(22050)
    return processed

st.markdown("---")

log = st.empty()
progress = st.progress(0)

# Button to preview and download lofi processed audio
if input_song:
    if st.button("🎧 Preview Lofi Audio"):
        with st.spinner("Processing lofi audio..."):
            try:
                lofi_preview = apply_lofi_with_params(input_song)
                with open(LOFI_AUDIO_PATH, "wb") as out_f:
                    lofi_preview.export(out_f, format="mp3")
                with open(LOFI_AUDIO_PATH, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                    st.audio(audio_bytes)
                    st.download_button("Download Lofi Audio", data=audio_bytes, file_name="lofi_audio.mp3", mime="audio/mpeg")
            except Exception as e:
                st.error(f"Error processing lofi audio: {e}")

generate = st.button("✨ Generate 1920x1080 Lofi Video")

if generate:
    try:
        if not (input_song or os.path.exists(TEMP_AUDIO_PATH)):
            st.warning("Please provide audio first.")
            raise RuntimeError("Missing audio")

        if not st.session_state.media_path or not os.path.exists(st.session_state.media_path):
            st.warning("Please fetch background media first.")
            raise RuntimeError("Missing media")

        if input_song is None and os.path.exists(TEMP_AUDIO_PATH):
            input_song = AudioSegment.from_file(TEMP_AUDIO_PATH)

        log.text("🌀 Applying lofi audio effects (customized)...")
        progress.progress(10)

        try:
            lofi_audio = apply_lofi_with_params(input_song)
            log.text("✅ Lofi audio effects applied.")
        except Exception as audio_err:
            log.text(f"Error during audio processing: {audio_err}")
            st.error(f"Error during audio processing: {audio_err}")
            raise audio_err

        log.text("💾 Exporting processed audio to mp3...")
        with open(LOFI_AUDIO_PATH, "wb") as out_f:
            lofi_audio.export(out_f, format="mp3")
        progress.progress(35)
        log.text("✅ Audio exported.")

        log.text("🔄 Generating video...")
        progress.progress(50)

        final_video = video.create_video_background(
            st.session_state.media_path,
            LOFI_AUDIO_PATH,
            OUTPUT_VIDEO_PATH,
            log=log.text
        )
        if not final_video:
            err_msg = "❌ Video creation failed."
            log.text(err_msg)
            st.error(err_msg)
            raise RuntimeError(err_msg)

        progress.progress(100)
        log.text("✅ Video generated successfully!")
        st.success("Your lofi video is ready!")

        with open(OUTPUT_VIDEO_PATH, "rb") as vf:
            video_bytes = vf.read()
            st.video(video_bytes)
            st.download_button("Download MP4", data=video_bytes, file_name="lofi_sad_anime_1080p.mp4", mime="video/mp4")

        log.text("🧹 Cleaning up temp files...")
        try:
            if os.path.exists(OUTPUT_VIDEO_PATH):
                os.remove(OUTPUT_VIDEO_PATH)
                log.text("Deleted output video.")
            if os.path.exists(LOFI_AUDIO_PATH):
                os.remove(LOFI_AUDIO_PATH)
                log.text("Deleted processed audio.")
        except Exception as cleanup_err:
            log.text(f"⚠️ Cleanup error: {cleanup_err}")

        log.text("🎉 Process complete!")

    except Exception as e:
        log.text(f"Unexpected error: {str(e)}")
        st.error(f"An error occurred: {str(e)}")

    finally:
        progress.empty()
        log.empty()
