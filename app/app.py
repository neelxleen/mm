import os
import streamlit as st
from pydub import AudioSegment
from pytubefix import YouTube

import audio
import media
import video

st.title("🎵 Lofi Music Video Generator 🎥 (Tenor)")
st.write("Paste a YouTube URL or upload an audio file, then generate a lofi video with a random Tenor background (SFW).")

# Select audio input method
method = st.radio("Choose your input method:", ['YouTube URL', 'Upload Audio File'], key="input_method_radio")
TEMP_AUDIO_PATH = "temp_audio.mp3"
input_song = None

# Handle input from YouTube URL
if method == "YouTube URL":
    youtube_url = st.text_input("Enter YouTube URL:")
    if youtube_url:
        try:
            st.write("Downloading audio from YouTube...")
            yt = YouTube(youtube_url)
            audio_stream = yt.streams.get_audio_only()
            audio_stream.download(filename=TEMP_AUDIO_PATH)
            input_song = AudioSegment.from_file(TEMP_AUDIO_PATH)
            st.success("Audio downloaded successfully!")
            st.audio(TEMP_AUDIO_PATH)
        except Exception as e:
            st.error(f"Failed to download audio from YouTube: {e}")

# Handle input from uploaded audio file
elif method == "Upload Audio File":
    uploaded_file = st.file_uploader("Upload audio file", type=["mp3", "wav", "ogg"])
    if uploaded_file is not None:
        try:
            with open(TEMP_AUDIO_PATH, "wb") as f:
                f.write(uploaded_file.getbuffer())
            input_song = AudioSegment.from_file(TEMP_AUDIO_PATH)
            st.success("File uploaded successfully!")
            st.audio(TEMP_AUDIO_PATH)
        except Exception as e:
            st.error(f"Failed to process uploaded file: {e}")

# User inputs for Tenor GIF tag and content filter
gif_tag = st.text_input("Enter a tag for the background GIF", value="lofi city")
content_filter = st.selectbox("Content filter", ["off", "low", "medium", "high"], index=3)

# Generate button and processing logic with real-time verbose logs and progress bar
if st.button("✨ Generate Lofi Video"):
    if not input_song:
        st.warning("Please provide a song via YouTube URL or file upload before generating.")
    else:
        # Create placeholders for logs and progress bar
        log_placeholder = st.empty()
        progress_bar = st.progress(0)

        try:
            log_placeholder.text("Starting lofi audio processing...")
            progress_bar.progress(5)

            # Step 1: Apply lofi audio effects
            lofi_audio = audio.apply_lofi_effects(input_song)
            lofi_audio_path = "lofi_audio.mp3"
            lofi_audio.export(lofi_audio_path, format="mp3")
            log_placeholder.text("Lofi audio effects applied.")
            progress_bar.progress(30)

            # Step 2: Fetch random GIF or MP4 from Tenor API
            log_placeholder.text("Fetching media from Tenor...")
            media_path = media.fetch_random_tenor_media(tag=gif_tag, contentfilter=content_filter)
            if not media_path:
                log_placeholder.text("Failed to fetch media from Tenor. Please check your tag or API key.")
                progress_bar.empty()
                st.error("Failed to fetch media from Tenor. Please try again with a different tag or check your API key.")
                raise RuntimeError("Media fetch failed")
            log_placeholder.text(f"Media fetched: {media_path}")
            progress_bar.progress(60)

            # Step 3: Create the final video
            log_placeholder.text("Generating the final video...")
            output_video_path = "lofi_video.mp4"
            final_video = video.create_video_background(media_path, lofi_audio_path, output_video_path)
            if not final_video:
                log_placeholder.text("Video creation failed.")
                progress_bar.empty()
                st.error("Video creation failed.")
                raise RuntimeError("Video creation failed")
            log_placeholder.text("Video created successfully!")
            progress_bar.progress(100)

            # Display video and download button
            with open(final_video, "rb") as vf:
                video_bytes = vf.read()
                st.video(video_bytes)
                st.download_button("Download Video", video_bytes, file_name=output_video_path, mime="video/mp4")

            # Cleanup temp files
            try:
                os.remove(final_video)
                os.remove(media_path)
            except Exception as e:
                st.warning(f"Error cleaning temporary files: {e}")

            for temp_file in [TEMP_AUDIO_PATH, lofi_audio_path]:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception as e:
                        st.warning(f"Error deleting temporary file {temp_file}: {e}")

        except Exception as ex:
            # Exception already handled by messages shown, but can add logging here if needed
            pass

        finally:
            # Clear placeholders after all processing is complete
            log_placeholder.empty()
            progress_bar.empty()
