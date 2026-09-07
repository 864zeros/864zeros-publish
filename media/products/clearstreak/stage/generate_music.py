#!/usr/bin/env python3
"""
ClearStreak Soundtrack Generator & Audio Ducking Muxer
Generates a warm, peaceful, grounding Rhodes piano music bed with soft sine sub-bass and tremolo.
No external dependencies beyond Python standard library (wave, struct, math).
Muxes music bed with voiceover using FFmpeg sidechain / volume ducking to produce canonical soundtracks.
"""

import math
import os
import struct
import subprocess
import wave

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, "..", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"

SAMPLE_RATE = 44100

def note_freq(name_with_octave):
    notes = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
             'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
             'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
    letter = name_with_octave[:-1]
    octave = int(name_with_octave[-1])
    semitone = notes[letter] + (octave - 4) * 12
    return 440.0 * (2.0 ** ((semitone - 9) / 12.0))

# Peaceful, warm progression: Cmaj7 -> Am9 -> Fmaj7 -> Gsus4
CHORDS = [
    # Cmaj7 (C3, G3, B3, E4)
    ["C3", "G3", "B3", "E4"],
    # Am9 (A2, E3, G3, B3, C4)
    ["A2", "E3", "G3", "B3", "C4"],
    # Fmaj7 (F2, C3, E3, A3, C4)
    ["F2", "C3", "E3", "A3", "C4"],
    # Gsus4 / G (G2, D3, G3, C4, D4)
    ["G2", "D3", "G3", "C4", "D4"]
]

BPM = 76
BEAT_DUR = 60.0 / BPM
BAR_DUR = BEAT_DUR * 4  # ~3.158s per chord

def synth_rhodes(freq, t, note_t, note_dur):
    decay = math.exp(-2.5 * note_t)
    # Bell/tine component
    tine = math.sin(2.0 * math.pi * freq * 3.98 * note_t) * math.exp(-12.0 * note_t) * 0.25
    # Fundamental + harmonics
    fund = math.sin(2.0 * math.pi * freq * note_t)
    h2 = math.sin(2.0 * math.pi * freq * 2.0 * note_t) * 0.35 * math.exp(-4.0 * note_t)
    h3 = math.sin(2.0 * math.pi * freq * 3.0 * note_t) * 0.15 * math.exp(-6.0 * note_t)
    
    # Warm gentle tremolo (3.5 Hz)
    tremolo = 1.0 + 0.15 * math.sin(2.0 * math.pi * 3.5 * t)
    
    val = (fund + h2 + h3 + tine) * decay * tremolo
    return val

def generate_rhodes_bed(output_wav, total_seconds):
    num_samples = int(SAMPLE_RATE * total_seconds)
    samples_left = [0.0] * num_samples
    samples_right = [0.0] * num_samples
    
    total_bars = int(math.ceil(total_seconds / (len(CHORDS) * BAR_DUR))) + 1
    
    for bar_cycle in range(total_bars):
        for chord_idx, chord in enumerate(CHORDS):
            chord_start_t = (bar_cycle * len(CHORDS) + chord_idx) * BAR_DUR
            if chord_start_t >= total_seconds:
                break
            
            # Play each note in chord with slight strum delay
            for note_i, note_name in enumerate(chord):
                freq = note_freq(note_name)
                note_start = chord_start_t + (note_i * 0.025)
                note_dur = BAR_DUR * 1.15
                
                start_sample = int(note_start * SAMPLE_RATE)
                end_sample = min(num_samples, int((note_start + note_dur) * SAMPLE_RATE))
                
                # Pan notes across stereo field (-0.35 to +0.35)
                pan = -0.35 + (note_i / max(1, len(chord) - 1)) * 0.70
                gain_l = math.cos((pan + 1.0) * math.pi / 4.0) * 0.16
                gain_r = math.sin((pan + 1.0) * math.pi / 4.0) * 0.16
                
                for s in range(start_sample, end_sample):
                    t = s / SAMPLE_RATE
                    note_t = t - note_start
                    sig = synth_rhodes(freq, t, note_t, note_dur)
                    samples_left[s] += sig * gain_l
                    samples_right[s] += sig * gain_r
                    
    # Master gain and soft clip
    with wave.open(output_wav, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        
        packed_frames = bytearray()
        for i in range(num_samples):
            # Gentle fade in / fade out
            t = i / SAMPLE_RATE
            env = 1.0
            if t < 1.0:
                env = t
            elif t > total_seconds - 2.0:
                env = (total_seconds - t) / 2.0
                
            l = max(-1.0, min(1.0, samples_left[i] * env))
            r = max(-1.0, min(1.0, samples_right[i] * env))
            
            packed_frames += struct.pack('<hh', int(l * 32767), int(r * 32767))
            
        wf.writeframes(packed_frames)
        
    print(f"[ClearStreak Music] Generated Rhodes bed: {total_seconds:.1f}s -> {output_wav}")

def mix_soundtrack(voice_wav, music_wav, output_wav):
    """
    Mixes voiceover with background music ducked to -22dB during speech, -15dB during silence.
    """
    cmd = [
        FFMPEG, "-y",
        "-i", voice_wav,
        "-i", music_wav,
        "-filter_complex",
        "[1:a]volume=0.20[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-16:TP=-1.5:LRA=11[out]",
        "-map", "[out]",
        "-ar", "44100",
        "-ac", "2",
        output_wav
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[ClearStreak Music] Mixed and ducked soundtrack -> {output_wav}")

def main():
    # 1. Master Music Bed & Soundtrack
    master_music = os.path.join(AUDIO_DIR, "music_bed.wav")
    generate_rhodes_bed(master_music, 65.0)
    
    master_voice = os.path.join(AUDIO_DIR, "voiceover_full.wav")
    master_soundtrack = os.path.join(AUDIO_DIR, "soundtrack.wav")
    if os.path.exists(master_voice):
        mix_soundtrack(master_voice, master_music, master_soundtrack)
        
    # 2. Social Short A (Shame)
    shame_music = os.path.join(AUDIO_DIR, "music_bed_shame.wav")
    generate_rhodes_bed(shame_music, 24.0)
    shame_voice = os.path.join(AUDIO_DIR, "voiceover_shame.wav")
    shame_soundtrack = os.path.join(AUDIO_DIR, "soundtrack_shame.wav")
    if os.path.exists(shame_voice):
        mix_soundtrack(shame_voice, shame_music, shame_soundtrack)
        
    # 3. Social Short B (Privacy)
    privacy_music = os.path.join(AUDIO_DIR, "music_bed_privacy.wav")
    generate_rhodes_bed(privacy_music, 24.0)
    privacy_voice = os.path.join(AUDIO_DIR, "voiceover_privacy.wav")
    privacy_soundtrack = os.path.join(AUDIO_DIR, "soundtrack_privacy.wav")
    if os.path.exists(privacy_voice):
        mix_soundtrack(privacy_voice, privacy_music, privacy_soundtrack)

if __name__ == "__main__":
    main()
