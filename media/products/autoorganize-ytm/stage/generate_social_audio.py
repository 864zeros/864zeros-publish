import asyncio
import os
import subprocess
import json
import edge_tts
import wave
import math
import struct

VOICE = "en-US-AvaNeural"
PITCH = "+5Hz" # 1.02x pitch (~+5Hz) per C:\dev\GEMINI.md
RATE = "+13%"

BASE_DIR = r"C:\dev\864zeros-llc\LLC-DIV-4-GTM\videos\autoorganize-ytm"
SOCIAL_DIR = os.path.join(BASE_DIR, "social_shorts")
AUDIO_DIR = os.path.join(SOCIAL_DIR, "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

VARIANTS = {
    "pain": [
        {
            "id": "pain_scene1_hook",
            "text": "Be honest: is your YouTube Music Liked Songs a chaotic graveyard of tracks you never actually listen to?",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "pain_scene2_split",
            "text": "AutoOrganize scans your library privately on-device and auto-splits it into real genre playlists right in your own account.",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "pain_scene3_cta",
            "text": "Synced to every device by Google. Try your first playlist free at eight sixty-four zeros dot com.",
            "lead": 0.15,
            "tail": 0.5
        }
    ],
    "price": [
        {
            "id": "price_scene1_hook",
            "text": "Why are music organizers charging ten dollars every month just to sort your playlists?",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "price_scene2_privacy",
            "text": "AutoOrganize runs locally in your browser. Real MusicBrainz genre tags, zero passwords uploaded, no subscriptions ever.",
            "lead": 0.15,
            "tail": 0.25
        },
        {
            "id": "price_scene3_cta",
            "text": "Just two ninety-nine one-time forever. Create your first playlist free at eight sixty-four zeros dot com.",
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
    BAR_LEN = BEAT_LEN * 4 # ~2.72s per chord
    
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
            
            chord_sig_l = 0.0
            chord_sig_r = 0.0
            for idx, freq in enumerate(chord[1]):
                note = (
                    math.sin(2 * math.pi * freq * t) +
                    0.35 * math.sin(2 * math.pi * freq * 2 * t) +
                    0.12 * math.sin(2 * math.pi * freq * 3 * t)
                )
                pan = 0.4 + 0.2 * (idx / len(chord[1]))
                chord_sig_l += note * pan
                chord_sig_r += note * (1.0 - pan)
                
            chord_sig_l *= chord_env * tremolo * 0.20
            chord_sig_r *= chord_env * tremolo * 0.20
            
            # Sub bass
            bass_root = chord[0] * 0.5
            bass_sig = math.sin(2 * math.pi * bass_root * t) * (math.exp(-bar_t * 0.6) * 0.3 + 0.1) * 0.22
            
            sig_l = chord_sig_l + bass_sig
            sig_r = chord_sig_r + bass_sig
            
            # Fade out at the end
            if t > duration_sec - 1.5:
                fade = max(0.0, (duration_sec - t) / 1.5)
                sig_l *= fade
                sig_r *= fade
                
            val_l = max(-32767, min(32767, int(sig_l * 32767)))
            val_r = max(-32767, min(32767, int(sig_r * 32767)))
            buffer += struct.pack("<hh", val_l, val_r)
            
        w.writeframes(buffer)

async def build_variant(variant_name, scenes):
    print(f"\n=== Processing Social Short: {variant_name} ===")
    timeline = []
    current_time = 0.0
    
    for sc in scenes:
        info = await generate_scene_audio(sc)
        info["start"] = current_time
        info["end"] = current_time + info["duration"]
        current_time += info["duration"]
        timeline.append(info)
        print(f"[{variant_name}] {sc['id']}: start={info['start']:.2f}s, dur={info['duration']:.2f}s, end={info['end']:.2f}s")
        
    total_dur = current_time
    print(f"[{variant_name}] Total speech duration: {total_dur:.2f}s")
    
    # Concat voiceover
    concat_list = os.path.join(AUDIO_DIR, f"concat_{variant_name}.txt")
    with open(concat_list, "w", encoding="utf-8") as f:
        for info in timeline:
            f.write(f"file '{os.path.basename(info['wav_path'])}'\n")
            
    voice_wav = os.path.join(AUDIO_DIR, f"voiceover_{variant_name}.wav")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list, "-c", "copy", voice_wav
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Generate music bed
    music_wav = os.path.join(AUDIO_DIR, f"music_bed_{variant_name}.wav")
    synthesize_music_bed(total_dur, music_wav)
    print(f"[{variant_name}] Music bed synthesized: {music_wav}")
    
    # Mix soundtrack: voiceover (100% volume) + music bed (18% volume) with sidechain ducking
    soundtrack_wav = os.path.join(AUDIO_DIR, f"soundtrack_{variant_name}.wav")
    mix_filter = (
        "[0:a]volume=1.0[voice];"
        "[1:a]volume=0.18[music];"
        "[music][voice]sidechaincompress=threshold=0.12:ratio=4:attack=20:release=250[ducked_music];"
        "[ducked_music][voice]amix=inputs=2:duration=first:dropout_transition=2[out]"
    )
    subprocess.run([
        "ffmpeg", "-y",
        "-i", voice_wav,
        "-i", music_wav,
        "-filter_complex", mix_filter,
        "-map", "[out]",
        "-ar", "44100", "-ac", "2",
        soundtrack_wav
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"[{variant_name}] Master soundtrack mixed: {soundtrack_wav}")
    
    # Save timeline JSON
    timeline_json = os.path.join(AUDIO_DIR, f"timeline_{variant_name}.json")
    with open(timeline_json, "w", encoding="utf-8") as f:
        json.dump({"variant": variant_name, "total_duration": total_dur, "scenes": timeline}, f, indent=2)
    print(f"[{variant_name}] Timeline saved: {timeline_json}")

async def main():
    for v_name, v_scenes in VARIANTS.items():
        await build_variant(v_name, v_scenes)

if __name__ == "__main__":
    asyncio.run(main())
