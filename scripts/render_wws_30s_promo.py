import asyncio
import math
import os
import struct
import subprocess
import wave
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
import edge_tts
import imageio_ffmpeg

OUT_DIR = r"C:\dev\864zeros-publish\media\video\wws_demo_promo"
IMG_DIR = os.path.join(OUT_DIR, "scraped_images")
EMP_DIR = os.path.join(OUT_DIR, "employees")
IG_DIR = os.path.join(OUT_DIR, "instagram")

VIDEO_OUT = os.path.join(OUT_DIR, "wws_864zeros_demo_30s_16x9.mp4")
THUMB_OUT = os.path.join(OUT_DIR, "wws_30s_promo_thumb.jpg")
SHEET_OUT = r"C:\Users\Jeff\.gemini\antigravity-cli\brain\a8bc81a3-5510-464b-8325-5b18dd52cc96\wws_30s_promo_contact_sheet.jpg"

W, H = 1920, 1080
FPS = 30
DURATION = 30.0
TOTAL_FRAMES = int(DURATION * FPS)  # 900 frames

VO_TEXT = (
    "Since nineteen seventy-nine, World Wide Stereo has been delivering happiness across Montgomeryville, "
    "Wayne, and the Main Line. "
    "From founder Bob Cole to master system designers Ron Rumer, Mario Patelmo, Chad Snedaker, "
    "Chris Barnhart, Ira Segall, and our entire integration and custom car audio team — "
    "we craft breathtaking McIntosh and Bowers and Wilkins listening rooms, "
    "reference Dolby Atmos private cinemas, and bespoke smart estates. "
    "World Wide Stereo. Awe-inspired since nineteen seventy-nine."
)

def get_font(size, bold=True):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibrib.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

FONT_HERO = get_font(62, True)
FONT_H1 = get_font(46, True)
FONT_H2 = get_font(30, True)
FONT_BODY = get_font(23, False)
FONT_BADGE = get_font(20, True)
FONT_NAME = get_font(24, True)
FONT_ROLE = get_font(17, False)
FONT_SM = get_font(16, True)

async def generate_audio(vo_mp3_path, final_wav_path):
    print("1. Generating broadcast voiceover via edge-tts...")
    communicate = edge_tts.Communicate(VO_TEXT, voice="en-US-AndrewMultilingualNeural", rate="+7%", pitch="-2Hz")
    await communicate.save(vo_mp3_path)

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    vo_wav = os.path.join(OUT_DIR, "vo_raw.wav")
    subprocess.run([
        ffmpeg_exe, "-y", "-i", vo_mp3_path,
        "-ar", "44100", "-ac", "2", vo_wav
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Synthesize warm McIntosh-inspired audiophile cinematic bed (30.0s, 44.1kHz stereo)
    bed_wav = os.path.join(OUT_DIR, "bed_raw.wav")
    sr = 44100
    n_samples = int(DURATION * sr)
    # Warm D-major9 / A-major audiophile progression
    chords = [
        (0.0, 7.5, [73.42, 146.83, 220.00, 293.66, 369.99, 440.00]),   # D maj7
        (7.5, 15.0, [55.00, 110.00, 220.00, 277.18, 329.63, 440.00]),  # A maj7
        (15.0, 22.5, [61.74, 123.47, 185.00, 246.94, 329.63, 369.99]), # Bm7
        (22.5, 30.0, [73.42, 146.83, 220.00, 293.66, 369.99, 587.33]), # D maj9 resolve
    ]
    cut_times = [0.0, 4.2, 9.0, 13.8, 18.6, 22.8, 26.6]

    with wave.open(bed_wav, "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        buf = bytearray()
        for i in range(n_samples):
            t = i / sr
            # Find active chord
            freqs = chords[-1][2]
            for c0, c1, cf in chords:
                if c0 <= t < c1:
                    freqs = cf
                    break
            # Smooth pad + warm pulse
            pulse = 0.72 + 0.28 * math.sin(2 * math.pi * 2.0 * t)
            sig_l = 0.0
            sig_r = 0.0
            for idx, f in enumerate(freqs):
                detune = 1.0 + (idx - 2.5) * 0.0008
                v = math.sin(2 * math.pi * f * t) * (0.35 / (idx + 1.2))
                v2 = math.sin(2 * math.pi * f * detune * t + 0.6) * (0.35 / (idx + 1.2))
                sig_l += v
                sig_r += v2
            # Subtle transition shimmer on act boundaries
            whoosh = 0.0
            for ct in cut_times:
                dt = abs(t - ct)
                if dt < 0.28:
                    whoosh += (1.0 - dt / 0.28) * 0.14 * math.sin(2 * math.pi * (180 + 420 * (0.28 - dt)) * t)

            # Fade in / out envelope
            env = 1.0
            if t < 0.6:
                env = t / 0.6
            elif t > DURATION - 1.2:
                env = max(0.0, (DURATION - t) / 1.2)

            val_l = max(-0.95, min(0.95, (sig_l * pulse * 0.22 + whoosh) * env))
            val_r = max(-0.95, min(0.95, (sig_r * pulse * 0.22 - whoosh) * env))
            buf.extend(struct.pack("<hh", int(val_l * 32767), int(val_r * 32767)))
        wf.writeframes(bytes(buf))

    # Mix voiceover + audiophile bed into final 30.0s WAV
    subprocess.run([
        ffmpeg_exe, "-y",
        "-i", bed_wav,
        "-i", vo_wav,
        "-filter_complex",
        "[0:a]volume=0.85[bed];[1:a]adelay=350|350,volume=1.55[vo];[bed][vo]amix=inputs=2:duration=first:dropout_transition=2[out]",
        "-map", "[out]",
        "-t", str(DURATION),
        final_wav_path
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"   Audio master ready -> {final_wav_path}")

def load_cover(path, w=W, h=H, zoom=1.0, pan_x=0.0, pan_y=0.0, darken=0.62):
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    target_ratio = w / h
    src_ratio = iw / ih
    if src_ratio > target_ratio:
        new_h = int(h * 1.18 * zoom)
        new_w = int(new_h * src_ratio)
    else:
        new_w = int(w * 1.18 * zoom)
        new_h = int(new_w / src_ratio)
    im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
    max_dx = max(0, new_w - w)
    max_dy = max(0, new_h - h)
    cx = int(max_dx * (0.5 + 0.45 * pan_x))
    cy = int(max_dy * (0.5 + 0.45 * pan_y))
    im = im.crop((cx, cy, cx + w, cy + h))
    if darken < 1.0:
        im = ImageEnhance.Brightness(im).enhance(darken)
    return im

def load_circle_avatar(path, size=150, border_color=(0, 212, 255)):
    im = Image.open(path).convert("RGBA")
    im = ImageOps.fit(im, (size, size), Image.Resampling.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.ellipse((2, 2, size - 3, size - 3), fill=255)
    out = Image.new("RGBA", (size + 10, size + 10), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(out)
    odraw.ellipse((0, 0, size + 9, size + 9), fill=(12, 18, 28, 240), outline=border_color + (255,), width=4)
    out.paste(im, (5, 5), mask)
    return out

def load_rounded_card_img(path, w, h, radius=18):
    im = Image.open(path).convert("RGB")
    im = ImageOps.fit(im, (w, h), Image.Resampling.LANCZOS)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    rgba = im.convert("RGBA")
    rgba.putalpha(mask)
    return rgba

def draw_top_chrome(canvas, draw, t, act_label):
    # Top glass bar
    overlay = Image.new("RGBA", (W, 74), (8, 12, 20, 210))
    canvas.paste(overlay, (0, 0), overlay)
    draw.line([(0, 74), (W, 74)], fill=(0, 210, 255), width=2)

    # Left brand pill
    draw.rounded_rectangle((36, 14, 495, 58), radius=10, fill=(18, 28, 46), outline=(0, 210, 255), width=2)
    draw.text((54, 23), "WORLD WIDE STEREO · EST. 1979", font=FONT_BADGE, fill=(255, 255, 255))

    # Center act indicator
    draw.text((530, 24), act_label, font=FONT_BADGE, fill=(130, 225, 255))

    # Right 864zeros Studio badge
    draw.rounded_rectangle((1410, 14, 1884, 58), radius=10, fill=(16, 36, 32), outline=(46, 235, 170), width=2)
    # Pulsing live dot
    dot_col = (46, 255, 170) if int(t * 4) % 2 == 0 else (18, 160, 110)
    draw.ellipse((1428, 29, 1442, 43), fill=dot_col)
    draw.text((1454, 23), "864ZEROS MEDIA STUDIO · 30s DEMO", font=FONT_BADGE, fill=(220, 255, 240))

def draw_bottom_bar(canvas, draw, headline, subline, accent=(0, 210, 255), progress=0.0):
    bar_h = 128
    y0 = H - bar_h
    overlay = Image.new("RGBA", (W, bar_h), (7, 10, 18, 228))
    canvas.paste(overlay, (0, y0), overlay)
    draw.line([(0, y0), (W, y0)], fill=accent, width=3)

    # Accent vertical bar
    draw.rounded_rectangle((42, y0 + 20, 52, H - 22), radius=4, fill=accent)
    draw.text((70, y0 + 18), headline, font=FONT_H1, fill=(255, 255, 255))
    draw.text((72, y0 + 74), subline, font=FONT_BODY, fill=(185, 215, 240))

    # Right location pill
    draw.rounded_rectangle((1445, y0 + 28, 1878, y0 + 98), radius=12, fill=(16, 24, 38), outline=accent, width=2)
    draw.text((1470, y0 + 38), "MONTGOMERYVILLE & WAYNE, PA", font=FONT_SM, fill=(255, 215, 110))
    draw.text((1470, y0 + 64), "worldwidestereo.com · @worldwidestereo", font=FONT_ROLE, fill=(210, 230, 250))

    # Timeline progress bar at very bottom
    pw = int(W * min(1.0, max(0.0, progress)))
    draw.rectangle((0, H - 5, W, H), fill=(25, 35, 50))
    draw.rectangle((0, H - 5, pw, H), fill=accent)

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    vo_mp3 = os.path.join(OUT_DIR, "vo_wws.mp3")
    final_wav = os.path.join(OUT_DIR, "audio_master_30s.wav")
    asyncio.run(generate_audio(vo_mp3, final_wav))

    # Pre-load Employee Avatars & Metadata
    emp_specs = [
        ("ron_rumer.png", "Ron Rumer", "Chief Regional Sales Director", "Featured in Philadelphia Style Magazine"),
        ("mario_patelmo.png", "Mario Patelmo", "Regional Sales & Showroom Mgr", "Montgomeryville & Wayne Showrooms"),
        ("chad_snedaker.png", "Chad Snedaker", "Sales & System Designer", "Whole House Audio & Home Theater"),
        ("chris_barnhart.png", "Chris Barnhart", "Sales & System Designer", "2-Channel Hi-Fi & Acoustic Design"),
        ("dave_sailer.png", "Dave Sailer", "Sales & System Designer", "Custom Home Cinema & Automation"),
        ("patrick_obrien.png", "Patrick O'Brien", "Sales & System Designer", "Ardmore / Wayne & Main Line Specialist"),
        ("ryan_rumer.png", "Ryan Rumer", "Sales & System Designer", "New Construction & Custom Estates"),
        ("chris_mulhearn.png", "Chris Mulhearn", "Car Sales & System Designer", "Porsche, Ferrari & Bespoke Mobile Audio"),
        ("frank_polek.png", "Frank Polek", "Car & Marine Specialist", "Custom Fabrication & Marine Audio"),
        ("ira_segall.png", "Ira Segall", "Senior Product Specialist", "17-Year World Wide Stereo Legend"),
        ("ben_morrow.png", "Ben Morrow", "Systems Integration", "Smart Lighting, Shades & Control"),
        ("noah_mastin.png", "Noah Mastin", "Systems Integration", "Enterprise Networking & Automation"),
        ("ross_whitecavage.png", "Ross Whitecavage", "Sales & System Designer", "Musician & Reference Audio Specialist"),
    ]
    emp_avatars_lg = {}
    emp_avatars_sm = {}
    for fn, name, role, note in emp_specs:
        p = os.path.join(EMP_DIR, fn)
        emp_avatars_lg[fn] = load_circle_avatar(p, size=136, border_color=(0, 215, 255))
        emp_avatars_sm[fn] = load_circle_avatar(p, size=104, border_color=(46, 235, 170))

    # Preload key hero images
    p_bob = os.path.join(IMG_DIR, "about_us_01.jpg")
    p_wayne = os.path.join(IMG_DIR, "wayne_pa_showroom_01.jpg")
    p_mont = os.path.join(IMG_DIR, "montgomeryville_pa_showr_06.jpg")
    p_design = os.path.join(IMG_DIR, "design_installation_01.jpg")
    p_event = os.path.join(IMG_DIR, "montgomeryville_pa_showr_07.jpg")
    p_mc1 = os.path.join(IMG_DIR, "mcintosh_listening_room__01.jpg")
    p_mc2 = os.path.join(IMG_DIR, "mcintosh_listening_room__02.jpg")
    p_mc8 = os.path.join(IMG_DIR, "mcintosh_listening_room__08.jpg")
    p_sf = os.path.join(IMG_DIR, "sonus_faber_mcintosh.jpg")
    p_bw = os.path.join(IMG_DIR, "a_9_1_channel_media_room_06.jpg")
    p_pool = os.path.join(IMG_DIR, "chad_snedaker_04.jpg")
    p_cinema1 = os.path.join(IMG_DIR, "home_theater_hero.jpg")
    p_cinema2 = os.path.join(IMG_DIR, "home_theater_design_and__03.jpg")
    p_cinema3 = os.path.join(IMG_DIR, "our_work_08.jpg")
    p_gladwyne = os.path.join(IMG_DIR, "a_5_1_4_dolby_atmos_base_01.jpg")

    # Preload IG post cards
    ig_cards = [
        ("ig_post_03.jpg", "@worldwidestereo", "Raising a glass to Ira Segall — 17 years of audio excellence!"),
        ("ig_post_04.jpg", "@worldwidestereo", "Ron Rumer featured in Philadelphia Style 'Men of Influence'"),
        ("ig_post_06.jpg", "@worldwidestereo", "Inside our new Wayne, PA Home Technology Experience Center"),
        ("ig_post_09.jpg", "@worldwidestereo", "What Is Dolby Atmos & Is It Worth It? Expert Breakdown"),
        ("ig_post_01.jpg", "@worldwidestereo", "An Evening with Focal — Exclusive Showroom Listening Event"),
        ("ig_post_10.jpg", "@worldwidestereo", "Radnor Hunt Concours d'Elegance — Bespoke Car Audio Upgrades"),
    ]
    ig_loaded = []
    for fn, handle, cap in ig_cards:
        pth = os.path.join(IG_DIR, fn)
        if os.path.exists(pth):
            ig_loaded.append((load_rounded_card_img(pth, 480, 340, radius=16), handle, cap))

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-i", final_wav,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        VIDEO_OUT
    ]

    print(f"2. Streaming {TOTAL_FRAMES} frames (1920x1080 @ {FPS}fps) to FFmpeg...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    sample_frames = {}

    for f_idx in range(TOTAL_FRAMES):
        t = f_idx / FPS
        prog = t / DURATION

        # =========================================================================
        # ACT 1 (0.0s - 4.2s): FOUNDER BOB COLE + WAYNE & MONTGOMERYVILLE SHOWROOMS
        # =========================================================================
        if t < 4.2:
            u = t / 4.2
            bg = load_cover(p_wayne, W, H, zoom=1.02 + 0.08 * u, pan_x=-0.3 + 0.6 * u, pan_y=0.0, darken=0.52)
            draw = ImageDraw.Draw(bg)

            # Left showcase card: Founder Bob Cole "AWE INSPIRED. SINCE 1979."
            card_bob = load_rounded_card_img(p_bob, 820, 430, radius=20)
            bg.paste(card_bob, (64, 130), card_bob)
            draw.rounded_rectangle((64, 130, 884, 560), radius=20, outline=(0, 215, 255), width=3)
            draw.rounded_rectangle((84, 492, 620, 542), radius=10, fill=(10, 16, 28))
            draw.text((100, 503), "BOB COLE · FOUNDER & CEO (EST. 1979)", font=FONT_BADGE, fill=(255, 215, 110))

            # Right showcase card: Montgomeryville & Wayne Showrooms
            card_mont = load_rounded_card_img(p_mont, 860, 280, radius=20)
            bg.paste(card_mont, (960, 130), card_mont)
            draw.rounded_rectangle((960, 130, 1820, 410), radius=20, outline=(46, 235, 170), width=3)
            draw.rounded_rectangle((980, 348, 1520, 396), radius=10, fill=(10, 16, 28))
            draw.text((998, 359), "MONTGOMERYVILLE & WAYNE, PA SHOWROOMS", font=FONT_BADGE, fill=(46, 235, 170))

            # Brand Legacy Stats Box
            draw.rounded_rectangle((960, 435, 1820, 560), radius=18, fill=(14, 22, 36), outline=(0, 215, 255), width=2)
            draw.text((990, 452), "3X 'BEST OF PHILLY' WINNER  ·  HTA LUXURY CERTIFIED", font=FONT_H2, fill=(255, 255, 255))
            draw.text((990, 498), "45+ Years Designing Reference Audio, Home Theater & Smart Estates", font=FONT_BODY, fill=(175, 215, 245))

            # Hero headline banner
            draw.rounded_rectangle((64, 595, 1820, 910), radius=22, fill=(10, 16, 28), outline=(0, 215, 255), width=2)
            draw.text((100, 622), "DELIVERING HAPPINESS SINCE 1979.", font=FONT_HERO, fill=(255, 255, 255))
            draw.text((100, 706), "Technology playgrounds in Montgomeryville & Wayne, PA where you can see, hear, and feel what's possible.", font=FONT_H2, fill=(120, 225, 255))
            draw.text((100, 765), "McIntosh  ·  Bowers & Wilkins 800 Diamond  ·  Sonus faber  ·  Focal  ·  Marantz  ·  Sony 4K  ·  Lutron", font=FONT_BODY, fill=(255, 215, 110))
            draw.text((100, 825), "LIVE SITE + SOCIAL + TEAM SCRAPE DEMO  ->  PRODUCED BY 864ZEROS MEDIA STUDIO", font=FONT_BADGE, fill=(46, 235, 170))

            draw_top_chrome(bg, draw, t, "ACT 01 // HERITAGE & EXPERIENCE CENTERS (MONTGOMERYVILLE & WAYNE, PA)")
            draw_bottom_bar(bg, draw, "WORLD WIDE STEREO — AWE INSPIRED SINCE 1979",
                            "Founded by Bob Cole · Experience Centers at 754 Route 309 (Montgomeryville) & 218 E Lancaster Ave (Wayne)",
                            accent=(0, 215, 255), progress=prog)

        # =========================================================================
        # ACT 2 (4.2s - 9.0s): MEET THE SYSTEM DESIGNERS (EMPLOYEE ROSTER PART 1)
        # =========================================================================
        elif t < 9.0:
            u = (t - 4.2) / 4.8
            bg = load_cover(p_design, W, H, zoom=1.04 + 0.06 * u, pan_x=0.3 - 0.6 * u, pan_y=0.0, darken=0.42)
            draw = ImageDraw.Draw(bg)

            # Header banner
            draw.rounded_rectangle((56, 98, 1864, 195), radius=16, fill=(12, 20, 34), outline=(0, 215, 255), width=2)
            draw.text((84, 112), "MEET THE WORLD WIDE STEREO SYSTEM ARCHITECTS", font=FONT_H1, fill=(255, 255, 255))
            draw.text((84, 160), "Real employee profiles & showroom specialists scraped live from worldwidestereo.com", font=FONT_BODY, fill=(120, 225, 255))

            # 7 Employee Cards (Row 1: 4 cards, Row 2: 3 cards + Live Showroom Event photo)
            team_batch_1 = emp_specs[:7]
            for idx, (fn, name, role, note) in enumerate(team_batch_1):
                row = 0 if idx < 4 else 1
                col = idx if idx < 4 else idx - 4
                cw, ch = 435, 335
                x0 = 56 + col * 454
                y0 = 216 + row * 355
                draw.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=18, fill=(14, 22, 36), outline=(0, 215, 255), width=2)
                av = emp_avatars_lg[fn]
                bg.paste(av, (x0 + (cw - av.width) // 2, y0 + 18), av)
                # Centered text
                nb = draw.textbbox((0, 0), name, font=FONT_NAME)
                draw.text((x0 + (cw - (nb[2] - nb[0])) // 2, y0 + 176), name, font=FONT_NAME, fill=(255, 255, 255))
                rb = draw.textbbox((0, 0), role, font=FONT_ROLE)
                draw.text((x0 + (cw - (rb[2] - rb[0])) // 2, y0 + 210), role, font=FONT_ROLE, fill=(0, 215, 255))
                draw.line([(x0 + 36, y0 + 244), (x0 + cw - 36, y0 + 244)], fill=(40, 60, 90), width=1)
                ntb = draw.textbbox((0, 0), note, font=FONT_SM)
                draw.text((x0 + (cw - (ntb[2] - ntb[0])) // 2, y0 + 262), note, font=FONT_SM, fill=(255, 215, 110))
                draw.text((x0 + (cw - 210) // 2, y0 + 292), "VERIFIED WWS SPECIALIST", font=FONT_SM, fill=(46, 235, 170))

            # 8th slot in grid: Showroom listening consultation photo
            x0, y0, cw, ch = 56 + 3 * 454, 216 + 355, 435, 335
            ev_card = load_rounded_card_img(p_event, cw, ch, radius=18)
            bg.paste(ev_card, (x0, y0), ev_card)
            draw.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=18, outline=(46, 235, 170), width=3)
            draw.rounded_rectangle((x0 + 16, y0 + ch - 68, x0 + cw - 16, y0 + ch - 14), radius=10, fill=(10, 16, 28))
            draw.text((x0 + 30, y0 + ch - 52), "LIVE IN-SHOWROOM CONSULTATIONS", font=FONT_SM, fill=(46, 235, 170))

            draw_top_chrome(bg, draw, t, "ACT 02 // SALES & SYSTEM DESIGN LEADERSHIP")
            draw_bottom_bar(bg, draw, "EXPERTLY DESIGNED. EXPERTLY INSTALLED.",
                            "Featuring Ron Rumer · Mario Patelmo · Chad Snedaker · Chris Barnhart · Dave Sailer · Patrick O'Brien · Ryan Rumer",
                            accent=(46, 235, 170), progress=prog)

        # =========================================================================
        # ACT 3 (9.0s - 13.8s): McINTOSH & SONUS FABER / BOWERS & WILKINS ROOMS
        # =========================================================================
        elif t < 13.8:
            u = (t - 9.0) / 4.8
            bg = load_cover(p_mc1, W, H, zoom=1.03 + 0.08 * u, pan_x=-0.35 + 0.7 * u, pan_y=0.0, darken=0.58)
            draw = ImageDraw.Draw(bg)

            # Left Hero Panel: Washington Crossing McIntosh Room
            c_mc2 = load_rounded_card_img(p_mc2, 560, 360, radius=18)
            bg.paste(c_mc2, (60, 115), c_mc2)
            draw.rounded_rectangle((60, 115, 620, 475), radius=18, outline=(46, 235, 170), width=3)
            draw.rounded_rectangle((78, 412, 602, 460), radius=10, fill=(8, 16, 24))
            draw.text((96, 424), "McINTOSH MT10 TURNTABLE & TUBE AMPS", font=FONT_BADGE, fill=(46, 235, 170))

            c_mc8 = load_rounded_card_img(p_mc8, 560, 360, radius=18)
            bg.paste(c_mc8, (60, 505), c_mc8)
            draw.rounded_rectangle((60, 505, 620, 865), radius=18, outline=(0, 215, 255), width=3)
            draw.rounded_rectangle((78, 802, 602, 850), radius=10, fill=(8, 16, 24))
            draw.text((96, 814), "VACUUM TUBE GLOW · WASHINGTON CROSSING", font=FONT_BADGE, fill=(0, 215, 255))

            # Center-Right Showcase: Sonus faber + Bowers & Wilkins 802 D3 Media Room
            c_sf = load_rounded_card_img(p_sf, 580, 440, radius=18)
            bg.paste(c_sf, (660, 115), c_sf)
            draw.rounded_rectangle((660, 115, 1240, 555), radius=18, outline=(255, 215, 110), width=3)
            draw.rounded_rectangle((680, 492, 1220, 540), radius=10, fill=(8, 16, 24))
            draw.text((698, 504), "SONUS FABER & McINTOSH REFERENCE STACK", font=FONT_BADGE, fill=(255, 215, 110))

            c_bw = load_rounded_card_img(p_bw, 580, 440, radius=18)
            bg.paste(c_bw, (1280, 115), c_bw)
            draw.rounded_rectangle((1280, 115, 1860, 555), radius=18, outline=(0, 215, 255), width=3)
            draw.rounded_rectangle((1300, 492, 1840, 540), radius=10, fill=(8, 16, 24))
            draw.text((1318, 504), "BOWERS & WILKINS 802 D3 + McINTOSH 9.1", font=FONT_BADGE, fill=(0, 215, 255))

            # Bottom Right Acoustic Spectrum & Project Callout Box
            draw.rounded_rectangle((660, 585, 1860, 865), radius=20, fill=(10, 18, 30), outline=(46, 235, 170), width=2)
            draw.text((695, 608), "THE ULTIMATE TWO-CHANNEL & 9.1 REFERENCE ROOMS", font=FONT_H1, fill=(255, 255, 255))
            draw.text((695, 668), "Acoustically treated listening sanctuaries with custom vinyl libraries, McIntosh monoblocks,", font=FONT_BODY, fill=(190, 225, 245))
            draw.text((695, 700), "Bowers & Wilkins 800 Series Diamond loudspeakers, and Sonus faber flagship towers.", font=FONT_BODY, fill=(190, 225, 245))

            # Animated McIntosh-Green Spectrum Bars
            for b_i in range(36):
                bx = 695 + b_i * 31
                bh = int(28 + 62 * abs(math.sin(t * 7.5 + b_i * 0.45)))
                by0 = 842 - bh
                col = (46, 245, 150) if b_i % 2 == 0 else (0, 210, 255)
                draw.rounded_rectangle((bx, by0, bx + 20, 842), radius=4, fill=col)

            draw_top_chrome(bg, draw, t, "ACT 03 // REFERENCE 2-CHANNEL & AUDIOPHILE LISTENING ROOMS")
            draw_bottom_bar(bg, draw, "McINTOSH · BOWERS & WILKINS · SONUS FABER · FOCAL",
                            "Featured Portfolio: Washington Crossing 2-Channel Sanctuary & Austin Marvel's 9.1 B&W 802 D3 Media Room",
                            accent=(46, 235, 170), progress=prog)

        # =========================================================================
        # ACT 4 (13.8s - 18.6s): SPECIALISTS ROSTER PART 2 + CAR AUDIO & OUTDOOR
        # =========================================================================
        elif t < 18.6:
            u = (t - 13.8) / 4.8
            bg = load_cover(p_pool, W, H, zoom=1.04 + 0.06 * u, pan_x=-0.2 + 0.4 * u, pan_y=0.0, darken=0.45)
            draw = ImageDraw.Draw(bg)

            # Header
            draw.rounded_rectangle((56, 96, 1864, 188), radius=16, fill=(12, 20, 34), outline=(255, 215, 110), width=2)
            draw.text((84, 108), "INTEGRATION, AUTOMATION & CUSTOM CAR / MARINE SPECIALISTS", font=FONT_H1, fill=(255, 255, 255))
            draw.text((84, 154), "If it rolls, floats, or lights up your estate — our veteran engineering team builds it to perfection.", font=FONT_BODY, fill=(255, 215, 110))

            # 6 Specialist Employee Cards (3x2 on Left/Center)
            team_batch_2 = emp_specs[7:]
            for idx, (fn, name, role, note) in enumerate(team_batch_2):
                row = idx // 3
                col = idx % 3
                cw, ch = 410, 330
                x0 = 56 + col * 428
                y0 = 208 + row * 350
                draw.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=18, fill=(14, 22, 36), outline=(255, 215, 110), width=2)
                av = emp_avatars_lg[fn]
                bg.paste(av, (x0 + (cw - av.width) // 2, y0 + 16), av)
                nb = draw.textbbox((0, 0), name, font=FONT_NAME)
                draw.text((x0 + (cw - (nb[2] - nb[0])) // 2, y0 + 172), name, font=FONT_NAME, fill=(255, 255, 255))
                rb = draw.textbbox((0, 0), role, font=FONT_ROLE)
                draw.text((x0 + (cw - (rb[2] - rb[0])) // 2, y0 + 204), role, font=FONT_ROLE, fill=(255, 215, 110))
                draw.line([(x0 + 30, y0 + 238), (x0 + cw - 30, y0 + 238)], fill=(45, 65, 95), width=1)
                ntb = draw.textbbox((0, 0), note, font=FONT_SM)
                draw.text((x0 + (cw - (ntb[2] - ntb[0])) // 2, y0 + 256), note, font=FONT_SM, fill=(130, 225, 255))
                draw.text((x0 + (cw - 210) // 2, y0 + 288), "WWS ENGINEERING ROSTER", font=FONT_SM, fill=(46, 235, 170))

            # Right column: Outdoor Entertainment Pavilion + Porsche/Ferrari Car Audio
            c_out = load_rounded_card_img(p_pool, 510, 330, radius=18)
            bg.paste(c_out, (1350, 208), c_out)
            draw.rounded_rectangle((1350, 208, 1860, 538), radius=18, outline=(0, 215, 255), width=3)
            draw.rounded_rectangle((1368, 475, 1842, 522), radius=10, fill=(10, 16, 28))
            draw.text((1386, 487), "POOLSIDE & OUTDOOR PAVILION SYSTEMS", font=FONT_SM, fill=(0, 215, 255))

            p_car = os.path.join(IG_DIR, "ig_post_10.jpg")
            c_car = load_rounded_card_img(p_car if os.path.exists(p_car) else p_design, 510, 330, radius=18)
            bg.paste(c_car, (1350, 558), c_car)
            draw.rounded_rectangle((1350, 558, 1860, 888), radius=18, outline=(255, 215, 110), width=3)
            draw.rounded_rectangle((1368, 825, 1842, 872), radius=10, fill=(10, 16, 28))
            draw.text((1386, 837), "PORSCHE 911, FERRARI 458 & BRONCO BUILDS", font=FONT_SM, fill=(255, 215, 110))

            draw_top_chrome(bg, draw, t, "ACT 04 // CUSTOM CAR AUDIO, MARINE & SMART AUTOMATION TEAM")
            draw_bottom_bar(bg, draw, "FROM PORSCHE 911 FOCAL UPGRADES TO WHOLE-ESTATE AUTOMATION",
                            "Featuring Chris Mulhearn · Frank Polek · Ira Segall · Ben Morrow · Noah Mastin · Ross Whitecavage",
                            accent=(255, 215, 110), progress=prog)

        # =========================================================================
        # ACT 5 (18.6s - 22.8s): REFERENCE DOLBY ATMOS PRIVATE HOME CINEMAS
        # =========================================================================
        elif t < 22.8:
            u = (t - 18.6) / 4.2
            bg = load_cover(p_cinema1, W, H, zoom=1.03 + 0.08 * u, pan_x=-0.3 + 0.6 * u, pan_y=0.0, darken=0.68)
            draw = ImageDraw.Draw(bg)

            # 3 Luxury Cinema Inset Cards across the bottom-middle
            cin_cards = [
                (p_cinema2, "BESPOKE PRIVATE CINEMA ENTRANCE", "Custom Acoustic Architecture & Marquee"),
                (p_cinema3, "STARLIGHT CEILING & PLUSH SEATING", "Motorized Shading & Kaleidescape 4K"),
                (p_gladwyne, "GLADWYNE, PA 5.1.4 DOLBY ATMOS", "133\" Sony 4K Anamorphic Projection"),
            ]
            for idx, (cp, ctitle, csub) in enumerate(cin_cards):
                x0 = 64 + idx * 608
                y0 = 470
                cim = load_rounded_card_img(cp, 576, 360, radius=18)
                bg.paste(cim, (x0, y0), cim)
                draw.rounded_rectangle((x0, y0, x0 + 576, y0 + 360), radius=18, outline=(0, 215, 255), width=3)
                draw.rounded_rectangle((x0 + 16, y0 + 276, x0 + 560, y0 + 344), radius=10, fill=(8, 12, 22))
                draw.text((x0 + 32, y0 + 284), ctitle, font=FONT_BADGE, fill=(255, 215, 110))
                draw.text((x0 + 32, y0 + 312), csub, font=FONT_ROLE, fill=(200, 230, 255))

            # Top Hero Callout Banner
            draw.rounded_rectangle((64, 110, 1856, 430), radius=22, fill=(10, 16, 28), outline=(0, 215, 255), width=2)
            draw.text((100, 138), "BELIEF-SUSPENDING PRIVATE HOME CINEMAS.", font=FONT_HERO, fill=(255, 255, 255))
            draw.text((100, 224), "Custom acoustic treatments, Sony 4K laser projection, JBL Synthesis & Bowers & Wilkins Dolby Atmos.", font=FONT_H2, fill=(120, 225, 255))
            draw.text((100, 286), "\"The awe-inspiring, fully immersive home theater experience we're known for doesn't come in a box —", font=FONT_BODY, fill=(230, 240, 255))
            draw.text((100, 322), "it comes with insight and expertise from our technology architects in Montgomeryville and Wayne.\"", font=FONT_BODY, fill=(230, 240, 255))
            draw.text((100, 372), "GLADWYNE, PA  ·  CHESTNUT HILL, PA  ·  AMBLER, PA  ·  FORT WASHINGTON, PA  ·  MAIN LINE", font=FONT_BADGE, fill=(46, 235, 170))

            draw_top_chrome(bg, draw, t, "ACT 05 // PRIVATE HOME CINEMAS & DOLBY ATMOS THEATERS")
            draw_bottom_bar(bg, draw, "CUSTOM HOME THEATER DESIGN & INSTALLATION",
                            "Private Cinemas · Media & Gaming Rooms · Custom Theatre Seating · Acoustic Treatments · Video Walls",
                            accent=(0, 215, 255), progress=prog)

        # =========================================================================
        # ACT 6 (22.8s - 26.6s): LIVE @WORLDWIDESTEREO INSTAGRAM FEED (APIFY SCRAPE)
        # =========================================================================
        elif t < 26.6:
            u = (t - 22.8) / 3.8
            bg = load_cover(p_wayne, W, H, zoom=1.06, pan_x=0.2 - 0.4 * u, pan_y=0.0, darken=0.36)
            draw = ImageDraw.Draw(bg)

            # Social Header Banner
            draw.rounded_rectangle((56, 96, 1864, 192), radius=16, fill=(14, 20, 36), outline=(255, 110, 190), width=2)
            draw.text((84, 108), "LIVE SOCIAL PULSE: @WORLDWIDESTEREO (SCRAPED VIA APIFY)", font=FONT_H1, fill=(255, 255, 255))
            draw.text((84, 156), "9,208 Followers · Employee Spotlights, Showroom First-Listen Events & Concours d'Elegance Builds", font=FONT_BODY, fill=(255, 165, 220))

            # 6 Instagram Cards (3x2 grid)
            for idx, (ig_im, handle, cap) in enumerate(ig_loaded[:6]):
                row = idx // 3
                col = idx % 3
                cw, ch = 580, 345
                x0 = 56 + col * 604
                y0 = 212 + row * 360
                draw.rounded_rectangle((x0, y0, x0 + cw, y0 + ch), radius=18, fill=(14, 22, 36), outline=(255, 110, 190), width=2)
                bg.paste(ig_im, (x0 + 12, y0 + 12), ig_im)
                # Overlay caption strip at bottom of card
                draw.rounded_rectangle((x0 + 12, y0 + ch - 92, x0 + cw - 12, y0 + ch - 12), radius=12, fill=(8, 12, 22))
                draw.text((x0 + 28, y0 + ch - 82), f"INSTAGRAM · {handle}", font=FONT_SM, fill=(255, 120, 200))
                draw.text((x0 + 28, y0 + ch - 54), cap[:56], font=FONT_ROLE, fill=(240, 245, 255))

            draw_top_chrome(bg, draw, t, "ACT 06 // LIVE APIFY SOCIAL FEED EXTRACTION (@WORLDWIDESTEREO)")
            draw_bottom_bar(bg, draw, "COMMUNITY, CULTURE & PASSION FOR SOUND",
                            "Celebrating Ira Segall's 17 Years · Ron Rumer in Philadelphia Style · Focal & Sonus faber Showroom Nights",
                            accent=(255, 110, 190), progress=prog)

        # =========================================================================
        # ACT 7 (26.6s - 30.0s): GRAND FINALE — ALL 13 EMPLOYEES + BOB COLE + CTA
        # =========================================================================
        else:
            u = (t - 26.6) / 3.4
            bg = load_cover(p_wayne, W, H, zoom=1.0 + 0.05 * u, pan_x=0.0, pan_y=0.0, darken=0.42)
            draw = ImageDraw.Draw(bg)

            # Top Row of 7 Employee Avatars + Names
            for idx in range(7):
                fn, name, role, _ = emp_specs[idx]
                av = emp_avatars_sm[fn]
                cx = 84 + idx * 258
                cy = 104
                bg.paste(av, (cx + 42, cy), av)
                nb = draw.textbbox((0, 0), name, font=FONT_SM)
                draw.text((cx + 100 - (nb[2] - nb[0]) // 2, cy + 118), name, font=FONT_SM, fill=(255, 255, 255))

            # Center Grand Finale Hero Card
            draw.rounded_rectangle((120, 265, 1800, 695), radius=26, fill=(10, 18, 32), outline=(0, 215, 255), width=3)
            # Left inset: Founder Bob Cole
            bob_sm = load_rounded_card_img(p_bob, 460, 370, radius=18)
            bg.paste(bob_sm, (152, 295), bob_sm)
            draw.rounded_rectangle((152, 295, 612, 665), radius=18, outline=(255, 215, 110), width=2)

            # Right Finale Copy
            draw.text((655, 305), "WORLD WIDE STEREO", font=FONT_HERO, fill=(255, 255, 255))
            draw.text((655, 385), "DELIVERING HAPPINESS SINCE 1979.", font=FONT_H1, fill=(0, 215, 255))
            draw.text((655, 455), "MONTGOMERYVILLE, PA:  754 Route 309  ·  (215) 368-8343", font=FONT_H2, fill=(255, 215, 110))
            draw.text((655, 502), "WAYNE / MAIN LINE, PA:  218 E Lancaster Ave  ·  (610) 649-7002", font=FONT_H2, fill=(255, 215, 110))
            draw.rounded_rectangle((655, 565, 1755, 645), radius=14, fill=(16, 38, 34), outline=(46, 235, 170), width=2)
            draw.text((685, 588), "VISIT WORLDWIDESTEREO.COM  |  DEMO PRODUCED BY 864ZEROS.COM", font=FONT_H2, fill=(46, 255, 180))

            # Bottom Row of 6 Employee Avatars + Names
            for idx in range(6):
                fn, name, role, _ = emp_specs[7 + idx]
                av = emp_avatars_sm[fn]
                cx = 190 + idx * 265
                cy = 720
                bg.paste(av, (cx + 42, cy), av)
                nb = draw.textbbox((0, 0), name, font=FONT_SM)
                draw.text((cx + 100 - (nb[2] - nb[0]) // 2, cy + 118), name, font=FONT_SM, fill=(255, 255, 255))

            draw_top_chrome(bg, draw, t, "ACT 07 // WORLD WIDE STEREO · MONTGOMERYVILLE & WAYNE, PA")
            draw_bottom_bar(bg, draw, "WORLDWIDESTEREO.COM — YOUR TECHNOLOGY ARCHITECTS SINCE 1979",
                            "Autonomous Site + Apify Social + Employee Promo Spot · Built & Published by 864zeros Media Studio",
                            accent=(46, 235, 170), progress=1.0)

        proc.stdin.write(bg.tobytes())

        # Capture key frames for contact sheet & thumbnail
        if f_idx in [45, 180, 330, 480, 615, 735, 840]:
            sample_frames[f_idx] = bg.copy()
        if f_idx == 840:
            thumb = bg.resize((1280, 720), Image.Resampling.LANCZOS)
            thumb.save(THUMB_OUT, quality=92)

    proc.stdin.close()
    proc.wait()
    print(f"3. Video rendered successfully -> {VIDEO_OUT} ({os.path.getsize(VIDEO_OUT) / (1024*1024):.2f} MB)")

    # Build contact sheet of all 7 acts
    cols = 2
    rows = 4
    tw, th = 640, 360
    sheet = Image.new("RGB", (cols * tw, rows * th), (10, 14, 22))
    sdraw = ImageDraw.Draw(sheet)
    keys = sorted(sample_frames.keys())
    for i, k in enumerate(keys):
        r = i // cols
        c = i % cols
        im_s = sample_frames[k].resize((tw - 12, th - 12), Image.Resampling.LANCZOS)
        sheet.paste(im_s, (c * tw + 6, r * th + 6))
        sdraw.rectangle((c * tw + 14, r * th + 14, c * tw + 210, r * th + 48), fill=(8, 12, 20))
        sdraw.text((c * tw + 24, r * th + 20), f"Frame {k} ({k/FPS:.1f}s)", font=FONT_BADGE, fill=(0, 215, 255))

    sheet.save(SHEET_OUT, quality=90)
    print(f"4. Saved contact sheet -> {SHEET_OUT}")

if __name__ == "__main__":
    main()
