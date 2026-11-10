#!/usr/bin/env python3
r"""
Generate FHG B-Roll Clips from FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv
using the Google Gemini Video API (Veo) — 16:9 first, then mastered to 1080p (16:9, 9:16, 1:1).

Reads GEMINI_API_KEY directly from C:\dev\864zeros-llc\.env (never prints the key).
"""

import base64
import csv
import json
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ENV_PATH = Path(r"C:\dev\864zeros-llc\.env")
CSV_PATH = Path(r"C:\dev\fhg-videos\FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv")
PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
DAM_BROLL_LIB = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo" / "broll_library"
WS_VIDEOS_DIR = Path(r"C:\dev\fhg-videos")

GLOBAL_CONTEXT = (
    "1st Century Levant/Judea/Galilee, Ancient Near East (1st Century AD). "
    "Authentic historical materials only (rough stone, unglazed clay, homespun wool, olive skin tone, natural sunlight or oil-lamp light, zero modern objects)."
)


def load_gemini_api_key() -> str:
    txt = ENV_PATH.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^GEMINI_API_KEY\s*=\s*(\S+)", txt, re.MULTILINE)
    if not m:
        raise RuntimeError("GEMINI_API_KEY not found in C:\\dev\\864zeros-llc\\.env")
    return m.group(1).strip().strip("\"'")


def list_veo_models(api_key: str) -> list[str]:
    # Test 1: Check if gemini-omni-1.1-flash supports responseModalities: ["VIDEO"] or Interactions API
    for endpoint, payload in [
        (
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-omni-1.1-flash:generateContent?key={api_key}",
            {
                "contents": [{"parts": [{"text": "Generate a 16:9 video of dark red grape juice dripping from crushed grapes into a rustic clay bowl."}]}],
                "generationConfig": {"responseModalities": ["VIDEO"]},
            },
        ),
        (
            f"https://generativelanguage.googleapis.com/v1alpha/models/veo-3.0-generate-preview:predictLongRunning?key={api_key}",
            {"instances": [{"prompt": "Crushed grapes dripping into clay bowl"}], "parameters": {"aspectRatio": "16:9"}},
        ),
        (
            f"https://generativelanguage.googleapis.com/v1alpha/models/veo-2.0-generate-001:predictLongRunning?key={api_key}",
            {"instances": [{"prompt": "Crushed grapes dripping into clay bowl"}], "parameters": {"aspectRatio": "16:9"}},
        ),
    ]:
        try:
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                print("SUCCESS:", endpoint.split("?")[0], r.read().decode("utf-8")[:300])
        except urllib.error.HTTPError as e:
            print("FAIL:", endpoint.split("?")[0], e.code, e.read().decode("utf-8")[:250])
    return []


def generate_veo_clip_16x9(api_key: str, models: list[str], prompt: str, out_raw_mp4: Path) -> tuple[bool, str]:
    last_err = ""
    for model_id in models:
        start_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:predictLongRunning?key={api_key}"
        payload = {
            "instances": [{"prompt": f"{prompt} {GLOBAL_CONTEXT}"}],
            "parameters": {
                "aspectRatio": "16:9",
                "sampleCount": 1,
                "personGeneration": "allow_adult",
            },
        }
        try:
            print(f"  -> Submitting 16:9 generation request to {model_id}...")
            req = urllib.request.Request(
                start_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                op = json.loads(resp.read().decode("utf-8"))
            op_name = op.get("name", "")
            print(f"     Operation started: {op_name}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            last_err = f"{model_id} HTTP {e.code}: {err_body[:350]}"
            print(f"     [Fallback] {last_err}")
            continue

        poll_url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}?key={api_key}"
        for attempt in range(60):
            time.sleep(8)
            with urllib.request.urlopen(poll_url, timeout=30) as pr:
                p_data = json.loads(pr.read().decode("utf-8"))
            if p_data.get("done"):
                if "error" in p_data:
                    last_err = f"{model_id} op error: {p_data['error']}"
                    print(f"     [Op Error] {last_err}")
                    break
                resp_obj = p_data.get("response", {})
                # Check Gemini API v1beta format (generateVideoResponse.generatedSamples)
                samples = (
                    resp_obj.get("generateVideoResponse", {})
                    .get("generatedSamples", [])
                )
                if samples:
                    vid_obj = samples[0].get("video", {})
                    vid_uri = vid_obj.get("uri", "")
                    b64 = vid_obj.get("bytesBase64Encoded", "")
                    if vid_uri:
                        dl_url = f"{vid_uri}&key={api_key}" if "?" in vid_uri else f"{vid_uri}?key={api_key}"
                        req_dl = urllib.request.Request(dl_url, headers={"x-goog-api-key": api_key})
                        with urllib.request.urlopen(req_dl, timeout=120) as vr:
                            out_raw_mp4.write_bytes(vr.read())
                        print(f"     [SUCCESS] Downloaded {out_raw_mp4.name} ({out_raw_mp4.stat().st_size / (1024*1024):.2f} MB) via {model_id}")
                        return True, model_id
                    elif b64:
                        out_raw_mp4.write_bytes(base64.b64decode(b64))
                        print(f"     [SUCCESS] Decoded {out_raw_mp4.name} ({out_raw_mp4.stat().st_size / (1024*1024):.2f} MB) via {model_id}")
                        return True, model_id
                # Check Vertex-style videos array fallback
                videos = resp_obj.get("videos", []) or resp_obj.get("predictions", [])
                if videos and isinstance(videos[0], dict):
                    b64 = videos[0].get("bytesBase64Encoded", "")
                    if b64:
                        out_raw_mp4.write_bytes(base64.b64decode(b64))
                        print(f"     [SUCCESS] Decoded {out_raw_mp4.name} ({out_raw_mp4.stat().st_size / (1024*1024):.2f} MB) via {model_id}")
                        return True, model_id
                last_err = f"Completed but unexpected payload structure: {str(resp_obj)[:350]}"
                print(f"     [Warn] {last_err}")
                break
            else:
                print(f"     ...polling {model_id} ({(attempt + 1) * 8}s elapsed)")
    return False, last_err


def master_16x9_to_all_1080p_channels(raw_mp4: Path, dam_id: str, slug: str) -> dict:
    out_16x9 = DAM_BROLL_LIB / f"{dam_id}_{slug}_16x9_1080p.mp4"
    out_9x16 = DAM_BROLL_LIB / f"{dam_id}_{slug}_9x16_1080p.mp4"
    out_1x1 = DAM_BROLL_LIB / f"{dam_id}_{slug}_1x1_1080p.mp4"

    # 1. 16:9 1080p (1920x1080)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(raw_mp4),
            "-vf", "scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p",
            "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            str(out_16x9),
        ],
        check=True,
        capture_output=True,
    )
    # 2. 9:16 1080p (1080x1920 dead-center crop from 16:9)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(raw_mp4),
            "-vf", "scale=-1:1920:flags=lanczos,crop=1080:1920:(iw-1080)/2:0,setsar=1,format=yuv420p",
            "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            str(out_9x16),
        ],
        check=True,
        capture_output=True,
    )
    # 3. 1:1 1080p (1080x1080 dead-center crop from 16:9)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(raw_mp4),
            "-vf", "scale=-1:1080:flags=lanczos,crop=1080:1080:(iw-1080)/2:0,setsar=1,format=yuv420p",
            "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            str(out_1x1),
        ],
        check=True,
        capture_output=True,
    )
    shutil.copy2(out_16x9, WS_VIDEOS_DIR / out_16x9.name)
    shutil.copy2(out_9x16, WS_VIDEOS_DIR / out_9x16.name)
    return {
        "16x9": str(out_16x9),
        "9x16": str(out_9x16),
        "1x1": str(out_1x1),
    }


def slugify(text: str) -> str:
    return "-".join("".join(c.lower() if c.isalnum() else " " for c in text).split())


def main() -> None:
    api_key = load_gemini_api_key()
    models = list_veo_models(api_key)

    target_ids = ["FHG-BR-001", "FHG-BR-005", "FHG-BR-007"]
    rows = []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if r["DAM_ID"] in target_ids:
                rows.append(r)

    results = []
    for r in rows:
        dam_id = r["DAM_ID"]
        concept = r["Concept"]
        prompt = r["Prompt_16x9_Master"]
        slug = slugify(concept)
        raw_out = DAM_BROLL_LIB / f"{dam_id}_{slug}_16x9_veo_raw.mp4"

        print(f"\n=== Generating {dam_id}: {concept} (16:9) ===")
        ok, model_or_err = generate_veo_clip_16x9(api_key, models, prompt, raw_out)
        if ok:
            masters = master_16x9_to_all_1080p_channels(raw_out, dam_id, slug)
            results.append({"dam_id": dam_id, "concept": concept, "model": model_or_err, "masters": masters})
        else:
            results.append({"dam_id": dam_id, "concept": concept, "error": model_or_err})

    print("\n=== SUMMARY ===")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
