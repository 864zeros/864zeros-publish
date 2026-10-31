import asyncio
import os
import shutil
import subprocess
import json
import edge_tts
import wave
import math
import struct

VOICE = "en-US-AvaNeural"
PITCH = "+5Hz"   # 1.02x pitch (~+5Hz) per C:\dev\GEMINI.md
RATE = "+18%"    # Crisp retention pacing: 0-2s Hook -> 2-5.5s Immediate Visual UI Payoff

SPECS = {
    "vaultpilot": {
        "gtm_dir": r"C:\dev\864zeros-llc\LLC-DIV-4-GTM\videos\vaultpilot",
        "dam_dir": r"C:\dev\864zeros-publish\media\products\vaultpilot",
        "social_variants": {
            "pain": [
                {
                    "id": "pain_scene1_hook",
                    "stepLabel": "0-2s Problem Hook",
                    "text": "Broken tables when clipping to Obsidian?",
                    "lead": 0.04,
                    "tail": 0.06
                },
                {
                    "id": "pain_scene2_payoff",
                    "stepLabel": "2-5s Immediate Visual UI Payoff",
                    "text": "Watch this: highlight any section, click once, and clean Markdown lands in your vault.",
                    "lead": 0.06,
                    "tail": 0.12
                },
                {
                    "id": "pain_scene3_walkthrough",
                    "stepLabel": "5-15s Quick Setup Walkthrough",
                    "text": "VaultPilot keeps every table, code block, and tag intact right inside your browser—with zero cloud middleman.",
                    "lead": 0.10,
                    "tail": 0.20
                },
                {
                    "id": "pain_scene4_cta",
                    "stepLabel": "15-21s Pricing Advantage & CTA",
                    "text": "No monthly rent, one-time unlock. Try it free on Chrome, Edge, or eight sixty-four zeros dot com.",
                    "lead": 0.10,
                    "tail": 0.40
                }
            ],
            "price": [
                {
                    "id": "price_scene1_hook",
                    "stepLabel": "0-2s Problem Hook",
                    "text": "Paying monthly rent just to save articles?",
                    "lead": 0.04,
                    "tail": 0.06
                },
                {
                    "id": "price_scene2_payoff",
                    "stepLabel": "2-5s Immediate Visual UI Payoff",
                    "text": "Click Clip in VaultPilot and watch the page save straight into your local folder.",
                    "lead": 0.06,
                    "tail": 0.12
                },
                {
                    "id": "price_scene3_walkthrough",
                    "stepLabel": "5-15s Quick Setup Walkthrough",
                    "text": "Your notes never touch an external server. Pick your Obsidian or Logseq folder once and capture clean Markdown anytime.",
                    "lead": 0.10,
                    "tail": 0.20
                },
                {
                    "id": "price_scene4_cta",
                    "stepLabel": "15-21s Pricing Advantage & CTA",
                    "text": "No recurring subscriptions—one-time unlock forever. Get VaultPilot on Chrome, Edge, or eight sixty-four zeros dot com.",
                    "lead": 0.10,
                    "tail": 0.40
                }
            ],
            "speed": [
                {
                    "id": "speed_scene1_hook",
                    "stepLabel": "0-2s Problem Hook",
                    "text": "Still copy-pasting web notes by hand?",
                    "lead": 0.04,
                    "tail": 0.06
                },
                {
                    "id": "speed_scene2_payoff",
                    "stepLabel": "2-5s Immediate Visual UI Payoff",
                    "text": "Select any paragraph and watch it appear as a formatted Obsidian note in one second.",
                    "lead": 0.06,
                    "tail": 0.12
                },
                {
                    "id": "speed_scene3_walkthrough",
                    "stepLabel": "5-15s Quick Setup Walkthrough",
                    "text": "VaultPilot strips page clutter automatically, adds your frontmatter tags, and writes straight to your computer.",
                    "lead": 0.10,
                    "tail": 0.20
                },
                {
                    "id": "speed_scene4_cta",
                    "stepLabel": "15-21s Pricing Advantage & CTA",
                    "text": "No monthly rent, one-time unlock. Test the live demo right now at eight sixty-four zeros dot com.",
                    "lead": 0.10,
                    "tail": 0.40
                }
            ]
        },
        "live_ui_scenes": [
            {
                "id": "live_step1_hook",
                "stepLabel": "STEP 1 · THE PROBLEM (0–2s)",
                "caption": "Copying web articles into Obsidian ruins tables and code blocks.",
                "text": "Copying web articles into Obsidian ruins tables and code blocks.",
                "lead": 0.04,
                "tail": 0.06
            },
            {
                "id": "live_step2_payoff",
                "stepLabel": "STEP 2 · INSTANT UI PAYOFF (2–5s)",
                "caption": "Click 'Clip Selection' — clean Markdown drops into your vault immediately.",
                "text": "Watch this: click Clip Selection, and clean Markdown lands in your vault immediately.",
                "lead": 0.06,
                "tail": 0.12
            },
            {
                "id": "live_step3_configure",
                "stepLabel": "STEP 3 · CUSTOMIZE RULES & TAGS",
                "caption": "Toggle frontmatter metadata, code-fence tags, and target vault folder.",
                "text": "In the side panel, toggle your frontmatter tags, keep code syntax intact, and choose your target vault folder.",
                "lead": 0.10,
                "tail": 0.20
            },
            {
                "id": "live_step4_write",
                "stepLabel": "STEP 4 · DIRECT LOCAL DISK WRITE",
                "caption": "Writes directly to your local folder with zero cloud servers or accounts.",
                "text": "Every note saves directly to your computer with zero cloud servers and zero tracking.",
                "lead": 0.10,
                "tail": 0.20
            },
            {
                "id": "live_step5_outro",
                "stepLabel": "STEP 5 · NO MONTHLY RENT · TRY FREE",
                "caption": "Free Markdown mode included · one-time lifetime unlock · Chrome & Edge",
                "text": "No monthly rent, one-time unlock. Try the interactive demo or install on Chrome and Edge at eight sixty-four zeros dot com.",
                "lead": 0.10,
                "tail": 0.45
            }
        ]
    },
    "autoorganize-ytm": {
        "gtm_dir": r"C:\dev\864zeros-llc\LLC-DIV-4-GTM\videos\autoorganize-ytm",
        "dam_dir": r"C:\dev\864zeros-publish\media\products\autoorganize-ytm",
        "social_variants": {
            "pain": [
                {
                    "id": "pain_scene1_hook",
                    "stepLabel": "0-2s Problem Hook",
                    "text": "A thousand unsorted songs in Liked Songs?",
                    "lead": 0.04,
                    "tail": 0.06
                },
                {
                    "id": "pain_scene2_payoff",
                    "stepLabel": "2-5s Immediate Visual UI Payoff",
                    "text": "Watch this: one click splits your chaotic library into clean genre playlists.",
                    "lead": 0.06,
                    "tail": 0.12
                },
                {
                    "id": "pain_scene3_walkthrough",
                    "stepLabel": "5-15s Quick Setup Walkthrough",
                    "text": "AutoOrganize scans your YouTube Music privately in your browser, groups songs by real genres, and lets you preview every playlist.",
                    "lead": 0.10,
                    "tail": 0.20
                },
                {
                    "id": "pain_scene4_cta",
                    "stepLabel": "15-21s Pricing Advantage & CTA",
                    "text": "No monthly rent, one-time unlock, and your first playlist is free at eight sixty-four zeros dot com.",
                    "lead": 0.10,
                    "tail": 0.40
                }
            ],
            "price": [
                {
                    "id": "price_scene1_hook",
                    "stepLabel": "0-2s Problem Hook",
                    "text": "Paying monthly just to sort playlists?",
                    "lead": 0.04,
                    "tail": 0.06
                },
                {
                    "id": "price_scene2_payoff",
                    "stepLabel": "2-5s Immediate Visual UI Payoff",
                    "text": "Click Create Playlists and watch your genres organize right inside YouTube Music.",
                    "lead": 0.06,
                    "tail": 0.12
                },
                {
                    "id": "price_scene3_walkthrough",
                    "stepLabel": "5-15s Quick Setup Walkthrough",
                    "text": "You never hand your Google login to an external website. Everything runs in your browser side panel and syncs to your phone.",
                    "lead": 0.10,
                    "tail": 0.20
                },
                {
                    "id": "price_scene4_cta",
                    "stepLabel": "15-21s Pricing Advantage & CTA",
                    "text": "No recurring rent—one-time unlock forever. Try your first playlist free on Chrome and Edge at eight sixty-four zeros dot com.",
                    "lead": 0.10,
                    "tail": 0.40
                }
            ],
            "speed": [
                {
                    "id": "speed_scene1_hook",
                    "stepLabel": "0-2s Problem Hook",
                    "text": "Dragging songs into playlists one by one?",
                    "lead": 0.04,
                    "tail": 0.06
                },
                {
                    "id": "speed_scene2_payoff",
                    "stepLabel": "2-5s Immediate Visual UI Payoff",
                    "text": "Watch AutoOrganize sort hundreds of Liked Songs into genre playlists in seconds.",
                    "lead": 0.06,
                    "tail": 0.12
                },
                {
                    "id": "speed_scene3_walkthrough",
                    "stepLabel": "5-15s Quick Setup Walkthrough",
                    "text": "Check the genres you want, merge similar styles together, and create clean playlists in your account with one click.",
                    "lead": 0.10,
                    "tail": 0.20
                },
                {
                    "id": "speed_scene4_cta",
                    "stepLabel": "15-21s Pricing Advantage & CTA",
                    "text": "No monthly rent, one-time unlock. Test the live sandbox free at eight sixty-four zeros dot com.",
                    "lead": 0.10,
                    "tail": 0.40
                }
            ]
        },
        "live_ui_scenes": [
            {
                "id": "live_step1_hook",
                "stepLabel": "STEP 1 · THE PROBLEM (0–2s)",
                "caption": "1,280+ Liked Songs mixed together in YouTube Music with no genre sort.",
                "text": "YouTube Music dumps every liked song into one unsorted list.",
                "lead": 0.04,
                "tail": 0.06
            },
            {
                "id": "live_step2_payoff",
                "stepLabel": "STEP 2 · INSTANT UI PAYOFF (2–5s)",
                "caption": "Click 'Scan & Group by Genre' — tracks split into clean genre playlists immediately.",
                "text": "Watch this: click Scan Library, and your tracks group into clean genre playlists immediately.",
                "lead": 0.06,
                "tail": 0.12
            },
            {
                "id": "live_step3_select",
                "stepLabel": "STEP 3 · PREVIEW & MERGE GENRES",
                "caption": "Select genre buckets, strip duplicates, or merge styles into one custom playlist.",
                "text": "Preview every song, select the genre buckets you want, or merge styles together before creating anything.",
                "lead": 0.10,
                "tail": 0.20
            },
            {
                "id": "live_step4_create",
                "stepLabel": "STEP 4 · CREATE IN YOUTUBE MUSIC",
                "caption": "One click creates the playlists right in your account and syncs to your phone.",
                "text": "Click Create Playlists and they appear right inside your YouTube Music account, synced to your phone.",
                "lead": 0.10,
                "tail": 0.20
            },
            {
                "id": "live_step5_outro",
                "stepLabel": "STEP 5 · NO MONTHLY RENT · TRY FREE",
                "caption": "First playlist free · one-time lifetime unlock · Chrome & Edge",
                "text": "No monthly rent, one-time unlock. Try the interactive demo or install on Chrome and Edge at eight sixty-four zeros dot com.",
                "lead": 0.10,
                "tail": 0.45
            }
        ]
    }
}

async def synthesize_scene(scene, out_dir):
    raw_mp3 = os.path.join(out_dir, f"{scene['id']}_raw.mp3")
    wav_path = os.path.join(out_dir, f"{scene['id']}.wav")
    comm = edge_tts.Communicate(scene["text"], VOICE, rate=RATE, pitch=PITCH)
    await comm.save(raw_mp3)

    lead = scene.get("lead", 0.08)
    tail = scene.get("tail", 0.15)
    af = (
        f"adelay={int(lead*1000)}|{int(lead*1000)},"
        f"apad=pad_dur={tail},"
        f"aresample=44100,"
        f"loudnorm=I=-15:LRA=11:TP=-1.5"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_mp3,
        "-af", af, "-ar", "44100", "-ac", "2", wav_path
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    res = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", wav_path
    ], check=True, stdout=subprocess.PIPE, text=True)
    dur = float(res.stdout.strip())
    return {
        "id": scene["id"],
        "stepLabel": scene.get("stepLabel", ""),
        "caption": scene.get("caption", scene["text"]),
        "text": scene["text"],
        "duration": dur,
        "durationMs": int(round(dur * 1000)),
        "wav_path": wav_path,
        "raw_mp3": raw_mp3
    }

def synthesize_rhodes_bed(duration_sec, out_wav):
    SAMPLE_RATE = 44100
    TOTAL_SAMPLES = int(SAMPLE_RATE * (duration_sec + 1.5))
    CHORDS = [
        (146.83, [146.83, 220.00, 277.18, 369.99]), # Dmaj7
        (164.81, [164.81, 246.94, 293.66, 392.00]), # E9
        (185.00, [185.00, 220.00, 277.18, 329.63]), # F#m7
        (138.59, [138.59, 207.65, 246.94, 329.63]), # C#m7
    ]
    BPM = 90.0
    BAR_LEN = (60.0 / BPM) * 4
    raw_wav = out_wav.replace(".wav", "_raw.wav")

    with wave.open(raw_wav, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        buf = bytearray()
        for i in range(TOTAL_SAMPLES):
            t = i / SAMPLE_RATE
            bar_idx = int(t / BAR_LEN)
            chord = CHORDS[bar_idx % len(CHORDS)]
            bar_t = t % BAR_LEN
            env = math.exp(-bar_t * 0.9) * 0.35 + 0.10
            trem = 1.0 + 0.10 * math.sin(2 * math.pi * 4.8 * t)
            sig_l = 0.0
            sig_r = 0.0
            for idx, freq in enumerate(chord[1]):
                note = (
                    math.sin(2 * math.pi * freq * t) +
                    0.30 * math.sin(2 * math.pi * freq * 2 * t) +
                    0.10 * math.sin(2 * math.pi * freq * 3 * t)
                )
                pan = 0.38 + 0.24 * (idx / len(chord[1]))
                sig_l += note * pan
                sig_r += note * (1.0 - pan)
            sig_l *= env * trem * 0.22
            sig_r *= env * trem * 0.22
            bass = math.sin(2 * math.pi * (chord[0] * 0.5) * t) * (math.exp(-bar_t * 0.55) * 0.3 + 0.12) * 0.22
            sig_l += bass
            sig_r += bass
            if t > duration_sec - 1.2:
                fade = max(0.0, (duration_sec - t) / 1.2)
                sig_l *= fade
                sig_r *= fade
            vl = max(-32767, min(32767, int(sig_l * 32767)))
            vr = max(-32767, min(32767, int(sig_r * 32767)))
            buf += struct.pack("<hh", vl, vr)
        w.writeframes(buf)

    subprocess.run([
        "ffmpeg", "-y", "-i", raw_wav,
        "-af", "loudnorm=I=-16:LRA=9:TP=-2.0",
        "-ar", "44100", "-ac", "2", out_wav
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

async def build_track_bundle(prefix, scenes, out_dir, dam_audio_dir):
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(dam_audio_dir, exist_ok=True)
    same_dir = os.path.abspath(out_dir).lower() == os.path.abspath(dam_audio_dir).lower()
    timeline = []
    cur = 0.0
    for sc in scenes:
        info = await synthesize_scene(sc, out_dir)
        info["start"] = round(cur, 3)
        cur += info["duration"]
        info["end"] = round(cur, 3)
        timeline.append(info)
        if not same_dir:
            shutil.copy2(info["raw_mp3"], os.path.join(dam_audio_dir, os.path.basename(info["raw_mp3"])))
            shutil.copy2(info["wav_path"], os.path.join(dam_audio_dir, os.path.basename(info["wav_path"])))
        print(f"  [{prefix}] {sc['id']}: {info['start']:.2f}s -> {info['end']:.2f}s ({info['duration']:.2f}s)")

    total_dur = round(cur, 3)
    concat_txt = os.path.join(out_dir, f"concat_{prefix}.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for info in timeline:
            f.write(f"file '{os.path.basename(info['wav_path'])}'\n")

    voice_wav = os.path.join(out_dir, f"voiceover_{prefix}.wav")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt, "-c", "copy", voice_wav
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    music_wav = os.path.join(out_dir, f"music_bed_{prefix}.wav")
    synthesize_rhodes_bed(total_dur, music_wav)

    soundtrack_wav = os.path.join(out_dir, f"soundtrack_{prefix}.wav")
    mix_filter = (
        "[0:a]volume=1.0[voice];"
        "[1:a]volume=0.34[music];"
        "[music][voice]sidechaincompress=threshold=0.09:ratio=3.5:attack=15:release=220[ducked];"
        "[ducked][voice]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[out]"
    )
    subprocess.run([
        "ffmpeg", "-y", "-i", voice_wav, "-i", music_wav,
        "-filter_complex", mix_filter, "-map", "[out]",
        "-ar", "44100", "-ac", "2", soundtrack_wav
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    tl_obj = {
        "variant": prefix,
        "total_duration": total_dur,
        "soundtrackWav": soundtrack_wav,
        "scenes": timeline
    }
    tl_json = os.path.join(out_dir, f"timeline_{prefix}.json")
    with open(tl_json, "w", encoding="utf-8") as f:
        json.dump(tl_obj, f, indent=2)

    if not same_dir:
        for fp in [concat_txt, voice_wav, music_wav, soundtrack_wav, tl_json]:
            shutil.copy2(fp, os.path.join(dam_audio_dir, os.path.basename(fp)))

    return tl_obj

async def main():
    for slug, cfg in SPECS.items():
        print(f"\n==========================================")
        print(f"Generating Audio Stems for: {slug}")
        print(f"==========================================")
        social_audio_dir = os.path.join(cfg["gtm_dir"], "social_shorts", "audio")
        dam_audio_dir = os.path.join(cfg["dam_dir"], "audio")
        os.makedirs(social_audio_dir, exist_ok=True)
        os.makedirs(dam_audio_dir, exist_ok=True)

        social_summary = {}
        for var_name, scenes in cfg["social_variants"].items():
            tl = await build_track_bundle(var_name, scenes, social_audio_dir, dam_audio_dir)
            social_summary[var_name] = tl

        with open(os.path.join(dam_audio_dir, "social_timeline.json"), "w", encoding="utf-8") as f:
            json.dump(social_summary, f, indent=2)

        live_tl = await build_track_bundle("live_ui", cfg["live_ui_scenes"], dam_audio_dir, dam_audio_dir)
        with open(os.path.join(dam_audio_dir, "live_ui_timeline.json"), "w", encoding="utf-8") as f:
            json.dump(live_tl, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
