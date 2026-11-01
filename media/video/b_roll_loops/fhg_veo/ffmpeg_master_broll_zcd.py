#!/usr/bin/env python3
"""
FFmpeg 1080p Multi-Aspect Production Mastering Pipeline for FHG Biblical B-Roll
===============================================================================
Rule Compliance:
- RULE-002: Never overwrite raw media files. Raw Flow renders remain untouched.
- Produces 1080p production masters across channel aspect ratios in ZeroCloudDAM:
  1. 16:9 Widescreen Master (1920x1080) -> YouTube Long-Form, Web Sanctuary, TV
  2. 9:16 Vertical Master   (1080x1920) -> YouTube Shorts, Reels, TikTok (center-cropped from 16:9 or mastered from native 9:16)
  3. 1:1  Square Master     (1080x1080) -> Instagram/FB/X/Community Feed (center-cropped)
- Applies verified QA frame trims:
  * FHG-BR-004 (Wind Blowing Chaff): 0.0s -> 8.5s (removes 8.6s hard cut)
  * FHG-BR-033 (Hauling Fishing Net Rope): 0.0s -> 5.5s (removes 6.0s-8.5s two-hand finger morph)
"""

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

DAM_ROOT = Path(r"C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo")
BROLL_LIB = DAM_ROOT / "broll_library"
CATALOG_JSON = DAM_ROOT / "FHG_BROLL_DAM_CATALOG.json"
CATALOG_CSV_DAM = DAM_ROOT / "FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv"
CATALOG_CSV_WS = Path(r"C:\dev\fhg-videos\FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv")

# QA Trim rules per broll_id (start_sec, end_sec)
QA_TRIMS = {
    "FHG-BR-004": (0.0, 8.5),  # Clean continuous wheat/chaff wind shot before 8.6s cut
    "FHG-BR-033": (0.0, 5.5),  # Clean single-hand rope haul + underwater net before 6.0s hand morph
}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def run_ffmpeg(cmd: list[str]) -> None:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed:\n{' '.join(cmd)}\n{res.stderr}")


def probe_video(path: Path) -> dict:
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-of", "json",
        str(path),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data = json.loads(res.stdout)
    stream = data["streams"][0]
    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "duration_s": round(float(stream.get("duration", 0.0)), 2),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def build_trim_args(broll_id: str) -> list[str]:
    if broll_id in QA_TRIMS:
        start, end = QA_TRIMS[broll_id]
        return ["-ss", str(start), "-to", str(end)]
    return []


def master_16x9_to_all_channels(broll_id: str, slug: str, src_16x9: Path) -> dict:
    out_16x9 = BROLL_LIB / f"{broll_id}_{slug}_16x9_1080p.mp4"
    out_9x16 = BROLL_LIB / f"{broll_id}_{slug}_9x16_1080p.mp4"
    out_1x1 = BROLL_LIB / f"{broll_id}_{slug}_1x1_1080p.mp4"

    trim_args = build_trim_args(broll_id)

    # 1. 16:9 1080p Master (1920x1080 Lanczos + subtle cinema sharpen)
    if not out_16x9.exists():
        cmd_16x9 = [
            "ffmpeg", "-y",
            *trim_args,
            "-i", str(src_16x9),
            "-vf", "scale=1920:1080:flags=lanczos,unsharp=3:3:0.45:3:3:0.0",
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_16x9),
        ]
        run_ffmpeg(cmd_16x9)

    # 2. 9:16 1080p Vertical Master (1080x1920 dead-center crop from 16:9)
    if not out_9x16.exists():
        cmd_9x16 = [
            "ffmpeg", "-y",
            *trim_args,
            "-i", str(src_16x9),
            "-vf", "crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920:flags=lanczos,unsharp=3:3:0.5:3:3:0.0",
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_9x16),
        ]
        run_ffmpeg(cmd_9x16)

    # 3. 1:1 1080p Square Master (1080x1080 dead-center crop from 16:9)
    if not out_1x1.exists():
        cmd_1x1 = [
            "ffmpeg", "-y",
            *trim_args,
            "-i", str(src_16x9),
            "-vf", "crop=ih:ih:(iw-ow)/2:0,scale=1080:1080:flags=lanczos,unsharp=3:3:0.45:3:3:0.0",
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_1x1),
        ]
        run_ffmpeg(cmd_1x1)

    return {
        "master_16x9_1080p": out_16x9.name,
        "vertical_9x16_1080p": out_9x16.name,
        "square_1x1_1080p": out_1x1.name,
        "probe_16x9": probe_video(out_16x9),
        "probe_9x16": probe_video(out_9x16),
        "probe_1x1": probe_video(out_1x1),
    }


def master_native_9x16_to_channels(broll_id: str, slug: str, src_9x16: Path) -> dict:
    out_9x16 = BROLL_LIB / f"{broll_id}_{slug}_9x16_1080p.mp4"
    out_1x1 = BROLL_LIB / f"{broll_id}_{slug}_1x1_1080p.mp4"

    trim_args = build_trim_args(broll_id)

    if not out_9x16.exists():
        cmd_9x16 = [
            "ffmpeg", "-y",
            *trim_args,
            "-i", str(src_9x16),
            "-vf", "scale=1080:1920:flags=lanczos,unsharp=3:3:0.45:3:3:0.0",
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_9x16),
        ]
        run_ffmpeg(cmd_9x16)

    if not out_1x1.exists():
        cmd_1x1 = [
            "ffmpeg", "-y",
            *trim_args,
            "-i", str(src_9x16),
            "-vf", "crop=iw:iw:0:(ih-oh)/2,scale=1080:1080:flags=lanczos,unsharp=3:3:0.45:3:3:0.0",
            "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
            "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            str(out_1x1),
        ]
        run_ffmpeg(cmd_1x1)

    return {
        "master_16x9_1080p": "",
        "vertical_9x16_1080p": out_9x16.name,
        "square_1x1_1080p": out_1x1.name,
        "probe_9x16": probe_video(out_9x16),
        "probe_1x1": probe_video(out_1x1),
    }


def main():
    catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    results_summary = []

    for item in catalog["items"]:
        broll_id = item["broll_id"]
        slug = slugify(item["title"])
        assets = item.get("dam_assets", [])

        src_16x9_asset = next((a for a in assets if "16:9" in a.get("aspect_ratio", "")), None)
        src_9x16_asset = next((a for a in assets if "9:16" in a.get("aspect_ratio", "")), None)

        if src_16x9_asset:
            src_path = BROLL_LIB / src_16x9_asset["dam_filename"]
            print(f"[FFMPEG] Mastering 16:9 -> 1080p (16:9, 9:16, 1:1) for {broll_id} ({item['title']})...")
            out_info = master_16x9_to_all_channels(broll_id, slug, src_path)
            item["dam_master_16x9_1080p"] = out_info["master_16x9_1080p"]
            item["dam_vertical_9x16_1080p"] = out_info["vertical_9x16_1080p"]
            item["dam_square_1x1_1080p"] = out_info["square_1x1_1080p"]
            item["status"] = "MASTERED_1080P_ALL_CHANNELS"
            item["channel_masters_1080p"] = out_info

            if src_9x16_asset:
                native_9x16_out = BROLL_LIB / f"{broll_id}_{slug}_9x16_native_1080p.mp4"
                if not native_9x16_out.exists():
                    run_ffmpeg([
                        "ffmpeg", "-y",
                        "-i", str(BROLL_LIB / src_9x16_asset["dam_filename"]),
                        "-vf", "scale=1080:1920:flags=lanczos,unsharp=3:3:0.45:3:3:0.0",
                        "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
                        "-crf", "17", "-preset", "slow", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+faststart",
                        str(native_9x16_out),
                    ])
                item["dam_vertical_9x16_native_1080p"] = native_9x16_out.name

            results_summary.append((broll_id, item["title"], "16:9 + 9:16 + 1:1 (1080p)", out_info))

        elif src_9x16_asset:
            src_path = BROLL_LIB / src_9x16_asset["dam_filename"]
            print(f"[FFMPEG] Mastering native 9:16 -> 1080p (9:16, 1:1) for {broll_id} ({item['title']})...")
            out_info = master_native_9x16_to_channels(broll_id, slug, src_path)
            item["dam_master_16x9_1080p"] = ""
            item["dam_vertical_9x16_1080p"] = out_info["vertical_9x16_1080p"]
            item["dam_square_1x1_1080p"] = out_info["square_1x1_1080p"]
            item["status"] = "MASTERED_1080P_9x16_1x1 (NEED_16x9_MASTER)"
            item["channel_masters_1080p"] = out_info
            results_summary.append((broll_id, item["title"], "9:16 + 1:1 (1080p)", out_info))
        else:
            item["dam_master_16x9_1080p"] = ""
            item["dam_vertical_9x16_1080p"] = ""
            item["dam_square_1x1_1080p"] = ""

    catalog["updated_at"] = datetime.now().isoformat()
    catalog["production_standard"] = {
        "master_aspect_ratio": "16:9",
        "master_resolution": "1920x1080 (1080p minimum)",
        "channel_outputs": {
            "youtube_web_tv_16x9": "1920x1080",
            "shorts_reels_tiktok_9x16": "1080x1920",
            "social_feed_square_1x1": "1080x1080",
        },
    }
    CATALOG_JSON.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")

    # Update both CSVs with the 1080p multi-channel columns
    fieldnames = [
        "DAM_ID",
        "Concept",
        "Prompt_16x9_Master",
        "Visual_Search_Terms",
        "Theological_Themes",
        "Scripture_Anchors",
        "Emotional_HALT_Tone",
        "Short_Hook_Archetype",
        "Render_Status",
        "DAM_Master_16x9_1080p",
        "DAM_Vertical_9x16_1080p",
        "DAM_Square_1x1_1080p",
        "QA_Notes",
    ]

    for csv_path in (CATALOG_CSV_DAM, CATALOG_CSV_WS):
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                "DAM_ID": "GLOBAL_RULES",
                "Concept": "GLOBAL CONTEXT & RULES",
                "Prompt_16x9_Master": catalog["global_context_and_rules"],
                "Visual_Search_Terms": "1st century levant, judea, galilee, ancient near east, olive skin, homespun wool, rough linen, leather sandals",
                "Theological_Themes": "biblical authenticity, historical grounding, sanctuary plain aesthetic",
                "Scripture_Anchors": "All 66 Books",
                "Emotional_HALT_Tone": "Sacred, Authentic, Grounded",
                "Short_Hook_Archetype": "Global Style Rule",
                "Render_Status": "LOCKED_16x9_1080P_STANDARD",
                "DAM_Master_16x9_1080p": "1920x1080 (YouTube / Web / TV)",
                "DAM_Vertical_9x16_1080p": "1080x1920 (Shorts / Reels / TikTok)",
                "DAM_Square_1x1_1080p": "1080x1080 (Social Feed)",
                "QA_Notes": "Create in 16:9 (>=1080p); FFmpeg produces 9:16 & 1:1 channel masters in ZeroCloudDAM.",
            })
            for item in catalog["items"]:
                qa_notes_list = [a.get("qa_notes", "") for a in item.get("dam_assets", []) if a.get("qa_notes")]
                writer.writerow({
                    "DAM_ID": item["broll_id"],
                    "Concept": item["title"],
                    "Prompt_16x9_Master": item["prompt"],
                    "Visual_Search_Terms": item["visual_search_terms"],
                    "Theological_Themes": item["thematic_tags"],
                    "Scripture_Anchors": item["scripture_anchors"],
                    "Emotional_HALT_Tone": item["soul_halt_tags"],
                    "Short_Hook_Archetype": item["short_hook_archetypes"],
                    "Render_Status": item["status"],
                    "DAM_Master_16x9_1080p": item.get("dam_master_16x9_1080p", ""),
                    "DAM_Vertical_9x16_1080p": item.get("dam_vertical_9x16_1080p", ""),
                    "DAM_Square_1x1_1080p": item.get("dam_square_1x1_1080p", ""),
                    "QA_Notes": " | ".join(qa_notes_list) if qa_notes_list else "Pending 16:9 1080p render.",
                })

    print(f"\nSUCCESS: Generated {len(results_summary)} multi-channel 1080p B-roll sets in {BROLL_LIB}")


if __name__ == "__main__":
    main()
