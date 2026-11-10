"""Generate YouTube Studio Thumbnails (16:9 1280x720 + 9:16 1080x1920) for For His Grace Video Shorts."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

BROLL_DIR = Path(r"C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo\broll_library")
OUT_DIR = Path(r"C:\dev\864zeros-publish\media\video\fhg_shorts\thumbnails")
WEB_OUT_DIR = Path(r"C:\dev\forhisgrace-web\media\thumbnails")
ARTIFACT_DIR = Path(r"C:\Users\Jeff\.gemini\antigravity-cli\brain\d9d60e79-f458-45cb-86b7-4d1ff406a611")
LOGO_PATH = Path(r"C:\dev\forhisgrace-web\images\fig-001-jeff-style.jpg")

MONTSERRAT_BLACK = r"C:\dev\864zeros-publish\media\graphics\fonts\Montserrat-Black.ttf"
GEORGIA_BOLD = r"C:\Windows\Fonts\georgiab.ttf"
GEORGIA_ITALIC = r"C:\Windows\Fonts\georgiai.ttf"
ARIAL_BOLD = r"C:\Windows\Fonts\arialbd.ttf"


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
    shadow_color: tuple[int, int, int, int] = (12, 9, 6, 235),
    shadow_offset: tuple[int, int] = (0, 5),
    stroke_width: int = 3,
    stroke_fill: tuple[int, int, int, int] = (18, 13, 9, 255),
) -> None:
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    sx = xy[0] + shadow_offset[0]
    sy = xy[1] + shadow_offset[1]
    d.text((sx, sy), text, font=font, fill=shadow_color, stroke_width=stroke_width + 2, stroke_fill=shadow_color)
    blurred = overlay.filter(ImageFilter.GaussianBlur(radius=6))
    canvas.alpha_composite(blurred)
    d2 = ImageDraw.Draw(canvas)
    d2.text(xy, text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def add_brand_badge(canvas: Image.Image, x: int, y: int, dark_mode: bool = True) -> None:
    d = ImageDraw.Draw(canvas)
    pill_w, pill_h = 276, 54
    bg_col = (28, 22, 17, 225) if dark_mode else (246, 239, 228, 240)
    border_col = (196, 154, 108, 255) if dark_mode else (139, 102, 66, 255)
    text_col = (250, 246, 238, 255) if dark_mode else (43, 33, 24, 255)
    sub_col = (230, 184, 117, 255) if dark_mode else (110, 77, 44, 255)

    d.rounded_rectangle([x, y, x + pill_w, y + pill_h], radius=12, fill=bg_col, outline=border_col, width=2)
    if LOGO_PATH.exists():
        logo = Image.open(LOGO_PATH).convert("RGB").resize((40, 40), Image.Resampling.LANCZOS)
        mask = Image.new("L", (40, 40), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 40, 40], radius=8, fill=255)
        canvas.paste(logo, (x + 8, y + 7), mask)
    f_title = ImageFont.truetype(GEORGIA_BOLD, 18)
    f_sub = ImageFont.truetype(ARIAL_BOLD, 10)
    d.text((x + 56, y + 9), "For His Grace", font=f_title, fill=text_col)
    d.text((x + 56, y + 32), "FAITH · SCRIPTURE · SOLITUDE", font=f_sub, fill=sub_col)


def apply_left_gradient(canvas: Image.Image, width_ratio: float = 0.72, max_alpha: int = 235) -> None:
    w, h = canvas.size
    grad_l = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd_l = ImageDraw.Draw(grad_l)
    limit = int(w * width_ratio)
    for x in range(limit):
        t = 1.0 - (x / limit)
        alpha = int(max_alpha * (t ** 1.45))
        gd_l.line([(x, 0), (x, h)], fill=(20, 15, 11, alpha))
    canvas.alpha_composite(grad_l)

    grad_b = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd_b = ImageDraw.Draw(grad_b)
    start_y = int(h * 0.58)
    for y in range(start_y, h):
        t = max(0.0, (y - start_y) / max(1, h - start_y))
        alpha = int(155 * (t ** 1.7))
        gd_b.line([(0, y), (w, y)], fill=(18, 13, 9, alpha))
    canvas.alpha_composite(grad_b)


def draw_scripture_pill(
    canvas: Image.Image,
    x: int,
    y: int,
    text: str,
    bg: tuple[int, int, int, int] = (46, 98, 69, 245),
    border: tuple[int, int, int, int] = (230, 184, 117, 255),
) -> int:
    d = ImageDraw.Draw(canvas)
    f = ImageFont.truetype(MONTSERRAT_BLACK, 19)
    bbox = d.textbbox((0, 0), text, font=f)
    tw = bbox[2] - bbox[0]
    pw = tw + 36
    ph = 42
    d.rounded_rectangle([x, y, x + pw, y + ph], radius=99, fill=bg, outline=border, width=2)
    d.text((x + 18, y + 9), text, font=f, fill=(255, 255, 255, 255))
    return ph


def build_thumb_001a(coins_img: Image.Image, out_path: Path) -> None:
    """Option A: Dark Dramatic Temple Coins — 'NOT THE PRICE OF A KING / 30 PIECES OF SILVER'."""
    w, h = 1280, 720
    bg = fit_cover(coins_img, w, h, align_x=0.75, align_y=0.5)
    bg = ImageEnhance.Contrast(bg).enhance(1.18)
    bg = ImageEnhance.Brightness(bg).enhance(0.95)
    canvas = bg.convert("RGBA")
    apply_left_gradient(canvas, width_ratio=0.78, max_alpha=242)

    # Outer subtle gold frame
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([14, 14, w - 15, h - 15], radius=16, outline=(196, 154, 108, 180), width=3)

    add_brand_badge(canvas, 46, 42, dark_mode=True)
    draw_scripture_pill(canvas, 46, 128, "EXODUS 21:32  ·  MATTHEW 27:3–10")

    f_hook1 = ImageFont.truetype(MONTSERRAT_BLACK, 54)
    f_hook2 = ImageFont.truetype(MONTSERRAT_BLACK, 82)
    f_hook3 = ImageFont.truetype(MONTSERRAT_BLACK, 68)
    f_sub = ImageFont.truetype(GEORGIA_ITALIC, 30)

    draw_text_with_shadow(canvas, (46, 196), "NOT THE PRICE", f_hook1, fill=(250, 246, 238, 255))
    draw_text_with_shadow(canvas, (46, 260), "OF A KING.", f_hook1, fill=(250, 246, 238, 255))
    draw_text_with_shadow(canvas, (46, 342), "30 PIECES", f_hook2, fill=(255, 191, 0, 255))
    draw_text_with_shadow(canvas, (46, 434), "OF SILVER", f_hook3, fill=(255, 191, 0, 255))

    # Bottom callout bar
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([46, 548, 760, 622], radius=12, fill=(32, 24, 18, 225), outline=(196, 154, 108, 220), width=2)
    d.text((66, 566), "“The legal compensation for a wounded servant…”", font=f_sub, fill=(246, 239, 228, 255))

    canvas.convert("RGB").save(out_path, "JPEG", quality=93, optimize=True)


def build_thumb_001b(coins_img: Image.Image, bread_img: Image.Image, out_path: Path) -> None:
    """Option B: Split Cinema (Coins vs Broken Bread) — 'WHY 30 PIECES? / THE WOUNDED SERVANT'."""
    w, h = 1280, 720
    canvas = Image.new("RGBA", (w, h), (24, 18, 14, 255))
    left_img = fit_cover(coins_img, 660, h, align_x=0.5, align_y=0.5)
    right_img = fit_cover(bread_img, 660, h, align_x=0.5, align_y=0.5)
    canvas.paste(left_img, (0, 0))
    canvas.paste(right_img, (620, 0))

    # Dark center & bottom gradient
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(h):
        t = y / h
        alpha = int(45 + 205 * (t ** 1.25))
        gd.line([(0, y), (w, y)], fill=(18, 13, 9, alpha))
    canvas.alpha_composite(grad)

    d = ImageDraw.Draw(canvas)
    # Center divider line
    d.line([(640, 0), (640, 410)], fill=(230, 184, 117, 210), width=4)
    d.rounded_rectangle([14, 14, w - 15, h - 15], radius=16, outline=(196, 154, 108, 190), width=3)

    add_brand_badge(canvas, 44, 38, dark_mode=True)
    draw_scripture_pill(canvas, 825, 44, "TORAH LAW · EXODUS 21:32", bg=(154, 74, 42, 245))

    f_big = ImageFont.truetype(MONTSERRAT_BLACK, 84)
    f_med = ImageFont.truetype(MONTSERRAT_BLACK, 52)
    f_sub = ImageFont.truetype(GEORGIA_BOLD, 28)

    draw_text_with_shadow(canvas, (52, 395), "WHY 30 PIECES?", f_big, fill=(255, 191, 0, 255))
    draw_text_with_shadow(canvas, (52, 495), "THE PRICE OF A WOUNDED SERVANT", f_med, fill=(250, 246, 238, 255))
    draw_text_with_shadow(canvas, (54, 575), "Judas (Matthew 27)  ×  Zechariah 11:12  ×  Exodus 21:32", f_sub, fill=(230, 184, 117, 255))

    canvas.convert("RGB").save(out_path, "JPEG", quality=93, optimize=True)


def build_thumb_001c(coins_img: Image.Image, out_path: Path) -> None:
    """Option C: Warm FHG Parchment Editorial Split + Cinema Frame."""
    w, h = 1280, 720
    canvas = Image.new("RGBA", (w, h), (246, 239, 228, 255))

    # Right half image in rounded frame
    right_img = fit_cover(coins_img, 580, 652, align_x=0.55, align_y=0.5)
    right_img = ImageEnhance.Contrast(right_img).enhance(1.15)
    mask = Image.new("L", (580, 652), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, 580, 652], radius=22, fill=255)
    canvas.paste(right_img, (664, 34), mask)

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([664, 34, 664 + 580, 34 + 652], radius=22, outline=(110, 77, 44, 255), width=4)
    d.rounded_rectangle([14, 14, w - 15, h - 15], radius=16, outline=(139, 102, 66, 255), width=3)

    add_brand_badge(canvas, 44, 40, dark_mode=False)
    draw_scripture_pill(canvas, 44, 122, "BEHIND THE MESSAGE #001", bg=(46, 98, 69, 255), border=(46, 98, 69, 255))

    f_serif_lg = ImageFont.truetype(GEORGIA_BOLD, 64)
    f_sans_xl = ImageFont.truetype(MONTSERRAT_BLACK, 72)
    f_serif_md = ImageFont.truetype(GEORGIA_ITALIC, 29)
    f_foot = ImageFont.truetype(ARIAL_BOLD, 20)

    d.text((44, 192), "Thirty Pieces", font=f_serif_lg, fill=(43, 33, 24, 255))
    d.text((44, 266), "of Silver:", font=f_serif_lg, fill=(43, 33, 24, 255))
    d.text((44, 355), "THE WOUNDED", font=f_sans_xl, fill=(154, 74, 42, 255))
    d.text((44, 436), "SERVANT’S PRICE", font=ImageFont.truetype(MONTSERRAT_BLACK, 56), fill=(46, 98, 69, 255))

    d.rounded_rectangle([44, 526, 632, 652], radius=14, fill=(238, 228, 211, 255), outline=(184, 158, 128, 255), width=2)
    d.text((64, 544), "Why Exodus 21:32 & Zechariah 11", font=f_serif_md, fill=(43, 33, 24, 255))
    d.text((64, 582), "change everything in Matthew 27.", font=f_serif_md, fill=(43, 33, 24, 255))
    d.text((64, 622), "FORHISGRACE.COM  ·  BIBLE STUDY", font=f_foot, fill=(110, 77, 44, 255))

    canvas.convert("RGB").save(out_path, "JPEG", quality=93, optimize=True)


def build_vertical_cover(frame_img: Image.Image, pill_text: str, line1: str, line2: str, line3: str, sub: str, out_path: Path) -> None:
    """9:16 Vertical Shorts Cover (1080x1920)."""
    w, h = 1080, 1920
    bg = fit_cover(frame_img, w, h, align_x=0.5, align_y=0.45)
    bg = ImageEnhance.Contrast(bg).enhance(1.12)
    canvas = bg.convert("RGBA")

    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    for y in range(h):
        if y < 380:
            alpha = int(190 * (1.0 - y / 380.0))
        elif y > 920:
            t = (y - 920) / (h - 920)
            alpha = int(245 * (t ** 1.15))
        else:
            alpha = 35
        gd.line([(0, y), (w, y)], fill=(18, 13, 9, alpha))
    canvas.alpha_composite(grad)

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([24, 24, w - 25, h - 25], radius=24, outline=(196, 154, 108, 180), width=3)

    add_brand_badge(canvas, 64, 72, dark_mode=True)
    draw_scripture_pill(canvas, 64, 1060, pill_text)

    f1 = ImageFont.truetype(MONTSERRAT_BLACK, 64)
    f2 = ImageFont.truetype(MONTSERRAT_BLACK, 88)
    f3 = ImageFont.truetype(MONTSERRAT_BLACK, 74)
    f_sub = ImageFont.truetype(GEORGIA_ITALIC, 36)

    draw_text_with_shadow(canvas, (64, 1132), line1, f1, fill=(250, 246, 238, 255))
    draw_text_with_shadow(canvas, (64, 1215), line2, f2, fill=(255, 191, 0, 255))
    draw_text_with_shadow(canvas, (64, 1320), line3, f3, fill=(255, 191, 0, 255))

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([64, 1445, w - 64, 1545], radius=16, fill=(32, 24, 18, 230), outline=(196, 154, 108, 220), width=2)
    d.text((92, 1474), sub, font=f_sub, fill=(246, 239, 228, 255))

    canvas.convert("RGB").save(out_path, "JPEG", quality=92, optimize=True)


def build_sepia_16x9(frame_img: Image.Image, pill_text: str, line1: str, line2: str, line3: str, sub: str, out_path: Path) -> None:
    """16:9 Thumbnail for FHG Sepia Sketch Shorts (1280x720)."""
    w, h = 1280, 720
    bg = fit_cover(frame_img, w, h, align_x=0.72, align_y=0.45)
    bg = ImageEnhance.Contrast(bg).enhance(1.12)
    canvas = bg.convert("RGBA")
    apply_left_gradient(canvas, width_ratio=0.76, max_alpha=240)

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([14, 14, w - 15, h - 15], radius=16, outline=(196, 154, 108, 190), width=3)

    add_brand_badge(canvas, 46, 42, dark_mode=True)
    draw_scripture_pill(canvas, 46, 128, pill_text)

    f1 = ImageFont.truetype(MONTSERRAT_BLACK, 50)
    f2 = ImageFont.truetype(MONTSERRAT_BLACK, 76)
    f3 = ImageFont.truetype(MONTSERRAT_BLACK, 66)
    f_sub = ImageFont.truetype(GEORGIA_ITALIC, 28)

    draw_text_with_shadow(canvas, (46, 200), line1, f1, fill=(250, 246, 238, 255))
    draw_text_with_shadow(canvas, (46, 275), line2, f2, fill=(255, 191, 0, 255))
    draw_text_with_shadow(canvas, (46, 368), line3, f3, fill=(255, 191, 0, 255))

    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([46, 548, 790, 622], radius=12, fill=(32, 24, 18, 225), outline=(196, 154, 108, 220), width=2)
    d.text((66, 568), sub, font=f_sub, fill=(246, 239, 228, 255))

    canvas.convert("RGB").save(out_path, "JPEG", quality=93, optimize=True)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WEB_OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp_dir = OUT_DIR / "_tmp_frames"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Extract crisp 1080p hero frames from our B-roll & Sepia library
    coins_16x9 = extract_video_frame(BROLL_DIR / "FHG-BR-002_falling-silver-coins_16x9_1080p.mp4", 3.65, tmp_dir / "coins_16x9.png")
    coins_9x16 = extract_video_frame(BROLL_DIR / "FHG-BR-002_falling-silver-coins_9x16_1080p.mp4", 3.65, tmp_dir / "coins_9x16.png")
    bread_9x16 = extract_video_frame(BROLL_DIR / "FHG-BR-003_breaking-bread_9x16_1080p.mp4", 2.0, tmp_dir / "bread_9x16.png")

    mustard_16x9 = Image.open(BROLL_DIR / "FHG-SK-013_parable-mustard-seed-tree_base_16x9_1080p.jpg").convert("RGB")
    mustard_9x16 = Image.open(BROLL_DIR / "FHG-SK-013_parable-mustard-seed-tree_base_9x16_1080p.jpg").convert("RGB")

    nets_16x9 = extract_video_frame(BROLL_DIR / "FHG-SK-055_sepia-fish-caught-in-woven-net-luke5_16x9_1080p.mp4", 1.5, tmp_dir / "nets_16x9.png")
    nets_9x16 = extract_video_frame(BROLL_DIR / "FHG-SK-055_sepia-fish-caught-in-woven-net-luke5_9x16_1080p.mp4", 1.5, tmp_dir / "nets_9x16.png")

    roof_16x9 = extract_video_frame(BROLL_DIR / "FHG-SK-051_sepia-men-tearing-open-roof-mark2_16x9_1080p.mp4", 1.5, tmp_dir / "roof_16x9.png")
    roof_9x16 = extract_video_frame(BROLL_DIR / "FHG-SK-051_sepia-men-tearing-open-roof-mark2_9x16_1080p.mp4", 1.5, tmp_dir / "roof_9x16.png")

    # 1. Video #001 (Thirty Pieces of Silver) — 3 Widescreen (1280x720) + 1 Vertical (1080x1920)
    build_thumb_001a(coins_16x9, OUT_DIR / "FHG-THUMB-001A_silver-coins_16x9.jpg")
    build_thumb_001b(coins_16x9, bread_9x16, OUT_DIR / "FHG-THUMB-001B_split-law-vs-cross_16x9.jpg")
    build_thumb_001c(coins_16x9, OUT_DIR / "FHG-THUMB-001C_parchment-editorial_16x9.jpg")
    build_vertical_cover(
        coins_9x16,
        "EXODUS 21:32  ·  MATTHEW 27",
        "NOT THE PRICE OF A KING",
        "30 PIECES",
        "OF SILVER",
        "“The legal price of a wounded servant…”",
        OUT_DIR / "FHG-THUMB-001_vertical_9x16.jpg",
    )

    # 2. Sepia Short #001 (Mustard Seed)
    build_sepia_16x9(
        mustard_16x9,
        "MATTHEW 13:31–32  ·  THE MUSTARD SEED",
        "NOT A TOWERING CEDAR",
        "THE WILD",
        "GARDEN SEED",
        "“Why Jesus compared Heaven to a tiny seed…”",
        OUT_DIR / "FHG-THUMB-SEPIA-001_mustard-seed_16x9.jpg",
    )
    build_vertical_cover(
        mustard_9x16,
        "MATTHEW 13:31–32  ·  PARABLES",
        "NOT A CEDAR OF LEBANON",
        "THE WILD",
        "MUSTARD SEED",
        "“Why Heaven starts smaller than you think…”",
        OUT_DIR / "FHG-THUMB-SEPIA-001_mustard-seed_9x16.jpg",
    )

    # 3. Sepia Short #002 (Fishermen of Galilee)
    build_sepia_16x9(
        nets_16x9,
        "LUKE 5:1–11  ·  SHORE OF GALILEE",
        "HE PASSED THE ELITE BY",
        "CALLOUSED",
        "HANDS AT DAWN",
        "“Why Jesus walked straight to tired fishermen…”",
        OUT_DIR / "FHG-THUMB-SEPIA-002_galilee-nets_16x9.jpg",
    )
    build_vertical_cover(
        nets_9x16,
        "LUKE 5:1–11  ·  SHORE OF GALILEE",
        "HE PASSED THE ELITE BY",
        "CALLOUSED",
        "HANDS AT DAWN",
        "“Why Jesus walked straight to tired fishermen…”",
        OUT_DIR / "FHG-THUMB-SEPIA-002_galilee-nets_9x16.jpg",
    )

    # 4. Sepia Short #003 (Tearing Open the Roof in Capernaum)
    build_sepia_16x9(
        roof_16x9,
        "MARK 2:1–12  ·  CAPERNAUM",
        "WHEN THE DOOR IS BLOCKED",
        "TEAR OPEN",
        "THE ROOF",
        "“Four friends who refused to turn back…”",
        OUT_DIR / "FHG-THUMB-SEPIA-003_capernaum-roof_16x9.jpg",
    )
    build_vertical_cover(
        roof_9x16,
        "MARK 2:1–12  ·  CAPERNAUM",
        "WHEN THE DOOR IS BLOCKED",
        "TEAR OPEN",
        "THE ROOF",
        "“Four friends who refused to turn back…”",
        OUT_DIR / "FHG-THUMB-SEPIA-003_capernaum-roof_9x16.jpg",
    )

    shutil.rmtree(tmp_dir, ignore_errors=True)

    # Copy all thumbnails to forhisgrace-web/media/thumbnails and artifact folder
    for f in sorted(OUT_DIR.glob("*.jpg")):
        shutil.copy2(f, WEB_OUT_DIR / f.name)
        shutil.copy2(f, ARTIFACT_DIR / f.name)
        kb = round(f.stat().st_size / 1024, 1)
        print(f"Rendered: {f.name} ({kb} KB)")


if __name__ == "__main__":
    main()
