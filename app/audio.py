from pydub import AudioSegment
from pydub.effects import normalize
import random
import io

def generate_vinyl_noise(duration_ms: int, volume_dB: float = -35.0) -> AudioSegment:
    """
    Generate subtle vinyl crackle/noise for the given duration.
    Here we generate white noise and lowpass filter it to sound like vinyl crackle.
    """
    # Create white noise
    noise = AudioSegment.white_noise(duration=duration_ms).apply_gain(volume_dB)

    # Low pass filter to mimic vinyl crackle characteristics
    noise = noise.low_pass_filter(8000)

    # Optionally, modulate volume randomly for more natural effect
    segments = []
    segment_len = 100  # ms
    for i in range(0, duration_ms, segment_len):
        seg = noise[i:i+segment_len]
        # Random volume modulation +-3 dB
        seg = seg + random.uniform(-3, 3)
        segments.append(seg)
    return sum(segments)

def apply_lofi_effects(song: AudioSegment) -> AudioSegment:
    """
    Apply lofi effects by downsampling, low-pass filtering, 
    plus adding subtle saturation, vinyl noise, slight echo and normalization.
    """
    # Normalize input audio to -1 dBFS max peak
    processed = normalize(song)

    # Downsample to 22050 Hz for vintage warmth
    processed = processed.set_frame_rate(22050)

    # Apply low-pass filter ~3000 Hz to muffle highs for lofi feel
    processed = processed.low_pass_filter(3000)

    # Add subtle saturation by soft clipping (simple distortion simulation)
    # Increase gain slightly then reduce volume for saturation effect
    processed = processed + 5
    processed = processed.apply_gain_stereo(-5, -5)

    # Overlay vinyl crackle/noise to add vintage texture
    noise = generate_vinyl_noise(len(processed), volume_dB=-40)
    processed = processed.overlay(noise)

    # Optional: add gentle echo effect by overlaying delayed, quieter audio
    delay_ms = 150
    echo_vol_reduction_db = 15
    delayed = processed - echo_vol_reduction_db
    delayed = delayed.delay(delay_ms)
    processed = processed.overlay(delayed)

    # Normalize again after effects
    processed = normalize(processed)

    return processed
