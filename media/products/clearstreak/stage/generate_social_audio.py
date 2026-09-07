#!/usr/bin/env python3
"""
ClearStreak Social Micro-Shorts - Voiceover Synthesis
Two Variants (<20s each):
  Variant A: "The Shame Hook" (Data Over Shame)
  Variant B: "The Privacy Hook" (Private by Architecture)
Voice: en-US-AvaNeural with +5Hz pitch shift (1.02x avatar voice rule per GEMINI.md) and +13% speed.
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

VARIANTS = {
    "shame": {
        "title": "Variant A - The Shame Hook (Data Over Shame)",
        "scenes": [
            {
                "id": "shame_scene1_hook",
                "text": "Why does every habit tracker make you feel like trash when you slip up? Miss one day, and they wipe your entire streak to zero."
            },
            {
                "id": "shame_scene2_body",
                "text": "ClearStreak is built on Data Over Shame. An off day resets today's count, but your milestones, past stretches, and personal bests stay permanent."
            },
            {
                "id": "shame_scene3_cta",
                "text": "Encrypted on your phone, no subscriptions. Break habits with dignity. Download ClearStreak on Google Play."
            }
        ]
    },
    "privacy": {
        "title": "Variant B - The Privacy Hook (Private by Architecture)",
        "scenes": [
            {
                "id": "privacy_scene1_hook",
                "text": "Who has access to the habits you're secretly trying to break? Most wellness apps upload your struggles to cloud servers."
            },
            {
                "id": "privacy_scene2_body",
                "text": "ClearStreak is private by architecture. No accounts, no servers, no tracking. Encrypted on your device and unlocked only by your fingerprint."
            },
            {
                "id": "privacy_scene3_cta",
                "text": "Your habits are yours alone. ClearStreak: the private habit and vice companion."
            }
        ]
    }
}

VOICE = "en-US-AvaNeural"
RATE = "+13%"
PITCH = "+5Hz"

async def synthesize_variant(var_key, var_data):
    print(f"\n[ClearStreak Social Audio] Synthesizing {var_data['title']}...")
    results = []
    
    for scene in var_data["scenes"]:
        mp3_p = os.path.join(AUDIO_DIR, f"{scene['id']}.mp3")
        wav_p = os.path.join(AUDIO_DIR, f"{scene['id']}.wav")
        
        comm = edge_tts.Communicate(scene["text"], VOICE, rate=RATE, pitch=PITCH)
        await comm.save(mp3_p)
        
        cmd = [
            FFMPEG, "-y",
            "-i", mp3_p,
            "-ar", "44100",
            "-ac", "2",
            "-c:a", "pcm_s16le",
            wav_p
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        probe_cmd = [
            r"C:\ffmpeg\bin\ffprobe.exe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            wav_p
        ]
        res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
        dur = float(res.stdout.strip())
        print(f"  {scene['id']}: {dur:.2f}s")
        results.append({
            "id": scene["id"],
            "wav": wav_p,
            "duration": dur,
            "text": scene["text"]
        })
    
    concat_txt = os.path.join(AUDIO_DIR, f"concat_{var_key}.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for r in results:
            clean_p = r["wav"].replace("\\", "/")
            f.write(f"file '{clean_p}'\n")
            
    raw_wav = os.path.join(AUDIO_DIR, f"voiceover_raw_{var_key}.wav")
    cmd_concat = [
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt,
        "-c", "copy",
        raw_wav
    ]
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    norm_wav = os.path.join(AUDIO_DIR, f"voiceover_{var_key}.wav")
    cmd_norm = [
        FFMPEG, "-y",
        "-i", raw_wav,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar", "44100",
        "-ac", "2",
        norm_wav
    ]
    subprocess.run(cmd_norm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    probe_cmd = [
        r"C:\ffmpeg\bin\ffprobe.exe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        norm_wav
    ]
    res = subprocess.run(probe_cmd, capture_output=True, text=True, check=True)
    total_dur = float(res.stdout.strip())
    print(f"  Total Master ({var_key}): {total_dur:.2f}s -> {norm_wav}")
    
    timeline = []
    curr = 0.0
    for r in results:
        timeline.append({
            "id": r["id"],
            "start": curr,
            "end": curr + r["duration"],
            "duration": r["duration"],
            "text": r["text"]
        })
        curr += r["duration"]
        
    tl_file = os.path.join(AUDIO_DIR, f"timeline_{var_key}.json")
    with open(tl_file, "w", encoding="utf-8") as f:
        json.dump({"variant": var_key, "total_duration": total_dur, "scenes": timeline}, f, indent=2)
    print(f"  Timeline saved -> {tl_file}")
    
    return total_dur

async def main():
    for k, v in VARIANTS.items():
        await synthesize_variant(k, v)

if __name__ == "__main__":
    asyncio.run(main())
