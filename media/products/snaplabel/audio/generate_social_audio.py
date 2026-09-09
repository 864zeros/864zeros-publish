import asyncio
import os
import subprocess
import json
import edge_tts
import wave
import math
import struct

VOICE = "en-US-AvaNeural"
PITCH = "+5Hz" # 1.02x pitch per C:\dev\GEMINI.md
RATE = "+13%"

BASE_DIR = r"C:\dev\864zeros-llc\LLC-DIV-4-GTM\videos\snaplabel"
SOCIAL_DIR = os.path.join(BASE_DIR, "social_shorts")
AUDIO_DIR = os.path.join(SOCIAL_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VARIANTS = {
    "pain": [
        {
            "id": "pain_scene1_hook",
            "text": "Ever printed 30 address labels only to watch every single one drift completely off the stickers?",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "pain_scene2_solution",
            "text": "SnapLabel merges Google Sheets directly into millimeter-calibrated Avery labels right inside your account. Zero drift, zero data upload.",
            "lead": 0.15,
            "tail": 0.25
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
            "text": "Why are cloud services charging 50 dollars a year just to align text boxes into Avery grids?",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "price_scene2_solution",
            "text": "SnapLabel runs 100% locally in Google Apps Script. Print calibrated labels, envelopes, and barcodes forever with zero subscriptions.",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "price_scene3_cta",
            "text": "Just a one-time twenty-nine dollar unlock. Available on the Google Workspace Marketplace for add-ons at eight sixty-four zeros dot com.",
            "lead": 0.15,
            "tail": 0.5
        }
    ]
}

async def generate_scene_audio(scene):
    raw_path = os.path.join(AUDIO_DIR, f"{scene['id']}_raw.mp3")
    clean_path = os.path.join(AUDIO_DIR, f"{scene['id']}.wav")
    
    comm = edge_tts.Communicate(scene["text"], VOICE, rate=RATE, pitch=PITCH)
    await comm.save(raw_path)
    
    lead = scene["lead"]
    tail = scene["tail"]
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

def synthesize_music_bed(duration_sec, out_wav):
    SAMPLE_RATE = 44100
    TOTAL_SAMPLES = int(SAMPLE_RATE * (duration_sec + 2.0))
    
    CHORDS = [
        (146.83, [146.83, 220.00, 277.18, 369.99]), # Dmaj7
        (164.81, [164.81, 246.94, 293.66, 392.00]), # E9
        (185.00, [185.00, 220.00, 277.18, 329.63]), # F#m7
        (138.59, [138.59, 207.65, 246.94, 329.63]), # C#m7
    ]
    BPM = 88.0
    BEAT_LEN = 60.0 / BPM
    BAR_LEN = BEAT_LEN * 4
    
    with wave.open(out_wav, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        
        buffer = bytearray()
        for i in range(TOTAL_SAMPLES):
            t = i / SAMPLE_RATE
            bar_idx = int(t / BAR_LEN)
            chord = CHORDS[bar_idx % len(CHORDS)]
            bar_t = t % BAR_LEN
            
            chord_env = math.exp(-bar_t * 0.95) * 0.35 + 0.08
            tremolo = 1.0 + 0.12 * math.sin(2 * math.pi * 5.0 * t)
            
            sig_l = 0.0
            sig_r = 0.0
            for idx, freq in enumerate(chord[1]):
                note = (
                    math.sin(2 * math.pi * freq * t) +
                    0.35 * math.sin(2 * math.pi * freq * 2 * t) +
                    0.12 * math.sin(2 * math.pi * freq * 3 * t)
                )
                pan = (idx / (len(chord[1]) - 1)) * 0.6 + 0.2
                sig_l += note * (1.0 - pan)
                sig_r += note * pan
                
            sig_l *= chord_env * tremolo * 0.18
            sig_r *= chord_env * tremolo * 0.18
            
            if t > duration_sec - 1.5:
                fade = max(0.0, (duration_sec + 0.5 - t) / 2.0)
                sig_l *= fade
                sig_r *= fade
                
            sample_l = int(max(-32767, min(32767, sig_l * 32767)))
            sample_r = int(max(-32767, min(32767, sig_r * 32767)))
            buffer.extend(struct.pack("<hh", sample_l, sample_r))
            
        w.writeframes(buffer)
    print(f"Synthesized bed: {out_wav} ({duration_sec + 2.0:.1f}s)")

async def main():
    metadata = {}
    for var_name, scenes in VARIANTS.items():
        print(f"\n--- Generating Variant: {var_name} ---")
        timeline = []
        curr_time = 0.0
        for sc in scenes:
            info = await generate_scene_audio(sc)
            info["start"] = curr_time
            info["end"] = curr_time + info["duration"]
            curr_time += info["duration"]
            timeline.append(info)
            print(f"Scene {sc['id']}: {info['duration']:.2f}s")
            
        total_dur = curr_time
        print(f"Total {var_name} VO duration: {total_dur:.2f}s")
        
        concat_path = os.path.join(AUDIO_DIR, f"concat_{var_name}.txt")
        with open(concat_path, "w", encoding="utf-8") as f:
            for item in timeline:
                f.write(f"file '{os.path.basename(item['wav_path'])}'\n")
                
        master_vo = os.path.join(AUDIO_DIR, f"voiceover_{var_name}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_path, "-c", "copy", master_vo
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        bed_wav = os.path.join(AUDIO_DIR, f"music_bed_{var_name}.wav")
        synthesize_music_bed(total_dur, bed_wav)
        
        soundtrack = os.path.join(AUDIO_DIR, f"soundtrack_{var_name}.wav")
        mix_cmd = [
            "ffmpeg", "-y",
            "-i", master_vo,
            "-i", bed_wav,
            "-filter_complex",
            "[0:a]volume=1.0[v];[1:a]volume=0.22[m];[v][m]amix=inputs=2:duration=first,loudnorm=I=-14:LRA=9:TP=-1.5",
            "-ar", "44100", "-ac", "2",
            soundtrack
        ]
        subprocess.run(mix_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Master soundtrack created: {soundtrack}")
        
        metadata[var_name] = {
            "total_duration": total_dur,
            "scenes": timeline,
            "soundtrack": soundtrack
        }
        
    meta_path = os.path.join(AUDIO_DIR, "social_timeline.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"\nSocial timeline saved: {meta_path}")

if __name__ == "__main__":
    asyncio.run(main())
