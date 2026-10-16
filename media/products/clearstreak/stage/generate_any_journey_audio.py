#!/usr/bin/env python3
"""
ClearStreak Social Short D — "Any Journey: Streak Doing OR Days Not Doing" (People Holding ClearStreak)
Synthesizes Edge-TTS voiceover (en-US-AvaNeural, +5Hz pitch, +13% rate) + procedural Rhodes music bed
and mixes to -14.0 LUFS broadcast standard.
"""

import asyncio
import edge_tts
import json
import math
import os
import struct
import subprocess
import wave

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, "..", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"
FFPROBE = r"C:\ffmpeg\bin\ffprobe.exe"

VOICE = "en-US-AvaNeural"
RATE = "+13%"
PITCH = "+5Hz"

SCENES = [
    {
        "id": "any_scene1_hook",
        "text": "Whether you're counting a streak of days doing what builds you up, or days not doing what holds you back, your journey belongs on your phone, not in the cloud."
    },
    {
        "id": "any_scene2_body",
        "text": "ClearStreak tracks both daily disciplines and habits you're leaving behind under Data Over Shame. An off day resets today's count, but never erases your lifetime days or milestone coins."
    },
    {
        "id": "any_scene3_cta",
        "text": "Eyes-free haptic grounding, fingerprint encryption, and zero subscriptions. Start any journey with ClearStreak."
    }
]

def generate_rhodes_bed(wav_path, duration_sec, sample_rate=44100):
    num_samples = int((duration_sec + 1.5) * sample_rate)
    chords = [
        [261.63, 329.63, 392.00, 493.88],  # Cmaj7
        [220.00, 261.63, 329.63, 392.00],  # Am7
        [174.61, 220.00, 261.63, 349.23],  # Fmaj7
        [196.00, 246.94, 293.66, 392.00],  # G6
    ]
    chord_len = 3.5
    with wave.open(wav_path, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            c_idx = int(t / chord_len) % len(chords)
            t_in_chord = t % chord_len
            env = min(1.0, t_in_chord / 0.15) * math.exp(-t_in_chord * 0.45)
            fade_out = max(0.0, min(1.0, (duration_sec + 1.2 - t) / 1.2))
            val = 0.0
            for f in chords[c_idx]:
                val += math.sin(2 * math.pi * f * t) * 0.6
                val += math.sin(2 * math.pi * (f * 2) * t) * 0.15 * math.exp(-t_in_chord * 1.2)
            sample = val * env * fade_out * 0.18
            s_int = max(-32767, min(32767, int(sample * 32767)))
            frames += struct.pack("<hh", s_int, s_int)
        wf.writeframes(frames)

async def main():
    import urllib.request, email.utils, time
    from edge_tts import drm
    try:
        req = urllib.request.Request("https://www.bing.com", method="HEAD")
        with urllib.request.urlopen(req, timeout=5) as resp:
            date_str = resp.headers.get("Date")
            if date_str:
                server_ts = email.utils.mktime_tz(email.utils.parsedate_tz(date_str))
                drm.DRM.adj_clock_skew_seconds(server_ts - time.time())
                print(f"Synced DRM clock skew: {drm.DRM.clock_skew_seconds:.1f}s")
    except Exception as e:
        print("Clock skew check skipped:", e)

    results = []
    for scene in SCENES:
        mp3_p = os.path.join(AUDIO_DIR, f"{scene['id']}.mp3")
        wav_p = os.path.join(AUDIO_DIR, f"{scene['id']}.wav")
        comm = edge_tts.Communicate(scene["text"], VOICE, rate=RATE, pitch=PITCH)
        await comm.save(mp3_p)
        subprocess.run([FFMPEG, "-y", "-i", mp3_p, "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", wav_p],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        res = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=noprint_wrappers=1:nokey=1", wav_p],
                             capture_output=True, text=True, check=True)
        dur = float(res.stdout.strip())
        print(f"  {scene['id']}: {dur:.2f}s")
        results.append({"id": scene["id"], "wav": wav_p, "duration": dur, "text": scene["text"]})

    concat_txt = os.path.join(AUDIO_DIR, "concat_any.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"file '{r['wav'].replace(chr(92), '/')}'\n")

    raw_wav = os.path.join(AUDIO_DIR, "voiceover_raw_any.wav")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt, "-c", "copy", raw_wav],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    norm_wav = os.path.join(AUDIO_DIR, "voiceover_any.wav")
    subprocess.run([FFMPEG, "-y", "-i", raw_wav, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "2", norm_wav],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    res = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=noprint_wrappers=1:nokey=1", norm_wav],
                         capture_output=True, text=True, check=True)
    total_dur = float(res.stdout.strip())

    bed_wav = os.path.join(AUDIO_DIR, "music_bed_any.wav")
    generate_rhodes_bed(bed_wav, total_dur)

    soundtrack_wav = os.path.join(AUDIO_DIR, "soundtrack_any.wav")
    subprocess.run([
        FFMPEG, "-y",
        "-i", norm_wav,
        "-i", bed_wav,
        "-filter_complex", "[0:a]volume=1.0[vo];[1:a]volume=0.22[bg];[vo][bg]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
        "-map", "[out]",
        "-ar", "44100", "-ac", "2",
        soundtrack_wav
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    timeline = []
    curr = 0.0
    for r in results:
        timeline.append({
            "id": r["id"],
            "start": round(curr, 3),
            "end": round(curr + r["duration"], 3),
            "duration": round(r["duration"], 3),
            "text": r["text"]
        })
        curr += r["duration"]

    tl_file = os.path.join(AUDIO_DIR, "timeline_any.json")
    with open(tl_file, "w", encoding="utf-8") as f:
        json.dump({"variant": "any", "total_duration": round(total_dur, 3), "scenes": timeline}, f, indent=2)
    print(f"Total Any-Journey Master: {total_dur:.2f}s -> {soundtrack_wav}")

if __name__ == "__main__":
    asyncio.run(main())
