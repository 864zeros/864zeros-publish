import os
import sys
import time
import shutil
import urllib.request
import subprocess
import imageio_ffmpeg
from gradio_client import Client, handle_file

JEFF_DIR = r"C:\dev\864zeros-publish\media\jeff"
PUBLIC_RIG_DIR = r"C:\dev\864zeros-pixel-office\public\kate-live-rig"
CROP_IMG = os.path.join(JEFF_DIR, "jeff_likeness_01_navy_blazer.jpg")
AUDIO_MP3 = os.path.join(JEFF_DIR, "jeff-likeness-voice.mp3")
RAW_MP4 = os.path.join(JEFF_DIR, "jeff-likeness-raw.mp4")
FINAL_MP4 = os.path.join(JEFF_DIR, "jeff-likeness-talking.mp4")
PUBLIC_MP4 = os.path.join(PUBLIC_RIG_DIR, "jeff-likeness-talking.mp4")

success = False

# Try 1: Engine B (KlingTeam/LivePortrait + ByteDance LatentSync)
try:
    print("Trying Engine B Stage 1: KlingTeam/LivePortrait...")
    driving_local = os.path.join(PUBLIC_RIG_DIR, "kate-neural-talking.mp4")
    lp = Client("KlingTeam/LivePortrait")
    res_lp = lp.predict(
        param_0=handle_file(CROP_IMG),
        param_1={"video": handle_file(driving_local), "subtitles": None},
        param_2=True,
        param_3=False,
        param_4=True,
        api_name="/gpu_wrapped_execute_video"
    )
    lp_vid = res_lp[0]["video"] if isinstance(res_lp[0], dict) else res_lp[0]
    lp_out = os.path.join(JEFF_DIR, "jeff-liveportrait-stage1.mp4")
    shutil.copyfile(lp_vid, lp_out)
    print("LivePortrait Stage 1 complete ->", lp_out)

    try:
        print("Trying Engine B Stage 2: fffiloni/LatentSync...")
        ls = Client("fffiloni/LatentSync")
        res_ls = ls.predict(
            input_video_path={"video": handle_file(lp_out), "subtitles": None},
            input_audio_path=handle_file(AUDIO_MP3),
            api_name="/generate_lip_sync_video"
        )
        ls_vid = res_ls["video"] if isinstance(res_ls, dict) else res_ls
        shutil.copyfile(ls_vid, RAW_MP4)
        print("LatentSync Stage 2 complete ->", RAW_MP4)
        success = True
    except Exception as e2:
        print("LatentSync Stage 2 note (using LivePortrait Stage 1):", str(e2)[:160])
        shutil.copyfile(lp_out, RAW_MP4)
        success = True
except Exception as e1:
    print("LivePortrait failed:", str(e1)[:160])

# Try 2: Lightricks/ltx-video-distilled
if not success:
    try:
        print("Trying Lightricks/ltx-video-distilled...")
        c = Client("Lightricks/ltx-video-distilled")
        res = c.predict(
            prompt="Cinematic medium close-up portrait of a distinguished silver-blonde bearded male CEO in a navy blazer and white open-collar shirt in a modern glass office. He looks directly into the camera and speaks warmly and articulately with natural lip movement, gentle head nods, and expressive eyes.",
            negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted, morphing face, bad anatomy",
            input_image_filepath=handle_file(CROP_IMG),
            input_video_filepath=None,
            height_ui=544,
            width_ui=640,
            mode="image-to-video",
            duration_ui=5.0,
            ui_frames_to_use=9,
            seed_ui=864,
            randomize_seed=False,
            ui_guidance_scale=1.0,
            improve_texture_flag=True,
            api_name="/image_to_video",
        )
        vid_path = res[0]["video"] if isinstance(res[0], dict) else res[0]
        shutil.copyfile(vid_path, RAW_MP4)
        print("LTX-Video complete ->", RAW_MP4)
        success = True
    except Exception as e3:
        print("LTX-Video failed:", str(e3)[:160])

if not success:
    sys.exit(1)

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
# Loop video if shorter than audio so the full 11.7s spoken intro plays cleanly
cmd = [
    ffmpeg_exe, "-y",
    "-stream_loop", "-1",
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
shutil.copyfile(FINAL_MP4, os.path.join(JEFF_DIR, "jeff-neural-talking.mp4"))
shutil.copyfile(FINAL_MP4, os.path.join(PUBLIC_RIG_DIR, "jeff-neural-talking.mp4"))
print("SUCCESS! Saved to:", PUBLIC_MP4)
