import asyncio
import os
import subprocess
import json
import shutil
import edge_tts

SCENES = [
    {
        "id": "scene1_hook",
        "text": "Be honest: is your YouTube Music Liked Songs a chaotic graveyard of thousands of tracks you never actually listen to?",
        "lead_silence": 0.3,
        "tail_silence": 0.4
    },
    {
        "id": "scene2_intro",
        "text": "Meet AutoOrganize. It automatically sorts your Liked Songs into clean, smart genre playlists, right inside your browser side panel.",
        "lead_silence": 0.2,
        "tail_silence": 0.4
    },
    {
        "id": "scene3_scan",
        "text": "It scans your library privately on your device. Zero passwords, no cookies lifted, and nothing is uploaded to the cloud.",
        "lead_silence": 0.2,
        "tail_silence": 0.4
    },
    {
        "id": "scene4_split",
        "text": "Then, it auto-splits your music into real genre playlists using MusicBrainz. Unknowns stay uncategorized instead of guessed wrong.",
        "lead_silence": 0.2,
        "tail_silence": 0.4
    },
    {
        "id": "scene5_create",
        "text": "Preview every track before anything happens. With one click, AutoOrganize creates the playlists right in your YouTube Music, and Google syncs them everywhere.",
        "lead_silence": 0.15,
        "tail_silence": 0.25
    },
    {
        "id": "scene6_pricing",
        "text": "Best of all, no monthly subscriptions! Other playlist tools lock you into recurring monthly rent. AutoOrganize gives you a free preview and your first playlist free, with a one-time lifetime unlock forever.",
        "lead_silence": 0.15,
        "tail_silence": 0.25
    },
    {
        "id": "scene7_cta",
        "text": "Get it now on the Chrome Web Store and Microsoft Edge Add-ons, or reclaim your Liked Songs today at eight sixty-four zeros dot com.",
        "lead_silence": 0.15,
        "tail_silence": 0.5
    }
]

VOICE = "en-US-AvaNeural"
PITCH = "+5Hz"
RATE = "+13%"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORIG_AUDIO_DIR = os.path.join(BASE_DIR, "audio")
OUT_DIR = os.path.join(BASE_DIR, "audio_v2")
os.makedirs(OUT_DIR, exist_ok=True)

orig_bed = os.path.join(ORIG_AUDIO_DIR, "music_bed.wav")
v2_bed = os.path.join(OUT_DIR, "music_bed.wav")
if os.path.exists(orig_bed) and not os.path.exists(v2_bed):
    shutil.copyfile(orig_bed, v2_bed)

async def generate_scene_audio(scene):
    raw_path = os.path.join(OUT_DIR, f"{scene['id']}_raw.mp3")
    clean_path = os.path.join(OUT_DIR, f"{scene['id']}.wav")
    
    comm = edge_tts.Communicate(scene["text"], VOICE, rate=RATE, pitch=PITCH)
    await comm.save(raw_path)
    
    lead = 0.15
    tail = 0.25
    if scene["id"] == "scene7_cta":
        tail = 0.6
    
    filter_str = (
        f"adelay={int(lead*1000)}|{int(lead*1000)},"
        f"apad=pad_dur={tail},"
        f"aresample=44100,"
        f"loudnorm=I=-16:LRA=11:TP=-1.5"
    )
    
    cmd = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", filter_str,
        "-ar", "44100", "-ac", "2",
        clean_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    dur_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", clean_path
    ]
    res = subprocess.run(dur_cmd, check=True, stdout=subprocess.PIPE, text=True)
    dur = float(res.stdout.strip())
    
    return {
        "id": scene["id"],
        "text": scene["text"],
        "duration": dur,
        "wav_path": clean_path
    }

async def main():
    timeline = []
    current_time = 0.0
    
    for sc in SCENES:
        info = await generate_scene_audio(sc)
        info["start"] = round(current_time, 2)
        info["end"] = round(current_time + info["duration"], 2)
        current_time += info["duration"]
        timeline.append(info)
        print(f"Generated {sc['id']}: start={info['start']:.2f}s, dur={info['duration']:.2f}s, end={info['end']:.2f}s")
        
    total_duration = round(current_time, 2)
    print(f"\nTotal video duration: {total_duration:.2f} seconds")
    
    concat_list_path = os.path.join(OUT_DIR, "concat_list.txt")
    with open(concat_list_path, "w", encoding="utf-8") as f:
        for info in timeline:
            clean_name = os.path.basename(info["wav_path"])
            f.write(f"file '{clean_name}'\n")
            
    master_wav = os.path.join(OUT_DIR, "voiceover_full.wav")
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy", master_wav
    ]
    subprocess.run(concat_cmd, check=True)
    print(f"Master voiceover saved to: {master_wav}")
    
    timeline_path = os.path.join(OUT_DIR, "timeline.json")
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump({"total_duration": total_duration, "scenes": timeline}, f, indent=2)
    print(f"Timeline JSON saved to: {timeline_path}")

    soundtrack = os.path.join(OUT_DIR, "soundtrack.wav")
    music_bed = os.path.join(OUT_DIR, "music_bed.wav")
    if os.path.exists(music_bed):
        subprocess.run([
            "ffmpeg", "-y", "-i", master_wav, "-i", music_bed,
            "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.22[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2",
            soundtrack
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"Master soundtrack mixed and ready: {soundtrack}")
    else:
        shutil.copyfile(master_wav, soundtrack)
        print(f"Soundtrack copied from voiceover: {soundtrack}")

if __name__ == "__main__":
    asyncio.run(main())
