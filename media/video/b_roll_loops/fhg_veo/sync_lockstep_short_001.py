#!/usr/bin/env python3
r"""
Assemble FHG-SHORT-BROLL-001 in 100% LOCKSTEP across 16:9 Widescreen (1920x1080) and 9:16 Vertical (1080x1920).
Every beat in 9:16 is center-cropped from the exact same 16:9 master clip sequence (including the powerful
Jesus Walking tracking shots), followed by the aspect-native 1080p Fig Tree Parchment Outro.
"""

from __future__ import annotations

import asyncio
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
DAM_BROLL_LIB = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo" / "broll_library"
JESUS_VEO_DIR = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo" / "jesus"
OUT_REELS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "rendered_reels"
WS_VIDEOS_DIR = Path(r"C:\dev\fhg-videos")
FONTS_DIR = PUBLISH_ROOT / "media" / "graphics" / "fonts"
WORK_DIR = PUBLISH_ROOT / "_build" / "video" / "fhg_shorts_engine" / "tmp_work" / "fhg_short_broll_001"


def get_audio_duration(path: Path) -> float:
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


def ensure_jesus_clips_in_zcd() -> None:
    """Vault and master the 16:9 Jesus Walking clips into 1080p (16:9 & 9:16) inside ZeroCloudDAM broll_library."""
    jesus_sources = [
        ("FHG-BR-034", "jesus-walking-olive-grove-dolly", JESUS_VEO_DIR / "Medium_shot,_centered_composition._A_6c5c8acc.mp4"),
        ("FHG-BR-035", "jesus-walking-golden-hour-tracking", JESUS_VEO_DIR / "Slow_lateral_tracking_shot_(dolly_1182e743.mp4"),
        ("FHG-BR-036", "jesus-courtyard-360-orbital", JESUS_VEO_DIR / "Continuous_360-degree_orbital_camera_movement_2d61b5d5.mp4"),
        ("FHG-BR-037", "jesus-village-profile-tracking", JESUS_VEO_DIR / "Slow_lateral_tracking_shot_(dolly_a169b089.mp4"),
    ]
    for dam_id, slug, src in jesus_sources:
        out_16x9 = DAM_BROLL_LIB / f"{dam_id}_{slug}_16x9_1080p.mp4"
        out_9x16 = DAM_BROLL_LIB / f"{dam_id}_{slug}_9x16_1080p.mp4"
        if not out_16x9.exists():
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(src),
                    "-vf", "scale=1920:1080:flags=lanczos,unsharp=3:3:0.45:3:3:0.0",
                    "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
                    "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    str(out_16x9),
                ],
                check=True,
                capture_output=True,
            )
        if not out_9x16.exists():
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(src),
                    "-vf", "crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920:flags=lanczos,unsharp=3:3:0.5:3:3:0.0",
                    "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
                    "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    str(out_9x16),
                ],
                check=True,
                capture_output=True,
            )


def build_hard_cut_visual_plus_outro(
    clip_specs: list[tuple[Path, float]],
    body_dur: float,
    outro_plate: Path,
    outro_dur: float,
    width: int,
    height: int,
    work_dir: Path,
    tag: str,
) -> Path:
    beat_step = 3.4
    num_beats = int(body_dur // beat_step) + 1
    beat_files: list[Path] = []

    accum = 0.0
    for i in range(num_beats):
        remaining = body_dur - accum
        if remaining <= 0.05:
            break
        is_last = (i == num_beats - 1) or (remaining <= beat_step + 0.3)
        dur = (remaining + 0.25) if is_last else min(beat_step, remaining)

        src_path, start_s = clip_specs[i % len(clip_specs)]
        beat_out = work_dir / f"beat_lock_{tag}_{i:02d}.mp4"
        if not beat_out.exists() or beat_out.stat().st_size == 0:
            subprocess.run(
                [
                    "ffmpeg", "-y", "-stream_loop", "-1",
                    "-ss", f"{start_s:.2f}",
                    "-i", str(src_path),
                    "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,crop={width}:{height},fps=60,setsar=1,format=yuv420p",
                    "-t", f"{dur:.3f}",
                    "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
                    str(beat_out),
                ],
                check=True,
                capture_output=True,
            )
        beat_files.append(beat_out)
        accum += beat_step
        if is_last:
            break

    concat_txt = work_dir / f"beats_lock_{tag}_concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in beat_files) + "\n", encoding="utf-8")
    body_mp4 = work_dir / f"body_lock_hardcuts_{tag}.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:v", "copy",
            str(body_mp4),
        ],
        check=True,
        capture_output=True,
    )

    outro_v = work_dir / f"outro_v_{tag}.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(outro_plate),
            "-vf", f"scale={width}:{height}:flags=lanczos,fps=60,setsar=1,format=yuv420p",
            "-t", f"{outro_dur + 0.25:.3f}",
            "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
            str(outro_v),
        ],
        check=True,
        capture_output=True,
    )

    full_visual = work_dir / f"full_lock_visual_{tag}.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(body_mp4),
            "-i", str(outro_v),
            "-filter_complex", f"[0:v][1:v]xfade=transition=fade:duration=0.250:offset={body_dur:.3f}[vout]",
            "-map", "[vout]",
            "-t", f"{body_dur + outro_dur:.3f}",
            "-r", "60", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
            str(full_visual),
        ],
        check=True,
        capture_output=True,
    )
    return full_visual


def main() -> None:
    print("[1/3] Mastering 16:9 Jesus Walking clips into 1080p (16:9 & 9:16) inside ZeroCloudDAM...")
    ensure_jesus_clips_in_zcd()

    main_vo_wav = WORK_DIR / "vo_main.wav"
    outro_vo_wav = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_vo_master_14lufs.wav"
    master_audio = WORK_DIR / "full_audio_master_14lufs.wav"
    body_dur = get_audio_duration(main_vo_wav)
    outro_dur = get_audio_duration(outro_vo_wav)

    # 100% IDENTICAL LOCKSTEP SEQUENCE across 16:9 and 9:16 (with the powerful Jesus Walking shots in both!)
    canonical_sequence = [
        ("FHG-BR-002_falling-silver-coins", 0.0),          # Beat 0: Falling Silver Coins (Hook)
        ("FHG-BR-002_falling-silver-coins", 3.6),          # Beat 1: Coins bouncing on dark temple stone
        ("FHG-BR-032_sandals-in-cracked-wilderness", 0.0), # Beat 2: Sandals stepping through cracked earth
        ("FHG-BR-004_wind-blowing-chaff", 0.0),            # Beat 3: Wind blowing wheat chaff
        ("FHG-BR-033_hauling-fishing-net-rope", 0.0),      # Beat 4: Calloused hand hauling net rope
        ("FHG-BR-034_jesus-walking-olive-grove-dolly", 0.0),      # Beat 5: Jesus walking toward camera in olive grove
        ("FHG-BR-035_jesus-walking-golden-hour-tracking", 0.0),   # Beat 6: Jesus golden-hour tracking shot
        ("FHG-BR-036_jesus-courtyard-360-orbital", 0.0),          # Beat 7: Jesus courtyard 360 orbital shot
        ("FHG-BR-031_pouring-anointing-oil", 0.0),         # Beat 8: Golden anointing oil pouring onto stone
        ("FHG-BR-031_pouring-anointing-oil", 3.5),         # Beat 9: Golden oil pooling in sunlight
    ]

    clips_16x9 = [(DAM_BROLL_LIB / f"{stem}_16x9_1080p.mp4", start_s) for stem, start_s in canonical_sequence]
    clips_9x16 = [(DAM_BROLL_LIB / f"{stem}_9x16_1080p.mp4", start_s) for stem, start_s in canonical_sequence]

    print("[2/3] Rendering Lockstep 9:16 Vertical Short from exact same 16:9 clip sequence (with Jesus Walking)...")
    vis_9x16 = build_hard_cut_visual_plus_outro(
        clips_9x16,
        body_dur,
        DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_9x16_1080p.jpg",
        outro_dur,
        1080,
        1920,
        WORK_DIR,
        "9x16",
    )
    vis_16x9 = build_hard_cut_visual_plus_outro(
        clips_16x9,
        body_dur,
        DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_16x9_1080p.jpg",
        outro_dur,
        1920,
        1080,
        WORK_DIR,
        "16x9",
    )

    print("[3/3] Exporting Lockstep 9:16 & 16:9 1080p 60fps Masters...")
    fonts_escaped = FONTS_DIR.as_posix().replace(":", "\\:")
    for aspect, vis_mp4 in [("9x16", vis_9x16), ("16x9", vis_16x9)]:
        ass_p = WORK_DIR / f"captions_{aspect}.ass"
        ass_escaped = ass_p.as_posix().replace(":", "\\:")
        out_dam = OUT_REELS_DIR / f"FHG-SHORT-BROLL-001_{aspect}_1080p.mp4"
        out_broll_lib = DAM_BROLL_LIB / f"FHG-SHORT-BROLL-001_{aspect}_1080p.mp4"
        out_ws = WS_VIDEOS_DIR / f"FHG-SHORT-BROLL-001_{aspect}_1080p.mp4"

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(vis_mp4),
                "-i", str(master_audio),
                "-vf", f"ass=filename='{ass_escaped}':fontsdir='{fonts_escaped}'",
                "-map", "0:v:0", "-map", "1:a:0",
                "-map_metadata", "-1",
                "-metadata", "title=Thirty Pieces of Silver — For His Grace",
                "-metadata", "artist=For His Grace",
                "-metadata", "comment=https://forhisgrace.com",
                "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
                "-preset", "fast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-r", "60",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-movflags", "+faststart",
                "-shortest",
                str(out_dam),
            ],
            check=True,
            capture_output=True,
        )
        shutil.copy2(out_dam, out_broll_lib)
        shutil.copy2(out_dam, out_ws)
        print(f"COMPLETE LOCKSTEP ({aspect}): {out_dam} ({out_dam.stat().st_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    main()
