import asyncio
import os
import subprocess
import json
import edge_tts
import wave
import math
import struct

VOICE = "en-US-AvaNeural"
PITCH = "+5Hz"
RATE = "+13%"

BASE_DIR = r"C:\dev\864zeros-llc\LLC-DIV-4-GTM\videos\rowarchiver"
SOCIAL_DIR = os.path.join(BASE_DIR, "social_shorts")
AUDIO_DIR = os.path.join(SOCIAL_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VARIANTS = {
    "pain": [
        {
            "id": "pain_scene1_hook",
            "text": "Every time you open your team tracker, your browser completely locks up for 30 seconds.",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "pain_scene2_solution",
            "text": "RowArchiver automatically moves completed rows into dedicated archive tabs with atomic LockService protection. Instantly restore formula calculation speed.",
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
            "text": "You don't need a 100-dollar-a-month enterprise database sync just to archive closed rows from Google Sheets.",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "price_scene2_solution",
            "text": "RowArchiver runs 100% locally inside Google Sheets Apps Script with zero recurring subscriptions and zero cloud databases.",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "price_scene3_cta",
            "text": "Just a one-time twelve ninety-nine unlock forever. Available on the Google Workspace Marketplace for add-ons at eight sixty-four zeros dot com.",
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
    TOTAL_SAMPLES = int(SAMPLE_RATE * duration_sec)
    
    CHORDS = [
        (146.83, [146.83, 220.00, 277.18, 369.99]),
        (164.81, [164.81, 246.94, 293.66, 392.00]),
        (185.00, [185.00, 220.00, 277.18, 329.63]),
        (138.59, [138.59, 207.65, 246.94, 329.63]),
    ]
    
    BPM = 84.0
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
                
            chord_sig_l *= chord_env * tremolo * 0.22
            chord_sig_r *= chord_env * tremolo * 0.22
            
            if t > duration_sec - 1.5:
                fade = (duration_sec - t) / 1.5
                chord_sig_l *= fade
                chord_sig_r *= fade
                
            sample_l = int(max(-32767, min(32767, chord_sig_l * 32767)))
            sample_r = int(max(-32767, min(32767, chord_sig_r * 32767)))
            buffer.extend(struct.pack("<hh", sample_l, sample_r))
            
        w.writeframes(buffer)

async def main():
    print("=== Generating RowArchiver Social Shorts Audio Stems ===")
    manifest = {}
    
    for variant_key, scenes in VARIANTS.items():
        print(f"\nProcessing variant: {variant_key}")
        variant_results = []
        total_time = 0.0
        
        for sc in scenes:
            info = await generate_scene_audio(sc)
            info["start"] = total_time
            info["end"] = total_time + info["duration"]
            total_time += info["duration"]
            variant_results.append(info)
            print(f"  [OK] {info['id']}: {info['duration']:.2f}s -> {info['text'][:40]}...")
            
        concat_txt = os.path.join(AUDIO_DIR, f"concat_{variant_key}.txt")
        with open(concat_txt, "w") as f:
            for r in variant_results:
                f.write(f"file '{os.path.basename(r['wav_path'])}'\n")
                
        vo_out = os.path.join(AUDIO_DIR, f"voiceover_{variant_key}.wav")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_txt, "-c", "copy", vo_out
        ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        bed_out = os.path.join(AUDIO_DIR, f"music_bed_{variant_key}.wav")
        bed_dur = total_time + 2.0
        synthesize_music_bed(bed_dur, bed_out)
        print(f"  [OK] Music bed generated: {bed_dur:.2f}s")
        
        soundtrack_out = os.path.join(AUDIO_DIR, f"soundtrack_{variant_key}.wav")
        mix_cmd = [
            "ffmpeg", "-y",
            "-i", vo_out,
            "-i", bed_out,
            "-filter_complex",
            "[0:a]volume=1.0[v];[1:a]volume=0.20[m];[v][m]amix=inputs=2:duration=first,loudnorm=I=-14:LRA=9:TP=-1.5",
            "-ar", "44100", "-ac", "2",
            soundtrack_out
        ]
        subprocess.run(mix_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"  [OK] Soundtrack mastered: {soundtrack_out} ({total_time:.2f}s)")
        
        manifest[variant_key] = {
            "total_duration": total_time,
            "scenes": variant_results,
            "soundtrack": soundtrack_out
        }
        
    timeline_file = os.path.join(AUDIO_DIR, "social_timeline.json")
    with open(timeline_file, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nTimeline written to: {timeline_file}")

if __name__ == "__main__":
    asyncio.run(main())
