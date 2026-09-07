#!/usr/bin/env python3
"""
ClearStreak Master Explainer - Voiceover Synthesis
Voice: en-US-AvaNeural with +5Hz pitch shift (1.02x avatar voice rule per GEMINI.md) and +13% speed.
Mastering: Scene cuts, concat, and EBU R128 (-16 LUFS) normalization via FFmpeg.
"""

import asyncio
import edge_tts
import json
import os
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(SCRIPT_DIR, "..", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"

SCENES = [
    {
        "id": "scene1_hook",
        "text": "Why does every habit tracker shame you the second you slip up? Break a streak, and they wipe your entire progress to zero. Not here."
    },
    {
        "id": "scene2_intro",
        "text": "Meet ClearStreak: the private habit and vice companion built on Data Over Shame."
    },
    {
        "id": "scene3_journeys",
        "text": "Track multiple habits at once — whether you're quitting vaping, cutting back alcohol, stopping doomscrolling, or overcoming late-night spending. Each with its own start date, streaks, and money saved."
    },
    {
        "id": "scene4_halt",
        "text": "An off day resets today's count, but never wipes your history. Your personal bests and total clear days stay permanent. Check in honestly with HALT: Hungry, Angry, Lonely, or Tired."
    },
    {
        "id": "scene5_grounding",
        "text": "In hard moments, use eyes-free haptic breathing circles to let an urge crest and pass, or tap the calm Rescue hub for trusted contacts and confidential lifelines."
    },
    {
        "id": "scene6_privacy",
        "text": "No cloud. No accounts. No servers to breach. Sealed with biometric encryption right on your phone. Screenshots are blocked."
    },
    {
        "id": "scene7_cta",
        "text": "No recurring subscriptions. Just a one-time unlock for lifetime peace of mind. Download ClearStreak on Google Play."
    }
]

VOICE = "en-US-AvaNeural"
RATE = "+13%"
PITCH = "+5Hz"

async def generate_scene(scene):
    mp3_path = os.path.join(AUDIO_DIR, f"{scene['id']}.mp3")
    wav_path = os.path.join(AUDIO_DIR, f"{scene['id']}.wav")
    
    communicate = edge_tts.Communicate(scene["text"], VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(mp3_path)
    
    # Convert to 44.1kHz 16-bit PCM WAV
    cmd = [
        FFMPEG, "-y",
        "-i", mp3_path,
        "-ar", "44100",
        "-ac", "2",
        "-c:a", "pcm_s16le",
        wav_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Get exact duration via ffprobe
    probe_cmd = [
        r"C:\ffmpeg\bin\ffprobe.exe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        wav_path
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    duration = float(res.stdout.strip())
    
    return {
        "id": scene["id"],
        "text": scene["text"],
        "wav": wav_path,
        "duration": duration
    }

async def main():
    print("[ClearStreak Master Audio] Synthesizing voiceover scenes...")
    results = []
    for scene in SCENES:
        r = await generate_scene(scene)
        print(f"  {r['id']}: {r['duration']:.2f}s")
        results.append(r)
    
    # Build concat file
    concat_txt = os.path.join(AUDIO_DIR, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for r in results:
            clean_p = r["wav"].replace("\\", "/")
            f.write(f"file '{clean_p}'\n")
    
    # Concat all into voiceover_raw.wav
    raw_wav = os.path.join(AUDIO_DIR, "voiceover_raw.wav")
    cmd = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        raw_wav
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Master with EBU R128 loudnorm (-16 LUFS)
    master_wav = os.path.join(AUDIO_DIR, "voiceover_full.wav")
    cmd_norm = [
        FFMPEG, "-y",
        "-i", raw_wav,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar", "44100",
        "-ac", "2",
        master_wav
    ]
    subprocess.run(cmd_norm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Get total master duration
    probe_cmd = [
        r"C:\ffmpeg\bin\ffprobe.exe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        master_wav
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    total_dur = float(res.stdout.strip())
    print(f"[ClearStreak Master Audio] Master voiceover generated: {total_dur:.2f}s -> {master_wav}")
    
    # Calculate timeline offsets
    timeline = []
    current_time = 0.0
    for r in results:
        timeline.append({
            "id": r["id"],
            "start": current_time,
            "end": current_time + r["duration"],
            "duration": r["duration"],
            "text": r["text"]
        })
        current_time += r["duration"]
    
    timeline_file = os.path.join(AUDIO_DIR, "timeline.json")
    with open(timeline_file, "w", encoding="utf-8") as f:
        json.dump({"total_duration": total_dur, "scenes": timeline}, f, indent=2)
    print(f"[ClearStreak Master Audio] Timeline map saved to {timeline_file}")

if __name__ == "__main__":
    asyncio.run(main())
