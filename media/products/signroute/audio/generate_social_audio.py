import asyncio
import os
import subprocess
import json
import math
import struct
import wave
import edge_tts

VOICE = "en-US-AvaNeural"
PITCH = "+5Hz"
RATE = "+13%"

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(AUDIO_DIR, exist_ok=True)

SCRIPTS = {
    "pain": [
        {
            "id": "pain_scene1_hook",
            "text": "Paying forty dollars every single month to DocuSign just to get a signature on a Google Doc?",
            "lead": 0.25,
            "tail": 0.35
        },
        {
            "id": "pain_scene2_solution",
            "text": "SignRoute Local lets you draw signatures on an HTML5 canvas, stamp verified signer metadata directly into Google Docs, and export sealed PDFs straight to Google Drive.",
            "lead": 0.2,
            "tail": 0.4
        },
        {
            "id": "pain_scene3_cta",
            "text": "Available on the Google Workspace Marketplace for add-ons, or visit eight sixty-four zeros dot com.",
            "lead": 0.15,
            "tail": 0.5
        }
    ],
    "price": [
        {
            "id": "price_scene1_hook",
            "text": "Why pay monthly subscriptions and per-envelope fees just to sign your own internal documents?",
            "lead": 0.25,
            "tail": 0.35
        },
        {
            "id": "price_scene2_solution",
            "text": "SignRoute Local runs 100% locally in your Google Workspace account with unlimited signatures, zero per-envelope caps, zero cloud relays, and complete document custody.",
            "lead": 0.2,
            "tail": 0.4
        },
        {
            "id": "price_scene3_cta",
            "text": "A one-time nineteen ninety-nine unlock forever. Available on the Google Workspace Marketplace for add-ons at eight sixty-four zeros dot com.",
            "lead": 0.15,
            "tail": 0.5
        }
    ]
}

async def generate_scene_audio(scene):
    raw_path = os.path.join(AUDIO_DIR, f"{scene['id']}_raw.mp3")
    clean_path = os.path.join(AUDIO_DIR, f"{scene['id']}.wav")
    
    for attempt in range(4):
        try:
            comm = edge_tts.Communicate(scene["text"], VOICE, rate=RATE, pitch=PITCH)
            await comm.save(raw_path)
            break
        except Exception as e:
            if attempt == 3:
                raise
            await asyncio.sleep(1.5 * (attempt + 1))
    
    lead = scene["lead"]
    tail = scene["tail"]
    filters = []
    if lead > 0:
        filters.append(f"adelay={int(lead*1000)}|{int(lead*1000)}")
    if tail > 0:
        filters.append(f"apad=pad_dur={tail}")
    filters.append("loudnorm=I=-16:LRA=7:tp=-1.5")
    filter_str = ",".join(filters) if filters else "anull"
    
    cmd = [
        "ffmpeg", "-y", "-i", raw_path,
        "-af", filter_str,
        "-ar", "44100", "-ac", "2",
        clean_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return clean_path

def get_duration(wav_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        wav_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def generate_music_bed(duration_sec, output_path):
    SAMPLE_RATE = 44100
    TOTAL_SAMPLES = int(SAMPLE_RATE * duration_sec)
    
    CHORDS = [
        (146.83, [146.83, 220.00, 277.18, 369.99]), # D3, A3, C#4, F#4
        (164.81, [164.81, 246.94, 293.66, 392.00]), # E3, B3, D4, G4
        (185.00, [185.00, 220.00, 277.18, 329.63]), # F#3, A3, C#4, E4
        (138.59, [138.59, 207.65, 246.94, 329.63]), # C#3, G#3, B3, E4
    ]
    BPM = 84.0
    BAR_LEN = (60.0 / BPM) * 4
    
    with wave.open(output_path, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        buf = bytearray()
        
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
            
            if t > duration_sec - 2.0:
                fade = (duration_sec - t) / 2.0
                chord_sig_l *= fade
                chord_sig_r *= fade
                
            sample_l = int(max(-32767, min(32767, chord_sig_l * 32767)))
            sample_r = int(max(-32767, min(32767, chord_sig_r * 32767)))
            buf.extend(struct.pack("<hh", sample_l, sample_r))
            
        w.writeframes(buf)

async def build_variant(variant_name, scenes):
    print(f"\nProcessing variant: {variant_name}")
    timeline = []
    current_time = 0.0
    wav_files = []
    
    for sc in scenes:
        wav = await generate_scene_audio(sc)
        wav_files.append(wav)
        dur = get_duration(wav)
        timeline.append({
            "id": sc["id"],
            "text": sc["text"],
            "duration": dur,
            "wav_path": wav,
            "start": round(current_time, 3),
            "end": round(current_time + dur, 3)
        })
        print(f"  [OK] {sc['id']}: {dur:.2f}s -> {sc['text'][:40]}...")
        current_time += dur
        
    concat_list = os.path.join(AUDIO_DIR, f"concat_{variant_name}.txt")
    with open(concat_list, "w") as f:
        for w in wav_files:
            f.write(f"file '{os.path.basename(w)}'\n")
            
    full_vo = os.path.join(AUDIO_DIR, f"voiceover_{variant_name}.wav")
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c", "copy", full_vo
    ]
    subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    
    total_dur = get_duration(full_vo)
    
    music_bed = os.path.join(AUDIO_DIR, f"music_bed_{variant_name}.wav")
    generate_music_bed(total_dur + 2.0, music_bed)
    print(f"  [OK] Music bed generated: {total_dur + 2.0:.2f}s")
    
    soundtrack = os.path.join(AUDIO_DIR, f"soundtrack_{variant_name}.wav")
    cmd_duck = [
        "ffmpeg", "-y",
        "-i", full_vo,
        "-i", music_bed,
        "-filter_complex",
        "[1:a]volume=0.16[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=7:tp=-1.5[out]",
        "-map", "[out]",
        "-ar", "44100", "-ac", "2",
        soundtrack
    ]
    subprocess.run(cmd_duck, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"  [OK] Soundtrack mastered: {soundtrack} ({total_dur:.2f}s)")
    
    return {
        "total_duration": total_dur,
        "scenes": timeline,
        "soundtrack": soundtrack
    }

async def main():
    print("=== Generating SignRoute Local Social Shorts Audio Stems ===")
    results = {}
    for variant, scenes in SCRIPTS.items():
        results[variant] = await build_variant(variant, scenes)
        
    timeline_path = os.path.join(AUDIO_DIR, "social_timeline.json")
    with open(timeline_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nTimeline written to: {timeline_path}")

if __name__ == "__main__":
    asyncio.run(main())
