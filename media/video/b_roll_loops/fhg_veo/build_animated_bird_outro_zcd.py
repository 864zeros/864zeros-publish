#!/usr/bin/env python3
r"""
Build the Official Full FHG Animated Bird-to-Parchment Outro (FHG-OUTRO-001) in 9:16 (1080x1920) & 16:9 (1920x1080):
1. Starts at 0.0s with the singular bird sketch animation (A_sepia_watercolor_and_ink_24a6bd59.mp4)
   from standing on the shoreline rock -> taking flight -> centering in flight (0.0s -> 3.35s).
   * In 16:9 (1920x1080): Full widescreen frame showing the sun on the horizon, shoreline rocks, and the bird taking off to center.
   * In 9:16 (1080x1920): Smooth camera pan tracking the bird from standing on the right rock (t=0.0s) to center in flight (t=3.0s).
   * Toned to match the exact FHG warm aged parchment paper palette (#DBCEB8) so the dissolve into the Outro card is 100% seamless!
2. At t=2.90s -> 3.35s (0.45s smooth parchment dissolve), right as the bird centers in flight, fades into the
   FHG Fig Tree Parchment Outro card (3.35s -> 7.96s).
3. The Outro Voiceover ("For His Grace. Solitude isn't lonely when it's the gift that He gave. Learn more on ForHisGrace.com.")
   starts at t=0.0s (the start of the bird animation), layered with the bird clip's gentle acoustic chord & wing flutter (-16dB)
   and mastered to -14.0 LUFS / -1.0 dBTP.
"""

import shutil
import subprocess
from pathlib import Path

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
VEO_DIR = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo"
DAM_BROLL_LIB = VEO_DIR / "broll_library"
OUT_REELS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "rendered_reels"
WS_VIDEOS_DIR = Path(r"C:\dev\fhg-videos")
FONTS_DIR = PUBLISH_ROOT / "media" / "graphics" / "fonts"
PAD_WAV = PUBLISH_ROOT / "media" / "audio" / "music" / "fhg_432hz_ambient_pad.wav"
FOLEY_DIR = PUBLISH_ROOT / "media" / "audio" / "sfx" / "fhg_foley"
WORK_DIR = PUBLISH_ROOT / "_build" / "video" / "fhg_shorts_engine" / "tmp_work" / "fhg_outro_vo"
SHORT_WORK_DIR = PUBLISH_ROOT / "_build" / "video" / "fhg_shorts_engine" / "tmp_work" / "fhg_short_broll_001"

BIRD_MP4 = VEO_DIR / "A_sepia_watercolor_and_ink_24a6bd59.mp4"


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


def build_outro_audio_with_bird_sfx() -> tuple[Path, float]:
    """
    Mix the Outro VO (starting right at t=0.0s of the bird animation) with:
    - The gentle acoustic guitar & wing-takeoff audio from A_sepia_watercolor_and_ink_24a6bd59.mp4 (0.0s -> 4.8s)
    - The 432Hz ambient pad + parchment_turn at the card dissolve (t=4.25s)
    - Mastered to -14.0 LUFS / -1.0 dBTP.
    """
    vo_raw = WORK_DIR / "outro_vo_raw.wav"
    vo_dur = get_duration(vo_raw)
    # Give 4.5s for the bird + 4.3s on the parchment card (8.80s total) so the card has generous reading hold
    total_dur = max(vo_dur + 0.85, 8.80)
    parchment_wav = FOLEY_DIR / "parchment_turn.wav"
    master_wav = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_vo_master_14lufs.wav"

    filter_complex = (
        f"[0:a]apad=whole_dur={total_dur:.3f},asplit=2[vo_sc][vo_main];"
        f"[1:a]atrim=0:4.85,afade=t=in:st=0:d=0.25,afade=t=out:st=3.95:d=0.85,volume=-11dB,apad=whole_dur={total_dur:.3f}[bird_a];"
        "[2:a]equalizer=f=1000:t=h:w=2700:g=-4,volume=-15dB,"
        f"afade=t=out:st={total_dur - 0.90:.2f}:d=0.90[pad_eq];"
        "[pad_eq][vo_sc]sidechaincompress=threshold=0.03:ratio=6:attack=10:release=280[pad_ducked];"
        f"[3:a]volume=-14dB,adelay=4250|4250,apad=whole_dur={total_dur:.3f}[fl_parch];"
        "[vo_main][bird_a][pad_ducked][fl_parch]amix=inputs=4:duration=first:dropout_transition=0:normalize=0[pre];"
        "[pre]loudnorm=I=-14.0:TP=-1.0:LRA=11.0[a_out]"
    )
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(vo_raw),
            "-i", str(BIRD_MP4),
            "-i", str(PAD_WAV),
            "-i", str(parchment_wav),
            "-filter_complex", filter_complex,
            "-map", "[a_out]",
            "-t", f"{total_dur:.3f}",
            "-ar", "48000", "-ac", "2",
            str(master_wav),
        ],
        check=True,
        capture_output=True,
    )
    print(f"Updated Outro Audio (VO at 0.0s + 4.5s Bird Wing/Guitar SFX): {master_wav} ({total_dur:.2f}s)")
    return master_wav, total_dur


def build_animated_outro_video(aspect: str, width: int, height: int, total_dur: float, master_wav: Path) -> Path:
    """
    Render the full animated Outro (total_dur = 8.80s):
    - 0.0s -> 4.70s: Bird standing on shoreline -> taking off -> soaring centered in flight for 4.5s (toned to warm FHG parchment #DBCEB8)
    - 4.25s -> 4.70s (0.45s dissolve): Fades into the FHG Fig Tree Parchment Outro card right at the 4.5s midpoint
    - 4.70s -> 8.80s: Holds on the FHG Fig Tree Parchment Outro card while VO finishes + 1s reading buffer.
    """
    bird_dur = 4.70
    xfade_dur = 0.45
    xfade_offset = 4.25  # 4.25s -> 4.70s dissolve (centered right at 4.5s!)
    card_dur = total_dur - xfade_offset + 0.15

    plate_jpg = DAM_BROLL_LIB / f"FHG-OUTRO-001_fig-tree-parchment_{aspect}_1080p.jpg"
    bird_seg = WORK_DIR / f"bird_seg_{aspect}.mp4"
    card_seg = WORK_DIR / f"card_seg_{aspect}.mp4"
    out_mp4 = DAM_BROLL_LIB / f"FHG-OUTRO-001_fig-tree-parchment_{aspect}_1080p.mp4"

    # Tone filter to match the bird clip's light cream paper to our warm FHG aged parchment (#DBCEB8)
    parchment_tone = "colorbalance=rs=0.05:gs=0.01:bs=-0.08:rm=0.06:gm=0.01:bm=-0.09:rh=0.04:gh=0.00:bh=-0.08,eq=brightness=-0.04:saturation=0.92"

    if aspect == "16x9":
        vf_bird = f"scale={width}:{height}:flags=lanczos,fps=60,{parchment_tone},setsar=1,format=yuv420p"
    else:
        # 9:16 Vertical (1080x1920): Scale height to 1920 (width becomes 3414), and smoothly pan X
        # from the bird standing on the shoreline rock (x_ratio=0.85 at t=0..1.0s) to dead center in flight (x_ratio=0.52 at t=3.2..4.7s)
        vf_bird = (
            f"scale=-1:{height}:flags=lanczos,"
            f"crop={width}:{height}:'(iw-ow)*clip(0.85 - 0.33*clip((t-1.0)/2.2, 0, 1), 0.52, 0.85)':0,"
            f"fps=60,{parchment_tone},setsar=1,format=yuv420p"
        )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(BIRD_MP4),
            "-vf", vf_bird,
            "-t", f"{bird_dur:.3f}",
            "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
            str(bird_seg),
        ],
        check=True,
        capture_output=True,
    )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-loop", "1", "-i", str(plate_jpg),
            "-vf", f"scale={width}:{height}:flags=lanczos,fps=60,setsar=1,format=yuv420p",
            "-t", f"{card_dur:.3f}",
            "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
            str(card_seg),
        ],
        check=True,
        capture_output=True,
    )

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(bird_seg),
            "-i", str(card_seg),
            "-i", str(master_wav),
            "-filter_complex", f"[0:v][1:v]xfade=transition=fade:duration={xfade_dur:.3f}:offset={xfade_offset:.3f}[vout]",
            "-map", "[vout]", "-map", "2:a:0",
            "-t", f"{total_dur:.3f}",
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-crf", "17", "-preset", "fast", "-pix_fmt", "yuv420p", "-r", "60",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart",
            "-shortest",
            str(out_mp4),
        ],
        check=True,
        capture_output=True,
    )
    shutil.copy2(out_mp4, WS_VIDEOS_DIR / out_mp4.name)
    print(f"Created Animated Bird->Parchment Outro ({aspect}): {out_mp4} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
    return out_mp4


def update_short_001_with_animated_outro(outro_dur: float, outro_vo_wav: Path) -> None:
    """Attach the new Animated Bird-to-Parchment Outro to FHG-SHORT-BROLL-001 (9:16 & 16:9)."""
    main_vo_wav = SHORT_WORK_DIR / "vo_main.wav"
    body_dur = get_duration(main_vo_wav)

    # Re-mix full audio master with the updated Outro audio (which now includes the bird wing/guitar SFX!)
    from assemble_fhg_broll_short_001 import mix_jcut_audio_with_outro
    cuts = [round(i * 3.4, 3) for i in range(1, int(body_dur // 3.4) + 1) if i * 3.4 < body_dur - 0.05]
    master_audio = mix_jcut_audio_with_outro(
        main_vo_wav, body_dur, cuts, outro_vo_wav, outro_dur, SHORT_WORK_DIR
    )

    fonts_escaped = FONTS_DIR.as_posix().replace(":", "\\:")
    for aspect, (W, H) in [("9x16", (1080, 1920)), ("16x9", (1920, 1080))]:
        body_mp4 = SHORT_WORK_DIR / f"body_lock_hardcuts_{aspect}.mp4"
        outro_mp4 = DAM_BROLL_LIB / f"FHG-OUTRO-001_fig-tree-parchment_{aspect}_1080p.mp4"
        full_vis = SHORT_WORK_DIR / f"full_bird_outro_vis_{aspect}.mp4"

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(body_mp4),
                "-i", str(outro_mp4),
                "-filter_complex", f"[0:v][1:v]xfade=transition=fade:duration=0.250:offset={body_dur:.3f}[vout]",
                "-map", "[vout]",
                "-t", f"{body_dur + outro_dur:.3f}",
                "-r", "60", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
                str(full_vis),
            ],
            check=True,
            capture_output=True,
        )

        ass_escaped = (SHORT_WORK_DIR / f"captions_{aspect}.ass").as_posix().replace(":", "\\:")
        out_dam = OUT_REELS_DIR / f"FHG-SHORT-BROLL-001_{aspect}_1080p.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(full_vis),
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
        shutil.copy2(out_dam, DAM_BROLL_LIB / out_dam.name)
        shutil.copy2(out_dam, WS_VIDEOS_DIR / out_dam.name)
        print(f"Updated Full Short ({aspect}) with Animated Bird Outro: {out_dam}")


def main() -> None:
    master_wav, total_dur = build_outro_audio_with_bird_sfx()
    build_animated_outro_video("9x16", 1080, 1920, total_dur, master_wav)
    build_animated_outro_video("16x9", 1920, 1080, total_dur, master_wav)
    update_short_001_with_animated_outro(total_dur, master_wav)


if __name__ == "__main__":
    main()
