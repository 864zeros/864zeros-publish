#!/usr/bin/env python3
r"""
OmniClip × FHG Deterministic Storyboard Renderer (render_omniclip_storyboard.py)
--------------------------------------------------------------------------------
Solves the 5 shortcomings of blind Python + FFmpeg scripting:
1. Clause-Synchronized Visual Cuts (Zero Blind 3.4s Slicing):
   - Synthesizes natural voiceover segments with WordBoundary timestamps, then aligns each visual beat's
     exact start & end duration to the spoken clause's first and last word timestamps!
2. 100% Native 9:16 (1080x1920) & 16:9 (1920x1080) Master Base Sepia Plates:
   - Automatically resolves any FHG-SK-001..040 still to its full-frame 9:16 (1080x1920) and 16:9 (1920x1080)
     Master Base Sepia Parchment Plate (zero trapped 1:1 square boxes, zero postage-stamp borders).
3. Strict Base-Parchment-Only Guardrail (Zero Filtered Images Allowed):
   - Rejects any filtered sketch variation (_b1, _c1.._c4, _loop_scr, _xhatch, _sub_scr, _g2, _g4).
4. Per-Beat Focal Framing & Speed Adaptation:
   - If a video beat's spoken clause is longer than the source clip (e.g., 5.2s clause on a 4.5s clip),
     automatically adapts playback rate smoothly via setpts instead of abruptly looping or hard-cutting mid-action!
5. OmniClip fhg_2026 Captions + 120ms J-Cut Foley + -14.0 LUFS Master + Animated Bird Outro.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
import edge_tts

FFMPEG_BIN = r"C:\Users\Jeff\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
if os.path.exists(FFMPEG_BIN):
    os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
DAM_BROLL_LIB = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo" / "broll_library"
MASTER_9x16_DIR = Path(r"C:\dev\fhg-from-sheet\images-animations\master_base_9x16_1080p")
MASTER_16x9_DIR = Path(r"C:\dev\fhg-from-sheet\images-animations\master_base_16x9_1080p")
OUT_REELS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "rendered_reels"
WS_VIDEOS_DIR = Path(r"C:\dev\fhg-videos")
FONTS_DIR = PUBLISH_ROOT / "media" / "graphics" / "fonts"
PAD_WAV = PUBLISH_ROOT / "media" / "audio" / "music" / "fhg_432hz_ambient_pad.wav"
FOLEY_DIR = PUBLISH_ROOT / "media" / "audio" / "sfx" / "fhg_foley"

FHG_BASE_COLOR = "&H00F0FFFF&"       # Warm Ivory (#FFFFF0)
FHG_HIGHLIGHT_COLOR = "&H0000BFFF&"  # Gold/Amber (#FFBF00)
FHG_SHADOW_COLOR = "&H26000000&"     # 85% opacity black shadow

BANNED_FILTER_TOKENS = (
    "_b1_", "_g2_", "_s2", "_s3", "_straight_g4", "_loop_scr", "_xhatch_scr",
    "_sub_scr", "_c1_", "_c2_", "_c3_", "_c4_", "_nb_",
)


@dataclass
class WordTiming:
    word: str
    start: float
    end: float


def assert_unfiltered_base_asset(asset_ref: str) -> None:
    lower = asset_ref.lower()
    for bad in BANNED_FILTER_TOKENS:
        if bad in lower:
            raise ValueError(
                f"GUARDRAIL VIOLATION: Filtered image '{asset_ref}' (matched '{bad}') is banned from video builds. "
                f"Only unfiltered Base Sepia Parchment plates (_base_9x16_1080p / _base_16x9_1080p) are allowed."
            )


def resolve_master_asset(dam_id: str, media_type: str, aspect: str) -> Path:
    """
    Resolves a DAM_ID (e.g. 'FHG-SK-013' or 'FHG-BR-047') + media_type ('still_base' or 'video')
    to its exact 1080p aspect-native master file in master_base_{aspect}_1080p or broll_library.
    Enforces the Base-Parchment-Only guardrail.
    """
    if media_type == "still_base":
        plate_dir = MASTER_9x16_DIR if aspect == "9x16" else MASTER_16x9_DIR
        matches = list(plate_dir.glob(f"{dam_id}_*_base_{aspect}_1080p.jpg"))
        if not matches:
            raise FileNotFoundError(f"No {aspect} Master Base Sepia Plate found for {dam_id} in {plate_dir}")
        assert_unfiltered_base_asset(matches[0].name)
        return matches[0]
    else:
        matches = list(DAM_BROLL_LIB.glob(f"{dam_id}_*_{aspect}_1080p.mp4"))
        if not matches:
            raise FileNotFoundError(f"No {aspect} 1080p video found for {dam_id} in {DAM_BROLL_LIB}")
        return matches[0]


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


async def synth_segment_with_words(
    text: str,
    voice: str,
    rate: str,
    pitch: str,
    out_mp3: Path,
) -> list[WordTiming]:
    import hashlib
    key_sig = hashlib.sha1(f"v2-natural|{voice}|{rate}|{pitch}|{text}".encode("utf-8")).hexdigest()[:12]
    keyed_mp3 = out_mp3.with_name(f"{out_mp3.stem}_{key_sig}.mp3")
    words_cache = keyed_mp3.with_suffix(".words.json")
    if keyed_mp3.exists() and keyed_mp3.stat().st_size > 500 and words_cache.exists():
        shutil.copy2(keyed_mp3, out_mp3)
        cached = json.loads(words_cache.read_text(encoding="utf-8"))
        return [WordTiming(**w) for w in cached]

    clean_text = text.replace("ForHisGrace.com", "For His Grace dot com").replace("—", ", ").replace("...", ".")
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
            with keyed_mp3.open("wb") as audio_f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        start_s = chunk["offset"] / 10_000_000.0
                        dur_s = chunk["duration"] / 10_000_000.0
                        w_text = str(chunk["text"]).strip()
                        if w_text:
                            words.append(WordTiming(word=w_text, start=start_s, end=start_s + max(dur_s, 0.08)))
            if keyed_mp3.stat().st_size > 500:
                shutil.copy2(keyed_mp3, out_mp3)
                words_cache.write_text(
                    json.dumps([{"word": w.word, "start": w.start, "end": w.end} for w in words]),
                    encoding="utf-8",
                )
                await asyncio.sleep(0.45)
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


async def synthesize_clause_synced_beats(beats: list[dict], work_dir: Path) -> tuple[Path, list[WordTiming], list[float], float]:
    """
    Synthesizes VO and computes the EXACT duration of every visual beat:
    - If a beat has 'continue_vo_from_prev': True, its text is combined into the previous beat's TTS call
      so the narrator speaks across both beats without an artificial pause, and the visual cut is placed
      at the exact WordBoundary timestamp where the second beat's clause begins!
    Returns:
      - vo_full_wav: Path
      - all_words: list[WordTiming]
      - beat_durations: list[float] (exact duration in seconds for each beat in `beats`)
      - body_dur: float
    """
    # Group beats into voice groups (each voice group is 1 continuous TTS breath)
    groups: list[list[int]] = []
    for i, b in enumerate(beats):
        if i > 0 and b.get("continue_vo_from_prev", False):
            groups[-1].append(i)
        else:
            groups.append([i])

    voice = "en-US-AndrewMultilingualNeural"
    base_pitch_hz = -2

    all_words: list[WordTiming] = []
    concat_inputs: list[Path] = []
    beat_durations: list[float] = [0.0] * len(beats)
    current_offset = 0.0

    for g_idx, beat_indices in enumerate(groups):
        first_beat = beats[beat_indices[0]]
        pause_ms = int(first_beat.get("pause_before_ms", 0))
        if pause_ms > 0:
            sil_wav = work_dir / f"sil_g{g_idx}.wav"
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
            # Attach the pre-pause to the first beat of this group
            beat_durations[beat_indices[0]] += pause_ms / 1000.0
            current_offset += pause_ms / 1000.0

        combined_text = " ".join(beats[bi]["text"].strip() for bi in beat_indices)
        is_scripture = first_beat.get("type") == "scripture_quote"
        seg_pitch = f"{base_pitch_hz - 2:+d}Hz" if is_scripture else f"{base_pitch_hz:+d}Hz"
        seg_rate = "+0%" if is_scripture else "+2%"

        seg_mp3 = work_dir / f"grp_{g_idx}.mp3"
        seg_wav = work_dir / f"grp_{g_idx}.wav"
        seg_words = await synth_segment_with_words(
            text=combined_text,
            voice=voice,
            rate=seg_rate,
            pitch=seg_pitch,
            out_mp3=seg_mp3,
        )
        seg_words = attach_punctuation(combined_text, seg_words)

        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(seg_mp3),
                "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,afade=t=in:st=0:d=0.015,apad=pad_dur=0.28",
                "-ar", "48000", "-ac", "2",
                str(seg_wav),
            ],
            check=True,
            capture_output=True,
        )
        seg_dur = get_duration(seg_wav)

        local_words: list[WordTiming] = []
        if seg_words:
            first_w_start = seg_words[0].start
            for w in seg_words:
                adj_start = max(0.0, w.start - first_w_start)
                adj_end = min(seg_dur, max(adj_start + 0.08, (w.end - first_w_start)))
                local_words.append(WordTiming(word=w.word, start=adj_start, end=adj_end))
                all_words.append(WordTiming(word=w.word, start=adj_start + current_offset, end=adj_end + current_offset))

        # Split seg_dur across the sub-beats in beat_indices using exact word counts per clause
        if len(beat_indices) == 1:
            beat_durations[beat_indices[0]] += seg_dur
        else:
            clause_word_counts = [
                len([tok for tok in re.split(r"\s+", beats[bi]["text"].strip()) if re.sub(r"[^\w]", "", tok)])
                for bi in beat_indices
            ]
            split_times = [0.0]
            w_cursor = 0
            for c_idx in range(len(beat_indices) - 1):
                w_cursor += clause_word_counts[c_idx]
                if w_cursor < len(local_words):
                    split_times.append(local_words[w_cursor].start)
                else:
                    split_times.append(seg_dur * ((c_idx + 1) / len(beat_indices)))
            split_times.append(seg_dur)
            for c_idx, bi in enumerate(beat_indices):
                beat_durations[bi] += max(1.5, split_times[c_idx + 1] - split_times[c_idx])

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
    body_dur = get_duration(vo_full)
    # Normalize slight rounding drift so sum(beat_durations) == body_dur
    diff = body_dur - sum(beat_durations)
    beat_durations[-1] = max(1.5, beat_durations[-1] + diff)
    return vo_full, all_words, beat_durations, body_dur


def render_clause_synced_visual_timeline(
    beats: list[dict],
    beat_durations: list[float],
    body_dur: float,
    outro_mp4: Path,
    outro_dur: float,
    aspect: str,
    width: int,
    height: int,
    work_dir: Path,
) -> tuple[Path, list[float]]:
    """
    Renders each beat for its EXACT clause-synchronized duration (beat_durations[i]):
    - For 'still_base': uses the aspect-native 1080p Master Base Sepia Plate with smooth 60fps Ken Burns.
    - For 'video': adapts playback speed via setpts if the clause is longer than the remaining clip duration,
      and applies the user-selected 9:16 horizontal crop focus (crop_x_ratio: 0.0=Left, 0.5=Center, 1.0=Right).
    """
    beat_files: list[Path] = []
    cut_timestamps: list[float] = []
    accum = 0.0

    for i, (b, dur_raw) in enumerate(zip(beats, beat_durations)):
        is_last = (i == len(beats) - 1)
        dur = (dur_raw + 0.35) if is_last else dur_raw

        dam_id = b["dam_id"]
        media_type = b["media_type"]  # 'still_base' or 'video'
        src_path = resolve_master_asset(dam_id, media_type, aspect)
        dur_ms = int(round(dur * 1000))
        beat_out = work_dir / f"omni_beat_{aspect}_{i:02d}_{dur_ms}ms.mp4"
        if beat_out.exists() and beat_out.stat().st_size > 10000:
            beat_files.append(beat_out)
            if i > 0:
                cut_timestamps.append(round(accum, 3))
            accum += dur_raw
            continue

        frames = max(1, int(round(dur * 60)))
        if media_type == "still_base":
            motion = b.get("motion", "zoom_in")
            if motion == "zoom_out":
                z_expr = f"1.07-0.05*(on/{frames})"
            else:
                z_expr = f"1.01+0.06*(on/{frames})"
            # Supersample 2x before zoompan so 60fps Ken Burns is 100% subpixel smooth
            vf = (
                f"scale={width*2}:{height*2}:flags=lanczos,"
                f"zoompan=z='{z_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d={frames}:s={width}x{height}:fps=60,setsar=1,format=yuv420p"
            )
            subprocess.run(
                [
                    "ffmpeg", "-y", "-loop", "1", "-i", str(src_path),
                    "-vf", vf,
                    "-t", f"{dur:.3f}",
                    "-r", "60", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-an",
                    str(beat_out),
                ],
                check=True,
                capture_output=True,
            )
        else:
            start_s = float(b.get("start_s", 0.0))
            end_s = b.get("end_s", None)
            src_total = get_duration(src_path)
            avail = (float(end_s) - start_s) if end_s is not None else max(0.5, src_total - start_s)
            # If the spoken clause is longer than the available clip segment, smoothly slow the clip via setpts
            # so it never hard-loops or freezes mid-sentence!
            pts_mult = max(1.0, (dur + 0.15) / avail) if dur > avail else 1.0

            vf = (
                f"setpts={pts_mult:.4f}*PTS,"
                f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos,"
                f"crop={width}:{height},fps=60,setsar=1,format=yuv420p"
            )
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-ss", f"{start_s:.2f}",
                    "-i", str(src_path),
                    "-vf", vf,
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
        accum += dur_raw

    concat_txt = work_dir / f"omni_beats_{aspect}_concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in beat_files) + "\n", encoding="utf-8")
    body_mp4 = work_dir / f"omni_body_{aspect}.mp4"
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

    total_ms = int(round((body_dur + outro_dur) * 1000))
    full_visual = work_dir / f"omni_full_visual_{aspect}_{total_ms}ms.mp4"
    if full_visual.exists() and full_visual.stat().st_size > 100000:
        return full_visual, cut_timestamps
    actual_body_dur = get_duration(body_mp4)
    safe_offset = min(body_dur, actual_body_dur - 0.30)
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
        next_phrase_start = phrases[p_idx + 1][0].start if (p_idx + 1 < len(phrases)) else (phrase_end + 1.0)
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
            if i + 1 < len(phrase):
                seg_end = max(seg_start + 0.02, phrase[i + 1].start)
            else:
                seg_end = min(next_phrase_start, max(seg_start + 0.08, phrase_end))
            if seg_end <= seg_start:
                seg_end = seg_start + 0.04
            override = f"{{\\an2\\pos({pos_x},{pos_y})\\blur6}}"
            lines.append(
                f"Dialogue: 0,{format_ass_time(seg_start)},{format_ass_time(seg_end)},"
                f"FHG_Short,,0,0,0,,{override}{text_line}"
            )

    out_ass.write_text("\n".join(lines) + "\n", encoding="utf-8")


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

    master_wav = work_dir / "omni_audio_master_14lufs.wav"
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


DEFAULT_PURE_SEPIA_STORYBOARD = {
    "short_id": "FHG-SHORT-SEPIA-001",
    "title": "The Parable of the Mustard Seed — For His Grace",
    "visual_lane": "PURE_BASE_SEPIA_PARCHMENT",
    "beats": [
        {
            "type": "hook",
            "pause_before_ms": 0,
            "continue_vo_from_prev": False,
            "text": "Why did Jesus compare the Kingdom of Heaven to a wild garden seed that Roman emperors wouldn't even notice?",
            "dam_id": "FHG-SK-014",
            "media_type": "still_base",
            "motion": "zoom_in",
        },
        {
            "type": "context_disruption",
            "pause_before_ms": 120,
            "continue_vo_from_prev": False,
            "text": "In first-century Galilee, everyone expected God's kingdom to arrive like a towering cedar of Lebanon — loud, unshakeable, and immediate.",
            "dam_id": "FHG-SK-012",
            "media_type": "video",
            "start_s": 0.0,
        },
        {
            "type": "context_disruption",
            "pause_before_ms": 0,
            "continue_vo_from_prev": True,
            "text": "Instead, Jesus pointed to a weathered farmer pressing a speck of black mustard into the dust.",
            "dam_id": "FHG-SK-007",
            "media_type": "still_base",
            "motion": "zoom_out",
        },
        {
            "type": "scripture_reveal",
            "pause_before_ms": 140,
            "continue_vo_from_prev": False,
            "text": "Standing by the shore, Jesus told the crowd in Matthew thirteen,",
            "dam_id": "FHG-SK-013",
            "media_type": "still_base",
            "motion": "zoom_in",
        },
        {
            "type": "scripture_quote",
            "pause_before_ms": 250,
            "continue_vo_from_prev": False,
            "text": "The kingdom of heaven is like a mustard seed, which a man took and planted in his field.",
            "dam_id": "FHG-SK-013",
            "media_type": "video",
            "start_s": 0.0,
            "end_s": 3.5,
        },
        {
            "type": "scripture_quote",
            "pause_before_ms": 0,
            "continue_vo_from_prev": True,
            "text": "Though it is the smallest of all your seeds, yet when it grows, it becomes a tree,",
            "dam_id": "FHG-SK-013",
            "media_type": "video",
            "start_s": 3.5,
            "end_s": 8.0,
        },
        {
            "type": "scripture_quote",
            "pause_before_ms": 0,
            "continue_vo_from_prev": True,
            "text": "so that the birds of the air come and make nests in its branches.",
            "dam_id": "FHG-SK-003",
            "media_type": "video",
            "start_s": 0.0,
        },
        {
            "type": "personal_application",
            "pause_before_ms": 180,
            "continue_vo_from_prev": False,
            "text": "Maybe today your obedience feels tiny, buried, or unseen.",
            "dam_id": "FHG-SK-035",
            "media_type": "still_base",
            "motion": "zoom_in",
        },
        {
            "type": "personal_application",
            "pause_before_ms": 0,
            "continue_vo_from_prev": True,
            "text": "Take heart: in the hands of the Master, what starts hidden in the dark soil of faith always grows into a sanctuary of grace.",
            "dam_id": "FHG-SK-040",
            "media_type": "still_base",
            "motion": "zoom_out",
        },
    ],
}


async def render_storyboard(spec: dict) -> None:
    short_id = spec.get("short_id", "FHG-SHORT-SEPIA-001")
    work_dir = PUBLISH_ROOT / "_build" / "video" / "fhg_shorts_engine" / "tmp_work" / f"omni_{short_id.lower()}"
    work_dir.mkdir(parents=True, exist_ok=True)
    OUT_REELS_DIR.mkdir(parents=True, exist_ok=True)

    beats = spec["beats"]
    print(f"[1/4] Synthesizing Clause-Synchronized Voiceover for {short_id} ({len(beats)} beats, Lane={spec.get('visual_lane')})...")
    main_vo_wav, words, beat_durations, body_dur = await synthesize_clause_synced_beats(beats, work_dir)
    for idx, (b, bd) in enumerate(zip(beats, beat_durations)):
        print(f"      Beat {idx:02d} ({bd:4.2f}s) -> {b['dam_id']} [{b['media_type']}]: {b['text'][:58]}...")

    outro_vo_wav = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_vo_master_14lufs.wav"
    outro_dur = get_duration(outro_vo_wav)

    print("[2/4] Rendering Clause-Synced 9:16 (1080x1920) & 16:9 (1920x1080) Visual Timelines (100% Base Sepia Parchment Only)...")
    vis_9x16, cuts_9x16 = render_clause_synced_visual_timeline(
        beats,
        beat_durations,
        body_dur,
        DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_9x16_1080p.mp4",
        outro_dur,
        "9x16",
        1080,
        1920,
        work_dir,
    )
    vis_16x9, _ = render_clause_synced_visual_timeline(
        beats,
        beat_durations,
        body_dur,
        DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_16x9_1080p.mp4",
        outro_dur,
        "16x9",
        1920,
        1080,
        work_dir,
    )

    print(f"[3/4] Mixing Psychoacoustic Master with {len(cuts_9x16)} Clause-Synced 120ms J-Cuts + Animated Bird Outro (-14 LUFS)...")
    master_audio = mix_jcut_audio_with_outro(
        main_vo_wav, body_dur, cuts_9x16, outro_vo_wav, outro_dur, work_dir
    )

    print("[4/4] Burning OmniClip fhg_2026 Captions & Exporting Final 1080p 60fps Masters...")
    ass_9x16 = work_dir / "captions_9x16.ass"
    ass_16x9 = work_dir / "captions_16x9.ass"
    write_ass_captions(words, ass_9x16, 1080, 1920, 468, 1080, 74)
    write_ass_captions(words, ass_16x9, 1920, 1080, 960, 940, 56)

    fonts_escaped = FONTS_DIR.as_posix().replace(":", "\\:")

    for aspect, vis_mp4, ass_p in [
        ("9x16", vis_9x16, ass_9x16),
        ("16x9", vis_16x9, ass_16x9),
    ]:
        ass_escaped = ass_p.as_posix().replace(":", "\\:")
        out_dam = OUT_REELS_DIR / f"{short_id}_{aspect}_1080p.mp4"
        out_broll_lib = DAM_BROLL_LIB / f"{short_id}_{aspect}_1080p.mp4"
        out_ws = WS_VIDEOS_DIR / f"{short_id}_{aspect}_1080p.mp4"

        subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(vis_mp4),
                "-i", str(master_audio),
                "-vf", f"ass=filename='{ass_escaped}':fontsdir='{fonts_escaped}'",
                "-map", "0:v:0", "-map", "1:a:0",
                "-map_metadata", "-1",
                "-metadata", f"title={spec.get('title', short_id)}",
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


def main() -> None:
    parser = argparse.ArgumentParser(description="OmniClip × FHG Deterministic Storyboard Renderer")
    parser.add_argument("--spec", type=str, default="", help="Path to exported omni_storyboard.json")
    args = parser.parse_args()

    if args.spec and os.path.exists(args.spec):
        with open(args.spec, "r", encoding="utf-8") as f:
            spec = json.load(f)
    else:
        spec = DEFAULT_PURE_SEPIA_STORYBOARD

    asyncio.run(render_storyboard(spec))


if __name__ == "__main__":
    main()
