import math
import struct
import wave
import os

SAMPLE_RATE = 44100
DURATION = 58.0
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

CHORDS = [
    (146.83, [146.83, 220.00, 277.18, 369.99]), # D3, A3, C#4, F#4
    (164.81, [164.81, 246.94, 293.66, 392.00]), # E3, B3, D4, G4
    (185.00, [185.00, 220.00, 277.18, 329.63]), # F#3, A3, C#4, E4
    (138.59, [138.59, 207.65, 246.94, 329.63]), # C#3, G#3, B3, E4
]

BPM = 84.0
BEAT_LEN = 60.0 / BPM
BAR_LEN = BEAT_LEN * 4

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
os.makedirs(OUT_DIR, exist_ok=True)
music_path = os.path.join(OUT_DIR, "music_bed.wav")

with wave.open(music_path, "w") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    buffer = bytearray()
    
    for i in range(TOTAL_SAMPLES):
        t = i / SAMPLE_RATE
        bar_idx = int(t / BAR_LEN)
        chord = CHORDS[bar_idx % len(CHORDS)]
        bar_t = t % BAR_LEN
        chord_env = math.exp(-bar_t * 0.9) * 0.35 + 0.08
        tremolo = 1.0 + 0.12 * math.sin(2 * math.pi * 5.0 * t)
        
        chord_sig_l = 0.0
        chord_sig_r = 0.0
        for idx, freq in enumerate(chord[1]):
            note = (
                math.sin(2 * math.pi * freq * t) +
                0.35 * math.sin(2 * math.pi * freq * 2 * t) +
                0.12 * math.sin(2 * math.pi * freq * 3 * t)
            )
            pan = (idx / (len(chord[1]) - 1)) * 0.6 + 0.2
            chord_sig_l += note * (1.0 - pan)
            chord_sig_r += note * pan
            
        chord_sig_l *= chord_env * tremolo * 0.20
        chord_sig_r *= chord_env * tremolo * 0.20
        
        # Master fade out in last 2.5 seconds
        if t > DURATION - 2.5:
            fade = (DURATION - t) / 2.5
            chord_sig_l *= fade
            chord_sig_r *= fade
            
        sample_l = int(max(-32767, min(32767, chord_sig_l * 32767)))
        sample_r = int(max(-32767, min(32767, chord_sig_r * 32767)))
        buffer.extend(struct.pack("<hh", sample_l, sample_r))
        
    w.writeframes(buffer)
print(f"Procedural Rhodes music bed generated: {music_path}")
