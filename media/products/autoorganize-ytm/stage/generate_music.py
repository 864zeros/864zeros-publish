import math
import struct
import wave
import os

SAMPLE_RATE = 44100
DURATION = 58.0 # seconds
TOTAL_SAMPLES = int(SAMPLE_RATE * DURATION)

# Chord progression in A major / F# minor (warm, thoughtful, modern tech vibe):
# 1: Dmaj7 (D3, F#3, A3, C#4)
# 2: E9 (E3, G#3, B3, D4)
# 3: F#m7 (F#3, A3, C#4, E4)
# 4: C#m7 (C#3, E3, G#3, B3)

CHORDS = [
    # root, notes
    (146.83, [146.83, 220.00, 277.18, 369.99]), # D3, A3, C#4, F#4
    (164.81, [164.81, 246.94, 293.66, 392.00]), # E3, B3, D4, G4
    (185.00, [185.00, 220.00, 277.18, 329.63]), # F#3, A3, C#4, E4
    (138.59, [138.59, 207.65, 246.94, 329.63]), # C#3, G#3, B3, E4
]

BPM = 84.0
BEAT_LEN = 60.0 / BPM
BAR_LEN = BEAT_LEN * 4 # ~2.857s per chord

out_dir = r"C:\dev\864zeros-llc\LLC-DIV-4-GTM\videos\autoorganize-ytm\audio"
music_path = os.path.join(out_dir, "music_bed.wav")

with wave.open(music_path, "w") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SAMPLE_RATE)
    
    buffer = bytearray()
    
    for i in range(TOTAL_SAMPLES):
        t = i / SAMPLE_RATE
        
        # Determine chord
        bar_idx = int(t / BAR_LEN)
        chord = CHORDS[bar_idx % len(CHORDS)]
        bar_t = t % BAR_LEN
        
        # Soft electric piano envelope for each chord strike
        chord_env = math.exp(-bar_t * 0.9) * 0.35 + 0.08
        
        # Gentle tremolo (5 Hz)
        tremolo = 1.0 + 0.12 * math.sin(2 * math.pi * 5.0 * t)
        
        # Synthesize chord harmonics (rich warm rhodes-like sound)
        chord_sig_l = 0.0
        chord_sig_r = 0.0
        for idx, freq in enumerate(chord[1]):
            # Fund + 2nd harmonic + 3rd harmonic
            note = (
                math.sin(2 * math.pi * freq * t) +
                0.35 * math.sin(2 * math.pi * freq * 2 * t) +
                0.12 * math.sin(2 * math.pi * freq * 3 * t)
            )
            pan = (idx / (len(chord[1]) - 1)) * 0.4 - 0.2 # subtle stereo spread
            chord_sig_l += note * (0.5 - pan)
            chord_sig_r += note * (0.5 + pan)
            
        chord_sig_l *= chord_env * tremolo * 0.18
        chord_sig_r *= chord_env * tremolo * 0.18
        
        # Warm sub bass
        bass_freq = chord[0] * 0.5 # Sub octave
        bass_env = math.exp(-bar_t * 0.7) * 0.3 + 0.15
        bass = (math.sin(2 * math.pi * bass_freq * t) + 0.2 * math.sin(2 * math.pi * bass_freq * 2 * t)) * bass_env * 0.22
        
        # Soft rhythmic pulse (kick on beat 1 & 3, soft tap on 2 & 4)
        beat_t = bar_t % BEAT_LEN
        beat_num = int(bar_t / BEAT_LEN)
        
        # Kick drum (deep 50Hz sine drop)
        kick = 0.0
        if beat_num in (0, 2):
            if beat_t < 0.18:
                inst_freq = 55.0 + 120.0 * math.exp(-beat_t * 35.0)
                kick = math.sin(2 * math.pi * inst_freq * beat_t) * math.exp(-beat_t * 18.0) * 0.25
                
        # Soft hi-hat / shaker on every 8th note
        eighth_t = bar_t % (BEAT_LEN / 2)
        hihat = 0.0
        if eighth_t < 0.04:
            # Pseudo white noise burst
            noise = (math.sin(i * 12.9898) * 43758.5453) % 1.0 - 0.5
            hihat = noise * math.exp(-eighth_t * 70.0) * 0.06
            
        # Overall master mix
        mix_l = chord_sig_l + bass + kick + hihat * 0.7
        mix_r = chord_sig_r + bass + kick + hihat * 0.9
        
        # Global Fade In (first 1s) and Fade Out (last 2s)
        fade = 1.0
        if t < 1.2:
            fade = t / 1.2
        elif t > (DURATION - 2.5):
            fade = max(0.0, (DURATION - t) / 2.5)
            
        mix_l *= fade * 0.4 # master bed volume
        mix_r *= fade * 0.4
        
        # Clamp to 16-bit
        int_l = max(-32767, min(32767, int(mix_l * 32767)))
        int_r = max(-32767, min(32767, int(mix_r * 32767)))
        
        buffer.extend(struct.pack('<hh', int_l, int_r))
        
        if len(buffer) >= 65536:
            w.writeframes(buffer)
            buffer = bytearray()
            
    if buffer:
        w.writeframes(buffer)

print(f"Music bed written to: {music_path}")
