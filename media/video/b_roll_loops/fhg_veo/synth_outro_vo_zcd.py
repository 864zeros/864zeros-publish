#!/usr/bin/env python3
r"""
Produce and lock the official FHG Fig Tree Parchment Outro Voiceover & Mastered MP4s (9:16 & 16:9 1080p)
in ZeroCloudDAM (C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo\broll_library\).
"""

import asyncio
import subprocess
from pathlib import Path
import edge_tts

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
DAM_BROLL_LIB = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo" / "broll_library"
PAD_WAV = PUBLISH_ROOT / "media" / "audio" / "music" / "fhg_432hz_ambient_pad.wav"
FOLEY_DIR = PUBLISH_ROOT / "media" / "audio" / "sfx" / "fhg_foley"
WORK_DIR = PUBLISH_ROOT / "_build" / "video" / "fhg_shorts_engine" / "tmp_work" / "fhg_outro_vo"


def get_duration(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


async def synth_seg(text: str, rate: str, pitch: str, out_mp3: Path) -> None:
    for attempt in range(6):
        try:
            comm = edge_tts.Communicate(text=text, voice="en-US-AndrewMultilingualNeural", rate=rate, pitch=pitch)
            await comm.save(str(out_mp3))
            if out_mp3.exists() and out_mp3.stat().st_size > 400:
                await asyncio.sleep(0.4)
                return
        except Exception as exc:
            if attempt == 5:
                raise exc
            await asyncio.sleep(1.2 * (attempt + 1))


async def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    # 3 reverent, intimate beats matching the visual hierarchy of the Outro (Natural Pause Standard):
    # 1. Title: "For His Grace."
    # 2. Slogan: "Solitude isn't lonely when it's the gift that He gave."
    # 3. H3 CTA: "Learn more on ForHisGrace.com."
    segs = [
        ("For His Grace.", "+2%", "-2Hz", 180),
        ("Solitude isn't lonely, when it's the gift that He gave.", "+1%", "-3Hz", 340),
        ("Learn more on For His Grace dot com.", "+2%", "-2Hz", 380),
    ]

    concat_files: list[Path] = []
    for i, (txt, rate, pitch, pause_before_ms) in enumerate(segs):
        sil = WORK_DIR / f"sil_{i}.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", "anullsrc=r=48000:cl=stereo",
                "-t", f"{pause_before_ms / 1000.0:.3f}",
                str(sil),
            ],
            check=True,
            capture_output=True,
        )
        concat_files.append(sil)

        mp3_p = WORK_DIR / f"vo_{i}.mp3"
        wav_p = WORK_DIR / f"vo_{i}.wav"
        await synth_seg(txt, rate, pitch, mp3_p)
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(mp3_p),
                "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,afade=t=in:st=0:d=0.015",
                "-ar", "48000", "-ac", "2",
                str(wav_p),
            ],
            check=True,
            capture_output=True,
        )
        concat_files.append(wav_p)

    # Add 0.65s tail breath at end
    tail_sil = WORK_DIR / "sil_tail.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", "anullsrc=r=48000:cl=stereo",
            "-t", "0.650",
            str(tail_sil),
        ],
        check=True,
        capture_output=True,
    )
    concat_files.append(tail_sil)

    concat_txt = WORK_DIR / "concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in concat_files) + "\n", encoding="utf-8")

    vo_raw = WORK_DIR / "outro_vo_raw.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "pcm_s16le",
            str(vo_raw),
        ],
        check=True,
        capture_output=True,
    )
    total_dur = get_duration(vo_raw)

    # Mix VO + 432Hz Pad + Parchment Turn & Felt Piano chord, mastered to -14 LUFS / -1 dBTP
    parchment_wav = FOLEY_DIR / "parchment_turn.wav"
    piano_wav = FOLEY_DIR / "felt_piano.wav"
    master_wav = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_vo_master_14lufs.wav"

    filter_complex = (
        "[0:a]asplit=2[vo_sc][vo_main];"
        "[1:a]equalizer=f=1000:t=h:w=2700:g=-4,volume=-14dB,"
        f"afade=t=out:st={max(0.5, total_dur - 0.8):.2f}:d=0.80[pad_eq];"
        "[pad_eq][vo_sc]sidechaincompress=threshold=0.03:ratio=6:attack=10:release=280[pad_ducked];"
        "[2:a]volume=-14dB,adelay=40|40[fl_parch];"
        "[3:a]volume=-15dB,adelay=1100|1100[fl_piano];"
        "[vo_main][pad_ducked][fl_parch][fl_piano]amix=inputs=4:duration=first:dropout_transition=0:normalize=0[pre];"
        "[pre]loudnorm=I=-14.0:TP=-1.0:LRA=11.0[a_out]"
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(vo_raw),
            "-i", str(PAD_WAV),
            "-i", str(parchment_wav),
            "-i", str(piano_wav),
            "-filter_complex", filter_complex,
            "-map", "[a_out]",
            "-t", f"{total_dur:.3f}",
            "-ar", "48000", "-ac", "2",
            str(master_wav),
        ],
        check=True,
        capture_output=True,
    )
    print(f"Created Mastered Outro VO Audio: {master_wav} ({total_dur:.2f}s)")

    # Mux into 9:16 (1080x1920) and 16:9 (1920x1080) Outro MP4s in ZeroCloudDAM
    for aspect, (w, h) in [("9x16", (1080, 1920)), ("16x9", (1920, 1080))]:
        plate_jpg = DAM_BROLL_LIB / f"FHG-OUTRO-001_fig-tree-parchment_{aspect}_1080p.jpg"
        out_mp4 = DAM_BROLL_LIB / f"FHG-OUTRO-001_fig-tree-parchment_{aspect}_1080p.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(plate_jpg),
                "-i", str(master_wav),
                "-vf", f"scale={w}:{h}:flags=lanczos,fps=60,format=yuv420p",
                "-t", f"{total_dur:.3f}",
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
                "-crf", "17", "-preset", "slow",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart",
                "-shortest",
                str(out_mp4),
            ],
            check=True,
            capture_output=True,
        )
        print(f"Locked Outro MP4 ({aspect} {w}x{h}, {total_dur:.2f}s): {out_mp4} ({out_mp4.stat().st_size} bytes)")


if __name__ == "__main__":
    asyncio.run(main())
