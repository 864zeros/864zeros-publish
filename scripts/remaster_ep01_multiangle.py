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
EP01_DIR = r"C:\dev\864zeros-publish\media\video\podcast_sovereign_frequency\s01e01"
TURNS_DIR = os.path.join(EP01_DIR, "turns_audio")
RIG_DIR = r"C:\dev\864zeros-pixel-office\public\kate-live-rig"

# Save to a NEW filename so we never overwrite existing media without approval (RULE-002)
OUT_MP4 = os.path.join(EP01_DIR, "sovereign_frequency_s01e01_multiangle_16x9.mp4")
PUB_MP4 = os.path.join(RIG_DIR, "sovereign_frequency_s01e01_multiangle_16x9.mp4")

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
FONT_HERO_BIG = load_font(72, bold=True)
FONT_HERO_MED = load_font(32, bold=False)
FONT_HERO_SM = load_font(23, bold=True)

# Selected 6 High-Impact Turns of Episode 01 (Director's Multi-Angle Cut — ~104s, 21 unique camera angles, zero repeats)
TURNS_SPEC = [
    {
        "turn_wav": "turn_01_kate.wav",
        "speaker": "KATE ZEFORE (COS-001)",
        "role": "Chief of Staff · Co-Host, The Sovereign Frequency",
        "topic": "ACT I // THE 86,400-SECOND SOVEREIGN MANDATE",
        "captions": [
            (0.0, 0.34, "Welcome to The Sovereign Frequency. Every day gives us 86,400 seconds—"),
            (0.34, 0.68, "and our mission at 864zeros is making sure you don't spend yours wrestling bloated software"),
            (0.68, 1.00, "or paying endless rent for simple tools. Sloane, let's start with what admins hit this week."),
        ],
        "angles": [
            (os.path.join(ROSTER_CLIPS, "campus_01_exterior_dusk.mp4"), "CAM 01 // 864ZEROS NORTHEAST CAMPUS"),
            (os.path.join(KATE_CLIPS, "clip_01_profile_window.mp4"), "CAM 02 // STUDIO A · KATE 90° PROFILE"),
            (os.path.join(KATE_CLIPS, "clip_04_hq_analytics_founder.mp4"), "CAM 03 // STUDIO HQ · TWO-SHOT BRIEFING"),
            (os.path.join(KATE_CLIPS, "clip_09_hero_boardroom_speaking.mp4"), "CAM 04 // STUDIO A · CENTER HOST CAM"),
        ]
    },
    {
        "turn_wav": "turn_02_sloane.wav",
        "speaker": "SLOANE STERLING (BRAND-012)",
        "role": "VP of Creative Studio · Co-Host, The Sovereign Frequency",
        "topic": "ACT I // THE TUESDAY NIGHT GOOGLE FORMS CRISIS",
        "captions": [
            (0.0, 0.33, "It's the classic Tuesday night scenario, Kate. You're a school coordinator or ops lead."),
            (0.33, 0.67, "All you want to do is cap a Google Form so once ten people sign up, that slot disappears."),
            (0.67, 1.00, "It's twenty lines of logic—yet the marketplace treats it like enterprise infrastructure."),
        ],
        "angles": [
            (os.path.join(ROSTER_CLIPS, "sloane_01_desk_speaking.mp4"), "CAM 05 // STUDIO B · SLOANE DESK CAM"),
            (os.path.join(ROSTER_CLIPS, "sloane_02_corridor_ipad.mp4"), "CAM 06 // STUDIO CORRIDOR · TRACKING CAM"),
            (os.path.join(KATE_CLIPS, "clip_02_profile_3quarter_office.mp4"), "CAM 07 // STUDIO A · KATE REACTION CAM"),
            (os.path.join(ROSTER_CLIPS, "sloane_03_profile_pipeline.mp4"), "CAM 08 // STUDIO B · 45° PIPELINE PROFILE"),
            (os.path.join(ROSTER_CLIPS, "sloane_04_whiteboard_timeline.mp4"), "CAM 09 // STUDIO B · WHITEBOARD ARCHITECTURE"),
        ]
    },
    {
        "turn_wav": "turn_04_sloane.wav",
        "speaker": "SLOANE STERLING (BRAND-012)",
        "role": "VP of Creative Studio · Introducing CPO Audrey Chen",
        "topic": "ACT II // WHY INCUMBENTS PROXY YOUR SPREADSHEETS",
        "captions": [
            (0.0, 0.45, "Which brings in our Chief Product Officer, Audrey Chen. Audrey, when we audited the top plugins,"),
            (0.45, 1.00, "why were so many routing basic spreadsheet rows through external vendor servers in the first place?"),
        ],
        "angles": [
            (os.path.join(ROSTER_CLIPS, "kate_allegra_01_corridor_walk.mp4"), "CAM 10 // EXECUTIVE WING · STEADICAM WALK"),
            (os.path.join(KATE_CLIPS, "clip_05_mahogany_desk_writing.mp4"), "CAM 11 // EXECUTIVE DESK · AUDIT NOTES"),
            (os.path.join(ROSTER_CLIPS, "campus_02_aerial_lake.mp4"), "CAM 12 // AERIAL DRONE · 864ZEROS CAMPUS"),
        ]
    },
    {
        "turn_wav": "turn_06_audrey.wav",
        "speaker": "AUDREY CHEN (CPO-004)",
        "role": "Chief Product Officer · 864zeros Product Architecture",
        "topic": "ACT II // [864F] CHOICEGUARD & FORM2DOCX NATIVE LOCKS",
        "captions": [
            (0.0, 0.35, "When we built ChoiceGuard and Form2Docx, we flipped that rule completely."),
            (0.35, 0.70, "Every trigger runs inside your native Google Workspace using deterministic script locks."),
            (0.70, 1.00, "Your form submissions never touch an external server—and never ambush you with watermarks."),
        ],
        "angles": [
            (os.path.join(ROSTER_CLIPS, "audrey_01_roadmap_desk.mp4"), "CAM 13 // PRODUCT LAB · AUDREY CHEN (CPO)"),
            (os.path.join(ROSTER_CLIPS, "zane_01_code_workstation.mp4"), "CAM 14 // SYSTEMS LAB · ZANE FIELDS (CTO) LOCKS"),
            (os.path.join(ROSTER_CLIPS, "zane_02_speaking_screen.mp4"), "CAM 15 // ARCHITECTURE REVIEW · ZERO-PROXY"),
            (os.path.join(ROSTER_CLIPS, "allegra_01_analytics_briefing.mp4"), "CAM 16 // TELEMETRY AUDIT · ALLEGRA KATZ (CFO)"),
        ]
    },
    {
        "turn_wav": "turn_10_sloane.wav",
        "speaker": "SLOANE STERLING (BRAND-012)",
        "role": "VP of Creative Studio · The 18-Tool Sovereign Standard",
        "topic": "ACT III // ONE-TIME LIFETIME LICENSE · ZERO CUSTODY",
        "captions": [
            (0.0, 0.48, "Acquire once when you need unlimited scale, keep it forever, and never hand over workspace custody."),
            (0.48, 1.00, "That's the standard across all eighteen Google Workspace tools and our browser utility fleet."),
        ],
        "angles": [
            (os.path.join(KATE_CLIPS, "clip_06_brick_lab_briefing.mp4"), "CAM 17 // HARDWARE & SYSTEMS LAB"),
            (os.path.join(KATE_CLIPS, "clip_08b_strategy_1on1_window.mp4"), "CAM 18 // EXECUTIVE STRATEGY LOUNGE"),
            (os.path.join(KATE_CLIPS, "clip_07_hq_mugs_laughing.mp4"), "CAM 19 // LEADERSHIP ROUNDTABLE"),
        ]
    },
    {
        "turn_wav": "turn_12_kate.wav",
        "speaker": "KATE ZEFORE (COS-001)",
        "role": "Chief of Staff · 864zeros LLC",
        "topic": "OUTRO // MAKE EVERY SECOND COUNT · 864ZEROS.COM",
        "captions": [
            (0.0, 0.50, "I'm Kate Zefore. Make every one of your 86,400 seconds count—"),
            (0.50, 1.00, "and we'll see you on the next edition of The Sovereign Frequency."),
        ],
        "angles": [
            (os.path.join(KATE_CLIPS, "clip_03_profile_golden_skyline.mp4"), "CAM 20 // GOLDEN HOUR HORIZON"),
            (os.path.join(ROSTER_CLIPS, "prya_02_gtm_boardroom.mp4"), "CAM 21 // GTM COMMAND · PRYA VANCE (CMO)"),
        ]
    }
]

def read_clip_frames(path, target_count):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing clip: {path}")
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
    print("=== Assembling Episode 01 Multi-Angle Audio & 21-Camera Shot Timeline ===")
    pause_sec = 0.35
    pause_samples = int(SR * pause_sec)
    end_card_sec = 3.2

    pcm_chunks = []
    shots_spec = []
    caption_windows = []
    cur_sec = 0.0

    for t_spec in TURNS_SPEC:
        wav_p = os.path.join(TURNS_DIR, t_spec["turn_wav"])
        with wave.open(wav_p, "rb") as wf:
            n_f = wf.getnframes()
            sr = wf.getframerate()
            pcm = np.frombuffer(wf.readframes(n_f), dtype=np.int16).astype(np.float32) / 32768.0
        dur = len(pcm) / float(sr)
        total_turn_dur = dur + pause_sec
        pcm_chunks.append(pcm)
        pcm_chunks.append(np.zeros(pause_samples, dtype=np.float32))

        for r0, r1, c_txt in t_spec["captions"]:
            caption_windows.append((cur_sec + r0 * dur, cur_sec + r1 * dur + 0.15, c_txt))

        n_angles = len(t_spec["angles"])
        angle_dur = total_turn_dur / float(n_angles)
        for clip_path, cam_tag in t_spec["angles"]:
            shots_spec.append({
                "file": clip_path,
                "dur": angle_dur,
                "tag": cam_tag,
                "title": t_spec["speaker"],
                "sub": f"{t_spec['role']}  ·  {t_spec['topic']}",
            })
        cur_sec += total_turn_dur

    # Add end card silence + ambient pad
    pcm_chunks.append(np.zeros(int(SR * end_card_sec), dtype=np.float32))
    vo_mono = np.concatenate(pcm_chunks)
    total_dur = len(vo_mono) / float(SR)

    # Mix subtle warm broadcast underscore pad
    t = np.linspace(0, total_dur, len(vo_mono), endpoint=False, dtype=np.float32)
    pad = (
        0.045 * np.sin(2 * math.pi * 110.0 * t)
        + 0.030 * np.sin(2 * math.pi * 164.81 * t)
        + 0.022 * np.sin(2 * math.pi * 220.0 * t)
    )
    mix = np.clip(vo_mono * 1.05 + pad, -0.98, 0.98)
    mix_int16 = (mix * 32767.0).astype(np.int16)

    master_wav = os.path.join(EP01_DIR, "ep01_multiangle_audio.wav")
    with wave.open(master_wav, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(mix_int16.tobytes())
    print(f"Saved multi-angle audio ({total_dur:.2f}s) across {len(shots_spec)} distinct camera shots")

    XFADE = 6

    def render_overlay(frame_np, f_idx, meta):
        sec = f_idx / float(FPS)
        im = Image.fromarray(frame_np).convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        BAR_H = 42
        draw.rectangle([0, 0, W, BAR_H], fill=(8, 10, 14, 245))
        draw.rectangle([0, H - BAR_H, W, H], fill=(8, 10, 14, 245))

        if meta.get("end_card"):
            prog = min(1.0, meta["k"] / 15.0)
            bg_alpha = int(230 * prog)
            draw.rectangle([0, BAR_H, W, H - BAR_H], fill=(10, 13, 19, bg_alpha))
            if prog > 0.2:
                draw.rectangle([W // 2 - 90, 320, W // 2 + 90, 324], fill=(216, 166, 87, 255))
                t1 = "THE SOVEREIGN FREQUENCY"
                b1 = draw.textbbox((0, 0), t1, font=FONT_HERO_BIG)
                draw.text(((W - (b1[2] - b1[0])) // 2, 355), t1, font=FONT_HERO_BIG, fill=(245, 247, 250, 255))

                t2 = "Episode 01 · Why Your Spreadsheet Add-On Wants a Monthly Mortgage"
                b2 = draw.textbbox((0, 0), t2, font=FONT_HERO_MED)
                draw.text(((W - (b2[2] - b2[0])) // 2, 460), t2, font=FONT_HERO_MED, fill=(205, 214, 228, 255))

                t3 = "CHOICEGUARD  ·  FORM2DOCX  ·  SHEETSYNC  ·  CLEARSTREAK"
                b3 = draw.textbbox((0, 0), t3, font=FONT_HERO_SM)
                draw.text(((W - (b3[2] - b3[0])) // 2, 535), t3, font=FONT_HERO_SM, fill=(216, 166, 87, 255))

                t4 = "864zeros.com  |  One-Time Lifetime License · Zero Subscriptions · Sovereign Custody"
                b4 = draw.textbbox((0, 0), t4, font=FONT_LOWER_SUB)
                draw.text(((W - (b4[2] - b4[0])) // 2, 610), t4, font=FONT_LOWER_SUB, fill=(165, 178, 198, 255))
        else:
            draw.rounded_rectangle([48, 62, 520, 102], radius=6, fill=(10, 14, 20, 190), outline=(216, 166, 87, 140), width=1)
            draw.ellipse([64, 76, 76, 88], fill=(216, 166, 87, 255))
            draw.text((88, 70), "THE SOVEREIGN FREQUENCY // S01E01", font=FONT_TAG, fill=(240, 244, 250, 245))

            tag_txt = meta["tag"]
            tb = draw.textbbox((0, 0), tag_txt, font=FONT_TAG)
            tw = tb[2] - tb[0]
            draw.rounded_rectangle([W - tw - 84, 62, W - 48, 102], radius=6, fill=(10, 14, 20, 180))
            draw.text((W - tw - 66, 70), tag_txt, font=FONT_TAG, fill=(216, 166, 87, 240))

            draw.rounded_rectangle([48, H - 216, 980, H - 128], radius=8, fill=(10, 14, 20, 195))
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

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    temp_vid = os.path.join(EP01_DIR, "temp_ep01_multiangle.mp4")

    cmd_vid = [
        ffmpeg_exe, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "rgb24",
        "-r", str(FPS),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        temp_vid,
    ]

    proc = subprocess.Popen(cmd_vid, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    global_f_idx = 0
    prev_tail = None
    prev_meta = None
    last_frame = None

    for idx, s in enumerate(shots_spec):
        n_f = int(round(s["dur"] * FPS)) + XFADE
        seq = read_clip_frames(s["file"], n_f)
        if idx == 0:
            body = seq[:-XFADE]
            for f_np in body:
                proc.stdin.write(render_overlay(f_np, global_f_idx, s).tobytes())
                global_f_idx += 1
        else:
            head = seq[:XFADE]
            for k in range(XFADE):
                alpha = (k + 1) / float(XFADE + 1)
                blend = cv2.addWeighted(prev_tail[k], 1.0 - alpha, head[k], alpha, 0)
                m_use = s if alpha >= 0.5 else prev_meta
                proc.stdin.write(render_overlay(blend, global_f_idx, m_use).tobytes())
                global_f_idx += 1
            body = seq[XFADE:-XFADE] if idx < len(shots_spec) - 1 else seq[XFADE:]
            for f_np in body:
                proc.stdin.write(render_overlay(f_np, global_f_idx, s).tobytes())
                global_f_idx += 1
        prev_tail = seq[-XFADE:]
        prev_meta = s
        last_frame = seq[-1]
        print(f"  Streamed shot {idx+1}/{len(shots_spec)}: {s['tag']}")

    total_target_frames = int(total_dur * FPS)
    end_card_count = max(0, total_target_frames - global_f_idx)
    for k in range(end_card_count):
        proc.stdin.write(render_overlay(last_frame, global_f_idx, {"end_card": True, "k": k}).tobytes())
        global_f_idx += 1

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
    print("Mastered Multi-Angle Episode 01 saved to:", OUT_MP4)
    print("Copied to live server path:", PUB_MP4)
    print("Size MB:", round(os.path.getsize(OUT_MP4) / (1024 * 1024), 2))

if __name__ == "__main__":
    main()
