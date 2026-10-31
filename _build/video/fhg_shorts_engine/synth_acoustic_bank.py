"""Synthesize the canonical FHG 432Hz Ambient Pad and 4 Organic Micro-Foley stems.

Outputs (48kHz, 16-bit stereo WAV):
- C:/dev/864zeros-publish/media/audio/music/fhg_432hz_ambient_pad.wav (60.0s)
- C:/dev/864zeros-publish/media/audio/sfx/fhg_foley/parchment_turn.wav (0.65s)
- C:/dev/864zeros-publish/media/audio/sfx/fhg_foley/leather_close.wav (0.70s)
- C:/dev/864zeros-publish/media/audio/sfx/fhg_foley/felt_piano.wav (1.80s)
- C:/dev/864zeros-publish/media/audio/sfx/fhg_foley/desert_wind.wav (1.40s)
"""
from __future__ import annotations

import wave
from pathlib import Path
import numpy as np

SR = 48000
MUSIC_DIR = Path(r"C:\dev\864zeros-publish\media\audio\music")
FOLEY_DIR = Path(r"C:\dev\864zeros-publish\media\audio\sfx\fhg_foley")


def save_stereo_wav(path: Path, left: np.ndarray, right: np.ndarray, peak: float = 0.85) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    max_val = max(float(np.max(np.abs(left))), float(np.max(np.abs(right))), 1e-6)
    scale = (peak / max_val) * 32767.0
    stereo = np.empty((left.size * 2,), dtype=np.int16)
    stereo[0::2] = np.clip(left * scale, -32768, 32767).astype(np.int16)
    stereo[1::2] = np.clip(right * scale, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(stereo.tobytes())
    print(f"Saved {path} ({path.stat().st_size:,} bytes)")


def build_432hz_pad(duration: float = 60.0) -> None:
    """Warm, cinematic 432Hz-tuned harmonic cello/choir pad with naturally carved midrange."""
    t = np.linspace(0.0, duration, int(SR * duration), endpoint=False)
    rng = np.random.default_rng(432)

    # A4 = 432Hz -> Root A2 = 108Hz, E3 = 161.82Hz, A3 = 216Hz, C#4 = 272.14Hz, E4 = 323.63Hz
    freqs = [54.0, 108.0, 161.82, 216.0, 272.14, 323.63, 432.0]
    amps = [0.32, 0.45, 0.28, 0.35, 0.16, 0.18, 0.12]

    left = np.zeros_like(t)
    right = np.zeros_like(t)

    for f, a in zip(freqs, amps):
        # Slow chorus detune & breathing LFO per harmonic
        lfo_l = 0.82 + 0.18 * np.sin(2 * np.pi * (0.07 + rng.uniform(0, 0.04)) * t + rng.uniform(0, 6.28))
        lfo_r = 0.82 + 0.18 * np.sin(2 * np.pi * (0.07 + rng.uniform(0, 0.04)) * t + rng.uniform(0, 6.28))
        detune = 0.0018 * f
        left += a * lfo_l * np.sin(2 * np.pi * (f - detune) * t)
        right += a * lfo_r * np.sin(2 * np.pi * (f + detune) * t)

    # Smooth fade in/out for seamless looping
    env = np.ones_like(t)
    fade_samples = int(SR * 2.0)
    env[:fade_samples] = np.linspace(0.0, 1.0, fade_samples)
    env[-fade_samples:] = np.linspace(1.0, 0.0, fade_samples)

    save_stereo_wav(MUSIC_DIR / "fhg_432hz_ambient_pad.wav", left * env, right * env, peak=0.75)


def build_foley_stems() -> None:
    rng = np.random.default_rng(2026)

    # 1. parchment_turn.wav (0.65s crisp dry papyrus/parchment page brush)
    dur = 0.65
    t = np.linspace(0.0, dur, int(SR * dur), endpoint=False)
    noise = rng.normal(0, 1, t.size)
    # Band-limited rustle via moving-average difference + double envelope
    smooth1 = np.convolve(noise, np.ones(12) / 12, mode="same")
    smooth2 = np.convolve(noise, np.ones(64) / 64, mode="same")
    band = smooth1 - smooth2
    env = np.exp(-((t - 0.18) ** 2) / (2 * 0.07**2)) + 0.55 * np.exp(-((t - 0.36) ** 2) / (2 * 0.09**2))
    save_stereo_wav(FOLEY_DIR / "parchment_turn.wav", band * env * 0.9, np.roll(band, 18) * env * 0.85, peak=0.70)

    # 2. leather_close.wav (0.70s warm low-frequency book thud + clasp transient)
    dur = 0.70
    t = np.linspace(0.0, dur, int(SR * dur), endpoint=False)
    f_sweep = 115.0 * np.exp(-t * 14.0) + 38.0
    phase = 2 * np.pi * np.cumsum(f_sweep) / SR
    thud = np.sin(phase) * np.exp(-t * 11.0)
    air_burst = np.convolve(rng.normal(0, 1, t.size), np.ones(40) / 40, mode="same") * np.exp(-t * 24.0) * 0.35
    sig = thud + air_burst
    save_stereo_wav(FOLEY_DIR / "leather_close.wav", sig, np.roll(sig, 10), peak=0.78)

    # 3. felt_piano.wav (1.80s soft, intimate 432Hz-tuned A3 + E4 felt piano hammer & decay)
    dur = 1.80
    t = np.linspace(0.0, dur, int(SR * dur), endpoint=False)
    hammer = np.convolve(rng.normal(0, 1, t.size), np.ones(35) / 35, mode="same") * np.exp(-t * 55.0) * 0.18
    tone_l = (
        0.65 * np.sin(2 * np.pi * 216.0 * t) * np.exp(-t * 2.4)
        + 0.28 * np.sin(2 * np.pi * 323.63 * t) * np.exp(-t * 2.9)
        + 0.14 * np.sin(2 * np.pi * 432.0 * t) * np.exp(-t * 3.6)
    )
    tone_r = (
        0.65 * np.sin(2 * np.pi * 216.15 * t) * np.exp(-t * 2.4)
        + 0.28 * np.sin(2 * np.pi * 323.45 * t) * np.exp(-t * 2.9)
        + 0.14 * np.sin(2 * np.pi * 431.85 * t) * np.exp(-t * 3.6)
    )
    attack = np.minimum(1.0, t / 0.012)
    save_stereo_wav(FOLEY_DIR / "felt_piano.wav", (tone_l + hammer) * attack, (tone_r + hammer) * attack, peak=0.72)

    # 4. desert_wind.wav (1.40s warm resonant Judean breeze swell across cut boundary)
    dur = 1.40
    t = np.linspace(0.0, dur, int(SR * dur), endpoint=False)
    raw = rng.normal(0, 1, t.size)
    low = np.convolve(raw, np.ones(90) / 90, mode="same")
    mid = np.convolve(raw, np.ones(24) / 24, mode="same") - low
    swell = np.sin(np.pi * (t / dur)) ** 1.6
    shimmer = 0.25 * np.sin(2 * np.pi * 108.0 * t) * swell
    wind_l = (0.65 * low + 0.35 * mid + shimmer) * swell
    wind_r = (0.65 * np.roll(low, 32) + 0.35 * np.roll(mid, 14) + shimmer) * swell
    save_stereo_wav(FOLEY_DIR / "desert_wind.wav", wind_l, wind_r, peak=0.68)


if __name__ == "__main__":
    build_432hz_pad()
    build_foley_stems()
