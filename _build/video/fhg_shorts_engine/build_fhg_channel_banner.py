"""Generate YouTube Studio Channel Header Banners (2560x1440 with 1546x423 All-Device Safe Zone)
and Channel Profile Avatar (800x800) for For His Grace (@ForHisGrace).

RULE-002 Compliance: C:\\dev\\forhisgrace-web\\images\\fig-001-jeff-style.jpg is opened strictly READ-ONLY.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BROLL_DIR = Path(r"C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo\broll_library")
OUT_DIR = Path(r"C:\dev\864zeros-publish\media\video\fhg_shorts\thumbnails")
WEB_OUT_DIR = Path(r"C:\dev\forhisgrace-web\media\thumbnails")
ARTIFACT_DIR = Path(r"C:\Users\Jeff\.gemini\antigravity-cli\brain\d9d60e79-f458-45cb-86b7-4d1ff406a611")
FIG_LOGO_PATH = Path(r"C:\dev\forhisgrace-web\images\fig-001-jeff-style.jpg")  # READ-ONLY (RULE-002)

GEORGIA_BOLD = r"C:\Windows\Fonts\georgiab.ttf"
GEORGIA_ITALIC = r"C:\Windows\Fonts\georgiai.ttf"
ARIAL_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

# YouTube Official Banner Dimensions (2560 x 1440)
W, H = 2560, 1440
# Desktop Horizontal Strip: 2560 x 423 (Y: 508 .. 931)
STRIP_Y1, STRIP_Y2 = 508, 931
# Mobile / All-Devices Safe Zone: 1546 x 423 (X: 507 .. 2053, Y: 508 .. 931)
SAFE_X1, SAFE_X2 = 507, 2053
SAFE_Y1, SAFE_Y2 = 508, 931


def extract_video_frame(mp4_path: Path, timestamp_sec: float, out_png: Path) -> Image.Image:
    out_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-ss", f"{timestamp_sec:.2f}",
        "-i", str(mp4_path),
        "-frames:v", "1",
        "-q:v", "2",
        str(out_png),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return Image.open(out_png).convert("RGB")


def fit_cover(img: Image.Image, target_w: int, target_h: int, align_x: float = 0.5, align_y: float = 0.5) -> Image.Image:
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = int(round(src_w * scale))
    new_h = int(round(src_h * scale))
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = int(round((new_w - target_w) * align_x))
    top = int(round((new_h - target_h) * align_y))
    return resized.crop((left, top, left + target_w, top + target_h))


def draw_text_with_shadow(
    canvas: Image.Image,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int] = (250, 246, 238, 255),
    shadow_color: tuple[int, int, int, int] = (10, 8, 6, 235),
    shadow_offset: tuple[int, int, int] = (0, 4),
    stroke_width: int = 2,
    stroke_fill: tuple[int, int, int, int] = (18, 13, 9, 255),
) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    sx = xy[0] + shadow_offset[0]
    sy = xy[1] + shadow_offset[1]
    d.text((sx, sy), text, font=font, fill=shadow_color, stroke_width=stroke_width + 2, stroke_fill=shadow_color)
    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=5))
    canvas.alpha_composite(blurred)
    d2 = ImageDraw.Draw(canvas)
    d2.text(xy, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def draw_pill_with_text(
    d: ImageDraw.Draw,
    x: int,
    y: int,
    h: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    bg_fill: tuple[int, int, int, int],
    border_fill: tuple[int, int, int, int] | None,
    text_fill: tuple[int, int, int, int],
    pad_x: int = 20,
) -> int:
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    w = tw + pad_x * 2
    d.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=8,
        fill=bg_fill,
        outline=border_fill,
        width=2 if border_fill else 0,
    )
    ty = y + (h - th) // 2 - bbox[1]
    d.text((x + pad_x, ty), text, font=font, fill=text_fill)
    return w


def save_asset(img: Image.Image, filename: str) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WEB_OUT_DIR.mkdir(parents=True, exist_ok=True)
    rgb = img.convert("RGB")
    out_path = OUT_DIR / filename
    rgb.save(out_path, "JPEG", quality=93, optimize=True)
    shutil.copy2(out_path, WEB_OUT_DIR / filename)
    shutil.copy2(out_path, ARTIFACT_DIR / filename)
    return out_path


def build_banner_option_a(coins_img: Image.Image, cross_img: Image.Image) -> Path:
    """Option A (Matches Locked 16:9 Thumbnail Option A):
    Dark Obsidian & Golden-Hour First-Century Cinema + Fig Tree Medallion inside 1546x423 Safe Zone.
    """
    bg_left = fit_cover(cross_img, W // 2, H, align_x=0.5, align_y=0.45)
    bg_right = fit_cover(coins_img, W // 2, H, align_x=0.55, align_y=0.5)

    canvas_rgb = Image.new("RGB", (W, H), (16, 12, 9))
    canvas_rgb.paste(bg_left, (0, 0))
    canvas_rgb.paste(bg_right, (W // 2, 0))
    canvas_rgb = ImageEnhance.Brightness(canvas_rgb).enhance(0.42)
    canvas_rgb = ImageEnhance.Contrast(canvas_rgb).enhance(1.18)
    canvas = canvas_rgb.convert("RGBA")

    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vignette)
    for y in range(H):
        if y < STRIP_Y1:
            t = (STRIP_Y1 - y) / STRIP_Y1
            alpha = int(round(135 + 90 * (t ** 1.3)))
        elif y > STRIP_Y2:
            t = (y - STRIP_Y2) / (H - STRIP_Y2)
            alpha = int(round(135 + 90 * (t ** 1.3)))
        else:
            alpha = 105
        vd.line([(0, y), (W, y)], fill=(14, 11, 8, alpha))
    canvas.alpha_composite(vignette)

    # Right-side focal feature shifted to X: 1470..2053 so text column (X: 808..1545) sits on clean dark obsidian
    feat_w = 580
    right_feature = fit_cover(coins_img, feat_w, 423, align_x=0.52, align_y=0.52)
    right_feature = ImageEnhance.Contrast(right_feature).enhance(1.24)
    right_feature = ImageEnhance.Brightness(right_feature).enhance(0.95)
    rf_rgba = right_feature.convert("RGBA")

    mask = Image.new("L", (feat_w, 423), 255)
    md = ImageDraw.Draw(mask)
    for x in range(feat_w):
        if x < 210:
            a = int(round(255 * ((x / 210.0) ** 1.7)))
        elif x > feat_w - 80:
            a = int(round(255 * (((feat_w - x) / 80.0) ** 1.4)))
        else:
            a = 255
        md.line([(x, 0), (x, 423)], fill=max(0, min(255, a)))
    canvas.paste(rf_rgba, (1470, STRIP_Y1), mask)

    d = ImageDraw.Draw(canvas)
    d.line([(0, STRIP_Y1), (W, STRIP_Y1)], fill=(196, 154, 108, 155), width=2)
    d.line([(0, STRIP_Y2), (W, STRIP_Y2)], fill=(196, 154, 108, 155), width=2)

    bx1, by1, bx2, by2 = SAFE_X1 + 16, SAFE_Y1 + 16, SAFE_X2 - 16, SAFE_Y2 - 16
    d.rounded_rectangle([bx1, by1, bx2, by2], radius=12, outline=(212, 168, 106, 195), width=2)

    # Read-only Fig Tree medallion on the left of the safe zone
    fig_src = Image.open(FIG_LOGO_PATH).convert("RGB")
    med_size = 232
    fig_crop = fit_cover(fig_src, med_size, med_size, align_x=0.5, align_y=0.45)
    fig_crop = ImageEnhance.Contrast(fig_crop).enhance(1.12)
    circle_mask = Image.new("L", (med_size, med_size), 0)
    ImageDraw.Draw(circle_mask).ellipse([0, 0, med_size - 1, med_size - 1], fill=255)

    med_x, med_y = SAFE_X1 + 44, SAFE_Y1 + 68
    d.ellipse([med_x - 6, med_y - 6, med_x + med_size + 6, med_y + med_size + 6], fill=(28, 21, 15, 240), outline=(228, 182, 106, 255), width=4)
    canvas.paste(fig_crop, (med_x, med_y), circle_mask)

    tx = med_x + med_size + 34
    f_kicker = ImageFont.truetype(ARIAL_BOLD, 19)
    f_title = ImageFont.truetype(GEORGIA_BOLD, 72)
    f_sub = ImageFont.truetype(GEORGIA_ITALIC, 29)
    f_pillars = ImageFont.truetype(ARIAL_BOLD, 20)
    f_url = ImageFont.truetype(ARIAL_BOLD, 18)

    draw_pill_with_text(
        d, tx, SAFE_Y1 + 42, 38,
        "FAITH  ·  SCRIPTURE IN CONTEXT  ·  SOLITUDE",
        f_kicker,
        bg_fill=(176, 125, 62, 240),
        border_fill=(245, 212, 150, 255),
        text_fill=(255, 249, 238, 255),
    )

    draw_text_with_shadow(
        canvas, (tx, SAFE_Y1 + 92), "FOR HIS GRACE", font=f_title,
        fill=(252, 248, 240, 255), stroke_width=3
    )

    draw_text_with_shadow(
        canvas, (tx + 2, SAFE_Y1 + 184),
        "“Solitude isn’t lonely when it’s the gift He gave.”",
        font=f_sub, fill=(255, 208, 122, 255), stroke_width=2
    )

    d = ImageDraw.Draw(canvas)
    d.line([(tx, SAFE_Y1 + 234), (tx + 760, SAFE_Y1 + 234)], fill=(212, 168, 106, 195), width=2)

    draw_text_with_shadow(
        canvas, (tx, SAFE_Y1 + 252),
        "1st-Century Biblical Context  ·  Original Greek & Hebrew  ·  Parables Illustrated",
        font=f_pillars, fill=(246, 238, 224, 255), stroke_width=3
    )

    d = ImageDraw.Draw(canvas)
    draw_pill_with_text(
        d, tx, SAFE_Y1 + 304, 46,
        "4 PARALLEL TRANSLATIONS (BSB · KJV · WEB · *FHG-SP)  |  FORHISGRACE.COM",
        f_url,
        bg_fill=(22, 17, 12, 242),
        border_fill=(212, 168, 106, 240),
        text_fill=(248, 214, 146, 255),
    )

    return save_asset(canvas, "FHG-BANNER-A_cinema-gold-sanctuary_2560x1440.jpg")


def build_banner_option_b() -> Path:
    """Option B: Warm Archival Parchment & Sepia Fig Tree Sanctuary
    Matches the light parchment editorial aesthetic of forhisgrace.com.
    """
    sk1 = Image.open(BROLL_DIR / "FHG-SK-013_parable-mustard-seed-tree_base_16x9_1080p.jpg").convert("RGB")

    # Full 2560x1440 TV backdrop: subtle sepia parchment texture with soft blurred sketch atmosphere
    tv_bg = fit_cover(sk1, W, H, align_x=0.5, align_y=0.5).filter(ImageFilter.GaussianBlur(radius=18))
    tv_overlay = Image.new("RGB", (W, H), (228, 215, 192))
    canvas_rgb = Image.blend(tv_bg, tv_overlay, 0.82)
    canvas = canvas_rgb.convert("RGBA")

    d = ImageDraw.Draw(canvas)
    # Warm parchment center ribbon (Y: 508..931)
    d.rectangle([0, STRIP_Y1, W, STRIP_Y2], fill=(247, 240, 228, 248))

    # Right side of safe zone (X: 1470..2050): Sepia Mustard Tree sketch with smooth left feather
    feat_w = 580
    sk_crop = fit_cover(sk1, feat_w, 423, align_x=0.5, align_y=0.45)
    sk_rgba = sk_crop.convert("RGBA")

    mask = Image.new("L", (feat_w, 423), 255)
    md = ImageDraw.Draw(mask)
    for x in range(feat_w):
        if x < 230:
            a = int(round(215 * ((x / 230.0) ** 1.8)))
        elif x > feat_w - 70:
            a = int(round(215 * (((feat_w - x) / 70.0) ** 1.4)))
        else:
            a = 215
        md.line([(x, 0), (x, 423)], fill=max(0, min(255, a)))
    canvas.paste(sk_rgba, (1470, STRIP_Y1), mask)

    d = ImageDraw.Draw(canvas)
    d.line([(0, STRIP_Y1), (W, STRIP_Y1)], fill=(139, 102, 66, 230), width=3)
    d.line([(0, STRIP_Y2), (W, STRIP_Y2)], fill=(139, 102, 66, 230), width=3)

    bx1, by1, bx2, by2 = SAFE_X1 + 16, SAFE_Y1 + 16, SAFE_X2 - 16, SAFE_Y2 - 16
    d.rounded_rectangle([bx1, by1, bx2, by2], radius=10, outline=(139, 102, 66, 235), width=3)
    d.rounded_rectangle([bx1 + 8, by1 + 8, bx2 - 8, by2 - 8], radius=8, outline=(176, 138, 96, 165), width=1)

    fig_src = Image.open(FIG_LOGO_PATH).convert("RGB")
    med_size = 232
    fig_crop = fit_cover(fig_src, med_size, med_size, align_x=0.5, align_y=0.45)
    circle_mask = Image.new("L", (med_size, med_size), 0)
    ImageDraw.Draw(circle_mask).ellipse([0, 0, med_size - 1, med_size - 1], fill=255)

    med_x, med_y = SAFE_X1 + 44, SAFE_Y1 + 68
    d.ellipse([med_x - 6, med_y - 6, med_x + med_size + 6, med_y + med_size + 6], fill=(247, 240, 228, 255), outline=(120, 82, 44, 255), width=4)
    canvas.paste(fig_crop, (med_x, med_y), circle_mask)

    tx = med_x + med_size + 34
    f_kicker = ImageFont.truetype(ARIAL_BOLD, 19)
    f_title = ImageFont.truetype(GEORGIA_BOLD, 72)
    f_sub = ImageFont.truetype(GEORGIA_ITALIC, 29)
    f_pillars = ImageFont.truetype(ARIAL_BOLD, 20)
    f_url = ImageFont.truetype(ARIAL_BOLD, 18)

    draw_pill_with_text(
        d, tx, SAFE_Y1 + 42, 38,
        "SCRIPTURE IN CONTEXT  ·  QUIET STUDY",
        f_kicker,
        bg_fill=(58, 41, 26, 255),
        border_fill=None,
        text_fill=(248, 239, 224, 255),
    )

    d.text((tx, SAFE_Y1 + 92), "FOR HIS GRACE", font=f_title, fill=(38, 28, 19, 255))
    d.text((tx + 2, SAFE_Y1 + 184), "“Solitude isn’t lonely when it’s the gift He gave.”", font=f_sub, fill=(125, 78, 32, 255))

    d.line([(tx, SAFE_Y1 + 234), (tx + 760, SAFE_Y1 + 234)], fill=(139, 102, 66, 210), width=2)
    d.text(
        (tx, SAFE_Y1 + 252),
        "1st-Century Biblical Context  ·  Original Greek & Hebrew  ·  Parables Illustrated",
        font=f_pillars, fill=(44, 32, 21, 255),
        stroke_width=2, stroke_fill=(247, 240, 228, 235)
    )

    draw_pill_with_text(
        d, tx, SAFE_Y1 + 304, 46,
        "4 PARALLEL TRANSLATIONS (BSB · KJV · WEB · *FHG-SP)  |  FORHISGRACE.COM",
        f_url,
        bg_fill=(238, 226, 204, 250),
        border_fill=(139, 102, 66, 255),
        text_fill=(58, 38, 20, 255),
    )

    return save_asset(canvas, "FHG-BANNER-B_warm-parchment-sanctuary_2560x1440.jpg")


def build_channel_avatar() -> Path:
    """Generate 800x800 Channel Profile Avatar (Circular-Safe Fig Tree & Cross Emblem)."""
    size = 800
    fig_src = Image.open(FIG_LOGO_PATH).convert("RGB")
    crop = fit_cover(fig_src, size, size, align_x=0.5, align_y=0.45)
    crop = ImageEnhance.Contrast(crop).enhance(1.12)
    canvas = crop.convert("RGBA")
    d = ImageDraw.Draw(canvas)

    d.ellipse([18, 18, size - 18, size - 18], outline=(196, 154, 108, 245), width=10)
    d.ellipse([34, 34, size - 34, size - 34], outline=(58, 41, 26, 200), width=3)

    return save_asset(canvas, "FHG-AVATAR_fig-tree-emblem_800x800.jpg")


def main() -> None:
    tmp_dir = OUT_DIR / "_tmp_banner_frames"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    coins_img = extract_video_frame(BROLL_DIR / "FHG-BR-002_falling-silver-coins_16x9_1080p.mp4", 3.65, tmp_dir / "coins_16x9.png")
    cross_img = extract_video_frame(BROLL_DIR / "FHG-BR-003_breaking-bread_9x16_1080p.mp4", 2.0, tmp_dir / "bread_9x16.png")

    p_a = build_banner_option_a(coins_img, cross_img)
    p_b = build_banner_option_b()
    p_av = build_channel_avatar()

    shutil.rmtree(tmp_dir, ignore_errors=True)

    for p in (p_a, p_b, p_av):
        kb = p.stat().st_size / 1024
        print(f"OK: {p.name} ({kb:.1f} KB)")


if __name__ == "__main__":
    main()
