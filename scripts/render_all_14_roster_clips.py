import os
import shutil
import time
import socket
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

prefixes = [
    None,
    "2a00:1098:2b::1:",
    "2a01:4f9:c010:3f02:64::",
    "2001:67c:2960:6464::",
    "2602:fc59:b0:64::",
]

in_dir = r"C:\dev\864zeros-publish\media\video\multi_angle_studio\ingredients"
out_dir = r"C:\dev\864zeros-publish\media\video\multi_angle_studio\clips"
os.makedirs(out_dir, exist_ok=True)

shots = [
    ("campus_01_exterior_dusk.mp4", "campus_01_exterior_864zeros_dusk.jpg", 4.0, 101,
     "Cinematic slow push-in establishing shot of the modern black glass 864zeros headquarters building at dusk after rain. Warm interior office lights glow softly and reflect on the wet pavement. 4k cinema camera."),
    ("campus_02_aerial_lake.mp4", "campus_02_aerial_autumn_lake.jpg", 4.0, 102,
     "Cinematic aerial drone shot gliding smoothly over a modern tech campus surrounded by golden autumn forest and a calm lake at sunset. Smooth 4k drone cinematography."),
    ("kate_allegra_01_corridor_walk.mp4", "kate_allegra_01_corridor_walk.jpg", 4.5, 103,
     "Cinematic tracking shot in a modern glass office corridor. Two executive women in tailored dark suits walk forward side by side, speaking and smiling warmly in conversation. Natural walking motion, 4k ARRI Alexa."),
    ("sloane_01_desk_speaking.mp4", "sloane_01_desk_864_mug.jpg", 4.5, 104,
     "Cinematic medium close-up of a warm brunette woman with curly hair in a dark pinstripe blazer seated at a wood desk in a creative studio. She looks into the camera and speaks warmly and articulately with natural lip movement, gentle nods, and expressive eyes."),
    ("sloane_02_corridor_ipad.mp4", "sloane_02_corridor_ipad_walk.jpg", 4.0, 105,
     "Cinematic medium shot in a glass office corridor. A smiling woman with curly dark hair in a blazer holds a tablet and stylus, speaking warmly with a colleague across from her. Natural head movement and gestures."),
    ("sloane_03_profile_pipeline.mp4", "sloane_03_profile_pipeline_screen.jpg", 4.5, 106,
     "Cinematic side-profile shot of a female studio director with curly dark hair in an olive jacket seated in a briefing room in front of a production pipeline display. She speaks articulately and gestures naturally with both hands."),
    ("sloane_04_whiteboard_timeline.mp4", "sloane_04_whiteboard_timeline.jpg", 4.0, 107,
     "Cinematic shot in a bright studio. A woman with curly dark hair in a pinstripe blazer stands at a glass whiteboard holding a marker, smiling warmly at the camera and gesturing toward the storyboard diagram."),
    ("zane_01_code_workstation.mp4", "zane_01_code_workstation_pointing.jpg", 4.5, 108,
     "Cinematic side-profile shot of a male software architect with glasses in a white polo shirt seated at a multi-monitor coding workstation. He points at the code on the screen and explains the architecture calmly."),
    ("zane_02_speaking_screen.mp4", "zane_02_speaking_864zeros_screen.jpg", 4.5, 109,
     "Cinematic three-quarter portrait of a male CTO with glasses in a white 864zeros polo shirt speaking articulately in a dark studio, gesturing naturally with both hands as he explains local-first engineering."),
    ("allegra_01_analytics_briefing.mp4", "allegra_01_analytics_screen_briefing.jpg", 4.5, 110,
     "Cinematic medium shot in a glass boardroom. A silver-haired female CFO in a charcoal suit and glasses points with a stylus at a financial bar chart display while speaking with an analyst seated at the table."),
    ("audrey_01_roadmap_desk.mp4", "audrey_01_product_roadmap_desk.jpg", 4.5, 111,
     "Cinematic medium shot of an Asian female product executive in a grey blazer seated at her desk writing with a stylus on a tablet, then looking up thoughtfully with calm focus."),
    ("audrey_02_portfolio_command.mp4", "audrey_02_portfolio_command_briefing.jpg", 4.5, 112,
     "Cinematic boardroom shot of an Asian female CPO in a navy suit standing at the head of a conference table, speaking confidently and gesturing slightly as executives listen attentively."),
    ("prya_01_gtm_telemetry.mp4", "prya_01_gtm_monitor_telemetry.jpg", 4.5, 113,
     "Cinematic office shot of a female marketing executive in an emerald green blazer and glasses pointing at a computer monitor while reviewing live campaign telemetry with a seated engineer."),
    ("prya_02_gtm_boardroom.mp4", "prya_02_gtm_boardroom_864zeros.jpg", 4.5, 114,
     "Cinematic wide boardroom shot by city windows. A female CMO in an emerald green blazer stands by a presentation screen speaking energetically and gesturing with her hands to the executive team.")
]

p_idx = 0
for out_name, src_img, dur, seed, prompt in shots:
    out_p = os.path.join(out_dir, out_name)
    if os.path.exists(out_p) and os.path.getsize(out_p) > 50000:
        print("Already exists:", out_name)
        continue
    for attempt in range(len(prefixes)):
        ACTIVE_PREFIX = prefixes[(p_idx + attempt) % len(prefixes)]
        try:
            t0 = time.time()
            print(f"Generating {out_name} via prefix {ACTIVE_PREFIX}...")
            c = Client("Lightricks/ltx-video-distilled")
            res = c.predict(
                prompt=prompt,
                negative_prompt="worst quality, inconsistent motion, blurry, jittery, distorted, morphing face, bad anatomy, deformed hands",
                input_image_filepath=handle_file(os.path.join(in_dir, src_img)),
                input_video_filepath=None,
                height_ui=512,
                width_ui=896,
                mode="image-to-video",
                duration_ui=dur,
                ui_frames_to_use=9,
                seed_ui=seed,
                randomize_seed=False,
                ui_guidance_scale=1.0,
                improve_texture_flag=True,
                api_name="/image_to_video",
            )
            vid_file = res[0]["video"] if isinstance(res[0], dict) else res[0]
            shutil.copy(vid_file, out_p)
            print(f"  -> Saved {out_name} in {time.time()-t0:.1f}s!")
            p_idx = (p_idx + attempt) % len(prefixes)
            break
        except Exception as e:
            print(f"  -> Prefix {ACTIVE_PREFIX} err: {str(e)[:120]}")
