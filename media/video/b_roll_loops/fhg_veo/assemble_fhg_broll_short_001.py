#!/usr/bin/env python3
r"""
Assemble FHG-SHORT-BROLL-001 (in both 9:16 Vertical 1080x1920 and 16:9 Widescreen 1920x1080 @ 60fps)
using the locked BUILD_SPEC_FHG_SHORTS.md pipeline:
1. Vaulted 1080p ZeroCloudDAM tactile macro B-Roll clips (FHG-BR-002, 032, 004, 033, 003, 006, 031).
2. 5-Beat High-Engagement Script with 250ms pre-Scripture reverence pause + pitch drop.
3. Locked Transition Standard:
   - Clip-to-Clip: 0.0s Hard Cut every ~3.5s + 120ms (-0.120s) J-Cut Micro-Foley Audio Pre-Roll ("Secret Weapon").
   - Final Clip -> FHG Fig Tree Parchment Outro: 250ms (0.25s) Warm Dissolve + 120ms Parchment J-Cut + Outro Voiceover.
4. Optical Safe-Zone Captions (X=468, Y=1080 on 9:16; X=960, Y=940 on 16:9), Montserrat Black,
   Warm Ivory (#FFFFF0) base + Gold/Amber (#FFBF00) active word highlight (2-3 words/frame).
5. Mastered to -14.0 LUFS integrated / -1.0 dBTP True Peak.
"""

from __future__ import annotations

import asyncio
import hashlib
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
import edge_tts

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
DAM_BROLL_LIB = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo" / "broll_library"
JESUS_VEO_DIR = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo" / "jesus"
OUT_REELS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "rendered_reels"
WS_VIDEOS_DIR = Path(r"C:\dev\fhg-videos")
FONTS_DIR = PUBLISH_ROOT / "media" / "graphics" / "fonts"
PAD_WAV = PUBLISH_ROOT / "media" / "audio" / "music" / "fhg_432hz_ambient_pad.wav"
FOLEY_DIR = PUBLISH_ROOT / "media" / "audio" / "sfx" / "fhg_foley"
WORK_DIR = PUBLISH_ROOT / "_build" / "video" / "fhg_shorts_engine" / "tmp_work" / "fhg_short_broll_001"

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
                await asyncio.sleep(0.25)
                return words
        except Exception as exc:
            print(f"      [TTS retry {attempt + 1}/4]: {exc}")
            await asyncio.sleep(0.8 * (attempt + 1))
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


def build_hard_cut_visual_plus_outro(
    clip_specs: list[tuple[Path, float]],
    body_dur: float,
    outro_plate: Path,
    outro_dur: float,
    width: int,
    height: int,
    work_dir: Path,
    tag: str,
) -> tuple[Path, list[float]]:
    """
    1. Cuts each B-roll beat to ~3.4s using 0.0s HARD CUTS (zero dissolve lag between B-roll clips!).
    2. Transitions from the final B-roll clip into the Fig Tree Parchment Outro using a crisp 250ms (0.25s) warm dissolve.
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
        # Add 0.25s overlap to the very last beat so the 250ms dissolve into the Outro doesn't shorten body_dur
        is_last = (i == num_beats - 1) or (remaining <= beat_step + 0.3)
        dur = (remaining + 0.25) if is_last else min(beat_step, remaining)

        src_path, start_s = clip_specs[i % len(clip_specs)]
        beat_out = work_dir / f"beat_{tag}_{i:02d}.mp4"
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
        if i > 0:
            cut_timestamps.append(round(accum, 3))
        accum += beat_step
        if is_last:
            break

    # Concat all B-roll beats with 0.0s HARD CUTS
    concat_txt = work_dir / f"beats_{tag}_concat.txt"
    concat_txt.write_text("\n".join(f"file '{p.as_posix()}'" for p in beat_files) + "\n", encoding="utf-8")
    body_mp4 = work_dir / f"body_hardcuts_{tag}.mp4"
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

    # Prepare the Fig Tree Parchment Outro video stream
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

    # Apply the 250ms (0.25s) Warm Dissolve from body_mp4 into outro_v at offset = body_dur
    full_visual = work_dir / f"full_visual_{tag}.mp4"
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
    return full_visual, cut_timestamps


def mix_jcut_audio_with_outro(
    main_vo_wav: Path,
    body_dur: float,
    cut_timestamps: list[float],
    outro_vo_master_wav: Path,
    outro_dur: float,
    work_dir: Path,
) -> Path:
    """
    Mixes:
    - Main body VO + 432Hz Pad (-4dB 300Hz-3kHz EQ carve + sidechaincompress)
    - 120ms (-0.120s) J-Cut Audio Pre-Roll ("Secret Weapon") on every hard cut!
    - 120ms J-Cut of parchment_turn.wav leading into the Fig Tree Parchment Outro voiceover master!
    - Final loudness normalization to -14.0 LUFS / -1.0 dBTP.
    """
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

    # 120ms (-0.120s) J-Cut Audio Pre-Roll on each hard cut
    for idx, cut_ts in enumerate(cut_timestamps):
        jcut_ts = max(0.0, cut_ts - 0.120)
        f_wav = foley_cycle[idx % len(foley_cycle)]
        in_idx = len(inputs) // 2
        inputs.extend(["-i", str(f_wav)])
        delay_ms = int(round(jcut_ts * 1000))
        lbl = f"[jcut_{idx}]"
        filter_lines.append(f"[{in_idx}:a]volume=-14dB,adelay={delay_ms}|{delay_ms}{lbl}")
        mix_labels.append(lbl)

    # 120ms J-Cut of parchment_turn.wav right before Outro dissolve
    parch_in_idx = len(inputs) // 2
    inputs.extend(["-i", str(FOLEY_DIR / "parchment_turn.wav")])
    outro_jcut_ms = int(round(max(0.0, body_dur - 0.120) * 1000))
    filter_lines.append(f"[{parch_in_idx}:a]volume=-13dB,adelay={outro_jcut_ms}|{outro_jcut_ms}[jcut_outro]")
    mix_labels.append("[jcut_outro]")

    # Append Outro Voiceover Master starting at body_dur
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

    # 5-Beat High-Engagement Script anchored to our vaulted tactile macro B-Roll clips:
    segments = [
        {
            "type": "hook",
            "pause_before_ms": 0,
            "text": "Thirty pieces of silver wasn't the price of a king — in first-century Judea, it was the legal compensation for a wounded servant.",
        },
        {
            "type": "context_disruption",
            "pause_before_ms": 120,
            "text": "When those coins hit the stone floor of the temple, the religious elite thought they were pricing Jesus at the lowest tier of human worth.",
        },
        {
            "type": "scripture_reveal",
            "pause_before_ms": 140,
            "text": "Yet long before the cross, the prophet Zechariah wrote,",
        },
        {
            "type": "scripture_quote",
            "pause_before_ms": 250,  # 250ms Reverence Pause + Pitch Drop
            "text": "So they weighed out for my wages thirty pieces of silver.",
        },
        {
            "type": "personal_application",
            "pause_before_ms": 180,
            "text": "Maybe today you feel exhausted, overlooked, or discarded by people who never saw your true worth. Remember this: the Savior who broke bread with the broken chose to be undervalued by the world, so you would know how priceless you are to the Father.",
        },
    ]

    print("[1/4] Synthesizing Main Voiceover + 250ms Pre-Scripture Reverence Pause...")
    main_vo_wav, words, body_dur = await build_main_vo(segments, WORK_DIR)
    outro_vo_wav = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_vo_master_14lufs.wav"
    outro_dur = get_audio_duration(outro_vo_wav)
    print(f"      -> Body VO: {body_dur:.2f}s ({len(words)} words) + Outro VO: {outro_dur:.2f}s = {body_dur + outro_dur:.2f}s total")

    # 9:16 Vertical Clip Sequence (using all 7 vaulted 1080p 9:16 B-roll masters!)
    clips_9x16 = [
        (DAM_BROLL_LIB / "FHG-BR-002_falling-silver-coins_9x16_1080p.mp4", 0.0),         # Beat 0: Falling Silver Coins (Hook)
        (DAM_BROLL_LIB / "FHG-BR-002_falling-silver-coins_9x16_1080p.mp4", 3.6),         # Beat 1: Coins bouncing on dark stone
        (DAM_BROLL_LIB / "FHG-BR-032_sandals-in-cracked-wilderness_9x16_1080p.mp4", 0.0),# Beat 2: Sandals in Cracked Wilderness
        (DAM_BROLL_LIB / "FHG-BR-004_wind-blowing-chaff_9x16_1080p.mp4", 0.0),           # Beat 3: Wind Blowing Chaff
        (DAM_BROLL_LIB / "FHG-BR-033_hauling-fishing-net-rope_9x16_1080p.mp4", 0.0),     # Beat 4: Hauling Fishing Net Rope
        (DAM_BROLL_LIB / "FHG-BR-003_breaking-bread_9x16_1080p.mp4", 0.0),               # Beat 5: Breaking Bread
        (DAM_BROLL_LIB / "FHG-BR-003_breaking-bread_9x16_1080p.mp4", 3.6),               # Beat 6: Breaking Bread (Jesus in bg)
        (DAM_BROLL_LIB / "FHG-BR-006_glowing-embers_9x16_1080p.mp4", 0.0),               # Beat 7: Glowing Embers
        (DAM_BROLL_LIB / "FHG-BR-031_pouring-anointing-oil_9x16_1080p.mp4", 0.0),        # Beat 8: Pouring Anointing Oil
        (DAM_BROLL_LIB / "FHG-BR-031_pouring-anointing-oil_9x16_native_1080p.mp4", 2.0), # Beat 9: Golden Oil Close-up
    ]

    # 16:9 Widescreen Clip Sequence (using vaulted 1080p 16:9 B-roll masters + 16:9 Jesus walk)
    clips_16x9 = [
        (DAM_BROLL_LIB / "FHG-BR-002_falling-silver-coins_16x9_1080p.mp4", 0.0),
        (DAM_BROLL_LIB / "FHG-BR-002_falling-silver-coins_16x9_1080p.mp4", 3.6),
        (DAM_BROLL_LIB / "FHG-BR-032_sandals-in-cracked-wilderness_16x9_1080p.mp4", 0.0),
        (DAM_BROLL_LIB / "FHG-BR-004_wind-blowing-chaff_16x9_1080p.mp4", 0.0),
        (DAM_BROLL_LIB / "FHG-BR-033_hauling-fishing-net-rope_16x9_1080p.mp4", 0.0),
        (JESUS_VEO_DIR / "Medium_shot,_centered_composition._A_6c5c8acc.mp4", 0.0),
        (JESUS_VEO_DIR / "Slow_lateral_tracking_shot_(dolly_1182e743.mp4", 0.0),
        (DAM_BROLL_LIB / "FHG-BR-004_wind-blowing-chaff_16x9_1080p.mp4", 4.0),
        (DAM_BROLL_LIB / "FHG-BR-031_pouring-anointing-oil_16x9_1080p.mp4", 0.0),
        (DAM_BROLL_LIB / "FHG-BR-031_pouring-anointing-oil_16x9_1080p.mp4", 3.5),
    ]

    print("[2/4] Building 0.0s Hard-Cut Visual Timelines + 250ms Warm Dissolve into Fig Tree Parchment Outros...")
    vis_9x16, cuts_9x16 = build_hard_cut_visual_plus_outro(
        clips_9x16,
        body_dur,
        DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_9x16_1080p.jpg",
        outro_dur,
        1080,
        1920,
        WORK_DIR,
        "9x16",
    )
    vis_16x9, _ = build_hard_cut_visual_plus_outro(
        clips_16x9,
        body_dur,
        DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_16x9_1080p.jpg",
        outro_dur,
        1920,
        1080,
        WORK_DIR,
        "16x9",
    )

    print(f"[3/4] Mixing Psychoacoustic Master with {len(cuts_9x16)} x 120ms J-Cut Audio Pre-Rolls + Outro VO (-14 LUFS)...")
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
        print(f"COMPLETE ({aspect}): {out_dam} ({out_dam.stat().st_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    asyncio.run(main())
