import os
import sys
import time
import shutil
import socket
import asyncio
import subprocess
from PIL import Image
import edge_tts
import imageio_ffmpeg
from gradio_client import Client, handle_file

orig_getaddrinfo = socket.getaddrinfo
ACTIVE_PREFIX = None

def patched_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    res = orig_getaddrinfo(host, port, family, type, proto, flags)
    if ACTIVE_PREFIX and isinstance(host, str) and ("hf.space" in host or "huggingface.co" in host):
        v6_res = []
        for af, socktype, pr, canon, sa in res:
            if af == socket.AF_INET:
                ip4 = sa[0]
                hex_part = "{:02x}{:02x}:{:02x}{:02x}".format(*map(int, ip4.split(".")))
                v6_addr = ACTIVE_PREFIX + hex_part
                v6_res.append((socket.AF_INET6, socktype, pr, canon, (v6_addr, sa[1], 0, 0)))
        if v6_res:
            return v6_res
    return res

socket.getaddrinfo = patched_getaddrinfo

PREFIXES = [
    None,
    "2a00:1098:2b::1:",
    "2a01:4f9:c010:3f02:64::",
    "2001:67c:2960:6464::",
    "2602:fc59:b0:64::",
]

JEFF_DIR = r"C:\dev\864zeros-publish\media\jeff"
PUBLIC_RIG_DIR = r"C:\dev\864zeros-pixel-office\public\kate-live-rig"
os.makedirs(PUBLIC_RIG_DIR, exist_ok=True)

SRC_IMG = os.path.join(JEFF_DIR, "1791260036807.jpg")
CROP_IMG = os.path.join(JEFF_DIR, "jeff-video-base.jpg")
AUDIO_MP3 = os.path.join(JEFF_DIR, "jeff-neural-test.mp3")
RAW_MP4 = os.path.join(JEFF_DIR, "jeff-neural-moda-raw.mp4")
FINAL_MP4 = os.path.join(JEFF_DIR, "jeff-neural-talking.mp4")
PUBLIC_MP4 = os.path.join(PUBLIC_RIG_DIR, "jeff-neural-talking.mp4")
PUBLIC_CROP = os.path.join(PUBLIC_RIG_DIR, "jeff-video-base.jpg")

# 1. Crop head-and-shoulders (640x540) from 1791260036807.jpg
im = Image.open(SRC_IMG)
w, h = im.size
print(f"Source image size: {w}x{h}")
# In 1791260036807.jpg, Jeff's head & upper torso are in the upper-center
crop_w = int(w * 0.46)
crop_h = int(crop_w * (540 / 640))
cx = int(w * 0.50)
top = int(h * 0.06)
left = max(0, cx - crop_w // 2)
right = min(w, left + crop_w)
bottom = min(h, top + crop_h)

cropped = im.crop((left, top, right, bottom)).resize((640, 540), Image.Resampling.LANCZOS)
cropped.save(CROP_IMG, quality=95)
shutil.copyfile(CROP_IMG, PUBLIC_CROP)
print(f"Saved 640x540 portrait crop -> {CROP_IMG}")

# 2. Synthesize Neural Voice Track (en-US-BrianMultilingualNeural)
SCRIPT_TEXT = (
    "Hey team — Jeff here. Welcome to 864 zeros. "
    "There are eighty-six thousand four hundred seconds in a day, "
    "and we build local-first software you own outright, so every second stays yours."
)

async def build_voice():
    comm = edge_tts.Communicate(SCRIPT_TEXT, "en-US-BrianMultilingualNeural", rate="+2%", pitch="-2Hz")
    await comm.save(AUDIO_MP3)

asyncio.run(build_voice())
print(f"Synthesized voice track -> {AUDIO_MP3} ({os.path.getsize(AUDIO_MP3)} bytes)")

# 3. Call NVIDIA A10G MoDA-fast-talking-head
success = False
for pfx in PREFIXES:
    ACTIVE_PREFIX = pfx
    try:
        t0 = time.time()
        print(f"Dispatching to multimodalart/MoDA-fast-talking-head (prefix={pfx})...")
        client = Client("multimodalart/MoDA-fast-talking-head")
        res = client.predict(
            source_image_path=handle_file(CROP_IMG),
            driving_audio_path=handle_file(AUDIO_MP3),
            emotion_name="None",
            cfg_scale=1.2,
            api_name="/generate_motion"
        )
        vid_path = res["video"] if isinstance(res, dict) else res
        shutil.copyfile(vid_path, RAW_MP4)
        print(f"MoDA A10G render complete in {time.time() - t0:.1f}s -> {RAW_MP4}")
        success = True
        break
    except Exception as e:
        print(f"  Prefix {pfx} failed: {str(e)[:160]}")

if not success:
    print("MoDA quota/connection failed on all prefixes; falling back to Lightricks/ltx-video-distilled...")
    for pfx in PREFIXES:
        ACTIVE_PREFIX = pfx
        try:
            t0 = time.time()
            c = Client("Lightricks/ltx-video-distilled")
            res = c.predict(
                prompt="Cinematic medium close-up portrait of a distinguished silver-haired male CEO with glasses and a beard in a navy blazer on a brick street. He looks directly into the camera and speaks confidently and warmly with natural lip sync, subtle head nods, and natural eye blinks.",
                negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted, morphing face, bad anatomy",
                input_image_filepath=handle_file(CROP_IMG),
                input_video_filepath=None,
                height_ui=544,
                width_ui=640,
                mode="image-to-video",
                duration_ui=6.0,
                ui_frames_to_use=9,
                seed_ui=864,
                randomize_seed=False,
                ui_guidance_scale=1.0,
                improve_texture_flag=True,
                api_name="/image_to_video",
            )
            vid_path = res[0]["video"] if isinstance(res[0], dict) else res[0]
            shutil.copyfile(vid_path, RAW_MP4)
            print(f"LTX-Video render complete in {time.time() - t0:.1f}s -> {RAW_MP4}")
            success = True
            break
        except Exception as e:
            print(f"  LTX prefix {pfx} failed: {str(e)[:160]}")

if not success:
    sys.exit(1)

# 4. Remux faststart H.264 + 192kbps AAC audio
ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
cmd = [
    ffmpeg_exe, "-y",
    "-i", RAW_MP4,
    "-i", AUDIO_MP3,
    "-map", "0:v:0",
    "-map", "1:a:0",
    "-c:v", "libx264",
    "-preset", "fast",
    "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac",
    "-b:a", "192k",
    "-ar", "44100",
    "-shortest",
    "-movflags", "+faststart",
    FINAL_MP4
]
subprocess.run(cmd, check=True)
shutil.copyfile(FINAL_MP4, PUBLIC_MP4)
print(f"DONE! Final talking-head video saved to:\n  1) {FINAL_MP4}\n  2) {PUBLIC_MP4}")
