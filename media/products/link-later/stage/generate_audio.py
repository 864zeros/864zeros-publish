import asyncio
import json
import math
import os
import struct
import subprocess
import wave
import edge_tts
import imageio_ffmpeg

FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE = "en-US-AvaNeural"
SAMPLE_RATE = 44100

CHORDS = [
    (146.83, [146.83, 220.00, 277.18, 369.99]),
    (164.81, [164.81, 246.94, 293.66, 392.00]),
    (185.00, [185.00, 220.00, 277.18, 329.63]),
    (138.59, [138.59, 207.65, 246.94, 329.63]),
]

def generate_rhodes_bed(music_path, duration_sec):
    total_samples = int(SAMPLE_RATE * duration_sec)
    bpm = 84.0
    beat_len = 60.0 / bpm
    bar_len = beat_len * 4

    with wave.open(music_path, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        buffer = bytearray()

        for i in range(total_samples):
            t = i / SAMPLE_RATE
            bar_idx = int(t / bar_len)
            chord = CHORDS[bar_idx % len(CHORDS)]
            bar_t = t % bar_len
            chord_env = math.exp(-bar_t * 0.9) * 0.35 + 0.08
            tremolo = 1.0 + 0.12 * math.sin(2 * math.pi * 5.0 * t)

            chord_sig_l = 0.0
            chord_sig_r = 0.0
            for idx, freq in enumerate(chord[1]):
                note = (
                    math.sin(2 * math.pi * freq * t)
                    + 0.35 * math.sin(2 * math.pi * freq * 2 * t)
                    + 0.12 * math.sin(2 * math.pi * freq * 3 * t)
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

            sample_l = int(max(-32767, min(32767, chord_sig_l * 32767)))
            sample_r = int(max(-32767, min(32767, chord_sig_r * 32767)))
            buffer.extend(struct.pack("<hh", sample_l, sample_r))

        w.writeframes(buffer)


def get_wav_duration(wav_path):
    with wave.open(wav_path, "r") as w:
        return w.getnframes() / float(w.getframerate())


async def build_track(out_dir, scenes, prefix=""):
    os.makedirs(out_dir, exist_ok=True)
    timeline = []
    current_time = 0.0
    wav_files = []

    for scene in scenes:
        raw_mp3 = os.path.join(out_dir, f"{prefix}{scene['id']}_raw.mp3")
        padded_wav = os.path.join(out_dir, f"{prefix}{scene['id']}.wav")
        rate = scene.get("rate", "+8%")
        pad = scene.get("pad", 0.35)

        communicate = edge_tts.Communicate(scene["text"], VOICE, rate=rate)
        await communicate.save(raw_mp3)

        subprocess.run(
            [
                FFMPEG_BIN, "-y",
                "-i", raw_mp3,
                "-af", f"apad=pad_dur={pad}",
                "-ar", "44100",
                "-ac", "2",
                padded_wav,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        dur = get_wav_duration(padded_wav)
        timeline.append(
            {
                "id": scene["id"],
                "start": round(current_time, 3),
                "end": round(current_time + dur, 3),
                "duration": round(dur, 3),
                "text": scene["text"],
            }
        )
        current_time += dur
        wav_files.append(padded_wav)

    concat_txt = os.path.join(out_dir, f"concat_{prefix.rstrip('_') or 'list'}.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for wf in wav_files:
            f.write(f"file '{wf.replace(os.sep, '/')}'\n")

    vo_name = f"voiceover_{prefix.rstrip('_')}.wav" if prefix else "voiceover_full.wav"
    full_vo_wav = os.path.join(out_dir, vo_name)
    subprocess.run(
        [
            FFMPEG_BIN, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_txt,
            "-c", "copy",
            full_vo_wav,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    music_name = f"music_bed_{prefix.rstrip('_')}.wav" if prefix else "music_bed.wav"
    music_wav = os.path.join(out_dir, music_name)
    generate_rhodes_bed(music_wav, current_time + 1.5)

    st_name = f"soundtrack_{prefix.rstrip('_')}.wav" if prefix else "soundtrack.wav"
    final_soundtrack = os.path.join(out_dir, st_name)
    subprocess.run(
        [
            FFMPEG_BIN, "-y",
            "-i", full_vo_wav,
            "-i", music_wav,
            "-filter_complex",
            f"[0:a]volume=1.45[vo];[1:a]volume=0.22,atrim=0:{current_time + 0.4}[bg];[vo][bg]amix=inputs=2:duration=first:dropout_transition=2[out]",
            "-map", "[out]",
            "-ar", "44100",
            "-ac", "2",
            final_soundtrack,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    tl_name = f"timeline_{prefix.rstrip('_')}.json" if prefix else "timeline.json"
    timeline_path = os.path.join(out_dir, tl_name)
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(
            {"total_duration": round(current_time, 3), "scenes": timeline},
            f,
            indent=2,
        )
    print(f"Synthesized {tl_name}: {current_time:.2f}s")


MASTER_SCENES = [
    {
        "id": "scene1_hook",
        "text": "Keeping forty browser tabs open just so you don't lose one good link?",
        "rate": "+12%",
        "pad": 0.25,
    },
    {
        "id": "scene2_intro",
        "text": "Watch this: click Save in LinkLater, jot a quick note, and click Send to Obsidian—your note lands inside your local vault in one second.",
        "rate": "+9%",
        "pad": 0.35,
    },
    {
        "id": "scene3_feature",
        "text": "Tag every link, filter unread versus read, export clean Markdown files free, or send your entire reading digest straight to Obsidian with zero cloud accounts.",
        "rate": "+8%",
        "pad": 0.35,
    },
    {
        "id": "scene4_pricing",
        "text": "Saving pages, notes, tags, and Markdown file export are free forever—with a one-time lifetime Obsidian Bridge unlock and zero monthly subscriptions.",
        "rate": "+8%",
        "pad": 0.35,
    },
    {
        "id": "scene5_cta",
        "text": "Own your reading list. Get LinkLater at eight sixty-four zeros dot com.",
        "rate": "+8%",
        "pad": 0.55,
    },
]

SOCIAL_PAIN_SCENES = [
    {
        "id": "scene1",
        "text": "Hoarding fifty open browser tabs as a reading list?",
        "rate": "+12%",
        "pad": 0.20,
    },
    {
        "id": "scene2",
        "text": "Watch how one click saves the page with your note and sends it straight to your Obsidian vault.",
        "rate": "+10%",
        "pad": 0.30,
    },
    {
        "id": "scene3",
        "text": "Add tags, filter unread links in your side panel, and close those tabs safely with zero cloud accounts.",
        "rate": "+9%",
        "pad": 0.30,
    },
    {
        "id": "scene4",
        "text": "Free Markdown export forever, one-time Obsidian Bridge unlock. Try it at eight sixty-four zeros dot com.",
        "rate": "+9%",
        "pad": 0.45,
    },
]

SOCIAL_PRICE_SCENES = [
    {
        "id": "scene1",
        "text": "Tired of cloud read-later apps shutting down or charging monthly rent?",
        "rate": "+12%",
        "pad": 0.20,
    },
    {
        "id": "scene2",
        "text": "LinkLater keeps your entire reading queue on your device and sends formatted notes straight into Obsidian.",
        "rate": "+10%",
        "pad": 0.30,
    },
    {
        "id": "scene3",
        "text": "Every save includes your personal note, tags, and YAML frontmatter—stored privately inside your browser.",
        "rate": "+9%",
        "pad": 0.30,
    },
    {
        "id": "scene4",
        "text": "No monthly subscriptions, ever. Test the live sandbox free at eight sixty-four zeros dot com.",
        "rate": "+9%",
        "pad": 0.45,
    },
]

SOCIAL_SPEED_SCENES = [
    {
        "id": "scene1",
        "text": "Still copy-pasting web links and notes into Obsidian by hand?",
        "rate": "+12%",
        "pad": 0.20,
    },
    {
        "id": "scene2",
        "text": "Click Save in LinkLater, type why it mattered, and click Send to Obsidian—done in one second.",
        "rate": "+10%",
        "pad": 0.30,
    },
    {
        "id": "scene3",
        "text": "Send a single saved card or your entire reading digest with clean YAML frontmatter and tags.",
        "rate": "+9%",
        "pad": 0.30,
    },
    {
        "id": "scene4",
        "text": "Free reading queue and Markdown export, one-time Obsidian unlock at eight sixty-four zeros dot com.",
        "rate": "+9%",
        "pad": 0.45,
    },
]


async def main():
    audio_dir = os.path.join(BASE_DIR, "audio")
    audio_v2_dir = os.path.join(BASE_DIR, "audio_v2")
    social_audio_dir = os.path.join(BASE_DIR, "social_shorts", "audio")

    await build_track(audio_dir, MASTER_SCENES, prefix="")
    await build_track(audio_v2_dir, MASTER_SCENES, prefix="")
    await build_track(social_audio_dir, SOCIAL_PAIN_SCENES, prefix="pain_")
    await build_track(social_audio_dir, SOCIAL_PRICE_SCENES, prefix="price_")
    await build_track(social_audio_dir, SOCIAL_SPEED_SCENES, prefix="speed_")


if __name__ == "__main__":
    asyncio.run(main())
