#!/usr/bin/env python3
r"""
Generate:
1. C:\dev\forhisgrace-web\images\fig-001-jeff-style_signature.jpg using jeff_canonical_signature.png
2. Vertical (9:16, 1080x1920) & Landscape (16:9, 1920x1080) FHG Fig Tree Parchment Outro plates & MP4s in ZeroCloudDAM
   using the exact Home Page Slogan font (Nunito from C:\dev\forhisgrace-web\fonts\nunito-latin.woff2):
   - Above image: "For His Grace" as Title (Nunito 800)
   - Image: Signed Fig Tree Logo (fig-001-jeff-style_signature.jpg)
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
DAM_SHARED_IMAGES = Path(r"C:\dev\864zeros-publish\shared\bible\images")
DAM_BROLL_LIB = Path(r"C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo\broll_library")
ARTIFACT_DIR = Path(r"C:\Users\Jeff\.gemini\antigravity-cli\brain\d9d60e79-f458-45cb-86b7-4d1ff406a611")

SRC_LOGO = WEB_IMAGES / "fig-001-jeff-style.jpg"
OUT_LOGO_SIG = WEB_IMAGES / "fig-001-jeff-style_signature.jpg"
VO_MASTER_WAV = DAM_BROLL_LIB / "FHG-OUTRO-001_fig-tree-parchment_vo_master_14lufs.wav"


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


def create_signed_logo() -> Path:
    """Stamp jeff_canonical_signature.png cleanly on bottom-right of fig-001-jeff-style.jpg."""
    base_img = Image.open(SRC_LOGO).convert("RGB")
    out_arr = np.array(base_img, dtype=np.float32)
    h, w, _ = out_arr.shape

    paper_patch = out_arr[80:220, 120:420]
    paper_rgb = paper_patch.mean(axis=(0, 1))
    ink_rgb = (24.0, 21.0, 19.0)

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

    for c in range(3):
        cleared = roi[:, :, c] * (1.0 - halo_mask) + paper_rgb[c] * halo_mask
        roi[:, :, c] = cleared * (1.0 - sig_mask * 0.96) + ink_rgb[c] * (sig_mask * 0.96)

    out_arr[py : py + target_h, px : px + target_w] = roi
    final_rgb = Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8), mode="RGB")

    final_rgb.save(OUT_LOGO_SIG, format="JPEG", quality=98, subsampling=0)
    DAM_SHARED_IMAGES.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT_LOGO_SIG, DAM_SHARED_IMAGES / "fig-001-jeff-style_signature.jpg")
    shutil.copy2(OUT_LOGO_SIG, ARTIFACT_DIR / "fig-001-jeff-style_signature.jpg")
    print(f"Created signed logo: {OUT_LOGO_SIG} ({OUT_LOGO_SIG.stat().st_size} bytes)")
    return OUT_LOGO_SIG


def build_parchment_canvas(width: int, height: int, logo_img: Image.Image) -> Image.Image:
    interior_patch = logo_img.crop((120, 80, 420, 220))
    bg_color = interior_patch.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0))
    return Image.new("RGB", (width, height), bg_color)


def paste_logo_seamlessly(canvas: Image.Image, logo: Image.Image, size: int, x: int, y: int) -> None:
    logo_resized = logo.resize((size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    draw_m = ImageDraw.Draw(mask)
    inset = 10
    draw_m.rectangle([inset, inset, size - inset, size - inset], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=6))
    canvas.paste(logo_resized, (x, y), mask)


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
    """Build 9:16 (1080x1920) Vertical Fig Tree Parchment Outro using Nunito."""
    W, H = 1080, 1920
    logo = Image.open(signed_logo_path).convert("RGB")
    canvas = build_parchment_canvas(W, H, logo)
    draw = ImageDraw.Draw(canvas)

    ink_charcoal = (45, 45, 45)      # --ink (#2D2D2D)
    ink_caption = (92, 82, 70)       # Warm umber/charcoal for small non-bold verse under logo
    ink_bronze = (139, 102, 66)      # --pillar-accent (#8B6642)
    ink_muted = (120, 113, 108)      # --muted (#78716c)

    font_title = load_nunito(size=56, weight=800)
    font_verse_sub = load_nunito(size=21, weight=400)  # Non-bold small font size directly under logo
    font_headline = load_nunito(size=38, weight=800)
    font_h3 = load_nunito(size=30, weight=800)
    font_footer_privacy = load_nunito(size=20, weight=700)
    font_footer_copy = load_nunito(size=18, weight=600)

    # 1. Above the image: "For His Grace" as a Title
    title_y = 135
    draw_centered_multiline(draw, ["For His Grace"], title_y, W // 2, font_title, ink_charcoal, line_spacing=8)

    # 2. Signed Fig Tree Logo Image
    logo_size = 750
    logo_x = (W - logo_size) // 2
    logo_y = 230
    paste_logo_seamlessly(canvas, logo, logo_size, logo_x, logo_y)

    # 3. Directly under the logo in same font, non-bold (weight 400), small font size:
    #    “When you were under the fig tree, I saw you.” -John 1:48
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

    # 4. Slogan underneath in headline text (Nunito 800, matching home page slogan)
    slogan_y = next_y + 42
    slogan_lines = [
        "“Solitude isn’t lonely when it’s",
        "the gift that He gave.”",
    ]
    next_y = draw_centered_multiline(
        draw, slogan_lines, slogan_y, W // 2, font_headline, ink_charcoal, line_spacing=14
    )

    # 5. Several line breaks -> H3 "Learn more on ForHisGrace.com"
    h3_y = next_y + 120
    draw_centered_multiline(
        draw, ["Learn more on ForHisGrace.com"], h3_y, W // 2, font_h3, ink_bronze, line_spacing=10
    )

    # 6. Clean Footer in small text at bottom
    rule_y = H - 210
    draw.line([(160, rule_y), (W - 160, rule_y)], fill=(214, 202, 184), width=2)

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
    print(f"Created Vertical 9:16 Outro Plate: {out_dam}")
    return out_dam


def build_landscape_outro_plate(signed_logo_path: Path) -> Path:
    """Build 16:9 (1920x1080) Landscape Fig Tree Parchment Outro using Nunito."""
    W, H = 1920, 1080
    logo = Image.open(signed_logo_path).convert("RGB")
    canvas = build_parchment_canvas(W, H, logo)
    draw = ImageDraw.Draw(canvas)

    ink_charcoal = (45, 45, 45)
    ink_caption = (92, 82, 70)
    ink_bronze = (139, 102, 66)
    ink_muted = (120, 113, 108)

    font_title = load_nunito(size=44, weight=800)
    font_verse_sub = load_nunito(size=18, weight=400)  # Non-bold small font size directly under logo
    font_headline = load_nunito(size=33, weight=800)
    font_h3 = load_nunito(size=26, weight=800)
    font_footer_privacy = load_nunito(size=18, weight=700)
    font_footer_copy = load_nunito(size=16, weight=600)

    # 1. Above the image: "For His Grace" as a Title
    title_y = 28
    draw_centered_multiline(draw, ["For His Grace"], title_y, W // 2, font_title, ink_charcoal, line_spacing=6)

    # 2. Signed Fig Tree Logo Image
    logo_size = 515
    logo_x = (W - logo_size) // 2
    logo_y = 92
    paste_logo_seamlessly(canvas, logo, logo_size, logo_x, logo_y)

    # 3. Directly under the logo in same font, non-bold (weight 400), small font size:
    #    “When you were under the fig tree, I saw you.” -John 1:48
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

    # 4. Slogan underneath in headline text (Nunito 800)
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

    # 5. Several line breaks -> H3 "Learn more on ForHisGrace.com"
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

    # 6. Clean Footer in small text at bottom
    rule_y = H - 118
    draw.line([(320, rule_y), (W - 320, rule_y)], fill=(214, 202, 184), width=2)

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
    print(f"Created Landscape 16:9 Outro Plate: {out_dam}")
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
