#!/usr/bin/env python3
"""
Animate 3 of the 12 4K Photorealistic Master Keyframes into 8.0s 1080p @ 60fps
Living-Cinema B-Roll Video Clips (16:9 Widescreen & 9:16 Vertical) for review:
  1. FHG-BR-016_olive-press-gethsemane
  2. FHG-BR-017_tearing-cherubim-temple-veil
  3. FHG-BR-085_jesus-finger-writing-in-temple-dust

Uses 2x supersampled (3840x2160 / 2160x3840) photorealistic framing with organic
torchlight/sunbeam luminance modulation and 60fps cinematic camera push/pan.
Zero sepia conversion — pure photorealistic 1st-century cinema.
"""

import subprocess
from pathlib import Path
from PIL import Image

VEO_DIR = Path(r"C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo")
KEYFRAMES_DIR = VEO_DIR / "keyframes_4k"
BROLL_LIB = VEO_DIR / "broll_library"
WORK_DIR = VEO_DIR / "_work_keyframe_anim"

BROLL_LIB.mkdir(parents=True, exist_ok=True)
WORK_DIR.mkdir(parents=True, exist_ok=True)

CLIPS = [
    {
        "id": "FHG-BR-016",
        "slug": "olive-press-gethsemane",
        "src": KEYFRAMES_DIR / "FHG-BR-016_olive-press-gethsemane_master_4k.jpg",
        "dur": 8.0,
        # Slow push-in toward the crushed olive pulp & golden oil stream with warm flickering torchlight
        "z_expr": "1.02+0.10*(on/480)",
        "x_expr": "iw/2-(iw/zoom/2)+18*sin(on/95)",
        "y_expr": "ih/2-(ih/zoom/2)+12*(on/480)",
        "eq_expr": "eq=brightness='0.018*sin(2*PI*t*1.35)+0.008*sin(2*PI*t*3.1)':contrast='1.03+0.015*sin(2*PI*t*1.35)':saturation=1.05",
    },
    {
        "id": "FHG-BR-017",
        "slug": "tearing-cherubim-temple-veil",
        "src": KEYFRAMES_DIR / "FHG-BR-017_tearing-cherubim-temple-veil_master_4k.jpg",
        "dur": 8.0,
        # Dramatic vertical tilt + push into the blinding golden Shekinah light bursting through the torn veil
        "z_expr": "1.03+0.11*(on/480)",
        "x_expr": "iw/2-(iw/zoom/2)",
        "y_expr": "ih*0.42-(ih/zoom/2)+28*(on/480)",
        "eq_expr": "eq=brightness='0.025*sin(2*PI*t*0.9)+0.012*cos(2*PI*t*2.4)':contrast='1.04+0.02*sin(2*PI*t*0.9)':saturation=1.06",
    },
    {
        "id": "FHG-BR-085",
        "slug": "jesus-finger-writing-in-temple-dust",
        "src": KEYFRAMES_DIR / "FHG-BR-085_jesus-finger-writing-in-temple-dust_master_4k.jpg",
        "dur": 8.0,
        # Low-angle lateral tracking + push across the Hebrew letters etched in the limestone dust
        "z_expr": "1.04+0.09*(on/480)",
        "x_expr": "iw*0.46-(iw/zoom/2)+34*(on/480)",
        "y_expr": "ih*0.54-(ih/zoom/2)-14*(on/480)",
        "eq_expr": "eq=brightness='0.014*sin(2*PI*t*0.75)':contrast=1.03:saturation=1.04",
    },
]


def prepare_supersampled_crop(src_jpg: Path, target_w: int, target_h: int, out_jpg: Path) -> Path:
    """
    Crops and scales the photorealistic keyframe to a 2x supersampled canvas
    (target_w*2 x target_h*2) using Lanczos resampling so zoompan has full sub-pixel precision.
    """
    im = Image.open(src_jpg).convert("RGB")
    src_w, src_h = im.size
    super_w, super_h = target_w * 2, target_h * 2
    target_aspect = super_w / super_h
    src_aspect = src_w / src_h

    if src_aspect > target_aspect:
        # Source is wider than target aspect: crop width
        new_w = int(round(src_h * target_aspect))
        left = (src_w - new_w) // 2
        im_cropped = im.crop((left, 0, left + new_w, src_h))
    else:
        # Source is taller/squarer than target aspect: crop height around optical center (46% from top)
        new_h = int(round(src_w / target_aspect))
        top = int(round((src_h - new_h) * 0.46))
        im_cropped = im.crop((0, top, src_w, top + new_h))

    im_super = im_cropped.resize((super_w, super_h), Image.Resampling.LANCZOS)
    im_super.save(out_jpg, "JPEG", quality=96)
    return out_jpg


def render_clip(clip: dict, aspect_tag: str, width: int, height: int) -> Path:
    plate_jpg = WORK_DIR / f"{clip['id']}_{aspect_tag}_super.jpg"
    prepare_supersampled_crop(clip["src"], width, height, plate_jpg)

    out_mp4 = BROLL_LIB / f"{clip['id']}_{clip['slug']}_{aspect_tag}_1080p.mp4"
    frames = int(round(clip["dur"] * 60))

    vf = (
        f"zoompan=z='{clip['z_expr']}':x='{clip['x_expr']}':y='{clip['y_expr']}':"
        f"d={frames}:s={width}x{height}:fps=60,"
        f"{clip['eq_expr']},"
        f"noise=alls=3:allf=t+u,"
        f"unsharp=3:3:0.45:3:3:0.0,"
        f"setsar=1,format=yuv420p"
    )

    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1",
            "-i", str(plate_jpg),
            "-vf", vf,
            "-t", f"{clip['dur']:.2f}",
            "-r", "60",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
            str(out_mp4),
        ],
        check=True,
        capture_output=True,
    )
    return out_mp4


def main() -> None:
    print("Rendering 3 Photorealistic 1080p @ 60fps Animated Keyframe Clips (16:9 & 9:16)...")
    for clip in CLIPS:
        out_16x9 = render_clip(clip, "16x9", 1920, 1080)
        out_9x16 = render_clip(clip, "9x16", 1080, 1920)
        print(f"  -> {out_16x9.name} ({out_16x9.stat().st_size / (1024*1024):.2f} MB)")
        print(f"  -> {out_9x16.name} ({out_9x16.stat().st_size / (1024*1024):.2f} MB)")


if __name__ == "__main__":
    main()
