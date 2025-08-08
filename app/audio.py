from pydub import AudioSegment

def apply_lofi_effects(song: AudioSegment) -> AudioSegment:
    """
    Apply lofi effects by downsampling and low-pass filtering.
    pydub supports low_pass_filter, so we use it here.
    """
    # Downsample to 22050 Hz
    processed = song.set_frame_rate(22050)
    # Apply low-pass filter for muffled lofi sound
    processed = processed.low_pass_filter(3000)
    # Optional: add some subtle saturation or noise here if needed

    return processed
