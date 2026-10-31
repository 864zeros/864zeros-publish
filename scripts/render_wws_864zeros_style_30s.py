import asyncio
import math
import os
import subprocess
import wave
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont
import edge_tts
import imageio_ffmpeg

OUT_DIR = r"C:\dev\864zeros-publish\media\video\wws_demo_promo"
VID_DIR = os.path.join(OUT_DIR, "scraped_videos")
IMG_DIR = os.path.join(OUT_DIR, "scraped_images")
AUD_DIR = os.path.join(OUT_DIR, "audio_v2")
os.makedirs(AUD_DIR, exist_ok=True)

OUT_MP4 = os.path.join(OUT_DIR, "wws_864zeros_sovereign_style_30s_16x9.mp4")
THUMB_OUT = os.path.join(OUT_DIR, "wws_864zeros_sovereign_style_thumb.jpg")
SHEET_OUT = r"C:\Users\Jeff\.gemini\antigravity-cli\brain\a8bc81a3-5510-464b-8325-5b18dd52cc96\wws_864zeros_style_contact_sheet.jpg"

W, H = 1920, 1080
FPS = 30
TOTAL_DUR = 30.0
TOTAL_FRAMES = int(TOTAL_DUR * FPS)  # 900 frames
SR = 44100
TOTAL_SAMPLES = int(TOTAL_DUR * SR)

def load_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

FONT_TAG = load_font(20, bold=True)
FONT_LOWER_TITLE = load_font(28, bold=True)
FONT_LOWER_SUB = load_font(20, bold=False)
FONT_CAP = load_font(32, bold=True)
FONT_HERO_BIG = load_font(72, bold=True)
FONT_HERO_MED = load_font(32, bold=False)
FONT_HERO_SM = load_font(23, bold=True)

# Voiceover segments timed to our 30.0s 864zeros Sovereign Film cadence
VO_SEGMENTS = [
    (0.30, "seg_01.wav", "Since 1979, World Wide Stereo has crafted spaces\nthat change the way you experience sound and cinema."),
    (6.20, "seg_02.wav", "Inside our Wayne and Montgomeryville Experience Centers,\nevery room is engineered for pure acoustic emotion."),
    (12.30, "seg_03.wav", "From founder Bob Cole, Ron Rumer, and Mario Patelmo\nto our master system designers and installation architects—"),
    (18.50, "seg_04.wav", "we bring reference McIntosh listening rooms\nand Dolby Atmos private theaters to life."),
    (24.00, "seg_05.wav", "World Wide Stereo. Awe-inspired since 1979."),
]

async def synth_vo_segments(ffmpeg_exe):
    for _, wav_name, txt in VO_SEGMENTS:
        wav_path = os.path.join(AUD_DIR, wav_name)
        mp3_path = wav_path.replace(".wav", ".mp3")
        clean_txt = txt.replace("\n", " ").replace("—", ", ")
        comm = edge_tts.Communicate(clean_txt, voice="en-US-AndrewMultilingualNeural", rate="+6%", pitch="-2Hz")
        await comm.save(mp3_path)
        subprocess.run([
            ffmpeg_exe, "-y", "-i", mp3_path,
            "-ar", str(SR), "-ac", "2", wav_path
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def build_master_audio(ffmpeg_exe):
    asyncio.run(synth_vo_segments(ffmpeg_exe))
    vo_buf = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)
    caption_windows = []

    for start_sec, wav_name, cap_text in VO_SEGMENTS:
        wav_path = os.path.join(AUD_DIR, wav_name)
        with wave.open(wav_path, "rb") as wf:
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)
            samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            if wf.getnchannels() == 2:
                samples = samples.reshape(-1, 2)
            else:
                samples = np.column_stack([samples, samples])
        s_idx = int(start_sec * SR)
        e_idx = min(TOTAL_SAMPLES, s_idx + len(samples))
        vo_buf[s_idx:e_idx] += samples[: e_idx - s_idx] * 1.12
        dur_sec = len(samples) / float(SR)
        if "\n" in cap_text:
            parts = cap_text.split("\n")
            mid = start_sec + dur_sec * 0.50
            caption_windows.append((start_sec, mid, parts[0]))
            caption_windows.append((mid, start_sec + dur_sec + 0.12, parts[1]))
        else:
            caption_windows.append((start_sec, start_sec + dur_sec + 0.15, cap_text))

    # Signature 864zeros warm D-minor-9th analog cinema score + subtle heartbeat pulse
    t = np.linspace(0, TOTAL_DUR, TOTAL_SAMPLES, endpoint=False, dtype=np.float32)
    freqs = [73.42, 110.0, 146.83, 174.61, 220.0, 261.63, 329.63]
    pad_l = np.zeros_like(t)
    pad_r = np.zeros_like(t)
    for idx, f in enumerate(freqs):
        amp = 0.18 / (idx + 1) ** 0.65
        lfo = 0.85 + 0.15 * np.sin(2 * math.pi * (0.11 + idx * 0.03) * t + idx)
        pad_l += amp * lfo * np.sin(2 * math.pi * f * t + idx * 0.4)
        pad_r += amp * lfo * np.sin(2 * math.pi * (f * 1.0015) * t + idx * 0.9)

    beat_env = np.exp(-6.5 * np.mod(t, 1.0)) * np.sin(2 * math.pi * 55.0 * t) * 0.06
    music_l = pad_l + beat_env
    music_r = pad_r + beat_env

    vo_env = np.abs(vo_buf[:, 0])
    kernel = np.ones(int(SR * 0.25), dtype=np.float32) / int(SR * 0.25)
    vo_smooth = np.convolve(vo_env, kernel, mode="same")
    duck = np.clip(1.0 - vo_smooth * 2.2, 0.32, 1.0)

    fade = np.ones_like(t)
    fade[: int(SR * 0.8)] = np.linspace(0.0, 1.0, int(SR * 0.8))
    fade[int(SR * 28.5) :] = np.linspace(1.0, 0.0, TOTAL_SAMPLES - int(SR * 28.5))

    mix_l = np.clip(vo_buf[:, 0] + music_l * duck * fade * 0.40, -0.98, 0.98)
    mix_r = np.clip(vo_buf[:, 1] + music_r * duck * fade * 0.40, -0.98, 0.98)
    mix_int16 = (np.column_stack([mix_l, mix_r]) * 32767.0).astype(np.int16)

    master_wav = os.path.join(AUD_DIR, "master_wws_sovereign_30s.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(mix_int16.tobytes())
    return master_wav, caption_windows

def apply_cinema_grade(rgb_np, flare_x=None, flare_strength=0.0):
    """Apply subtle 864zeros cinema contrast/warmth grade + optional anamorphic window flare."""
    arr = rgb_np.astype(np.float32)
    # Slight S-curve contrast and warm highlight / cool shadow split-tone
    arr = (arr - 128.0) * 1.06 + 128.0
    arr[:, :, 0] *= 1.02  # warm red/amber lift
    arr[:, :, 2] *= 1.01
    if flare_x is not None and flare_strength > 0:
        yy, xx = np.mgrid[0:H, 0:W]
        cx = int(flare_x * W)
        cy = int(0.46 * H)
        # Horizontal anamorphic streak + warm glow
        dist_sq = ((xx - cx) / 420.0) ** 2 + ((yy - cy) / 140.0) ** 2
        glow = np.exp(-dist_sq) * flare_strength
        arr[:, :, 0] += glow * 55.0
        arr[:, :, 1] += glow * 38.0
        arr[:, :, 2] += glow * 18.0
    return np.clip(arr, 0, 255).astype(np.uint8)

def generate_flyby_frames(img_path, n_frames, mode="drone_flyby_right", flare=True):
    """
    Generate 3D perspective drone fly-by / interior fly-through frames from high-res showroom photography.
    Uses 3D homography warp + camera dolly + subtle yaw/pitch so architecture moves with true depth.
    """
    im = Image.open(img_path).convert("RGB")
    # Upscale to super-resolution working canvas for razor-sharp homography warp
    sw, sh = 2880, 1620
    im_ratio = im.width / float(im.height)
    target_ratio = sw / float(sh)
    if im_ratio > target_ratio:
        nh = sh
        nw = int(nh * im_ratio)
    else:
        nw = sw
        nh = int(nw / im_ratio)
    im_resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    ox = (nw - sw) // 2
    oy = (nh - sh) // 2
    src_np = np.array(im_resized.crop((ox, oy, ox + sw, oy + sh)))

    frames = []
    for i in range(n_frames):
        u = i / float(max(1, n_frames - 1))
        # Smooth ease-in-out
        s = 0.5 - 0.5 * math.cos(math.pi * u)

        if mode == "drone_flyby_right":
            # Sweeping low-altitude drone fly-by across the Wayne showroom facade with perspective yaw
            zoom = 1.12 + 0.14 * s
            pan_x = -0.75 + 1.50 * s
            pan_y = 0.15 - 0.30 * s
            yaw = -0.035 + 0.070 * s
            pitch = 0.015 * (1.0 - s)
        elif mode == "interior_flythrough":
            # Forward camera dolly gliding deep into the showroom listening lounge
            zoom = 1.04 + 0.24 * s
            pan_x = -0.25 + 0.50 * s
            pan_y = 0.10 - 0.25 * s
            yaw = -0.020 + 0.040 * s
            pitch = -0.015 * s
        elif mode == "drone_flyover_pullback":
            # High-altitude fly-over pulling back & rising above the showroom
            zoom = 1.28 - 0.20 * s
            pan_x = 0.55 - 1.10 * s
            pan_y = -0.20 + 0.45 * s
            yaw = 0.030 - 0.060 * s
            pitch = -0.020 + 0.035 * s
        else:  # cinema_glide
            zoom = 1.08 + 0.16 * s
            pan_x = -0.45 + 0.90 * s
            pan_y = 0.08 - 0.16 * s
            yaw = -0.022 + 0.044 * s
            pitch = 0.0

        # Compute 3D perspective quadrilateral on the (sw, sh) canvas
        cw = sw / zoom
        ch = sh / zoom
        max_dx = (sw - cw) * 0.48
        max_dy = (sh - ch) * 0.48
        cx = sw * 0.5 + pan_x * max_dx
        cy = sh * 0.5 + pan_y * max_dy

        x0, x1 = cx - cw * 0.5, cx + cw * 0.5
        y0, y1 = cy - ch * 0.5, cy + ch * 0.5

        # Perspective keystone offsets for 3D yaw & pitch
        dy_left = ch * yaw
        dy_right = -ch * yaw
        dx_top = cw * pitch
        dx_bot = -cw * pitch

        src_pts = np.float32([
            [x0 + dx_top, y0 + dy_left],
            [x1 - dx_top, y0 + dy_right],
            [x1 - dx_bot, y1 - dy_right],
            [x0 + dx_bot, y1 - dy_left],
        ])
        dst_pts = np.float32([
            [0, 0],
            [W, 0],
            [W, H],
            [0, H],
        ])
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(src_np, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT_101)
        fl_x = 0.25 + 0.50 * s if flare else None
        fl_str = 0.55 * math.sin(math.pi * s) if flare else 0.0
        frames.append(apply_cinema_grade(warped, flare_x=fl_x, flare_strength=fl_str))
    return frames

def extract_video_subclip(vid_path, start_sec, dur_sec, target_frames, zoom=1.04, pan_dir=1.0):
    """Extract real 1080p video frames from official WWS films with subtle cinema push-in."""
    cap = cv2.VideoCapture(vid_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    start_f = int(start_sec * fps)
    raw_count = max(8, int(dur_sec * fps))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_f)

    raw_frames = []
    for _ in range(raw_count):
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        raw_frames.append(rgb)
    cap.release()

    if not raw_frames:
        raise RuntimeError(f"Could not read frames from {vid_path} at {start_sec}s")

    indices = np.linspace(0, len(raw_frames) - 1, target_frames)
    out = []
    for k, idx in enumerate(indices):
        u = k / float(max(1, target_frames - 1))
        i0 = int(math.floor(idx))
        i1 = min(len(raw_frames) - 1, i0 + 1)
        alpha = idx - i0
        blended = cv2.addWeighted(raw_frames[i0], 1.0 - alpha, raw_frames[i1], alpha, 0)

        # Fit 16:9 with subtle cinema camera drift
        ih, iw = blended.shape[:2]
        z = zoom + 0.04 * u
        cw = int(iw / z)
        ch = int(cw * H / float(W))
        if ch > ih:
            ch = int(ih / z)
            cw = int(ch * W / float(H))
        ox = int((iw - cw) * (0.5 + 0.25 * pan_dir * (u - 0.5)))
        oy = int((ih - ch) * 0.5)
        ox = max(0, min(iw - cw, ox))
        oy = max(0, min(ih - ch, oy))
        cropped = blended[oy:oy + ch, ox:ox + cw]
        resized = cv2.resize(cropped, (W, H), interpolation=cv2.INTER_LANCZOS4)
        out.append(apply_cinema_grade(resized))
    return out

def main():
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    print("1. Building 30.0s 864zeros Sovereign Film audio master...")
    master_wav, caption_windows = build_master_audio(ffmpeg_exe)

    p_wayne_ext = os.path.join(IMG_DIR, "wayne_extra_20250915-MKT-Wayne-Showroom-Header-3000x1280_2800x@3x.jpg")
    p_wayne_int = os.path.join(IMG_DIR, "wayne_extra_visit-showroom-bckg_desktop_2800x@3x.jpg")
    p_mont_int = os.path.join(IMG_DIR, "wayne_extra_Portfolio-Showroom-Montgomeryville-42-1200x1200_4a965a11-9487-48d8-9e31-36d030623bf7.jpg")
    p_wayne_det = os.path.join(IMG_DIR, "wayne_extra_20250915-MKT-Wayne-Showroom-Detail.jpg")
    p_cinema = os.path.join(IMG_DIR, "home_theater_hero.jpg")
    p_mont_ext = os.path.join(IMG_DIR, "wayne_extra_20240404-WEB-Showrooms-Page-Header-3000x1500_2800x@3x.jpg")

    v_about = os.path.join(VID_DIR, "yt_about_us_official.mp4")
    v_mcintosh = os.path.join(VID_DIR, "yt_mcintosh_room_official.mp4")

    # 9 Widescreen Cinema Shots (total 27.6s + 2.4s Sovereign Film End Card = 30.0s)
    XFADE = 6
    shots_spec = [
        {
            "dur": 3.20,
            "type": "flyby",
            "path": p_wayne_ext,
            "mode": "drone_flyby_right",
            "tag": "SCENE 01 // WAYNE, PA SHOWROOM EXTERIOR FLY-BY",
            "title": "WORLD WIDE STEREO · WAYNE, PA",
            "sub": "218 E Lancaster Ave · Home Technology Experience Center",
        },
        {
            "dur": 3.00,
            "type": "video_combo",
            "parts": [
                (v_about, 37.3, 1.3, 1.04, 1.0),   # Brushed steel WORLD WIDE STEREO AWE INSPIRED wall
                (v_about, 1.8, 1.7, 1.05, -1.0),   # Founder Bob Cole speaking in listening room
            ],
            "tag": "SCENE 02 // FOUNDER & HERITAGE · EST. 1979",
            "title": "BOB COLE · FOUNDER & CEO",
            "sub": "Awe Inspired Since 1979 · Over Four Decades of Acoustic Craft",
        },
        {
            "dur": 3.10,
            "type": "flyby",
            "path": p_wayne_int,
            "mode": "interior_flythrough",
            "tag": "SCENE 03 // SHOWROOM INTERIOR FLY-THROUGH",
            "title": "REFERENCE LISTENING LOUNGES",
            "sub": "Wayne & Montgomeryville Showrooms · McIntosh & Bowers & Wilkins",
        },
        {
            "dur": 3.20,
            "type": "video_combo",
            "parts": [
                (v_about, 46.8, 1.7, 1.04, 1.0),   # Bob Cole & Ron Rumer laughing in showroom
                (v_about, 72.5, 1.5, 1.05, -1.0),  # Ron Rumer cinematic profile
            ],
            "tag": "SCENE 04 // SHOWROOM LEADERSHIP · LIVE FOOTAGE",
            "title": "BOB COLE & RON RUMER",
            "sub": "Founder & Chief Regional Sales Director · Main Line & Montgomeryville",
        },
        {
            "dur": 3.10,
            "type": "flyby",
            "path": p_mont_int,
            "mode": "interior_flythrough",
            "tag": "SCENE 05 // SHOWROOM AMPLIFIER SANCTUARY FLY-OVER",
            "title": "THE MONOBLOCK & SPEAKER WALL",
            "sub": "Live A/B Auditioning inside our Pennsylvania Experience Centers",
        },
        {
            "dur": 3.20,
            "type": "video_combo",
            "parts": [
                (v_about, 82.0, 1.6, 1.04, 1.0),   # Mario Patelmo in showroom
                (v_about, 226.2, 1.6, 1.05, -1.0), # System Designer in showroom
            ],
            "tag": "SCENE 06 // SYSTEM ARCHITECTS & DESIGNERS",
            "title": "MARIO PATELMO & DESIGN TEAM",
            "sub": "Regional Showroom Manager & Custom Integration Specialists",
        },
        {
            "dur": 3.10,
            "type": "video_combo",
            "parts": [
                (v_mcintosh, 46.2, 1.5, 1.04, 1.0), # Tube glow & amplifier rack
                (v_mcintosh, 54.5, 1.6, 1.05, -1.0),# Placing vinyl on green McIntosh MT10 platter
            ],
            "tag": "SCENE 07 // WASHINGTON CROSSING LISTENING ROOM",
            "title": "McINTOSH · SONUS FABER · FOCAL",
            "sub": "Acoustically Treated Two-Channel & Vinyl Sanctuaries",
        },
        {
            "dur": 2.90,
            "type": "flyby",
            "path": p_cinema,
            "mode": "cinema_glide",
            "tag": "SCENE 08 // PRIVATE CINEMA FLY-OVER",
            "title": "DOLBY ATMOS PRIVATE CINEMAS",
            "sub": "Sony 4K Laser Projection · Custom Seating & Acoustic Architecture",
        },
        {
            "dur": 2.80,
            "type": "flyby",
            "path": p_mont_ext,
            "mode": "drone_flyover_pullback",
            "tag": "SCENE 09 // MONTGOMERYVILLE & WAYNE FLY-OVER",
            "title": "EXPERIENCE WHAT'S POSSIBLE",
            "sub": "Montgomeryville (754 Route 309) · Wayne (218 E Lancaster Ave)",
        },
    ]

    print("2. Building 9 widescreen cinema sequences (fly-bys + live 1080p showroom footage)...")
    raw_shot_sequences = []
    for s in shots_spec:
        n_f = int(round(s["dur"] * FPS)) + XFADE
        if s["type"] == "flyby":
            seq = generate_flyby_frames(s["path"], n_f, mode=s["mode"], flare=True)
        else:
            seq = []
            parts = s["parts"]
            for p_idx, (vp, st, dur_p, zm, pdir) in enumerate(parts):
                pf = n_f // len(parts) if p_idx < len(parts) - 1 else (n_f - len(seq))
                seq.extend(extract_video_subclip(vp, st, dur_p, pf, zoom=zm, pan_dir=pdir))
        raw_shot_sequences.append((seq, s))

    timeline_frames = []
    timeline_meta = []

    for idx, (seq, meta) in enumerate(raw_shot_sequences):
        if idx == 0:
            for f in seq[:-XFADE]:
                timeline_frames.append(f)
                timeline_meta.append(meta)
        else:
            prev_seq, prev_meta = raw_shot_sequences[idx - 1]
            tail = prev_seq[-XFADE:]
            head = seq[:XFADE]
            for k in range(XFADE):
                alpha = (k + 1) / float(XFADE + 1)
                blend = cv2.addWeighted(tail[k], 1.0 - alpha, head[k], alpha, 0)
                timeline_frames.append(blend)
                timeline_meta.append(meta if alpha >= 0.5 else prev_meta)
            body = seq[XFADE:-XFADE] if idx < len(raw_shot_sequences) - 1 else seq[XFADE:]
            for f in body:
                timeline_frames.append(f)
                timeline_meta.append(meta)

    end_card_count = max(0, TOTAL_FRAMES - len(timeline_frames))
    last_frame = timeline_frames[-1].copy()
    for k in range(end_card_count):
        timeline_frames.append(last_frame)
        timeline_meta.append({"end_card": True, "k": k, "total_k": end_card_count})

    print(f"   Assembled {len(timeline_frames)} frames ({len(timeline_frames)/FPS:.2f}s)")

    def render_overlay(frame_np, f_idx, meta):
        sec = f_idx / float(FPS)
        im = Image.fromarray(frame_np).convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Signature 864zeros 44px Cinema Letterbox Bars
        BAR_H = 44
        draw.rectangle([0, 0, W, BAR_H], fill=(8, 10, 14, 245))
        draw.rectangle([0, H - BAR_H, W, H], fill=(8, 10, 14, 245))

        if meta.get("end_card"):
            prog = min(1.0, meta["k"] / 14.0)
            bg_alpha = int(228 * prog)
            draw.rectangle([0, BAR_H, W, H - BAR_H], fill=(10, 13, 19, bg_alpha))
            if prog > 0.18:
                draw.rectangle([W // 2 - 90, 320, W // 2 + 90, 324], fill=(216, 166, 87, 255))
                t1 = "WORLD WIDE STEREO"
                b1 = draw.textbbox((0, 0), t1, font=FONT_HERO_BIG)
                draw.text(((W - (b1[2] - b1[0])) // 2, 350), t1, font=FONT_HERO_BIG, fill=(245, 247, 250, 255))

                t2 = "Delivering Happiness Since 1979. Experience What's Possible."
                b2 = draw.textbbox((0, 0), t2, font=FONT_HERO_MED)
                draw.text(((W - (b2[2] - b2[0])) // 2, 460), t2, font=FONT_HERO_MED, fill=(205, 214, 228, 255))

                t3 = "WAYNE, PA (218 E LANCASTER AVE)  ·  MONTGOMERYVILLE, PA (754 ROUTE 309)  ·  WORLDWIDESTEREO.COM"
                b3 = draw.textbbox((0, 0), t3, font=FONT_HERO_SM)
                draw.text(((W - (b3[2] - b3[0])) // 2, 535), t3, font=FONT_HERO_SM, fill=(216, 166, 87, 255))

                t4 = "864zeros.com   |   Sovereign Film Demo · Produced by 864zeros Studio"
                b4 = draw.textbbox((0, 0), t4, font=FONT_LOWER_SUB)
                draw.text(((W - (b4[2] - b4[0])) // 2, 615), t4, font=FONT_LOWER_SUB, fill=(155, 168, 188, 255))
        else:
            # Top-left 864zeros Sovereign Film badge
            draw.rounded_rectangle([48, 66, 405, 108], radius=6, fill=(10, 14, 20, 185), outline=(216, 166, 87, 140), width=1)
            draw.ellipse([64, 81, 76, 93], fill=(216, 166, 87, 255))
            draw.text((88, 75), "864ZEROS // SOVEREIGN FILM", font=FONT_TAG, fill=(240, 244, 250, 245))

            # Top-right camera scene telemetry tag
            tag_txt = meta["tag"]
            tb = draw.textbbox((0, 0), tag_txt, font=FONT_TAG)
            tw = tb[2] - tb[0]
            draw.rounded_rectangle([W - tw - 84, 66, W - 48, 108], radius=6, fill=(10, 14, 20, 175))
            draw.text((W - tw - 66, 75), tag_txt, font=FONT_TAG, fill=(216, 166, 87, 240))

            # Signature minimal lower-left glass lower-third
            draw.rounded_rectangle([48, H - 220, 740, H - 128], radius=8, fill=(10, 14, 20, 190))
            draw.rectangle([48, H - 220, 54, H - 128], fill=(216, 166, 87, 255))
            draw.text((70, H - 208), meta["title"], font=FONT_LOWER_TITLE, fill=(245, 247, 252, 255))
            draw.text((70, H - 168), meta["sub"], font=FONT_LOWER_SUB, fill=(185, 196, 212, 245))

        # Centered cinema subtitle pill
        active_cap = None
        for c_start, c_end, c_txt in caption_windows:
            if c_start <= sec <= c_end:
                active_cap = c_txt
                break
        if active_cap:
            cb = draw.textbbox((0, 0), active_cap, font=FONT_CAP)
            cw = cb[2] - cb[0]
            ch = cb[3] - cb[1]
            px = (W - cw) // 2
            py = H - 102
            draw.rounded_rectangle([px - 28, py - 10, px + cw + 28, py + ch + 16], radius=10, fill=(8, 11, 16, 215), outline=(255, 255, 255, 45), width=1)
            draw.text((px, py), active_cap, font=FONT_CAP, fill=(252, 253, 255, 255))

        comp = Image.alpha_composite(im, overlay).convert("RGB")
        return np.array(comp)

    print("3. Encoding 1080p @ 30fps Sovereign Film master...")
    temp_vid = os.path.join(OUT_DIR, "temp_sovereign_vid.mp4")
    cmd_vid = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo", "-vcodec", "rawvideo",
        "-s", f"{W}x{H}", "-pix_fmt", "rgb24", "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        "-pix_fmt", "yuv420p",
        temp_vid,
    ]

    sample_frames = {}
    sample_indices = [45, 135, 225, 315, 410, 505, 600, 690, 775, 865]

    proc = subprocess.Popen(cmd_vid, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    for idx, (f_np, meta) in enumerate(zip(timeline_frames, timeline_meta)):
        out_rgb = render_overlay(f_np, idx, meta)
        proc.stdin.write(out_rgb.tobytes())
        if idx in sample_indices:
            sample_frames[idx] = Image.fromarray(out_rgb)
        if idx == 45:
            Image.fromarray(out_rgb).resize((1280, 720), Image.Resampling.LANCZOS).save(THUMB_OUT, quality=92)
    proc.stdin.close()
    proc.wait()

    cmd_mux = [
        ffmpeg_exe, "-y",
        "-i", temp_vid,
        "-i", master_wav,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        OUT_MP4,
    ]
    subprocess.run(cmd_mux, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(temp_vid):
        os.remove(temp_vid)

    print(f"4. Mastered 1080p Sovereign Film saved -> {OUT_MP4} ({os.path.getsize(OUT_MP4)/(1024*1024):.2f} MB)")

    # Save 10-frame visual verification contact sheet
    cols, rows = 2, 5
    tw, th = 640, 360
    sheet = Image.new("RGB", (cols * tw, rows * th), (8, 10, 14))
    for i, k in enumerate(sorted(sample_frames.keys())):
        r, c = i // cols, i % cols
        im_s = sample_frames[k].resize((tw - 8, th - 8), Image.Resampling.LANCZOS)
        sheet.paste(im_s, (c * tw + 4, r * th + 4))
    sheet.save(SHEET_OUT, quality=90)
    print(f"5. Contact sheet saved -> {SHEET_OUT}")

if __name__ == "__main__":
    main()
