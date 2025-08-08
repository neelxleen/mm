from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Loop import Loop
from moviepy.video.fx.Crop import Crop
from moviepy.video.fx.Loop import Loop  # for looping gifs before conversion
import streamlit as st

def extend_gif_to_mp4(gif_path: str, output_mp4_path: str, duration: float, log_func=None):
    """
    Loads a GIF, loops it until the specified duration by repeating,
    and writes out as an MP4 video file.
    """
    if log_func:
        log_func(f"Converting GIF '{gif_path}' to MP4 and looping to {duration:.2f} seconds...")
    else:
        st.write(f"Converting GIF '{gif_path}' to MP4 and looping to {duration:.2f} seconds...")

    clip = VideoFileClip(gif_path)

    # Loop the clip to desired duration
    looped_clip = loop(clip, duration=duration)

    # Write the looped video to MP4
    looped_clip.write_videofile(
        output_mp4_path,
        codec="libx264",
        audio=False,
        fps=clip.fps,
        remove_temp=True,
        logger=None
    )

    clip.close()
    looped_clip.close()

    if log_func:
        log_func(f"Conversion complete: '{output_mp4_path}' ready for processing.")
    else:
        st.write(f"Conversion complete: '{output_mp4_path}' ready for processing.")

    return output_mp4_path


def create_video_background(media_path: str, audio_path: str, output_file: str, log_func=None):
    try:
        audio_clip = AudioFileClip(audio_path)

        # If input media is a GIF, convert it to a looped MP4 matching the audio duration
        if media_path.lower().endswith('.gif'):
            looped_mp4_path = media_path.rsplit('.', 1)[0] + '_looped.mp4'
            media_path = extend_gif_to_mp4(media_path, looped_mp4_path, duration=audio_clip.duration, log_func=log_func)

        if log_func:
            log_func(f"Loading video clip from '{media_path}'...")
        else:
            st.write(f"Loading video clip from '{media_path}'...")

        video_clip = VideoFileClip(media_path)

        # Resize to height 1080, keeping aspect ratio
        resize_effect = Resize(height=1080)
        resized_clip = resize_effect.apply(video_clip)

        # If width is smaller than 1920, resize width to 1920, keeping aspect ratio
        if resized_clip.w < 1920:
            resize_effect_width = Resize(width=1920)
            resized_clip = resize_effect_width.apply(resized_clip)

        # Crop to exactly 1920x1080 centered
        crop_effect = Crop(
            x_center=resized_clip.w / 2,
            y_center=resized_clip.h / 2,
            width=1920,
            height=1080
        )
        cropped_clip = crop_effect.apply(resized_clip)

        # Loop the clip to match audio duration
        loop_effect = Loop(duration=audio_clip.duration)
        looped_clip = loop_effect.apply(cropped_clip)

        # Set audio to the video clip
        final_clip = looped_clip.with_audio(audio_clip)

        if log_func:
            log_func("Starting final video encoding...")
        else:
            st.write("Starting final video encoding...")

        # Write out the final video file
        final_clip.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            bitrate="5000k",
            fps=30,
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            logger=None
        )

        if log_func:
            log_func(f"Video encoding complete. Output file: '{output_file}'")
        else:
            st.write(f"Video encoding complete. Output file: '{output_file}'")

        return output_file

    except Exception as e:
        if log_func:
            log_func(f"Error creating video: {e}")
        else:
            st.error(f"Error creating video: {e}")
        return None
