#!/usr/bin/env python3
"""
Pure Gemini / Veo Image-to-Video Animation Caller.
Sends ONLY the source image and prompt="animate" to the Veo API endpoint
(no FFmpeg zoompan, no synthetic camera math).

API Key Metadata:
  - Name: Gemini API Key
  - Project Title: 864z Drive Vault
  - Project Name: projects/100480155220
  - Project Number: 100480155220
  - Enable URL (your own project):
    https://console.developers.google.com/apis/api/aiplatform.googleapis.com/overview?project=100480155220
  - Stored in: C:\\dev\\864zeros-llc\\.env (GEMINI_API_KEY)
"""

import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ENV_PATH = Path(r"C:\dev\864zeros-llc\.env")
TO_ANIMATE_DIR = Path(r"C:\dev\fhg-videos\why-way\to-animate")
OUT_DIR = Path(r"C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo\broll_library")
PROJECT_ID = "100480155220"
LOCATION = "us-central1"
VERTEX_MODELS = [
    "veo-3.1-generate-preview",
    "veo-3.0-generate-001",
    "veo-3.0-generate-preview",
    "veo-2.0-generate-001",
]


def load_api_key() -> str:
    for var in ("VEO_API_KEY", "GEMINI_API_KEY"):
        if os.environ.get(var):
            return os.environ[var].strip()
    txt = ENV_PATH.read_text(encoding="utf-8")
    for var in ("VEO_API_KEY", "GEMINI_API_KEY"):
        m = re.search(rf"^{var}\s*=\s*([^\s#]+)", txt, flags=re.MULTILINE)
        if m:
            return m.group(1).strip()
    raise RuntimeError(f"GEMINI_API_KEY not found in {ENV_PATH}")


def animate_image_vertex(image_path: Path, out_mp4: Path, api_key: str, aspect_ratio: str = "16:9") -> Path:
    """Send image + 'animate' to Vertex AI Veo predictLongRunning on projects/100480155220."""
    img_b64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
    payload = {
        "instances": [
            {
                "prompt": "animate",
                "image": {
                    "bytesBase64Encoded": img_b64,
                    "mimeType": "image/jpeg",
                },
            }
        ],
        "parameters": {
            "aspectRatio": aspect_ratio,
            "sampleCount": 1,
        },
    }

    chosen_model = None
    op = None
    last_err = None
    for model in VERTEX_MODELS:
        url = (
            f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/"
            f"locations/{LOCATION}/publishers/google/models/{model}:predictLongRunning?key={api_key}"
        )
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                op = json.loads(resp.read().decode("utf-8"))
                chosen_model = model
                break
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            last_err = f"HTTP {e.code} on {model}: {body}"
            if e.code == 404:
                continue
            raise RuntimeError(last_err) from e

    if not op or not chosen_model:
        raise RuntimeError(f"No Vertex Veo model succeeded. Last error: {last_err}")

    op_name = op["name"]
    print(f"    Started {chosen_model} operation: {op_name}")
    poll_url = (
        f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/"
        f"locations/{LOCATION}/publishers/google/models/{chosen_model}:fetchPredictOperation?key={api_key}"
    )

    while True:
        time.sleep(8)
        poll_req = urllib.request.Request(
            poll_url,
            data=json.dumps({"operationName": op_name}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(poll_req, timeout=30) as poll_resp:
            status = json.loads(poll_resp.read().decode("utf-8"))
        if status.get("done"):
            if "error" in status:
                raise RuntimeError(f"Veo operation failed: {json.dumps(status['error'])}")
            response = status.get("response", {})
            videos = response.get("videos", [])
            if videos and videos[0].get("bytesBase64Encoded"):
                out_mp4.write_bytes(base64.b64decode(videos[0]["bytesBase64Encoded"]))
                return out_mp4
            samples = response.get("generateVideoResponse", {}).get("generatedSamples", [])
            if samples and samples[0].get("video", {}).get("uri"):
                dl_req = urllib.request.Request(
                    samples[0]["video"]["uri"],
                    headers={"x-goog-api-key": api_key},
                )
                with urllib.request.urlopen(dl_req, timeout=120) as dl_resp:
                    out_mp4.write_bytes(dl_resp.read())
                return out_mp4
            raise RuntimeError(f"Unexpected Veo completion payload: {json.dumps(status)[:500]}")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    api_key = load_api_key()
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    images = sorted(TO_ANIMATE_DIR.glob("*_master_4k.jpg"))
    print(f"Found {len(images)} keyframes in {TO_ANIMATE_DIR} (Project: {PROJECT_ID})...")

    count = 0
    for img in images:
        stem = img.stem.replace("_master_4k", "")
        for aspect, tag in [("16:9", "16x9"), ("9:16", "9x16")]:
            out_mp4 = OUT_DIR / f"{stem}_{tag}_1080p.mp4"
            if out_mp4.exists() and out_mp4.stat().st_size > 0:
                print(f"  [SKIP] {out_mp4.name} already exists")
                continue
            print(f"  [ANIMATE] {img.name} ({aspect}) -> {out_mp4.name} ...")
            animate_image_vertex(img, out_mp4, api_key=api_key, aspect_ratio=aspect)
            print(f"  [DONE] {out_mp4.name} ({out_mp4.stat().st_size / (1024*1024):.2f} MB)")
            count += 1
            if limit and count >= limit:
                print(f"Reached test limit ({limit}). Stopping.")
                return


if __name__ == "__main__":
    main()
