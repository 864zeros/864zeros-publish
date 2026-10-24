import os
import cv2
import wave
import math
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import imageio_ffmpeg

KATE_CLIPS = r"C:\dev\864zeros-publish\media\video\kate_864zeros_promo\clips"
ROSTER_CLIPS = r"C:\dev\864zeros-publish\media\video\multi_angle_studio\clips"
STUDIO_DIR = r"C:\dev\864zeros-publish\media\video\multi_angle_studio"
AUD_DIR = os.path.join(STUDIO_DIR, "audio")
os.makedirs(AUD_DIR, exist_ok=True)
RIG_DIR = r"C:\dev\864zeros-pixel-office\public\kate-live-rig"

OUT_MP4 = os.path.join(STUDIO_DIR, "live_edge_suite_gtm_promo_16x9.mp4")
PUB_MP4 = os.path.join(RIG_DIR, "live_edge_suite_gtm_promo_16x9.mp4")

EDGE_TTS_EXE = r"C:\Users\Jeff\AppData\Local\Programs\Python\Python313\Scripts\edge-tts.exe"
if not os.path.exists(EDGE_TTS_EXE):
    EDGE_TTS_EXE = r"C:\Users\Jeff\AppData\Local\Python\pythoncore-3.14-64\Scripts\edge-tts.exe"

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1920, 1080
FPS = 30
SR = 24000

def load_font(size, bold=False):
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

FONT_TAG = load_font(19, bold=True)
FONT_LOWER_TITLE = load_font(27, bold=True)
FONT_LOWER_SUB = load_font(19, bold=False)
FONT_CAP = load_font(30, bold=True)
FONT_HERO_BIG = load_font(68, bold=True)
FONT_HERO_MED = load_font(30, bold=False)
FONT_HERO_SM = load_font(22, bold=True)

# 100% RULE-003 Compliant GTM Script (Zero price numbers in dialogue/captions)
GTM_TURNS = [
    {
        "id": "gtm_01",
        "voice": "en-US-EmmaMultilingualNeural",
        "pitch": "+1Hz",
        "rate": "+4%",
        "speaker": "PRYA VANCE (CMO-003)",
        "role": "Chief Marketing Officer · 864zeros GTM Command",
        "text": "Your browser is where your most valuable thinking happens. Today, our flagship 864zeros Sovereign Extensions Suite is live on the Microsoft Edge Add-ons Store.",
        "captions": [
            (0.0, 0.46, "Your browser is where your most valuable thinking happens."),
            (0.46, 1.00, "Today, our flagship 864zeros Sovereign Extensions Suite is live on Microsoft Edge."),
        ],
        "angles": [
            (os.path.join(ROSTER_CLIPS, "campus_02_aerial_lake.mp4"), "CAM 01 // 864ZEROS CAMPUS · LIVE GTM LAUNCH"),
            (os.path.join(ROSTER_CLIPS, "prya_02_gtm_boardroom.mp4"), "CAM 02 // GTM COMMAND · PRYA VANCE (CMO)"),
        ]
    },
    {
        "id": "gtm_02",
        "voice": "en-US-AriaNeural",
        "pitch": "+1Hz",
        "rate": "+4%",
        "speaker": "AUDREY CHEN (CPO-004)",
        "role": "Chief Product Officer · VaultPilot & AutoOrganize: YTM",
        "text": "Capture clean Markdown into Obsidian with VaultPilot, silence algorithmic noise with TuneOut2FocusIn, and deduplicate massive YouTube Music libraries with AutoOrganize.",
        "captions": [
            (0.0, 0.48, "Capture clean Markdown into Obsidian with VaultPilot and focus with TuneOut2FocusIn,"),
            (0.48, 1.00, "or deduplicate massive YouTube Music playlists instantly with AutoOrganize: YTM."),
        ],
        "angles": [
            (os.path.join(ROSTER_CLIPS, "audrey_01_roadmap_desk.mp4"), "CAM 03 // PRODUCT LAB · VAULTPILOT & TUNEOUT2FOCUSIN"),
            (os.path.join(ROSTER_CLIPS, "sloane_03_profile_pipeline.mp4"), "CAM 04 // STUDIO B · AUTOORGANIZE: YTM"),
        ]
    },
    {
        "id": "gtm_03",
        "voice": "en-US-ChristopherNeural",
        "pitch": "+0Hz",
        "rate": "+4%",
        "speaker": "ZANE FIELDS (CTO-002)",
        "role": "Chief Technology Officer · 864z Chronicle & Signal2Noise",
        "text": "With 864z Chronicle and Signal2Noise, every session bookmark, reading queue, and focus filter executes 100% locally inside your browser—with zero cloud telemetry.",
        "captions": [
            (0.0, 0.50, "With 864z Chronicle and Signal2Noise, every session archive and focus filter"),
            (0.50, 1.00, "executes 100% locally inside your browser—with zero cloud telemetry."),
        ],
        "angles": [
            (os.path.join(ROSTER_CLIPS, "zane_01_code_workstation.mp4"), "CAM 05 // SYSTEMS LAB · ZANE FIELDS (CTO)"),
            (os.path.join(ROSTER_CLIPS, "zane_02_speaking_screen.mp4"), "CAM 06 // ARCHITECTURE · 864Z CHRONICLE & SIGNAL2NOISE"),
        ]
    },
    {
        "id": "gtm_04",
        "voice": "en-US-AvaMultilingualNeural",
        "pitch": "+2Hz",
        "rate": "+3%",
        "speaker": "KATE ZEFORE (COS-001)",
        "role": "Chief of Staff · Sovereign Ownership Guarantee",
        "text": "One-time lifetime license. Zero recurring subscriptions. Install the live 864zeros suite on Microsoft Edge and Chrome today at 864zeros.com.",
        "captions": [
            (0.0, 0.45, "One-time lifetime license. Zero recurring subscriptions."),
            (0.45, 1.00, "Install the live 864zeros suite on Microsoft Edge and Chrome today at 864zeros.com."),
        ],
        "angles": [
            (os.path.join(ROSTER_CLIPS, "allegra_01_analytics_briefing.mp4"), "CAM 07 // FINANCE BRIEFING · ZERO SUBSCRIPTION RENT"),
            (os.path.join(KATE_CLIPS, "clip_09_hero_boardroom_speaking.mp4"), "CAM 08 // EXECUTIVE BOARDROOM · KATE ZEFORE"),
        ]
    }
]

def read_clip_frames(path, target_count):
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
        im = ImageEnhance.Sharpness(im).enhance(1.10)
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

def main():
    print("=== Synthesizing Multi-Executive GTM Audio & 8-Camera Shot Timeline ===")
    pause_sec = 0.28
    pause_samples = int(SR * pause_sec)
    end_card_sec = 3.0

    pcm_chunks = []
    shots_spec = []
    caption_windows = []
    cur_sec = 0.0

    for t_spec in GTM_TURNS:
        mp3_p = os.path.join(AUD_DIR, f"{t_spec['id']}.mp3")
        wav_p = os.path.join(AUD_DIR, f"{t_spec['id']}.wav")
        if not os.path.exists(wav_p):
            subprocess.run([
                EDGE_TTS_EXE,
                "--voice", t_spec["voice"],
                f"--pitch={t_spec['pitch']}",
                f"--rate={t_spec['rate']}",
                "--text", t_spec["text"],
                "--write-media", mp3_p
            ], check=True)
            subprocess.run([
                FFMPEG_EXE, "-y", "-i", mp3_p, "-ac", "1", "-ar", str(SR), wav_p
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with wave.open(wav_p, "rb") as wf:
            n_f = wf.getnframes()
            pcm = np.frombuffer(wf.readframes(n_f), dtype=np.int16).astype(np.float32) / 32768.0
        dur = len(pcm) / float(SR)
        total_turn_dur = dur + pause_sec
        pcm_chunks.append(pcm)
        pcm_chunks.append(np.zeros(pause_samples, dtype=np.float32))

        for r0, r1, c_txt in t_spec["captions"]:
            caption_windows.append((cur_sec + r0 * dur, cur_sec + r1 * dur + 0.12, c_txt))

        n_angles = len(t_spec["angles"])
        angle_dur = total_turn_dur / float(n_angles)
        for clip_path, cam_tag in t_spec["angles"]:
            shots_spec.append({
                "file": clip_path,
                "dur": angle_dur,
                "tag": cam_tag,
                "title": t_spec["speaker"],
                "sub": t_spec["role"],
            })
        cur_sec += total_turn_dur

    pcm_chunks.append(np.zeros(int(SR * end_card_sec), dtype=np.float32))
    vo_mono = np.concatenate(pcm_chunks)
    total_dur = len(vo_mono) / float(SR)

    t = np.linspace(0, total_dur, len(vo_mono), endpoint=False, dtype=np.float32)
    pad = (
        0.055 * np.sin(2 * math.pi * 110.0 * t)
        + 0.035 * np.sin(2 * math.pi * 164.81 * t)
        + 0.025 * np.sin(2 * math.pi * 220.0 * t)
    )
    mix = np.clip(vo_mono * 1.06 + pad, -0.98, 0.98)
    mix_int16 = (mix * 32767.0).astype(np.int16)

    master_wav = os.path.join(AUD_DIR, "live_suite_gtm_master.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(mix_int16.tobytes())

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

    total_target_frames = int(total_dur * FPS)
    end_card_count = max(0, total_target_frames - len(timeline_frames))
    last_frame = timeline_frames[-1].copy()
    for k in range(end_card_count):
        timeline_frames.append(last_frame)
        timeline_meta.append({"end_card": True, "k": k})

    def render_overlay(frame_np, f_idx, meta):
        sec = f_idx / float(FPS)
        im = Image.fromarray(frame_np).convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        BAR_H = 42
        draw.rectangle([0, 0, W, BAR_H], fill=(8, 10, 14, 245))
        draw.rectangle([0, H - BAR_H, W, H], fill=(8, 10, 14, 245))

        if meta.get("end_card"):
            prog = min(1.0, meta["k"] / 14.0)
            bg_alpha = int(230 * prog)
            draw.rectangle([0, BAR_H, W, H - BAR_H], fill=(10, 13, 19, bg_alpha))
            if prog > 0.2:
                draw.rectangle([W // 2 - 90, 315, W // 2 + 90, 319], fill=(216, 166, 87, 255))
                t1 = "864ZEROS LIVE EXTENSIONS SUITE"
                b1 = draw.textbbox((0, 0), t1, font=FONT_HERO_BIG)
                draw.text(((W - (b1[2] - b1[0])) // 2, 350), t1, font=FONT_HERO_BIG, fill=(245, 247, 250, 255))

                t2 = "VaultPilot · TuneOut2FocusIn · AutoOrganize: YTM · 864z Chronicle · Signal2Noise"
                b2 = draw.textbbox((0, 0), t2, font=FONT_HERO_MED)
                draw.text(((W - (b2[2] - b2[0])) // 2, 455), t2, font=FONT_HERO_MED, fill=(205, 214, 228, 255))

                t3 = "LIVE NOW ON MICROSOFT EDGE ADD-ONS & CHROME WEB STORE"
                b3 = draw.textbbox((0, 0), t3, font=FONT_HERO_SM)
                draw.text(((W - (b3[2] - b3[0])) // 2, 530), t3, font=FONT_HERO_SM, fill=(216, 166, 87, 255))

                t4 = "864zeros.com  |  One-Time Lifetime License · Zero Subscriptions · Sovereign Custody"
                b4 = draw.textbbox((0, 0), t4, font=FONT_LOWER_SUB)
                draw.text(((W - (b4[2] - b4[0])) // 2, 605), t4, font=FONT_LOWER_SUB, fill=(165, 178, 198, 255))
        else:
            draw.rounded_rectangle([48, 62, 510, 102], radius=6, fill=(10, 14, 20, 190), outline=(216, 166, 87, 140), width=1)
            draw.ellipse([64, 76, 76, 88], fill=(52, 211, 153, 255))
            draw.text((88, 70), "864ZEROS // LIVE STORE SUITE GTM", font=FONT_TAG, fill=(240, 244, 250, 245))

            tag_txt = meta["tag"]
            tb = draw.textbbox((0, 0), tag_txt, font=FONT_TAG)
            tw = tb[2] - tb[0]
            draw.rounded_rectangle([W - tw - 84, 62, W - 48, 102], radius=6, fill=(10, 14, 20, 180))
            draw.text((W - tw - 66, 70), tag_txt, font=FONT_TAG, fill=(216, 166, 87, 240))

            draw.rounded_rectangle([48, H - 216, 760, H - 128], radius=8, fill=(10, 14, 20, 195))
            draw.rectangle([48, H - 216, 54, H - 128], fill=(216, 166, 87, 255))
            draw.text((70, H - 205), meta["title"], font=FONT_LOWER_TITLE, fill=(245, 247, 252, 255))
            draw.text((70, H - 166), meta["sub"], font=FONT_LOWER_SUB, fill=(185, 196, 212, 245))

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
            py = H - 100
            draw.rounded_rectangle([px - 26, py - 8, px + cw + 26, py + ch + 14], radius=10, fill=(8, 11, 16, 220), outline=(255, 255, 255, 45), width=1)
            draw.text((px, py), active_cap, font=FONT_CAP, fill=(252, 253, 255, 255))

        comp = Image.alpha_composite(im, overlay).convert("RGB")
        return np.array(comp)

    temp_vid = os.path.join(STUDIO_DIR, "temp_live_suite_gtm.mp4")
    cmd_vid = [
        FFMPEG_EXE, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
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
        FFMPEG_EXE, "-y",
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
    print("Mastered Live Suite GTM Promo saved to:", OUT_MP4)
    print("Copied to live server path:", PUB_MP4)
    print("Size MB:", round(os.path.getsize(OUT_MP4) / (1024 * 1024), 2))

if __name__ == "__main__":
    main()
