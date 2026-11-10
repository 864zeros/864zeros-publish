#!/usr/bin/env python3
r"""
Assemble FHG-SHORT-SEPIA-001 ("The Parable of the Mustard Seed & Small Beginnings" — Matthew 13:31-32)
in 100% LOCKSTEP across 9:16 Vertical (1080x1920 @ 60fps) and 16:9 Widescreen (1920x1080 @ 60fps)
using the locked BUILD_SPEC_FHG_SHORTS.md pipeline:
1. Newly Generated 1st-Century Sepia Parchment Sketches + 19-Style Python Filter Variations:
   - FHG-SK-014 (study_par_14_parable_sower_four_soils_b1_g2_s2.jpg)
   - FHG-SK-013 (study_par_13_parable_mustard_seed_tree_b1_g2_s2.jpg)
   - FHG-SK-028 (study_par_28_parable_growing_seed_secretly_night_day_c3_ukiyoe_riso.jpg)
   - FHG-SK-040 (study_par_40_tree_planted_by_streams_of_water_psalm1_b1_g2_s2.jpg)
2. Mastered 1080p Living Sepia Sketch Animations:
   - FHG-SK-013_sepia-mustard-seed-tree_{9x16,16x9}_1080p.mp4 (0.0s-3.4s & 3.4s-6.8s)
   - FHG-SK-003_sepia-humble-sparrow-hopping_{9x16,16x9}_1080p.mp4
3. 1st-Century Live-Action Judean/Galilean B-Roll Masters:
   - FHG-BR-047 (Jesus teaching disciples in the olive grove)
   - FHG-BR-053 (Birds taking flight from ancient olive trees)
   - FHG-BR-034 (Jesus walking toward camera in golden-hour olive grove)
4. Official Animated Bird-to-Parchment Outro (FHG-OUTRO-001_fig-tree-parchment_{9x16,16x9}_1080p.mp4).
5. Optical Safe-Zone Captions (X=468, Y=1080 on 9:16; X=960, Y=940 on 16:9), Montserrat Black,
   Warm Ivory (#FFFFF0) base + Gold/Amber (#FFBF00) active word highlight (2-3 words/frame).
6. Mastered to -14.0 LUFS integrated / -1.0 dBTP True Peak with 120ms J-Cut Micro-Foley Audio Pre-Rolls.
"""

from __future__ import annotations

import asyncio
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
import edge_tts

FFMPEG_BIN = r"C:\Users\Jeff\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
if os.path.exists(FFMPEG_BIN):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
DAM_BROLL_LIB = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo" / "broll_library"
SKETCHES_DIR = PUBLISH_ROOT / "shared" / "bible" / "sketches"
OUT_REELS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "rendered_reels"
WS_VIDEOS_DIR = Path(r"C:\dev\fhg-videos")
FONTS_DIR = PUBLISH_ROOT / "media" / "graphics" / "fonts"
PAD_WAV = PUBLISH_ROOT / "media" / "audio" / "music" / "fhg_432hz_ambient_pad.wav"
FOLEY_DIR = PUBLISH_ROOT / "media" / "audio" / "sfx" / "fhg_foley"
WORK_DIR = PUBLISH_ROOT / "_build" / "video" / "fhg_shorts_engine" / "tmp_work" / "fhg_short_sepia_001"

FHG_BASE_COLOR = "&H00F0FFFF&"       # Warm Ivory (#FFFFF0)
FHG_HIGHLIGHT_COLOR = "&H0000BFFF&"  # Gold/Amber (#FFBF00)
FHG_SHADOW_COLOR = "&H26000000&"     # 85% opacity black shadow


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


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


async def synth_segment_with_words(
    text: str,
    voice: str,
    rate: str,
    pitch: str,
    out_mp3: Path,
) -> list[WordTiming]:
    import json
    words_cache = out_mp3.with_suffix(".words.json")
    if out_mp3.exists() and out_mp3.stat().st_size > 500 and words_cache.exists():
        cached = json.loads(words_cache.read_text(encoding="utf-8"))
        return [WordTiming(**w) for w in cached]

    clean_text = text.replace("—", ", ").replace("...", ".")
    voices_to_try = [voice, "en-US-AndrewNeural", "en-US-BrianNeural"]
    for attempt in range(8):
        v_use = voices_to_try[min(attempt // 3, len(voices_to_try) - 1)]
        try:
            communicate = edge_tts.Communicate(
                text=clean_text,
                voice=v_use,
                rate=rate,
                pitch=pitch,
                boundary="WordBoundary",
            )
            words: list[WordTiming] = []
            with out_mp3.open("wb") as audio_f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        start_s = chunk["offset"] / 10_000_000.0
                        dur_s = chunk["duration"] / 10_000_000.0
                        w_text = str(chunk["text"]).strip()
                        if w_text:
                            words.append(WordTiming(word=w_text, start=start_s, end=start_s + max(dur_s, 0.08)))
            if out_mp3.stat().st_size > 500:
                words_cache.write_text(
                    json.dumps([{"word": w.word, "start": w.start, "end": w.end} for w in words]),
                    encoding="utf-8",
                )
                await asyncio.sleep(0.6)
                return words
        except Exception as exc:
            print(f"      [TTS retry {attempt + 1}/8 ({v_use})]: {exc}")
            await asyncio.sleep(1.2 * (attempt + 1))
    raise RuntimeError(f"Failed TTS synthesis for segment: {text[:40]}")


def attach_punctuation(raw_text: str, words: list[WordTiming]) -> list[WordTiming]:
    tokens = raw_text.replace("—", " — ").split()
    cleaned: list[WordTiming] = []
    idx = 0
    for w in words:
        matched_display = w.word
        for lookahead in range(idx, min(idx + 4, len(tokens))):
            bare = re.sub(r"[^\w']", "", tokens[lookahead]).lower()
            if bare == re.sub(r"[^\w']", "", w.word).lower():
                matched_display = tokens[lookahead]
                idx = lookahead + 1
                break
        cleaned.append(WordTiming(word=matched_display, start=w.start, end=w.end))
    return cleaned


async def build_main_vo(segments: list[dict], work_dir: Path) -> tuple[Path, list[WordTiming], float]:
    voice = "en-US-AndrewMultilingualNeural"
    base_pitch_hz = -1

    all_words: list[WordTiming] = []
    concat_inputs: list[Path] = []
    current_offset = 0.0

    for idx, seg in enumerate(segments):
        pause_ms = int(seg.get("pause_before_ms", 0))
        if pause_ms > 0:
            sil_wav = work_dir / f"sil_{idx}.wav"
            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", f"{pause_ms / 1000.0:.3f}",
                    str(sil_wav),
                ],
                check=True,
                capture_output=True,
            )
            concat_inputs.append(sil_wav)
            current_offset += pause_ms / 1000.0

        is_scripture = seg.get("type") == "scripture_quote"
        seg_pitch = f"{base_pitch_hz - 3:+d}Hz" if is_scripture else f"{base_pitch_hz:+d}Hz"
        seg_rate = "+11%" if is_scripture else "+15%"

        seg_mp3 = work_dir / f"seg_{idx}.mp3"
        seg_wav = work_dir / f"seg_{idx}.wav"
        seg_words = await synth_segment_with_words(
            text=seg["text"],
            voice=voice,
            rate=seg_rate,
            pitch=seg_pitch,
            out_mp3=seg_mp3,
        )
        seg_words = attach_punctuation(seg["text"], seg_words)

        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(seg_mp3),
                "-af", "areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB,areverse,apad=pad_dur=0.06",
                "-ar", "48000", "-ac", "2",
                str(seg_wav),
            ],
            check=True,
            capture_output=True,
        )
        seg_dur = get_audio_duration(seg_wav)
        if seg_words:
            first_w_start = seg_words[0].start
            for w in seg_words:
                adj_start = max(0.0, w.start - first_w_start) + current_offset
                adj_end = min(seg_dur + current_offset, max(adj_start + 0.08, (w.end - first_w_start) + current_offset))
                all_words.append(WordTiming(word=w.word, start=adj_start, end=adj_end))

        concat_inputs.append(seg_wav)
        current_offset += seg_dur

    concat_list = work_dir / "vo_concat.txt"
    concat_list.write_text("\n".join(f"file '{p.as_posix()}'" for p in concat_inputs) + "\n", encoding="utf-8")

    vo_full = work_dir / "vo_main.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c:a", "pcm_s16le",
            str(vo_full),
        ],
        check=True,
        capture_output=True,
    )
    return vo_full, all_words, get_audio_duration(vo_full)


def format_ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - (h * 3600 + m * 60)
    return f"{h:d}:{m:02d}:{s:05.2f}"


def write_ass_captions(
    words: list[WordTiming],
    out_ass: Path,
    play_w: int,
    play_h: int,
    pos_x: int,
    pos_y: int,
    font_size: int,
) -> None:
    phrases: list[list[WordTiming]] = []
    cur: list[WordTiming] = []
    cur_chars = 0
    for w in words:
        if cur:
            gap = w.start - cur[-1].end
            if len(cur) >= 3 or (cur_chars + len(w.word) + 1 > 20) or gap > 0.35:
                phrases.append(cur)
                cur = []
                cur_chars = 0
        cur.append(w)
        cur_chars += len(w.word) + 1
    if cur:
        phrases.append(cur)

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {play_w}
PlayResY: {play_h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: FHG_Short,Montserrat Black,{font_size},{FHG_BASE_COLOR},{FHG_HIGHLIGHT_COLOR},{FHG_SHADOW_COLOR},{FHG_SHADOW_COLOR},-1,0,0,0,100,100,0,0,1,4,6,2,48,192,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for p_idx, phrase in enumerate(phrases):
        phrase_end = phrase[-1].end
        if p_idx + 1 < len(phrases):
            next_phrase_start = phrases[p_idx + 1][0].start
            if 0.0 < (next_phrase_start - phrase_end) <= 0.35:
                phrase_end = next_phrase_start
        for i, active in enumerate(phrase):
            parts = []
            for j, w in enumerate(phrase):
                tok = w.word.replace("{", "").replace("}", "")
                if j == i:
                    parts.append(f"{{\\c{FHG_HIGHLIGHT_COLOR}}}{tok}{{\\c{FHG_BASE_COLOR}}}")
                else:
                    parts.append(tok)
            text_line = " ".join(parts)
            seg_start = active.start
            seg_end = phrase[i + 1].start if (i + 1 < len(phrase)) else max(seg_start + 0.12, phrase_end)
            override = f"{{\\an2\\pos({pos_x},{pos_y})\\blur6}}"
            lines.append(
                f"Dialogue: 0,{format_ass_time(seg_start)},{format_ass_time(seg_end)},"
                f"FHG_Short,,0,0,0,,{override}{text_line}"
            )

    out_ass.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_seamless_parchment_plate(sketch_path: Path, width: int, height: int, out_jpg: Path) -> Path:
    """
    Composites a 1:1 (1024x1024) 1st-Century Sepia Parchment Sketch onto a 2x supersampled
    (width*2 x height*2) clean, museum-grade warm aged parchment canvas with soft feathered edges
    and a delicate antique sepia border frame (matching the exact look of FHG-SK-001..013 animations):
      1. 100% of the 1st-Century illustration is preserved without cropping top/bottom or sides.
      2. Zero dark blurred smudges above or below the artwork — pure warm parchment paper with organic fiber grain.
      3. Ready for jitter-free 60fps 102% -> 108% Ken Burns zoompan!
    """
    if out_jpg.exists() and out_jpg.stat().st_size > 0:
        return out_jpg

    from PIL import ImageDraw

    im = Image.open(sketch_path).convert("RGB")
    arr = np.array(im, dtype=np.float32)

    # Sample the brightest paper pixels near the border so we get the clean warm parchment paper color (no ink smudge!)
    border_pixels = np.concatenate([
        arr[:20, :, :].reshape(-1, 3),
        arr[-20:, :, :].reshape(-1, 3),
        arr[:, :20, :].reshape(-1, 3),
        arr[:, -20:, :].reshape(-1, 3),
    ], axis=0)
    lum = 0.299 * border_pixels[:, 0] + 0.587 * border_pixels[:, 1] + 0.114 * border_pixels[:, 2]
    bright_mask = lum >= np.percentile(lum, 65)
    paper_rgb = np.median(border_pixels[bright_mask], axis=0)
    # Blend slightly toward our canonical FHG warm parchment (#E5D7BF = 229, 215, 191) so all plates feel cohesive
    canonical_parch = np.array([229.0, 215.0, 191.0], dtype=np.float32)
    bg_rgb = 0.65 * paper_rgb + 0.35 * canonical_parch

    target_w, target_h = width * 2, height * 2

    # Build clean organic parchment paper with subtle warm vignette & fine paper grain (zero dark ink blur!)
    yy, xx = np.mgrid[0:target_h, 0:target_w].astype(np.float32)
    ny = (yy / target_h) - 0.5
    nx = (xx / target_w) - 0.5
    rad2 = nx * nx + ny * ny
    vignette = 1.0 - 0.10 * np.clip(rad2 / 0.45, 0.0, 1.0)

    rng = np.random.default_rng(42)
    fine_grain = rng.normal(0.0, 2.4, size=(target_h, target_w, 1)).astype(np.float32)

    canvas_arr = np.zeros((target_h, target_w, 3), dtype=np.float32)
    for c in range(3):
        canvas_arr[:, :, c] = bg_rgb[c] * vignette
    canvas_arr = np.clip(canvas_arr + fine_grain, 0, 255).astype(np.uint8)
    canvas = Image.fromarray(canvas_arr)

    # Scale the 1:1 sketch to fit generously inside the frame with feathered parchment margins
    if height > width:
        # 9:16 Vertical (2160x3840): place 2040x2040 sketch centered in upper-middle optical zone
        sk_size = int(target_w * 0.94)
        sk_resized = im.resize((sk_size, sk_size), Image.Resampling.LANCZOS)
        paste_x = (target_w - sk_size) // 2
        paste_y = int((target_h - sk_size) * 0.38)
    else:
        # 16:9 Widescreen (3840x2160): place 2020x2020 sketch centered horizontally
        sk_size = int(target_h * 0.94)
        sk_resized = im.resize((sk_size, sk_size), Image.Resampling.LANCZOS)
        paste_x = (target_w - sk_size) // 2
        paste_y = (target_h - sk_size) // 2

    # Soft feathered alpha mask along the edges of the 1:1 sketch so paper transitions seamlessly
    mask = np.ones((sk_size, sk_size), dtype=np.float32)
    feather = int(sk_size * 0.06)
    ramp = np.linspace(0.0, 1.0, feather, dtype=np.float32)
    for i in range(feather):
        mask[i, :] = np.minimum(mask[i, :], ramp[i])
        mask[sk_size - 1 - i, :] = np.minimum(mask[sk_size - 1 - i, :], ramp[i])
        mask[:, i] = np.minimum(mask[:, i], ramp[i])
        mask[:, sk_size - 1 - i] = np.minimum(mask[:, sk_size - 1 - i], ramp[i])

    mask_img = Image.fromarray((mask * 255).astype(np.uint8), mode="L")
    canvas.paste(sk_resized, (paste_x, paste_y), mask_img)

    # Add delicate antique sepia ruled border around the full parchment plate (matching FHG-SK-013 & FHG-SK-003)
    draw = ImageDraw.Draw(canvas)
    pad_outer = 54
    pad_inner = 68
    sepia_line = (138, 114, 86)
    draw.rectangle([pad_outer, pad_outer, target_w - pad_outer, target_h - pad_outer], outline=sepia_line, width=4)
    draw.rectangle([pad_inner, pad_inner, target_w - pad_inner, target_h - pad_inner], outline=sepia_line, width=2)

    canvas.save(out_jpg, "JPEG", quality=95)
    return out_jpg


def build_hard_cut_visual_plus_outro(
    beat_specs: list[dict],
    body_dur: float,
    outro_mp4: Path,
    outro_dur: float,
    width: int,
    height: int,
    work_dir: Path,
    tag: str,
) -> tuple[Path, list[float]]:
    """
    Renders each 3.4s beat in 1080p @ 60fps:
    - If beat['mode'] == 'sketch_still': composites seamless parchment plate + applies 102%->108% 60fps Ken Burns zoompan.
    - If beat['mode'] == 'video': trims & scales 1080p living sepia animation or live-action B-roll @ 60fps.
    Then concatenates with 0.0s HARD CUTS and transitions into the Official Animated Bird-to-Parchment Outro
    via a 250ms (0.25s) warm dissolve.
    """
    beat_step = 3.4
    num_beats = int(body_dur // beat_step) + 1
    beat_files: list[Path] = []
    cut_timestamps: list[float] = []

    accum = 0.0
    for i in range(num_beats):
        remaining = body_dur - accum
        if remaining <= 0.05:
            break
        is_last = (i == num_beats - 1) or (remaining <= beat_step + 0.3)
        dur = (remaining + 0.25) if is_last else min(beat_step, remaining)

        spec = beat_specs[i % len(beat_specs)]
        beat_out = work_dir / f"beat_{tag}_{i:02d}.mp4"

        if not beat_out.exists() or beat_out.stat().st_size == 0:
            if spec["mode"] == "sketch_still":
                plate_jpg = work_dir / f"plate_{tag}_{i:02d}_{spec['path'].stem}.jpg"
                prepare_seamless_parchment_plate(spec["path"], width, height, plate_jpg)
                frames = max(1, int(round(dur * 60)))
                zoom_in = spec.get("zoom_in", True)
                z_expr = f"1.02+0.06*(on/{frames})" if zoom_in else f"1.08-0.06*(on/{frames})"
                vf = (
                    f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                    f"d={frames}:s={width}x{height}:fps=60,setsar=1,format=yuv420p"
                )
                subprocess.run(
                    [
                        "ffmpeg", "-y", "-loop", "1", "-i", str(plate_jpg),
                        "-vf", vf,
                        "-t", f"{dur:.3f}",
                        "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
                        str(beat_out),
                    ],
                    check=True,
                    capture_output=True,
                )
            else:
                start_s = float(spec.get("start_s", 0.0))
                subprocess.run(
                    [
                        "ffmpeg", "-y", "-stream_loop", "-1",
                        "-ss", f"{start_s:.2f}",
                        "-i", str(spec["path"]),
                        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,crop={width}:{height},fps=60,setsar=1,format=yuv420p",
                        "-t", f"{dur:.3f}",
                        "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
                        str(beat_out),
                    ],
                    check=True,
                    capture_output=True,
                )

        beat_files.append(beat_out)
        if i > 0:
            cut_timestamps.append(round(accum, 3))
        accum += beat_step
        if is_last:
            break

    concat_txt = work_dir / f"beats_{tag}_concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in beat_files) + "\n", encoding="utf-8")
    body_mp4 = work_dir / f"body_hardcuts_{tag}.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-reinit_filter", "0",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-vf", "format=yuv420p,setsar=1",
            "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
            str(body_mp4),
        ],
        check=True,
        capture_output=True,
    )

    # Transition from body_mp4 into the Official Animated Bird-to-Parchment Outro (outro_mp4) via 250ms Warm Dissolve
    actual_body_dur = get_audio_duration(body_mp4)
    safe_offset = min(body_dur, actual_body_dur - 0.30)
    full_visual = work_dir / f"full_visual_{tag}.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(body_mp4),
            "-i", str(outro_mp4),
            "-filter_complex",
            f"[0:v]fps=60,settb=AVTB[v0];[1:v]fps=60,settb=AVTB[v1];"
            f"[v0][v1]xfade=transition=fade:duration=0.250:offset={safe_offset:.3f}[vout]",
            "-map", "[vout]",
            "-t", f"{body_dur + outro_dur:.3f}",
            "-r", "60", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
            str(full_visual),
        ],
        check=True,
        capture_output=True,
    )
    return full_visual, cut_timestamps


def mix_jcut_audio_with_outro(
    main_vo_wav: Path,
    body_dur: float,
    cut_timestamps: list[float],
    outro_vo_master_wav: Path,
    outro_dur: float,
    work_dir: Path,
) -> Path:
    foley_cycle = [
        FOLEY_DIR / "parchment_turn.wav",
        FOLEY_DIR / "felt_piano.wav",
        FOLEY_DIR / "leather_close.wav",
        FOLEY_DIR / "desert_wind.wav",
    ]
    inputs = ["-i", str(main_vo_wav), "-i", str(PAD_WAV)]
    filter_lines = [
        "[0:a]asplit=2[vo_sc][vo_main]",
        f"[1:a]equalizer=f=1000:t=h:w=2700:g=-4,volume=-14dB,atrim=0:{body_dur + 0.25:.3f},afade=t=out:st={body_dur - 0.15:.3f}:d=0.35[pad_eq]",
        "[pad_eq][vo_sc]sidechaincompress=threshold=0.03:ratio=6:attack=10:release=280[pad_ducked]",
    ]
    mix_labels = ["[vo_main]", "[pad_ducked]"]

    for idx, cut_ts in enumerate(cut_timestamps):
        jcut_ts = max(0.0, cut_ts - 0.120)
        f_wav = foley_cycle[idx % len(foley_cycle)]
        in_idx = len(inputs) // 2
        inputs.extend(["-i", str(f_wav)])
        delay_ms = int(round(jcut_ts * 1000))
        lbl = f"[jcut_{idx}]"
        filter_lines.append(f"[{in_idx}:a]volume=-14dB,adelay={delay_ms}|{delay_ms}{lbl}")
        mix_labels.append(lbl)

    parch_in_idx = len(inputs) // 2
    inputs.extend(["-i", str(FOLEY_DIR / "parchment_turn.wav")])
    outro_jcut_ms = int(round(max(0.0, body_dur - 0.120) * 1000))
    filter_lines.append(f"[{parch_in_idx}:a]volume=-13dB,adelay={outro_jcut_ms}|{outro_jcut_ms}[jcut_outro]")
    mix_labels.append("[jcut_outro]")

    outro_in_idx = len(inputs) // 2
    inputs.extend(["-i", str(outro_vo_master_wav)])
    outro_start_ms = int(round(body_dur * 1000))
    filter_lines.append(f"[{outro_in_idx}:a]adelay={outro_start_ms}|{outro_start_ms}[outro_a]")
    mix_labels.append("[outro_a]")

    total_dur = body_dur + outro_dur
    n_mix = len(mix_labels)
    filter_lines.append(
        f"{''.join(mix_labels)}amix=inputs={n_mix}:duration=longest:dropout_transition=0:normalize=0[pre_lufs]"
    )
    filter_lines.append("[pre_lufs]loudnorm=I=-14.0:TP=-1.0:LRA=11.0[a_master]")

    master_wav = work_dir / "full_audio_master_14lufs.wav"
    subprocess.run(
        [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", ";".join(filter_lines),
            "-map", "[a_master]",
            "-t", f"{total_dur:.3f}",
            "-ar", "48000", "-ac", "2",
            str(master_wav),
        ],
        check=True,
        capture_output=True,
    )
    return master_wav


async def main() -> None:
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REELS_DIR.mkdir(parents=True, exist_ok=True)

    segments = [
        {
            "type": "hook",
            "pause_before_ms": 0,
            "text": "Why did Jesus compare the Kingdom of Heaven to a wild garden seed that Roman emperors wouldn't even notice?",
        },
        {
            "type": "context_disruption",
            "pause_before_ms": 120,
            "text": "In first-century Galilee, everyone expected God's kingdom to arrive like a towering cedar of Lebanon — loud, unshakeable, and immediate. Instead, Jesus pointed to a weathered farmer pressing a speck of black mustard into the dust.",
        },
        {
            "type": "scripture_reveal",
            "pause_before_ms": 140,
            "text": "Standing by the shore, Jesus told the crowd in Matthew thirteen,",
        },
        {
            "type": "scripture_quote",
            "pause_before_ms": 250,  # 250ms Reverence Pause + Pitch Drop
            "text": "The kingdom of heaven is like a mustard seed, which a man took and planted in his field. Though it is the smallest of all your seeds, yet when it grows, it becomes a tree, so that the birds of the air come and make nests in its branches.",
        },
        {
            "type": "personal_application",
            "pause_before_ms": 180,
            "text": "Maybe today your obedience feels tiny, buried, or unseen. Take heart: in the hands of the Master, what starts hidden in the dark soil of faith always grows into a sanctuary of grace.",
        },
    ]

    print("[1/4] Synthesizing Main Voiceover + 250ms Pre-Scripture Reverence Pause...")
    main_vo_wav, words, body_dur = await build_main_vo(segments, WORK_DIR)
    outro_vo_wav = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_vo_master_14lufs.wav"
    outro_dur = get_audio_duration(outro_vo_wav)
    print(f"      -> Body VO: {body_dur:.2f}s ({len(words)} words) + Outro VO: {outro_dur:.2f}s = {body_dur + outro_dur:.2f}s total")

    def build_beats_for_aspect(aspect: str) -> list[dict]:
        return [
            # Beat 0 (0.0-3.4s — "Why did Jesus compare the Kingdom of Heaven to a wild garden seed..."):
            # NEW 1st-Century Sepia Parchment Sketch FHG-SK-013 (Base Sepia Drawing of Galilean farmer's palm & mustard tree)
            {
                "mode": "sketch_still",
                "path": SKETCHES_DIR / "study_par_13_parable_mustard_seed_tree_base.jpg",
                "zoom_in": True,
            },
            # Beat 1 (3.4-6.8s — "...that Roman emperors wouldn't even notice? In first-century Galilee..."):
            # NEW 1st-Century Sepia Parchment Sketch FHG-SK-014 (Base Sepia Drawing of Galilean Sower & Four Soils)
            {
                "mode": "sketch_still",
                "path": SKETCHES_DIR / "study_par_14_parable_sower_four_soils_base.jpg",
                "zoom_in": True,
            },
            # Beat 2 (6.8-10.2s — "...everyone expected God's kingdom to arrive like a towering cedar of Lebanon..."):
            # LIVING SEPIA ANIMATION FHG-SK-012 (Majestic Eagle soaring over mountain thermals on parchment)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-SK-012_sepia-soaring-eagle-thermals_{aspect}_1080p.mp4",
                "start_s": 0.0,
            },
            # Beat 3 (10.2-13.6s — "...Instead, Jesus pointed to a weathered farmer..."):
            # LIVING SEPIA ANIMATION FHG-SK-007 (1st-Century Plowing Ox & Yoke turning rocky Galilean soil on parchment)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-SK-007_sepia-plowing-ox-yoke_{aspect}_1080p.mp4",
                "start_s": 0.0,
            },
            # Beat 4 (13.6-17.0s — "...pressing a speck of black mustard into the dust."):
            # NEW 1st-Century Sepia Sketch FHG-SK-013 Filter Variation (3-Color Earth Risograph C2)
            {
                "mode": "sketch_still",
                "path": SKETCHES_DIR / "study_par_13_parable_mustard_seed_tree_c2_riso_earth.jpg",
                "zoom_in": False,
            },
            # Beat 5 (17.0-20.4s — "Standing by the shore, Jesus told the crowd..."):
            # 1st-Century Live-Action B-Roll FHG-BR-047 (Jesus teaching disciples in the sunlit Galilean grove)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-BR-047_jesus-teaching-disciples-in-olive-grove-peace-i-leave-with-you_{aspect}_1080p.mp4",
                "start_s": 0.0,
            },
            # Beat 6 (20.4-23.8s — "...in Matthew thirteen, <250ms Reverence Pause>"):
            # NEW 1st-Century Sepia Sketch FHG-SK-035 (Base Sepia Drawing: Seed Growing Secretly Night & Day)
            {
                "mode": "sketch_still",
                "path": SKETCHES_DIR / "study_par_35_parable_growing_seed_night_and_day_base.jpg",
                "zoom_in": True,
            },
            # Beat 7 (23.8-27.2s — "The kingdom of heaven is like a mustard seed, which a man took and planted in his field..."):
            # LIVING SEPIA ANIMATION FHG-SK-013 Part 1 (Tiny mustard seed taking root & sprouting upward on parchment!)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-SK-013_sepia-mustard-seed-tree_{aspect}_1080p.mp4",
                "start_s": 0.0,
            },
            # Beat 8 (27.2-30.6s — "...Though it is the smallest of all your seeds, yet when it grows, it becomes a tree..."):
            # LIVING SEPIA ANIMATION FHG-SK-013 Part 2 (Sapling expanding into a great branching mustard tree as birds fly in!)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-SK-013_sepia-mustard-seed-tree_{aspect}_1080p.mp4",
                "start_s": 3.4,
            },
            # Beat 9 (30.6-34.0s — "...so that the birds of the air come and make nests in its branches."):
            # LIVING SEPIA ANIMATION FHG-SK-003 (Humble Judean Sparrow hopping along the warm parchment branch!)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-SK-003_sepia-humble-sparrow-hopping_{aspect}_1080p.mp4",
                "start_s": 0.0,
            },
            # Beat 10 (34.0-37.4s — "...make nests in its branches. Maybe today your obedience..."):
            # LIVING SEPIA ANIMATION FHG-SK-002 (Turtledove rustling wings & taking flight on warm parchment)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-SK-002_sepia-turtledove-taking-flight_{aspect}_1080p.mp4",
                "start_s": 0.0,
            },
            # Beat 11 (37.4-40.8s — "...feels tiny, buried, or unseen. Take heart..."):
            # NEW 1st-Century Sepia Sketch FHG-SK-035 Filter Variation (Ukiyo-e Earth Risograph C3 of hidden seed sprouting)
            {
                "mode": "sketch_still",
                "path": SKETCHES_DIR / "study_par_35_parable_growing_seed_night_and_day_c3_ukiyoe_riso.jpg",
                "zoom_in": False,
            },
            # Beat 12 (40.8-44.2s — "...in the hands of the Master, what starts hidden in the dark soil of faith..."):
            # NEW 1st-Century Sepia Sketch FHG-SK-040 (Base Sepia Drawing: Tree Planted by Streams of Water Psalm 1)
            {
                "mode": "sketch_still",
                "path": SKETCHES_DIR / "study_par_40_tree_planted_by_streams_of_water_psalm1_base.jpg",
                "zoom_in": True,
            },
            # Beat 13 (44.2-47.6s — "...always grows into a sanctuary of grace."):
            # 1st-Century Live-Action B-Roll FHG-BR-034 (Jesus walking toward camera in golden-hour olive grove)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-BR-034_jesus-walking-olive-grove-dolly_{aspect}_1080p.mp4",
                "start_s": 0.0,
            },
            # Beat 14 (47.6s-end — visual bridge into Animated Bird-to-Parchment Outro):
            # 1st-Century Live-Action B-Roll FHG-BR-053 (Birds taking flight from ancient olive branches in golden light)
            {
                "mode": "video",
                "path": DAM_BROLL_LIB / f"FHG-BR-053_birds-taking-flight-from-ancient-olive-trees_{aspect}_1080p.mp4",
                "start_s": 0.0,
            },
        ]

    print("[2/4] Building Lockstep 9:16 & 16:9 Visual Timelines (New Sepia Sketches + Sepia Animations + 1st-Century B-Roll + Animated Bird Outro)...")
    vis_9x16, cuts_9x16 = build_hard_cut_visual_plus_outro(
        build_beats_for_aspect("9x16"),
        body_dur,
        DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_9x16_1080p.mp4",
        outro_dur,
        1080,
        1920,
        WORK_DIR,
        "9x16",
    )
    vis_16x9, _ = build_hard_cut_visual_plus_outro(
        build_beats_for_aspect("16x9"),
        body_dur,
        DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_16x9_1080p.mp4",
        outro_dur,
        1920,
        1080,
        WORK_DIR,
        "16x9",
    )

    print(f"[3/4] Mixing Psychoacoustic Master with {len(cuts_9x16)} x 120ms J-Cut Audio Pre-Rolls + Animated Bird Outro VO (-14 LUFS)...")
    master_audio = mix_jcut_audio_with_outro(
        main_vo_wav, body_dur, cuts_9x16, outro_vo_wav, outro_dur, WORK_DIR
    )

    print("[4/4] Burning Active-Word Captions & Exporting Final 1080p 60fps Deliverables...")
    ass_9x16 = WORK_DIR / "captions_9x16.ass"
    ass_16x9 = WORK_DIR / "captions_16x9.ass"
    write_ass_captions(words, ass_9x16, 1080, 1920, 468, 1080, 74)
    write_ass_captions(words, ass_16x9, 1920, 1080, 960, 940, 56)

    fonts_escaped = FONTS_DIR.as_posix().replace(":", "\\:")

    for aspect, vis_mp4, ass_p in [
        ("9x16", vis_9x16, ass_9x16),
        ("16x9", vis_16x9, ass_16x9),
    ]:
        ass_escaped = ass_p.as_posix().replace(":", "\\:")
        out_dam = OUT_REELS_DIR / f"FHG-SHORT-SEPIA-001_{aspect}_1080p.mp4"
        out_broll_lib = DAM_BROLL_LIB / f"FHG-SHORT-SEPIA-001_{aspect}_1080p.mp4"
        out_ws = WS_VIDEOS_DIR / f"FHG-SHORT-SEPIA-001_{aspect}_1080p.mp4"

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(vis_mp4),
                "-i", str(master_audio),
                "-vf", f"ass=filename='{ass_escaped}':fontsdir='{fonts_escaped}'",
                "-map", "0:v:0", "-map", "1:a:0",
                "-map_metadata", "-1",
                "-metadata", "title=The Parable of the Mustard Seed — For His Grace",
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
        print(f"COMPLETE ({aspect}): {out_dam} ({out_dam.stat().st_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    asyncio.run(main())
