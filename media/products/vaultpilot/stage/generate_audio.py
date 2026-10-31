import asyncio
import os
import subprocess
import json
import shutil
import edge_tts

SCENES = [
    {
        "id": "scene1_hook",
        "text": "Tired of cloud-based web clippers trapping your research behind proprietary subscriptions?",
        "lead_silence": 0.3,
        "tail_silence": 0.4
    },
    {
        "id": "scene2_intro",
        "text": "Meet VaultPilot. 100% sovereign, local-first web clipping straight into your Obsidian vault.",
        "lead_silence": 0.2,
        "tail_silence": 0.4
    },
    {
        "id": "scene3_feature",
        "text": "Clip any page or selection to clean Markdown — straight into your local Obsidian, Logseq, or Capacities vault. 100% local, no account.",
        "lead_silence": 0.2,
        "tail_silence": 0.4
    },
    {
        "id": "scene4_pricing",
        "text": "Best of all, zero recurring subscriptions! Other tools charge monthly rent. VaultPilot gives you free Markdown capture forever, with a one-time lifetime Direct-to-Vault unlock.",
        "lead_silence": 0.15,
        "tail_silence": 0.25
    },
    {
        "id": "scene5_cta",
        "text": "Get it now on the Chrome Web Store and Microsoft Edge Add-ons, or take back sovereign control today at eight sixty-four zeros dot com.",
        "lead_silence": 0.15,
        "tail_silence": 0.5
    }
]

VOICE = "en-US-AvaNeural"
PITCH = "+5Hz"
RATE = "+13%"

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
ORIG_AUDIO_DIR = os.path.join(OUT_DIR, "audio")
AUDIO_DIR = os.path.join(OUT_DIR, "audio_v2")
os.makedirs(AUDIO_DIR, exist_ok=True)

orig_bed = os.path.join(ORIG_AUDIO_DIR, "music_bed.wav")
v2_bed = os.path.join(AUDIO_DIR, "music_bed.wav")
if os.path.exists(orig_bed) and not os.path.exists(v2_bed):
    shutil.copyfile(orig_bed, v2_bed)

async def generate_scene_audio(scene):
    scene_id = scene["id"]
    text = scene["text"]
    raw_mp3 = os.path.join(AUDIO_DIR, f"{scene_id}_raw.mp3")
    clean_wav = os.path.join(AUDIO_DIR, f"{scene_id}.wav")
    
    communicate = edge_tts.Communicate(text, VOICE, pitch=PITCH, rate=RATE)
    await communicate.save(raw_mp3)
    
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
    print("Synthesizing RULE-017 zero-price omnichannel voiceover stems for vaultpilot (v2)...")
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
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    print(f"Timeline map written: {timeline_path}")
    
    concat_txt = os.path.join(AUDIO_DIR, "concat_list.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for w in wav_files:
            f.write(f"file '{os.path.basename(w)}'\n")
            
    full_vo = os.path.join(AUDIO_DIR, "voiceover_full.wav")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", full_vo
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"Master voiceover compiled: {full_vo} ({round(current_time, 2)}s)")

    soundtrack = os.path.join(AUDIO_DIR, "soundtrack.wav")
    music_bed = os.path.join(AUDIO_DIR, "music_bed.wav")
    if os.path.exists(music_bed):
        subprocess.run([
            "ffmpeg", "-y", "-i", full_vo, "-i", music_bed,
            "-filter_complex", "[0:a]volume=1.0[v];[1:a]volume=0.22[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2",
            soundtrack
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    else:
        shutil.copyfile(full_vo, soundtrack)
    print(f"Soundtrack ready: {soundtrack}")

if __name__ == "__main__":
    asyncio.run(main())
