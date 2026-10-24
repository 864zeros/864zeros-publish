import os
import cv2
import wave
import math
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import imageio_ffmpeg

BASE_DIR = r"C:\dev\864zeros-publish\media\video\kate_864zeros_promo"
CLIPS_DIR = os.path.join(BASE_DIR, "clips")
AUD_DIR = os.path.join(BASE_DIR, "audio")
RIG_DIR = r"C:\dev\864zeros-pixel-office\public\kate-live-rig"
OUT_MP4 = os.path.join(BASE_DIR, "kate_864zeros_flagship_promo_16x9.mp4")
PUB_MP4 = os.path.join(RIG_DIR, "kate_864zeros_flagship_promo_16x9.mp4")

W, H = 1920, 1080
FPS = 30

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
FONT_CAP = load_font(34, bold=True)
FONT_HERO_BIG = load_font(76, bold=True)
FONT_HERO_MED = load_font(34, bold=False)
FONT_HERO_SM = load_font(24, bold=True)

# 1. Build Master Audio Track (43.5s @ 44100Hz stereo)
SR = 44100
TOTAL_DUR = 43.5
TOTAL_SAMPLES = int(TOTAL_DUR * SR)

vo_timeline = [
    (0.25, "seg_01.wav", "Every single day gives you 86,400 seconds."),
    (5.15, "seg_02.wav", "Yet modern software spends most of them renting back your own attention,\nand streaming your private workspace to someone else's cloud."),
    (13.20, "seg_03.wav", "At 864zeros, we build a different kind of software.\nQuiet, precision-engineered tools designed for sovereign custody."),
    (21.85, "seg_04.wav", "Zero telemetry leaks. Zero dark patterns.\nAnd zero recurring subscription rent."),
    (29.35, "seg_05.wav", "You acquire a tool once, it lives on your machine,\nand it belongs to you forever."),
    (34.95, "seg_06.wav", "I'm Kate Zefore. Welcome to 864zeros.\nOwn your tools. Own your time."),
]

vo_buf = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)
caption_windows = []

for start_sec, wav_name, cap_text in vo_timeline:
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
    vo_buf[s_idx:e_idx] += samples[: e_idx - s_idx] * 1.08
    dur_sec = len(samples) / float(SR)
    if "\n" in cap_text:
        parts = cap_text.split("\n")
        mid = start_sec + dur_sec * 0.50
        caption_windows.append((start_sec, mid, parts[0]))
        caption_windows.append((mid, start_sec + dur_sec + 0.15, parts[1]))
    else:
        caption_windows.append((start_sec, start_sec + dur_sec + 0.15, cap_text))

# Generate warm cinematic ambient score (D minor 9th warm analog pad + subtle pulse)
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
fade[: int(SR * 1.0)] = np.linspace(0.0, 1.0, int(SR * 1.0))
fade[int(SR * 41.5) :] = np.linspace(1.0, 0.0, TOTAL_SAMPLES - int(SR * 41.5))

mix_l = np.clip(vo_buf[:, 0] + music_l * duck * fade * 0.38, -0.98, 0.98)
mix_r = np.clip(vo_buf[:, 1] + music_r * duck * fade * 0.38, -0.98, 0.98)
mix_int16 = (np.column_stack([mix_l, mix_r]) * 32767.0).astype(np.int16)

master_wav = os.path.join(AUD_DIR, "master_promo_mix.wav")
with wave.open(master_wav, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(mix_int16.tobytes())
print("Saved master audio:", master_wav)

# 2. Define 9-Shot Pure Widescreen Image-to-Video Timeline (ZERO repeated clips)
shots_spec = [
    {
        "file": os.path.join(CLIPS_DIR, "clip_01_profile_window.mp4"),
        "dur": 3.50,
        "tag": "ANGLE 01 // 90° SKYLINE PROFILE",
        "title": "KATE ZEFORE (COS-001)",
        "sub": "Chief of Staff · 864zeros LLC",
    },
    {
        "file": os.path.join(CLIPS_DIR, "clip_02_profile_3quarter_office.mp4"),
        "dur": 4.50,
        "tag": "ANGLE 02 // 45° THREE-QUARTER PROFILE",
        "title": "THE ATTENTION ECONOMY TRAP",
        "sub": "Zero Cloud Surveillance · Sovereign Architecture",
    },
    {
        "file": os.path.join(CLIPS_DIR, "clip_03_profile_golden_skyline.mp4"),
        "dur": 4.00,
        "tag": "ANGLE 03 // GOLDEN HOUR HORIZON",
        "title": "86,400 SECONDS IN EVERY DAY",
        "sub": "Reclaiming Human Focus from Rental Software",
    },
    {
        "file": os.path.join(CLIPS_DIR, "clip_04_hq_analytics_founder.mp4"),
        "dur": 4.50,
        "tag": "SCENE 04 // 864ZEROS STUDIO HQ",
        "title": "FOUNDER & CHIEF OF STAFF BRIEFING",
        "sub": "Precision-Engineered Local-First Software",
    },
    {
        "file": os.path.join(CLIPS_DIR, "clip_05_mahogany_desk_writing.mp4"),
        "dur": 4.50,
        "tag": "SCENE 05 // EXECUTIVE DESK · 864 DAILY",
        "title": "BUILT FOR SOVEREIGN CUSTODY",
        "sub": "Quiet Craftsmanship · Local Execution",
    },
    {
        "file": os.path.join(CLIPS_DIR, "clip_06_brick_lab_briefing.mp4"),
        "dur": 4.00,
        "tag": "SCENE 06 // HARDWARE & SYSTEMS LAB",
        "title": "ZERO TELEMETRY · ZERO DARK PATTERNS",
        "sub": "Your Data Never Leaves Your Machine",
    },
    {
        "file": os.path.join(CLIPS_DIR, "clip_08b_strategy_1on1_window.mp4"),
        "dur": 4.50,
        "tag": "SCENE 07 // EXECUTIVE STRATEGY BRIEFING",
        "title": "ZERO RECURRING SUBSCRIPTION RENT",
        "sub": "One-Time Lifetime License · Pay Once, Keep Forever",
    },
    {
        "file": os.path.join(CLIPS_DIR, "clip_07_hq_mugs_laughing.mp4"),
        "dur": 4.00,
        "tag": "SCENE 08 // 864ZEROS LEADERSHIP TABLE",
        "title": "SOFTWARE THAT BELONGS TO YOU",
        "sub": "864zeros LLC · Sovereign Digital Craft",
    },
    {
        "file": os.path.join(CLIPS_DIR, "clip_09_hero_boardroom_speaking.mp4"),
        "dur": 5.00,
        "tag": "SCENE 09 // EXECUTIVE BOARDROOM",
        "title": "KATE ZEFORE · CHIEF OF STAFF",
        "sub": "Welcome to 864zeros · Own Your Tools · Own Your Time",
    },
]

def read_clip_frames(path, target_count):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing clip file: {path}")
    cap = cv2.VideoCapture(path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(rgb)
        cw, ch = im.size
        target_ratio = W / float(H)
        cur_ratio = cw / float(ch)
        if cur_ratio > target_ratio:
            nw = int(ch * target_ratio)
            off = (cw - nw) // 2
            im = im.crop((off, 0, off + nw, ch))
        else:
            nh = int(cw / target_ratio)
            off = (ch - nh) // 2
            im = im.crop((0, off, cw, off + nh))
        im = im.resize((W, H), Image.Resampling.LANCZOS)
        im = ImageEnhance.Contrast(im).enhance(1.05)
        im = ImageEnhance.Sharpness(im).enhance(1.12)
        frames.append(np.array(im))
    cap.release()
    if len(frames) >= target_count:
        return frames[:target_count]
    indices = np.linspace(0, len(frames) - 1, target_count)
    out = []
    for idx in indices:
        i0 = int(math.floor(idx))
        i1 = min(len(frames) - 1, i0 + 1)
        alpha = idx - i0
        blended = cv2.addWeighted(frames[i0], 1.0 - alpha, frames[i1], alpha, 0)
        out.append(blended)
    return out

XFADE = 6
raw_shot_sequences = []
for s in shots_spec:
    n_f = int(round(s["dur"] * FPS)) + XFADE
    seq = read_clip_frames(s["file"], n_f)
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

total_target_frames = int(TOTAL_DUR * FPS)
end_card_count = max(0, total_target_frames - len(timeline_frames))
last_frame = timeline_frames[-1].copy()

for k in range(end_card_count):
    timeline_frames.append(last_frame)
    timeline_meta.append({"end_card": True, "k": k, "total_k": end_card_count})

print(f"Total assembled frames: {len(timeline_frames)} ({len(timeline_frames)/FPS:.2f}s)")

def render_overlay(frame_np, f_idx, meta):
    sec = f_idx / float(FPS)
    im = Image.fromarray(frame_np).convert("RGBA")
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    BAR_H = 44
    draw.rectangle([0, 0, W, BAR_H], fill=(8, 10, 14, 245))
    draw.rectangle([0, H - BAR_H, W, H], fill=(8, 10, 14, 245))

    if meta.get("end_card"):
        prog = min(1.0, meta["k"] / 15.0)
        bg_alpha = int(225 * prog)
        draw.rectangle([0, BAR_H, W, H - BAR_H], fill=(10, 13, 19, bg_alpha))
        if prog > 0.20:
            draw.rectangle([W // 2 - 90, 340, W // 2 + 90, 344], fill=(216, 166, 87, 255))
            t1 = "864ZEROS"
            b1 = draw.textbbox((0, 0), t1, font=FONT_HERO_BIG)
            draw.text(((W - (b1[2] - b1[0])) // 2, 370), t1, font=FONT_HERO_BIG, fill=(245, 247, 250, 255))

            t2 = "86,400 Seconds in a Day. Own Your Tools. Own Your Time."
            b2 = draw.textbbox((0, 0), t2, font=FONT_HERO_MED)
            draw.text(((W - (b2[2] - b2[0])) // 2, 480), t2, font=FONT_HERO_MED, fill=(205, 214, 228, 255))

            t3 = "ONE-TIME LIFETIME LICENSE  ·  ZERO SUBSCRIPTIONS  ·  SOVEREIGN CUSTODY"
            b3 = draw.textbbox((0, 0), t3, font=FONT_HERO_SM)
            draw.text(((W - (b3[2] - b3[0])) // 2, 555), t3, font=FONT_HERO_SM, fill=(216, 166, 87, 255))

            t4 = "864zeros.com   |   Featuring Kate Zefore (COS-001)"
            b4 = draw.textbbox((0, 0), t4, font=FONT_LOWER_SUB)
            draw.text(((W - (b4[2] - b4[0])) // 2, 635), t4, font=FONT_LOWER_SUB, fill=(155, 168, 188, 255))
    else:
        draw.rounded_rectangle([48, 66, 390, 108], radius=6, fill=(10, 14, 20, 185), outline=(216, 166, 87, 140), width=1)
        draw.ellipse([64, 81, 76, 93], fill=(216, 166, 87, 255))
        draw.text((88, 75), "864ZEROS // SOVEREIGN FILM", font=FONT_TAG, fill=(240, 244, 250, 245))

        tag_txt = meta["tag"]
        tb = draw.textbbox((0, 0), tag_txt, font=FONT_TAG)
        tw = tb[2] - tb[0]
        draw.rounded_rectangle([W - tw - 84, 66, W - 48, 108], radius=6, fill=(10, 14, 20, 175))
        draw.text((W - tw - 66, 75), tag_txt, font=FONT_TAG, fill=(216, 166, 87, 240))

        draw.rounded_rectangle([48, H - 220, 650, H - 128], radius=8, fill=(10, 14, 20, 190))
        draw.rectangle([48, H - 220, 54, H - 128], fill=(216, 166, 87, 255))
        draw.text((70, H - 208), meta["title"], font=FONT_LOWER_TITLE, fill=(245, 247, 252, 255))
        draw.text((70, H - 168), meta["sub"], font=FONT_LOWER_SUB, fill=(185, 196, 212, 245))

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

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
temp_vid = os.path.join(BASE_DIR, "temp_video_only.mp4")

cmd_vid = [
    ffmpeg_exe, "-y",
    "-f", "rawvideo",
    "-vcodec", "rawvideo",
    "-s", f"{W}x{H}",
    "-pix_fmt", "rgb24",
    "-r", str(FPS),
    "-i", "-",
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "17",
    "-pix_fmt", "yuv420p",
    temp_vid,
]

proc = subprocess.Popen(cmd_vid, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
for idx, (f_np, meta) in enumerate(zip(timeline_frames, timeline_meta)):
    out_rgb = render_overlay(f_np, idx, meta)
    proc.stdin.write(out_rgb.tobytes())
proc.stdin.close()
proc.wait()

cmd_mux = [
    ffmpeg_exe, "-y",
    "-i", temp_vid,
    "-i", master_wav,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    "-shortest",
    OUT_MP4,
]
subprocess.run(cmd_mux, check=True)
if os.path.exists(temp_vid):
    os.remove(temp_vid)

shutil.copy(OUT_MP4, PUB_MP4)
print("Mastered 1080p promo saved to:", OUT_MP4)
print("Copied to live server path:", PUB_MP4)
print("Size MB:", round(os.path.getsize(OUT_MP4) / (1024 * 1024), 2))
