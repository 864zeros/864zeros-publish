#!/usr/bin/env python3
"""
864zeros 9:16 Vertical Video Storyboard Manifest Builder (`video_manifest_builder.py`)
======================================================================================
Reads `assets/templates/social_video_short.json` and the 3 HALT content packs in `data/packs/`,
producing deterministic 9:16 (1080x1920 @ 30fps) kinetic storyboard & TTS manifests in
`build/video_manifests/<pack_name>_9x16_reels.json`.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
PACKS_DIR = ROOT_DIR / "data" / "packs"
TEMPLATE_PATH = ROOT_DIR / "assets" / "templates" / "social_video_short.json"
OUT_DIR = ROOT_DIR / "build" / "video_manifests"


def build_video_manifest(pack_name: str, template: dict) -> Path:
    pack_path = PACKS_DIR / f"{pack_name}.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    reels = []
    reel_idx = 1
    for cat in pack["categories"]:
        trigger = cat["trigger_key"]
        emotion = cat["canonical_emotion"]
        for entry in cat["entries"]:
            reels.append({
                "reel_id": f"{pack['pack_id']}_reel_{reel_idx:02d}",
                "entry_id": entry["entry_id"],
                "trigger_key": trigger,
                "canonical_emotion": emotion,
                "reference": entry["reference"],
                "qr_payload": entry["qr_payload"],
                "aspect_ratio": template["aspect_ratio"],
                "resolution": template["resolution"],
                "duration_seconds": template["duration_seconds"],
                "audio_track": {
                    "voice_persona": template["audio_profile"]["voice_persona"],
                    "narration_script": (
                        f"When you feel {trigger.lower()}—{emotion.lower()}—hear {entry['reference']}: "
                        f"\"{entry['text']}\" "
                        f"In plain terms: {entry['plain']} "
                        f"Your sixty-second Floor Rep right now: {entry['micro_action']}"
                    )
                },
                "visual_dagr_prompts": {
                    "pass_1_sketch": (
                        f"jeff_sketch style, expressive hand-drawn artwork, bold contour lines, "
                        f"detailed cross-hatching, monochrome pencil on paper. Scene evoking {entry['reference']} "
                        f"({trigger}: {emotion}), architectural stillness, vast stark white negative space."
                    ),
                    "pass_2_painting": (
                        f"jeff_painting style, expressive painterly brushwork, rich oil color layering, "
                        f"tactile canvas texture, warm chiaroscuro depth revealing calm resolution for {entry['reference']}."
                    )
                },
                "timeline": [
                    {
                        "beat_id": "hook_affect_trigger",
                        "start_sec": 0.0,
                        "end_sec": 4.5,
                        "on_screen_text": f"FEELING {trigger}? ({emotion})"
                    },
                    {
                        "beat_id": "verbatim_anchor",
                        "start_sec": 4.5,
                        "end_sec": 14.0,
                        "on_screen_text": f"“{entry['text']}” — {entry['reference']}"
                    },
                    {
                        "beat_id": "plain_distillation",
                        "start_sec": 14.0,
                        "end_sec": 22.5,
                        "on_screen_text": entry["plain"]
                    },
                    {
                        "beat_id": "micro_action_cta",
                        "start_sec": 22.5,
                        "end_sec": 30.0,
                        "on_screen_text": f"60s Floor Rep: {entry['micro_action']}",
                        "qr_overlay": entry["qr_payload"]
                    }
                ]
            })
            reel_idx += 1

    manifest = {
        "manifest_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pack_name": pack_name,
        "pack_id": pack["pack_id"],
        "template_id": template["template_id"],
        "total_reels": len(reels),
        "reels": reels
    }

    out_path = OUT_DIR / f"{pack_name}_9x16_reels.json"
    out_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build 9:16 Vertical Video Storyboard Manifests")
    parser.add_argument("--pack", type=str, default="all", help="Pack stem name or 'all'")
    args = parser.parse_args()

    template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    pack_names = (
        ["halt_kjv_scripture", "stoic_marcus_aurelius", "habit_franklin_virtues"]
        if args.pack == "all"
        else [args.pack.replace(".json", "")]
    )

    print("=== 864zeros 9:16 Vertical Video Manifest Builder ===")
    for pname in pack_names:
        out_path = build_video_manifest(pname, template)
        data = json.loads(out_path.read_text(encoding="utf-8"))
        print(f"  [OK] {pname}: {data['total_reels']} vertical 9:16 reel storyboards -> {out_path}")


if __name__ == "__main__":
    main()
