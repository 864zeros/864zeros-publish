"""864zGenStudioNow (BRK-MEDIA-004) — Official FHG Bible Shorts Compositor.

Executes the locked BUILD_SPEC_FHG_SHORTS.md pipeline using ONLY historically accurate
First-Century Judea/Galilee & Sepia/Charcoal Parchment assets + live Fly-Over Outlines-on-Parchment:
1. 30-45s 5-stage script with seamless loop bridge & 250ms pre-Scripture pause + pitch drop.
2. Close-mic conversational baritone TTS at ~1.15x (165-175 WPM) with word-level boundary timestamps.
3. Optical safe-zone .ass captions (X = 468, Y = 1080 <= 1100, Montserrat Black 74pt,
   Warm Ivory #FFFFF0 base + Gold/Amber #FFBF00 single-active-word highlight, 2-3 words/frame).
4. 3.5s visual pacing with 300ms luminance dissolve (xfade=transition=fadegrays:duration=0.3),
   Mid-Flight Sketch-on-Parchment -> Real Fly-Over transformation, and bounded 102% -> 108% Ken Burns at 60fps.
5. 432Hz ambient pad (-4dB EQ carve at 300Hz-3kHz + sidechaincompress ducking) + 3.5s cut-synced
   organic Micro-Foley (parchment_turn, leather_close, felt_piano, desert_wind) mastered to -14 LUFS / -1 dBTP.
6. Strict RULE-004 brand firewall (-map_metadata -1, clean fhg_short_*.mp4 output).
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import edge_tts

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
QUEUE_JSONL = PUBLISH_ROOT / "apps" / "forhisgrace" / "shorts_queue.jsonl"
VEO_DIR = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo"
STILLS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "plates" / "stills"
STORYBOARDS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "storyboards"
OUT_REELS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "rendered_reels"
FONTS_DIR = PUBLISH_ROOT / "media" / "graphics" / "fonts"
PAD_WAV = PUBLISH_ROOT / "media" / "audio" / "music" / "fhg_432hz_ambient_pad.wav"
FOLEY_DIR = PUBLISH_ROOT / "media" / "audio" / "sfx" / "fhg_foley"
WORK_DIR = PUBLISH_ROOT / "_build" / "video" / "fhg_shorts_engine" / "tmp_work"

# ASS BGR Colors (&HAABBGGRR)
FHG_BASE_COLOR = "&H00F0FFFF&"       # Warm Ivory (#FFFFF0)
FHG_HIGHLIGHT_COLOR = "&H0000BFFF&"  # Gold/Amber (#FFBF00)
FHG_SHADOW_COLOR = "&H26000000&"     # 85% opacity black shadow
FHG_OPTICAL_X = 468
FHG_OPTICAL_Y = 1080
FHG_FONT_SIZE = 74


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


def get_audio_duration(path: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    out = subprocess.check_output(cmd, text=True).strip()
    return float(out)


async def synth_segment_with_words(
    text: str,
    voice: str,
    rate: str,
    pitch: str,
    out_mp3: Path,
) -> list[WordTiming]:
    """Synthesize a segment with edge_tts and capture exact WordBoundary timestamps (with retry)."""
    clean_text = text.replace("—", ", ").replace("...", ".")
    for attempt in range(4):
        try:
            communicate = edge_tts.Communicate(
                text=clean_text,
                voice=voice,
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
            if out_mp3.stat().st_size > 0:
                await asyncio.sleep(0.35)
                return words
        except Exception as exc:
            print(f"      [TTS retry {attempt + 1}/4]: {exc}")
            await asyncio.sleep(1.0 * (attempt + 1))
    raise RuntimeError(f"Failed TTS synthesis for segment: {text[:40]}")


def attach_punctuation(raw_text: str, words: list[WordTiming]) -> list[WordTiming]:
    """Restore clean display punctuation from raw_text onto the WordBoundary tokens."""
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


async def build_voiceover_and_timestamps(short_spec: dict, work_dir: Path) -> tuple[Path, list[WordTiming], float]:
    """Synthesize all segments with 1.15x rate, per-video pitch jitter, and 250ms pre-Scripture pause + pitch drop."""
    short_id = short_spec["short_id"]
    seed_int = int(hashlib.sha256(short_id.encode()).hexdigest()[:6], 16)
    base_pitch_hz = -2 + (seed_int % 3)  # -2Hz, -1Hz, or 0Hz per-video originality contour
    voice = "en-US-AndrewMultilingualNeural"

    segments = short_spec["segments"]
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
                "-af", "areverse,silenceremove=start_periods=1:start_duration=0.05:start_threshold=-45dB,areverse,apad=pad_dur=0.08",
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
    with concat_list.open("w", encoding="utf-8") as f:
        for p in concat_inputs:
            f.write(f"file '{p.as_posix()}'\n")

    vo_full = work_dir / "vo_full.wav"
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
    total_dur = get_audio_duration(vo_full)
    return vo_full, all_words, total_dur


def format_ass_time(seconds: float) -> str:
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds - (h * 3600 + m * 60)
    return f"{h:d}:{m:02d}:{s:05.2f}"


def write_fhg_ass_captions(words: list[WordTiming], out_ass: Path) -> None:
    """Write .ass captions anchored at X=468, Y=1080 (<=1100), 2-3 words/frame, Warm Ivory + Gold active word."""
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
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: FHG_Short,Montserrat Black,{FHG_FONT_SIZE},{FHG_BASE_COLOR},{FHG_HIGHLIGHT_COLOR},{FHG_SHADOW_COLOR},{FHG_SHADOW_COLOR},-1,0,0,0,100,100,0,0,1,4,6,2,48,192,820,1

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
            override = f"{{\\an2\\pos({FHG_OPTICAL_X},{FHG_OPTICAL_Y})\\blur6}}"
            lines.append(
                f"Dialogue: 0,{format_ass_time(seg_start)},{format_ass_time(seg_end)},"
                f"FHG_Short,,0,0,0,,{override}{text_line}"
            )

    out_ass.parent.mkdir(parents=True, exist_ok=True)
    out_ass.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prepare_beat_clip(
    asset_path: Path,
    mode: str,
    beat_dur: float,
    out_clip: Path,
    start_sec: float = 0.0,
    zoom_in: bool = True,
    crop_x_ratio: float = 0.5,
) -> None:
    """Render a single 1080x1920 @ 60fps visual beat clip.

    mode:
      - 'still': High-res still with jitter-free 102% -> 108% Ken Burns zoompan at 60fps
      - 'video_real': Native Veo/Sketch motion video cropped to 9:16 @ 60fps starting at start_sec
      - 'video_sketch': Live conversion of a fly-over video into Fine-Line Ink Outlines on Warm Parchment
                        starting at start_sec so it can dissolve mid-flight into 'video_real'!
    """
    frames = int(round(beat_dur * 60))
    if mode == "still":
        z_expr = f"1.02+0.06*(on/{max(1, frames)})" if zoom_in else f"1.08-0.06*(on/{max(1, frames)})"
        x_bias = f"(iw - iw/zoom)*{crop_x_ratio:.2f}"
        vf = (
            f"scale=2160:3840:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=2160:3840,"
            f"zoompan=z='{z_expr}':x='{x_bias}':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps=60,"
            f"eq=contrast=1.06:saturation=1.06:brightness=-0.01,"
            f"setsar=1,format=yuv420p"
        )
        cmd = [
            "ffmpeg", "-y", "-loop", "1", "-i", str(asset_path),
            "-vf", vf,
            "-t", f"{beat_dur:.3f}",
            "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
            str(out_clip),
        ]
    elif mode == "video_sketch":
        # Convert moving fly-over video into Fine-Line Ink Outlines on Warm Aged Parchment (#F5ECD9)
        vf = (
            f"scale=1124:1998:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1080:1920:(iw-1080)*{crop_x_ratio:.2f}:(ih-1920)/2,"
            f"fps=60,format=gray,split=3[g1][g2][e];"
            f"[g1]gblur=sigma=0.8[b1];"
            f"[g2]gblur=sigma=3.2[b2];"
            f"[b1][b2]blend=all_mode=grainextract,curves=all='0/0 0.46/0.15 0.51/0.96 1/1'[dog];"
            f"[e]edgedetect=low=0.10:high=0.26:mode=wires,negate[wires];"
            f"[dog][wires]blend=all_mode=multiply:all_opacity=0.65,"
            f"format=rgb24,lutrgb=r='val*0.96':g='val*0.92':b='val*0.83',"
            f"vignette=angle=PI/7,setsar=1,format=yuv420p"
        )
        cmd = [
            "ffmpeg", "-y", "-stream_loop", "-1",
            "-ss", f"{start_sec:.3f}",
            "-i", str(asset_path),
            "-vf", vf,
            "-t", f"{beat_dur:.3f}",
            "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
            str(out_clip),
        ]
    else:  # 'video_real'
        vf = (
            f"scale=1124:1998:force_original_aspect_ratio=increase:flags=lanczos,"
            f"crop=1080:1920:(iw-1080)*{crop_x_ratio:.2f}:(ih-1920)/2,"
            f"fps=60,"
            f"eq=contrast=1.06:saturation=1.06,"
            f"setsar=1,format=yuv420p"
        )
        cmd = [
            "ffmpeg", "-y", "-stream_loop", "-1",
            "-ss", f"{start_sec:.3f}",
            "-i", str(asset_path),
            "-vf", vf,
            "-t", f"{beat_dur:.3f}",
            "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
            str(out_clip),
        ]
    subprocess.run(cmd, check=True, capture_output=True)


def get_sequence_for_short(short_id: str) -> list[tuple[Path, str, float, bool, float]]:
    """Return curated list of (asset_path, mode, start_sec, zoom_in, crop_x_ratio) per short_id."""
    if short_id == "fhg_short_002":
        # Matthew 5:5 — "The word meek in the Bible does not mean weak (Greek praus = warhorse)"
        return [
            (VEO_DIR / "Charcoal_sketch_of_warhorse_680e0275.mp4", "video_real", 0.0, True, 0.52),
            (VEO_DIR / "Charcoal_sketch_of_warhorse_680e0275.mp4", "video_real", 3.5, True, 0.48),
            (VEO_DIR / "Slow,_dramatic_descending_aerial_fly-through._92dd6274.mp4", "video_sketch", 0.0, True, 0.45),
            (VEO_DIR / "Slow,_dramatic_descending_aerial_fly-through._92dd6274.mp4", "video_real", 3.5, True, 0.45),
            (STILLS_DIR / "Gemini_Generated_Image_sn7ujjsn7ujjsn7u.jpg", "still", 0.0, True, 0.50),
            (VEO_DIR / "Subject_&_Action__A_grove_a44402a8.mp4", "video_real", 0.0, True, 0.50),
            (VEO_DIR / "Continuous_aerial_fly-over_and_dynamic_4e9aad2c.mp4", "video_sketch", 0.0, True, 0.50),
            (VEO_DIR / "Continuous_aerial_fly-over_and_dynamic_4e9aad2c.mp4", "video_real", 3.5, True, 0.50),
            (STILLS_DIR / "Gemini_Generated_Image_83mm8b83mm8b83mm.jpg", "still", 0.0, False, 0.35),
            (VEO_DIR / "Traditional_fine-line_ink_sketch_and_ca5bb9f7.mp4", "video_real", 0.0, True, 0.48),
            (VEO_DIR / "Charcoal_sketch_of_warhorse_680e0275.mp4", "video_real", 6.2, True, 0.50),
        ]

    # Default / fhg_short_001: John 5:39 — "How are you supposed to read the Bible in context?"
    return [
        # Beat 0 (0.0-3.5s): Ink POV walking down ancient tree-lined path on parchment
        (VEO_DIR / "First-person_point-of-view_(POV)_camera_walking_73e58820.mp4", "video_real", 0.0, True, 0.50),
        # Beat 1 (3.5-7.0s): Judean Hillside Fly-Over as Fine-Line Ink Outlines on Parchment (0.0-3.8s)
        (VEO_DIR / "Continuous_aerial_fly-over_and_dynamic_4e9aad2c.mp4", "video_sketch", 0.0, True, 0.48),
        # Beat 2 (7.0-10.5s): Mid-Flight 300ms Luma Dissolve into Photorealistic Judean Hillside Fly-Over (3.5-7.3s)!
        (VEO_DIR / "Continuous_aerial_fly-over_and_dynamic_4e9aad2c.mp4", "video_real", 3.5, True, 0.48),
        # Beat 3 (10.5-14.0s): Animated Ink & Sepia Wash Olive Grove behind stone wall
        (VEO_DIR / "Subject_&_Action__A_grove_a44402a8.mp4", "video_real", 0.0, True, 0.50),
        # Beat 4 (14.0-17.5s): Second Temple Aerial Flight as Fine-Line Ink Outlines on Parchment
        (VEO_DIR / "Camera_flying_toward_Second_Temple_0a20fa4c.mp4", "video_sketch", 0.0, True, 0.50),
        # Beat 5 (17.5-21.0s): Mid-Flight 300ms Luma Dissolve into Photorealistic Second Temple Aerial Flight!
        (VEO_DIR / "Camera_flying_toward_Second_Temple_0a20fa4c.mp4", "video_real", 0.4, True, 0.50),
        # Beat 6 (21.0-24.5s): First-Century Jerusalem Street Tracking Shot
        (VEO_DIR / "Camera_moving_down_Jerusalem_street_d54131af.mp4", "video_real", 0.0, True, 0.50),
        # Beat 7 (24.5-28.0s): Close-up portrait of Jesus ("...testify about Me") with 102%->108% Ken Burns
        (STILLS_DIR / "Gemini_Generated_Image_sn7ujjsn7ujjsn7u.jpg", "still", 0.0, True, 0.50),
        # Beat 8 (28.0-31.5s): Sea of Galilee Aerial Fly-Through as Fine-Line Ink Outlines on Parchment (0.0-3.8s)
        (VEO_DIR / "Slow,_dramatic_descending_aerial_fly-through._92dd6274.mp4", "video_sketch", 0.0, True, 0.45),
        # Beat 9 (31.5-35.0s): Mid-Flight 300ms Luma Dissolve into Photorealistic Sea of Galilee Fly-Through (3.5-7.3s)!
        (VEO_DIR / "Slow,_dramatic_descending_aerial_fly-through._92dd6274.mp4", "video_real", 3.5, True, 0.45),
        # Beat 10 (35.0-38.5s): Animated Ink-Wash Saddled Donkey walking across Judean desert on parchment
        (VEO_DIR / "Subject_&_Action__A_saddled_d901030a.mp4", "video_real", 0.0, True, 0.50),
        # Beat 11 (38.5-39.8s): Sepia Ink-Wash Partridge in flight bridging seamlessly back to Beat 0!
        (VEO_DIR / "A_sepia_watercolor_and_ink_24a6bd59.mp4", "video_real", 0.0, True, 0.50),
    ]


def build_visual_track_with_luma_dissolves(short_id: str, total_dur: float, work_dir: Path) -> tuple[Path, list[float]]:
    """Build 3.5s beat sequence with 300ms Luma Dissolves and Mid-Flight Sketch-to-Real transitions."""
    beat_step = 3.5
    xfade_dur = 0.30
    num_beats = int(total_dur // beat_step) + 1
    single_clip_dur = beat_step + xfade_dur

    sequence_blueprint = get_sequence_for_short(short_id)

    beat_clips: list[Path] = []
    for i in range(num_beats):
        asset, mode, start_s, z_in, cx = sequence_blueprint[i % len(sequence_blueprint)]
        clip_p = work_dir / f"beat_v2_{i:02d}.mp4"
        if not clip_p.exists() or clip_p.stat().st_size == 0:
            prepare_beat_clip(
                asset_path=asset,
                mode=mode,
                beat_dur=single_clip_dur,
                out_clip=clip_p,
                start_sec=start_s,
                zoom_in=z_in,
                crop_x_ratio=cx,
            )
        beat_clips.append(clip_p)

    inputs_cmd: list[str] = []
    for p in beat_clips:
        inputs_cmd.extend(["-i", str(p)])

    filter_parts: list[str] = []
    cut_timestamps: list[float] = []
    prev_label = "[0:v]"
    for i in range(1, len(beat_clips)):
        offset = round(i * beat_step, 3)
        cut_timestamps.append(offset)
        out_label = f"[vx{i}]" if i < len(beat_clips) - 1 else "[v_chained]"
        filter_parts.append(
            f"{prev_label}[{i}:v]xfade=transition=fadegrays:duration={xfade_dur:.3f}:offset={offset:.3f}{out_label}"
        )
        prev_label = out_label

    raw_visual = work_dir / "visual_chained_v2.mp4"
    if not raw_visual.exists() or raw_visual.stat().st_size == 0:
        subprocess.run(
            [
                "ffmpeg", "-y",
                *inputs_cmd,
                "-filter_complex", ";".join(filter_parts),
                "-map", "[v_chained]",
                "-t", f"{total_dur:.3f}",
                "-r", "60", "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p",
                str(raw_visual),
            ],
            check=True,
            capture_output=True,
        )
    return raw_visual, cut_timestamps


def mix_psychoacoustic_master(
    vo_wav: Path,
    pad_wav: Path,
    cut_timestamps: list[float],
    total_dur: float,
    work_dir: Path,
) -> Path:
    """Mix VO + 432Hz Pad (-4dB 300Hz-3kHz EQ carve + sidechaincompress) + 3.5s Micro-Foley -> -14 LUFS."""
    foley_cycle = [
        FOLEY_DIR / "parchment_turn.wav",
        FOLEY_DIR / "felt_piano.wav",
        FOLEY_DIR / "leather_close.wav",
        FOLEY_DIR / "desert_wind.wav",
    ]
    inputs = ["-i", str(vo_wav), "-i", str(pad_wav)]
    filter_lines = [
        "[0:a]asplit=2[vo_sc][vo_main]",
        "[1:a]equalizer=f=1000:t=h:w=2700:g=-4,volume=-14dB[pad_eq]",
        "[pad_eq][vo_sc]sidechaincompress=threshold=0.03:ratio=6:attack=10:release=280[pad_ducked]",
    ]
    mix_labels = ["[vo_main]", "[pad_ducked]"]

    for idx, ts in enumerate(cut_timestamps):
        if ts >= total_dur - 0.4:
            continue
        f_wav = foley_cycle[idx % len(foley_cycle)]
        in_idx = idx + 2
        inputs.extend(["-i", str(f_wav)])
        delay_ms = int(round(ts * 1000))
        lbl = f"[fl{idx}]"
        filter_lines.append(f"[{in_idx}:a]volume=-15dB,adelay={delay_ms}|{delay_ms}{lbl}")
        mix_labels.append(lbl)

    n_mix = len(mix_labels)
    filter_lines.append(
        f"{''.join(mix_labels)}amix=inputs={n_mix}:duration=first:dropout_transition=0:normalize=0[pre_lufs]"
    )
    filter_lines.append("[pre_lufs]loudnorm=I=-14.0:TP=-1.0:LRA=11.0[a_master]")

    master_wav = work_dir / "audio_master_14lufs.wav"
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


async def render_short_from_spec(short_spec: dict) -> Path:
    short_id = short_spec["short_id"]
    short_work = WORK_DIR / short_id
    short_work.mkdir(parents=True, exist_ok=True)
    STORYBOARDS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_REELS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[1/4] Synthesizing VO + Word Boundaries + 250ms Scripture Reverence Pause for {short_id}...")
    vo_wav, words, total_dur = await build_voiceover_and_timestamps(short_spec, short_work)
    print(f"      -> Voiceover duration: {total_dur:.2f}s ({len(words)} words, {len(words)/(total_dur/60.0):.1f} WPM)")

    ass_path = STORYBOARDS_DIR / f"{short_id}.ass"
    print(f"[2/4] Generating Optical Safe-Zone .ass Captions (X=468, Y=1080<=1100) -> {ass_path.name}...")
    write_fhg_ass_captions(words, ass_path)

    print(f"[3/4] Rendering 60fps 3.5s Visual Beats + Mid-Flight Sketch->Real Luma Dissolves...")
    visual_mp4, cut_timestamps = build_visual_track_with_luma_dissolves(short_id, total_dur, short_work)

    print(f"[4/4] Mastering Psychoacoustic Mix (-4dB EQ carve, sidechain duck, {len(cut_timestamps)} Micro-Foley cuts, -14 LUFS)...")
    master_wav = mix_psychoacoustic_master(vo_wav, PAD_WAV, cut_timestamps, total_dur, short_work)

    out_mp4 = OUT_REELS_DIR / f"{short_id}.mp4"
    ass_escaped = ass_path.as_posix().replace(":", "\\:")
    fonts_escaped = FONTS_DIR.as_posix().replace(":", "\\:")

    subprocess.run(
        [
            "ffmpeg", "-y",
            "-i", str(visual_mp4),
            "-i", str(master_wav),
            "-vf", f"ass=filename='{ass_escaped}':fontsdir='{fonts_escaped}'",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-map_metadata", "-1",
            "-metadata", "title=" + short_spec["title"],
            "-metadata", "artist=For His Grace",
            "-metadata", "comment=https://forhisgrace.com",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-pix_fmt", "yuv420p", "-r", "60",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart",
            "-shortest",
            str(out_mp4),
        ],
        check=True,
        capture_output=True,
    )
    print(f"COMPLETE: {out_mp4} ({out_mp4.stat().st_size / (1024*1024):.2f} MB, {total_dur:.2f}s @ 60fps)")
    return out_mp4


async def main() -> None:
    target_id = sys.argv[1] if len(sys.argv) > 1 else "fhg_short_001"
    lines = QUEUE_JSONL.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if not line.strip():
            continue
        spec = json.loads(line)
        if target_id in ("all", spec["short_id"]):
            await render_short_from_spec(spec)


if __name__ == "__main__":
    asyncio.run(main())
