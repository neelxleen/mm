from pydub import AudioSegment
from pydub.effects import normalize, low_pass_filter

def add_delay(audio: AudioSegment, delay_ms: int, decay: float = 0.5) -> AudioSegment:
    """
    Adds a delay/echo effect by overlaying a delayed and attenuated copy of audio.
    """
    if delay_ms <= 0:
        return audio

    silent_segment = AudioSegment.silent(duration=delay_ms)
    delayed_audio = audio - (1 - decay) * 20  # attenuate volume according to decay (in dB)
    delayed_audio = silent_segment + delayed_audio  # shift delayed audio right by delay_ms
    combined_audio = audio.overlay(delayed_audio)
    return combined_audio


def _simple_reverb(sound: AudioSegment, delay_ms=220, decay=0.75, repeats=1):
    out = sound
    for i in range(1, repeats + 1):
        delayed = add_delay(sound, delay_ms * i, decay ** i)
        out = out.overlay(delayed)
    return out


def _speed_change(sound: AudioSegment, speed: float) -> AudioSegment:
    new_frame_rate = int(sound.frame_rate * speed)
    changed = sound._spawn(sound.raw_data, overrides={"frame_rate": new_frame_rate})
    return changed.set_frame_rate(sound.frame_rate)


def _bass_boost(sound: AudioSegment, gain_db=3, cutoff=150):
    lows = low_pass_filter(sound, cutoff)
    lows = lows + gain_db
    return sound.overlay(lows)


def apply_saturation(sound: AudioSegment, gain_db=2):
    saturated = sound + gain_db
    return saturated.apply_gain_stereo(-gain_db, -gain_db)


def apply_lofi_effects_pydub(song: AudioSegment) -> AudioSegment:
    # Normalize audio first
    processed = normalize(song)

    # Slow down to ~0.9x speed for lofi vibe
    processed = _speed_change(processed, speed=0.9)

    # Moderate low pass filter to soften highs (warmth)
    processed = low_pass_filter(processed, 3000)

    # Apply modest bass boost to reduce booming
    processed = _bass_boost(processed, gain_db=3, cutoff=150)

    # Apply subtle reverb with reduced repeats & higher decay for smoothness
    processed = _simple_reverb(processed, delay_ms=220, decay=0.75, repeats=1)

    # Add gentle saturation for analog warmth
    processed = apply_saturation(processed, gain_db=2)

    # Slight volume increase and normalize once more for balance
    processed = processed + 1
    processed = normalize(processed)

    # Final smoothing low pass to remove harshness (~7.5 kHz cutoff)
    processed = low_pass_filter(processed, 7500)

    # Downsample to 22050 Hz for vintage texture and smaller file
    processed = processed.set_frame_rate(22050)

    return processed
