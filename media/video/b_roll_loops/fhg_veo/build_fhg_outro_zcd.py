#!/usr/bin/env python3
r"""
Generate:
1. C:\dev\forhisgrace-web\images\fig-001-jeff-style_signature.jpg using jeff_canonical_signature.png
   on the canonical FHG warm aged parchment paper color (RGB 219, 206, 184 / #DBCEB8, NOT white).
2. Vertical (9:16, 1080x1920) & Landscape (16:9, 1920x1080) FHG Fig Tree Parchment Outro plates & MP4s in ZeroCloudDAM
   on the exact canonical FHG warm aged parchment paper (#DBCEB8) with cold-pressed paper tooth and Nunito typography:
   - Above image: "For His Grace" as Title (Nunito 800)
   - Image: Signed Fig Tree Logo blended seamlessly onto the warm parchment paper
   - Directly under the logo in same font, non-bold (weight 400), small font size:
     “When you were under the fig tree, I saw you.” -John 1:48
   - Underneath in headline text (Nunito 800):
     “Solitude isn’t lonely when it’s the gift that He gave.”
   - Several line breaks -> H3 (Nunito 800):
     "Learn more on ForHisGrace.com"
   - Beneath that in small text: clean footer
"""

import shutil
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

WEB_ROOT = Path(r"C:\dev\forhisgrace-web")
WEB_IMAGES = WEB_ROOT / "images"
NUNITO_WOFF2 = WEB_ROOT / "fonts" / "nunito-latin.woff2"
CANONICAL_SIG = Path(r"C:\dev\864zeros-publish\media\visuals\jeff_canonical_signature.png")
REF_PARCHMENT_SKETCH = Path(r"C:\dev\864zeros-publish\shared\bible\sketches\verse_25_mark_2_17_sepia_signed_right.jpg")
DAM_SHARED_IMAGES = Path(r"C:\dev\864zeros-publish\shared\bible\images")
DAM_BROLL_LIB = Path(r"C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo\broll_library")
ARTIFACT_DIR = Path(r"C:\Users\Jeff\.gemini\antigravity-cli\brain\d9d60e79-f458-45cb-86b7-4d1ff406a611")

SRC_LOGO = WEB_IMAGES / "fig-001-jeff-style.jpg"
OUT_LOGO_SIG = WEB_IMAGES / "fig-001-jeff-style_signature.jpg"
VO_MASTER_WAV = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_vo_master_14lufs.wav"

# Canonical FHG Warm Aged Parchment Paper RGB (matching verse_25_mark_2_17_sepia_signed_right.jpg: [219, 206, 184])
FHG_PARCHMENT_RGB = (219.0, 206.0, 184.0)
FHG_INK_RGB = (24.0, 21.0, 19.0)


def load_nunito(size: int, weight: int = 800) -> ImageFont.FreeTypeFont:
    font = ImageFont.truetype(str(NUNITO_WOFF2), size=size)
    font.set_variation_by_axes([weight])
    return font


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


def make_parchment_paper_array(width: int, height: int, seed: int = 77) -> np.ndarray:
    """Generate authentic FHG aged sepia parchment paper with subtle organic grain & warm edge vignette."""
    rng = np.random.default_rng(seed)
    # Multi-scale organic paper fiber texture
    coarse = Image.fromarray(rng.normal(0.0, 1.0, (height // 8 + 1, width // 8 + 1)).astype(np.float32)).resize(
        (width, height), resample=Image.Resampling.BICUBIC
    )
    fine = rng.normal(0.0, 1.0, (height, width)).astype(np.float32)
    grain = np.array(coarse, dtype=np.float32) * 2.2 + fine * 1.4

    # Subtle warm age vignette around outer edges
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    nx = (xx / max(1, width - 1)) * 2.0 - 1.0
    ny = (yy / max(1, height - 1)) * 2.0 - 1.0
    dist2 = np.clip((nx * nx + ny * ny) * 0.5, 0.0, 1.0)
    vignette = dist2 * 10.0

    r = np.clip(FHG_PARCHMENT_RGB[0] + grain - vignette * 0.9, 0, 255)
    g = np.clip(FHG_PARCHMENT_RGB[1] + grain * 0.92 - vignette * 1.0, 0, 255)
    b = np.clip(FHG_PARCHMENT_RGB[2] + grain * 0.82 - vignette * 1.15, 0, 255)
    return np.stack([r, g, b], axis=-1)


def extract_ink_alpha_from_logo(logo_img: Image.Image) -> np.ndarray:
    """Extract strictly the dark ink strokes (0.0 = paper, 1.0 = dark ink) with zero outer box vignette."""
    arr = np.array(logo_img.convert("RGB"), dtype=np.float32)
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
    # Threshold strictly below 195 so paper background and corner vignette are 0.0 (100% transparent to parchment)
    ink_alpha = np.clip((195.0 - lum) / (195.0 - 25.0), 0.0, 1.0)
    return ink_alpha


def create_signed_logo() -> Path:
    """Create fig-001-jeff-style_signature.jpg on canonical FHG warm aged parchment paper with bottom-right signature."""
    base_img = Image.open(SRC_LOGO).convert("RGB")
    w, h = base_img.size

    paper_arr = make_parchment_paper_array(w, h, seed=101)
    ink_alpha = extract_ink_alpha_from_logo(base_img)

    out_arr = np.zeros_like(paper_arr)
    for c in range(3):
        out_arr[:, :, c] = paper_arr[:, :, c] * (1.0 - ink_alpha) + FHG_INK_RGB[c] * ink_alpha

    # Stamp canonical signature in bottom-right inside border
    sig = Image.open(CANONICAL_SIG).convert("RGBA")
    sig_alpha = np.array(sig, dtype=np.float32)[:, :, 3] / 255.0

    target_w = int(w * 0.22)
    target_h = int(sig.height * (target_w / sig.width))
    sig_alpha_pil = Image.fromarray((sig_alpha * 255).astype(np.uint8), mode="L").resize(
        (target_w, target_h), resample=Image.Resampling.LANCZOS
    )
    sig_mask = np.array(sig_alpha_pil, dtype=np.float32) / 255.0

    halo_pil = sig_alpha_pil.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(radius=4.5))
    halo_mask = np.clip(np.array(halo_pil, dtype=np.float32) / 255.0 * 1.45, 0.0, 0.90)

    px = int(w * 0.940) - target_w
    py = int(h * 0.958) - target_h
    roi = out_arr[py : py + target_h, px : px + target_w]
    roi_paper = paper_arr[py : py + target_h, px : px + target_w]

    for c in range(3):
        cleared = roi[:, :, c] * (1.0 - halo_mask) + roi_paper[:, :, c] * halo_mask
        roi[:, :, c] = cleared * (1.0 - sig_mask * 0.96) + FHG_INK_RGB[c] * (sig_mask * 0.96)

    out_arr[py : py + target_h, px : px + target_w] = roi
    final_rgb = Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8), mode="RGB")

    final_rgb.save(OUT_LOGO_SIG, format="JPEG", quality=98, subsampling=0)
    DAM_SHARED_IMAGES.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT_LOGO_SIG, DAM_SHARED_IMAGES / "fig-001-jeff-style_signature.jpg")
    shutil.copy2(OUT_LOGO_SIG, ARTIFACT_DIR / "fig-001-jeff-style_signature.jpg")
    print(f"Created signed logo on FHG parchment: {OUT_LOGO_SIG}")
    return OUT_LOGO_SIG


def build_parchment_canvas_with_logo(
    width: int, height: int, signed_logo_path: Path, logo_size: int, logo_x: int, logo_y: int, seed: int
) -> Image.Image:
    """Create a 100% seamless FHG warm aged parchment canvas and composite the signed logo ink directly onto it."""
    paper_arr = make_parchment_paper_array(width, height, seed=seed)
    logo_img = Image.open(signed_logo_path).convert("RGB").resize((logo_size, logo_size), Image.Resampling.LANCZOS)
    ink_alpha = extract_ink_alpha_from_logo(logo_img)

    roi = paper_arr[logo_y : logo_y + logo_size, logo_x : logo_x + logo_size]
    for c in range(3):
        roi[:, :, c] = roi[:, :, c] * (1.0 - ink_alpha) + FHG_INK_RGB[c] * ink_alpha
    paper_arr[logo_y : logo_y + logo_size, logo_x : logo_x + logo_size] = roi

    return Image.fromarray(np.clip(paper_arr, 0, 255).astype(np.uint8), mode="RGB")


def draw_centered_multiline(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    y_start: int,
    center_x: int,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    line_spacing: int = 10,
) -> int:
    y = y_start
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text((center_x - w // 2, y), line, font=font, fill=fill)
        y += h + line_spacing
    return y


def build_vertical_outro_plate(signed_logo_path: Path) -> Path:
    """Build 9:16 (1080x1920) Vertical Fig Tree Parchment Outro on canonical FHG parchment."""
    W, H = 1080, 1920
    logo_size = 750
    logo_x = (W - logo_size) // 2
    logo_y = 230

    canvas = build_parchment_canvas_with_logo(W, H, signed_logo_path, logo_size, logo_x, logo_y, seed=202)
    draw = ImageDraw.Draw(canvas)

    ink_charcoal = (32, 27, 23)      # Deep warm charcoal-ink on parchment
    ink_caption = (78, 66, 54)       # Warm umber for non-bold verse under logo
    ink_bronze = (112, 76, 42)       # Rich dark bronze on parchment
    ink_muted = (96, 84, 72)

    font_title = load_nunito(size=56, weight=800)
    font_verse_sub = load_nunito(size=21, weight=400)
    font_headline = load_nunito(size=38, weight=800)
    font_h3 = load_nunito(size=30, weight=800)
    font_footer_privacy = load_nunito(size=20, weight=700)
    font_footer_copy = load_nunito(size=18, weight=600)

    # 1. Above the image: "For His Grace" as a Title
    title_y = 135
    draw_centered_multiline(draw, ["For His Grace"], title_y, W // 2, font_title, ink_charcoal, line_spacing=8)

    # 2. Directly under the logo in same font, non-bold (weight 400), small font size:
    verse_y = logo_y + logo_size + 12
    next_y = draw_centered_multiline(
        draw,
        ["“When you were under the fig tree, I saw you.” -John 1:48"],
        verse_y,
        W // 2,
        font_verse_sub,
        ink_caption,
        line_spacing=6,
    )

    # 3. Slogan underneath in headline text (Nunito 800)
    slogan_y = next_y + 42
    slogan_lines = [
        "“Solitude isn’t lonely when it’s",
        "the gift that He gave.”",
    ]
    next_y = draw_centered_multiline(
        draw, slogan_lines, slogan_y, W // 2, font_headline, ink_charcoal, line_spacing=14
    )

    # 4. Several line breaks -> H3 "Learn more on ForHisGrace.com"
    h3_y = next_y + 120
    draw_centered_multiline(
        draw, ["Learn more on ForHisGrace.com"], h3_y, W // 2, font_h3, ink_bronze, line_spacing=10
    )

    # 5. Clean Footer in small text at bottom
    rule_y = H - 210
    draw.line([(160, rule_y), (W - 160, rule_y)], fill=(182, 168, 146), width=2)

    footer_y = rule_y + 28
    footer_y = draw_centered_multiline(
        draw,
        ["No ads. No tracking. Your data stays yours."],
        footer_y,
        W // 2,
        font_footer_privacy,
        ink_charcoal,
        line_spacing=12,
    )
    footer_y += 8
    draw_centered_multiline(
        draw,
        ["© 2026 For His Grace, a DBA of 864zeros LLC. All rights reserved."],
        footer_y,
        W // 2,
        font_footer_copy,
        ink_muted,
        line_spacing=8,
    )

    out_dam = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_9x16_1080p.jpg"
    out_web = WEB_IMAGES / "fhg-outro-fig-tree-parchment_9x16_1080p.jpg"
    out_art = ARTIFACT_DIR / "fhg-outro-fig-tree-parchment_9x16_1080p.jpg"
    canvas.save(out_dam, format="JPEG", quality=96, subsampling=0)
    shutil.copy2(out_dam, out_web)
    shutil.copy2(out_dam, out_art)
    print(f"Created Vertical 9:16 Outro Plate on FHG Parchment: {out_dam}")
    return out_dam


def build_landscape_outro_plate(signed_logo_path: Path) -> Path:
    """Build 16:9 (1920x1080) Landscape Fig Tree Parchment Outro on canonical FHG parchment."""
    W, H = 1920, 1080
    logo_size = 515
    logo_x = (W - logo_size) // 2
    logo_y = 92

    canvas = build_parchment_canvas_with_logo(W, H, signed_logo_path, logo_size, logo_x, logo_y, seed=303)
    draw = ImageDraw.Draw(canvas)

    ink_charcoal = (32, 27, 23)
    ink_caption = (78, 66, 54)
    ink_bronze = (112, 76, 42)
    ink_muted = (96, 84, 72)

    font_title = load_nunito(size=44, weight=800)
    font_verse_sub = load_nunito(size=18, weight=400)
    font_headline = load_nunito(size=33, weight=800)
    font_h3 = load_nunito(size=26, weight=800)
    font_footer_privacy = load_nunito(size=18, weight=700)
    font_footer_copy = load_nunito(size=16, weight=600)

    # 1. Above the image: "For His Grace" as a Title
    title_y = 28
    draw_centered_multiline(draw, ["For His Grace"], title_y, W // 2, font_title, ink_charcoal, line_spacing=6)

    # 2. Directly under the logo in same font, non-bold (weight 400), small font size:
    verse_y = logo_y + logo_size + 8
    next_y = draw_centered_multiline(
        draw,
        ["“When you were under the fig tree, I saw you.” -John 1:48"],
        verse_y,
        W // 2,
        font_verse_sub,
        ink_caption,
        line_spacing=6,
    )

    # 3. Slogan underneath in headline text (Nunito 800)
    slogan_y = next_y + 24
    next_y = draw_centered_multiline(
        draw,
        ["“Solitude isn’t lonely when it’s the gift that He gave.”"],
        slogan_y,
        W // 2,
        font_headline,
        ink_charcoal,
        line_spacing=10,
    )

    # 4. Several line breaks -> H3 "Learn more on ForHisGrace.com"
    h3_y = next_y + 62
    draw_centered_multiline(
        draw,
        ["Learn more on ForHisGrace.com"],
        h3_y,
        W // 2,
        font_h3,
        ink_bronze,
        line_spacing=8,
    )

    # 5. Clean Footer in small text at bottom
    rule_y = H - 118
    draw.line([(320, rule_y), (W - 320, rule_y)], fill=(182, 168, 146), width=2)

    footer_y = rule_y + 18
    footer_y = draw_centered_multiline(
        draw,
        ["No ads. No tracking. Your data stays yours."],
        footer_y,
        W // 2,
        font_footer_privacy,
        ink_charcoal,
        line_spacing=8,
    )
    footer_y += 6
    draw_centered_multiline(
        draw,
        ["© 2026 For His Grace, a DBA of 864zeros LLC. All rights reserved."],
        footer_y,
        W // 2,
        font_footer_copy,
        ink_muted,
        line_spacing=6,
    )

    out_dam = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_16x9_1080p.jpg"
    out_web = WEB_IMAGES / "fhg-outro-fig-tree-parchment_16x9_1080p.jpg"
    out_art = ARTIFACT_DIR / "fhg-outro-fig-tree-parchment_16x9_1080p.jpg"
    canvas.save(out_dam, format="JPEG", quality=96, subsampling=0)
    shutil.copy2(out_dam, out_web)
    shutil.copy2(out_dam, out_art)
    print(f"Created Landscape 16:9 Outro Plate on FHG Parchment: {out_dam}")
    return out_dam


def render_outro_mp4_with_vo(img_path: Path, out_mp4: Path, width: int, height: int) -> None:
    dur = get_audio_duration(VO_MASTER_WAV)
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-i", str(VO_MASTER_WAV),
        "-vf", f"scale={width}:{height}:flags=lanczos,fps=60,format=yuv420p",
        "-t", f"{dur:.3f}",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
        "-crf", "17", "-preset", "slow",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-movflags", "+faststart",
        "-shortest",
        str(out_mp4),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Updated Outro MP4 with VO: {out_mp4} ({out_mp4.stat().st_size} bytes, {dur:.2f}s)")


def main():
    signed_logo = create_signed_logo()
    v_plate = build_vertical_outro_plate(signed_logo)
    h_plate = build_landscape_outro_plate(signed_logo)

    render_outro_mp4_with_vo(v_plate, DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_9x16_1080p.mp4", 1080, 1920)
    render_outro_mp4_with_vo(h_plate, DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_16x9_1080p.mp4", 1920, 1080)


if __name__ == "__main__":
    main()
