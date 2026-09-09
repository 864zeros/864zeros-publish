import asyncio
import os
import subprocess
import json
import edge_tts

SCENES = [
    {
        "id": "scene1_hook",
        "text": "Typing 60 project milestones from a spreadsheet into Google Calendar one by one?",
        "lead_silence": 0.3,
        "tail_silence": 0.4
    },
    {
        "id": "scene2_intro",
        "text": "Meet Sheet2Calendar Sync. 100% sovereign, local-first execution right inside your Google Workspace account.",
        "lead_silence": 0.2,
        "tail_silence": 0.4
    },
    {
        "id": "scene3_feature",
        "text": "Turn Google Sheets rows into synchronized Google Calendar events with dynamic two-way updates and scheduled background triggers. Zero third-party servers, zero recurring subscriptions.",
        "lead_silence": 0.2,
        "tail_silence": 0.4
    },
    {
        "id": "scene4_pricing",
        "text": "Best of all, zero recurring subscriptions! Other tools charge monthly rent. Sheet2Calendar Sync is a one-time twelve ninety-nine unlock forever.",
        "lead_silence": 0.15,
        "tail_silence": 0.25
    },
    {
        "id": "scene5_cta",
        "text": "Get it on the Google Workspace Marketplace for add-ons, or take back sovereign control today at eight sixty-four zeros dot com.",
        "lead_silence": 0.15,
        "tail_silence": 0.5
    }
]

VOICE = "en-US-AvaNeural"
PITCH = "+5Hz"
RATE = "+13%"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(OUT_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

async def generate_scene_audio(scene):
    scene_id = scene["id"]
    text = scene["text"]
    raw_mp3 = os.path.join(AUDIO_DIR, f"{scene_id}_raw.mp3")
    clean_wav = os.path.join(AUDIO_DIR, f"{scene_id}.wav")
    
    for attempt in range(4):
        try:
            communicate = edge_tts.Communicate(text, VOICE, pitch=PITCH, rate=RATE)
            await communicate.save(raw_mp3)
            break
        except Exception as e:
            if attempt == 3:
                raise e
            await asyncio.sleep(1.5 ** attempt)
    
    lead_s = scene.get("lead_silence", 0.0)
    tail_s = scene.get("tail_silence", 0.0)
    
    filter_chain = []
    if lead_s > 0:
        filter_chain.append(f"adelay={int(lead_s*1000)}|{int(lead_s*1000)}")
    if tail_s > 0:
        filter_chain.append(f"apad=pad_dur={tail_s}")
    filter_chain.append("loudnorm=I=-16:LRA=7:tp=-1.5")
    
    filter_str = ",".join(filter_chain) if filter_chain else "anull"
    
    cmd = [
        "ffmpeg", "-y", "-i", raw_mp3,
        "-af", filter_str,
        "-ar", "44100", "-ac", "2",
        clean_wav
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return clean_wav

def get_duration(wav_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        wav_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

async def main():
    print(f"Synthesizing voiceover stems for sheet2calendar...")
    timeline = []
    current_time = 0.0
    wav_files = []
    
    for scene in SCENES:
        wav_path = await generate_scene_audio(scene)
        wav_files.append(wav_path)
        dur = get_duration(wav_path)
        timeline.append({
            "id": scene["id"],
            "start": round(current_time, 2),
            "end": round(current_time + dur, 2),
            "duration": round(dur, 2),
            "text": scene["text"]
        })
        current_time += dur
    
    timeline_path = os.path.join(AUDIO_DIR, "timeline.json")
    with open(timeline_path, "w") as f:
        json.dump(timeline, f, indent=2)
    print(f"Timeline map written: {timeline_path}")
    
    concat_txt = os.path.join(AUDIO_DIR, "concat_list.txt")
    with open(concat_txt, "w") as f:
        for w in wav_files:
            f.write(f"file '{os.path.basename(w)}'\n")
            
    full_vo = os.path.join(AUDIO_DIR, "voiceover_full.wav")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", full_vo
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Master voiceover compiled: {full_vo} ({round(current_time, 2)}s)")

if __name__ == "__main__":
    asyncio.run(main())
