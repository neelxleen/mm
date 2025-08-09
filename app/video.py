import math
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.fx.Resize import Resize
from moviepy.video.fx.Loop import Loop  # lowercase 'loop'
from moviepy.video.fx.Crop import Crop


def extend_gif_to_mp4(gif_path: str, output_mp4_path: str, duration: float, log=None):
    """
    Convert a GIF to a smoothly looped MP4 by concatenating it repeatedly to fill the duration,
    then trimming the last clip to exact duration.
    """
    if log:
        log(f"Converting GIF to looped MP4 ({duration:.2f} seconds)...")
    clip = VideoFileClip(gif_path)
    clip_duration = clip.duration

    repeats = math.ceil(duration / clip_duration)
    clips = [clip] * repeats
    looped_clip = concatenate_videoclips(clips)
    looped_clip = looped_clip.subclip(0, duration)

    looped_clip.write_videofile(
        output_mp4_path,
        codec="libx264",
        audio=False,
        fps=clip.fps or 24,
        remove_temp=True,
        logger=None
    )

    clip.close()
    looped_clip.close()

    if log:
        log("GIF conversion complete.")
    return output_mp4_path


def create_video_background(media_path: str, audio_path: str, output_file: str, log=None):
    """
    Creates a 1920x1080 video by combining provided media (GIF or MP4) with audio.
    GIFs are converted to looped MP4s matching audio duration for stable processing.
    The video is resized, cropped, looped, and merged with audio for final output.
    """
    try:
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        if media_path.lower().endswith(".gif"):
            looped_mp4 = media_path.rsplit(".", 1)[0] + "_looped.mp4"
            media_path = extend_gif_to_mp4(media_path, looped_mp4, duration=duration, log=log)

        if log:
            log(f"Loading background media: {media_path}")
        video_clip = VideoFileClip(media_path)

        resized = Resize(height=1080).apply(video_clip)

        if resized.w < 1920:
            resized = Resize(width=1920).apply(resized)

        cropped = Crop(
            x_center=resized.w / 2,
            y_center=resized.h / 2,
            width=1920,
            height=1080
        ).apply(resized)

        looped_bg = Loop(duration=duration).apply(cropped)
        final = looped_bg.with_audio(audio_clip)

        if log:
            log("Starting final video encoding...")

        final.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            bitrate="3000k",       # Halve bitrate for speed
            fps=24,                # Lower frame rate
            preset="ultrafast",         # Fast encoding preset, if supported
            temp_audiofile="temp-audio.m4a",
            remove_temp=True,
            logger=None
        )

        if log:
            log(f"Video saved: {output_file}")

        video_clip.close()
        resized.close()
        cropped.close()
        looped_bg.close()
        final.close()
        audio_clip.close()

        return output_file

    except Exception as e:
        if log:
            log(f"Error creating video: {e}")
        return None
