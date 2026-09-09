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
            "text": "What happens to your business tomorrow if your Google account gets unexpectedly suspended?",
            "lead": 0.25,
            "tail": 0.35
        },
        {
            "id": "pain_scene2_solution",
            "text": "DriveVault creates client-side AES-256 encrypted backup snapshots of your Google Drive files directly on your local hardware. Zero third-party servers in custody.",
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
            "text": "Why pay recurring monthly storage rent to a cloud backup company for files you already own?",
            "lead": 0.25,
            "tail": 0.35
        },
        {
            "id": "price_scene2_solution",
            "text": "DriveVault executes 100% locally inside your Google Workspace account with unlimited encrypted backups and zero monthly subscriptions.",
            "lead": 0.2,
            "tail": 0.4
        },
        {
            "id": "price_scene3_cta",
            "text": "A one-time twenty-nine dollars unlock forever. Available on the Google Workspace Marketplace for add-ons at eight sixty-four zeros dot com.",
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

def generate_rhodes_bed(duration_sec, out_wav):
    sample_rate = 44100
    total_samples = int(sample_rate * duration_sec)
    
    chords = [
        (146.83, [146.83, 220.00, 277.18, 369.99]), # D3, A3, C#4, F#4
        (164.81, [164.81, 246.94, 293.66, 392.00]), # E3, B3, D4, G4
        (185.00, [185.00, 220.00, 277.18, 329.63]), # F#3, A3, C#4, E4
        (138.59, [138.59, 207.65, 246.94, 329.63]), # C#3, G#3, B3, E4
    ]
    bpm = 84.0
    beat_len = 60.0 / bpm
    bar_len = beat_len * 4
    
    with wave.open(out_wav, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        buf = bytearray()
        for i in range(total_samples):
            t = i / sample_rate
            bar_idx = int(t / bar_len)
            chord = chords[bar_idx % len(chords)]
            bar_t = t % bar_len
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
                fade = max(0.0, (duration_sec - t) / 2.0)
                chord_sig_l *= fade
                chord_sig_r *= fade
                
            s_l = int(max(-32767, min(32767, chord_sig_l * 32767)))
            s_r = int(max(-32767, min(32767, chord_sig_r * 32767)))
            buf.extend(struct.pack("<hh", s_l, s_r))
        w.writeframes(buf)

async def main():
    print("=== Generating DriveVault Social Shorts Audio Stems ===")
    timeline_master = {}
    
    for variant, scenes in SCRIPTS.items():
        print(f"\nProcessing variant: {variant}")
        variant_timeline = []
        curr_t = 0.0
        wav_files = []
        
        for sc in scenes:
            info = await generate_scene_audio(sc)
            info["start"] = curr_t
            info["end"] = curr_t + info["duration"]
            curr_t += info["duration"]
            variant_timeline.append(info)
            wav_files.append(info["wav_path"])
            print(f"  [OK] {info['id']}: {info['duration']:.2f}s -> {info['text'][:40]}...")
            
        total_voice_dur = curr_t
        concat_txt = os.path.join(AUDIO_DIR, f"concat_{variant}.txt")
        with open(concat_txt, "w") as f:
            for w in wav_files:
                f.write(f"file '{w}'\n")
                
        voiceover_combined = os.path.join(AUDIO_DIR, f"voiceover_{variant}.wav")
        cmd_concat = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", concat_txt, "-c", "copy", voiceover_combined
        ]
        subprocess.run(cmd_concat, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        music_bed = os.path.join(AUDIO_DIR, f"music_bed_{variant}.wav")
        music_dur = total_voice_dur + 2.0
        generate_rhodes_bed(music_dur, music_bed)
        print(f"  [OK] Music bed generated: {music_dur:.2f}s")
        
        soundtrack = os.path.join(AUDIO_DIR, f"soundtrack_{variant}.wav")
        cmd_mux = [
            "ffmpeg", "-y",
            "-i", voiceover_combined,
            "-i", music_bed,
            "-filter_complex",
            "[1:a]volume=0.20[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2,loudnorm=I=-14:LRA=7:tp=-1.5[out]",
            "-map", "[out]",
            "-ar", "44100", "-ac", "2",
            soundtrack
        ]
        subprocess.run(cmd_mux, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"  [OK] Soundtrack mastered: {soundtrack} ({total_voice_dur:.2f}s)")
        
        timeline_master[variant] = {
            "total_duration": total_voice_dur,
            "scenes": variant_timeline,
            "soundtrack": soundtrack
        }
        
    timeline_file = os.path.join(AUDIO_DIR, "social_timeline.json")
    with open(timeline_file, "w") as f:
        json.dump(timeline_master, f, indent=2)
    print(f"\nTimeline written to: {timeline_file}")

if __name__ == "__main__":
    asyncio.run(main())
