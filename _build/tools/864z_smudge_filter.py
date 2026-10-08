#!/usr/bin/env python3
"""864z-smudge-filter — Charcoal & Graphite Smudge Filter Tool for 864zeros

Applies directional advection, paper grain roughness, and diffusion softness
to vector SVGs and raster fine-art drawings. Can be run as a CLI tool or
as a local server receiving filter variables from the web UI.
"""

import argparse
import json
import math
import os
import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
from PIL import Image
import numpy as np

try:
    import vtracer
except ImportError:
    vtracer = None


def apply_native_svg_filter(
    input_svg: str,
    output_svg: str,
    angle: float = 45.0,
    dist: float = 9.0,
    soft: float = 3.0,
    tooth: float = 9.0,
    opacity: float = 0.55,
    filter_id: str = "charcoal_smudge",
) -> str:
    """Injects or updates a parameterized native SVG smudge filter inside an SVG file."""
    if not os.path.exists(input_svg):
        raise FileNotFoundError(f"Input SVG not found: {input_svg}")

    with open(input_svg, "r", encoding="utf-8") as f:
        content = f.read()

    rad = math.radians(angle)
    dx = round(abs(math.cos(rad) * dist) + soft, 2)
    dy = round(abs(math.sin(rad) * dist) + soft, 2)
    tooth_val = round(tooth, 1)
    op_val = round(opacity, 2)

    filter_def = f"""  <filter id="{filter_id}" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">
    <!-- Directional Advection Smear: angle={angle}deg dist={dist}px -->
    <feGaussianBlur in="SourceGraphic" stdDeviation="{dx} {dy}" result="directional_smear" />
    <!-- Paper Grain Roughness: tooth={tooth_val} -->
    <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" result="paper_tooth" />
    <feDisplacementMap in="directional_smear" in2="paper_tooth" scale="{tooth_val}" xChannelSelector="R" yChannelSelector="G" result="textured_smudge" />
    <!-- Charcoal Haze Opacity: {op_val} -->
    <feColorMatrix in="textured_smudge" type="matrix" 
      values="0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 {op_val} 0" result="charcoal_haze" />
    <feMerge>
      <feMergeNode in="charcoal_haze" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>"""

    # If file already has a <filter id="...">, replace it
    if f'id="{filter_id}"' in content:
        import re
        content = re.sub(
            rf'<filter id="{filter_id}".*?</filter>',
            filter_def.strip(),
            content,
            flags=re.DOTALL,
        )
    else:
        # Check if <defs> exists
        if "<defs>" in content:
            content = content.replace("<defs>", f"<defs>\n{filter_def}")
        else:
            # Wrap paths in <defs> and <g filter="...">
            first_path = content.find("<path")
            if first_path == -1:
                first_path = content.find("<g")
            
            if first_path != -1:
                header = content[:first_path]
                body = content[first_path:]
                
                # Check closing </svg>
                if body.rstrip().endswith("</svg>"):
                    body = body.rstrip()[:-6] + f"</g>\n</svg>"
                
                content = (
                    f'{header}<defs>\n{filter_def}\n</defs>\n'
                    f'<g id="artwork_smudged" filter="url(#{filter_id})">\n{body}'
                )

    os.makedirs(os.path.dirname(os.path.abspath(output_svg)), exist_ok=True)
    with open(output_svg, "w", encoding="utf-8") as f:
        f.write(content)

    return output_svg


def apply_advection_smudge(
    input_image: str,
    output_svg: str,
    output_jpg: str = None,
    strokes: list = None,
    strength: float = 0.85,
    radius: int = 70,
) -> tuple[str, str]:
    """Runs a discrete physics-based Advection-Diffusion simulation on raster art and traces to vector."""
    if not os.path.exists(input_image):
        raise FileNotFoundError(f"Input image not found: {input_image}")

    img = Image.open(input_image).convert("L")
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape

    if not strokes:
        # Default artistic strokes along face / center
        strokes = [
            (int(w * 0.53), int(h * 0.41), int(w * 0.47), int(h * 0.49), radius, strength, 14),
            (int(w * 0.55), int(h * 0.51), int(w * 0.49), int(h * 0.59), int(radius * 1.1), strength, 12),
            (int(w * 0.41), int(h * 0.30), int(w * 0.35), int(h * 0.36), int(radius * 0.9), strength * 0.9, 10),
        ]

    y_coords, x_coords = np.mgrid[0:h, 0:w].astype(np.float32)
    canvas = arr.copy()

    for sx, sy, ex, ey, rad, strn, steps in strokes:
        for step in range(steps):
            t0 = step / steps
            t1 = (step + 1) / steps
            p0 = np.array([sx + t0 * (ex - sx), sy + t0 * (ey - sy)], dtype=np.float32)
            p1 = np.array([sx + t1 * (ex - sx), sy + t1 * (ey - sy)], dtype=np.float32)
            v = p1 - p0

            dist = np.sqrt((x_coords - p1[0]) ** 2 + (y_coords - p1[1]) ** 2)
            mask = np.clip(1.0 - (dist / rad), 0.0, 1.0) ** 1.8

            src_x = np.clip(x_coords - strn * mask * v[0], 0, w - 1)
            src_y = np.clip(y_coords - strn * mask * v[1], 0, h - 1)

            x0 = np.floor(src_x).astype(int)
            x1 = np.clip(x0 + 1, 0, w - 1)
            y0 = np.floor(src_y).astype(int)
            y1 = np.clip(y0 + 1, 0, h - 1)

            wx = src_x - x0
            wy = src_y - y0

            c00 = canvas[y0, x0]
            c10 = canvas[y0, x1]
            c01 = canvas[y1, x0]
            c11 = canvas[y1, x1]

            warped = (1 - wx) * (1 - wy) * c00 + wx * (1 - wy) * c10 + (1 - wx) * wy * c01 + wx * wy * c11
            canvas = warped

    smudged_img = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))
    
    if not output_jpg:
        output_jpg = os.path.splitext(output_svg)[0] + ".jpg"

    os.makedirs(os.path.dirname(os.path.abspath(output_jpg)), exist_ok=True)
    smudged_img.save(output_jpg, quality=95)

    if vtracer:
        os.makedirs(os.path.dirname(os.path.abspath(output_svg)), exist_ok=True)
        vtracer.convert_image_to_svg_py(
            output_jpg, output_svg,
            "binary", "stacked", "spline",
            10, 6, 16, 60, 4.0, 10, 45, 2
        )

    return output_svg, output_jpg


class SmudgeServerHandler(SimpleHTTPRequestHandler):
    """Handles web requests, serving UI and receiving smudge parameters via POST."""

    def do_POST(self):
        if self.path == "/api/smudge":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                in_file = data.get("input")
                angle = float(data.get("angle", 45.0))
                dist = float(data.get("dist", 9.0))
                soft = float(data.get("soft", 3.0))
                tooth = float(data.get("tooth", 9.0))
                opacity = float(data.get("opacity", 0.55))
                out_file = data.get("out")
                mode = data.get("mode", "native")

                # Default fallback file if none supplied
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
                if not in_file:
                    in_file = os.path.join(base_dir, "media", "visuals", "rendered_art", "gestalt_raw_freehand_clean_strokes.svg")
                elif not os.path.isabs(in_file):
                    in_file = os.path.join(base_dir, in_file)

                if not out_file:
                    out_file = os.path.join(base_dir, "media", "visuals", "tablet_vector_pack_s8_ultra", "ui_custom_smudge.svg")
                elif not os.path.isabs(out_file):
                    out_file = os.path.join(base_dir, out_file)

                if mode == "native":
                    result_path = apply_native_svg_filter(
                        in_file, out_file, angle=angle, dist=dist, soft=soft, tooth=tooth, opacity=opacity
                    )
                    size_kb = os.path.getsize(result_path) / 1024
                    res = {
                        "status": "success",
                        "mode": "native",
                        "saved_file": result_path,
                        "size_kb": round(size_kb, 1),
                        "variables": {
                            "angle": angle, "dist": dist, "soft": soft, "tooth": tooth, "opacity": opacity
                        }
                    }
                else:
                    # Advection mode
                    jpg_ref = in_file if in_file.endswith((".jpg", ".png")) else in_file.replace(".svg", ".jpg")
                    svg_out, jpg_out = apply_advection_smudge(jpg_ref, out_file, strength=dist / 10.0)
                    size_kb = os.path.getsize(svg_out) / 1024
                    res = {
                        "status": "success",
                        "mode": "advection",
                        "saved_file": svg_out,
                        "saved_raster": jpg_out,
                        "size_kb": round(size_kb, 1)
                    }

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(res, indent=2).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def run_cli(args=None) -> int:
    parser = argparse.ArgumentParser(
        prog="864z-smudge-filter",
        description="Charcoal & Graphite Smudge Filter Tool (864zeros)",
    )
    parser.add_argument("input", nargs="?", help="Path to input SVG or image file")
    parser.add_argument("--angle", "-a", type=float, default=45.0, help="Smudge angle in degrees (default: 45)")
    parser.add_argument("--dist", "-d", type=float, default=9.0, help="Smudge displacement / distance (default: 9)")
    parser.add_argument("--soft", "-s", type=float, default=3.0, help="Diffusion softness (default: 3)")
    parser.add_argument("--tooth", "-t", type=float, default=9.0, help="Paper tooth roughness (default: 9)")
    parser.add_argument("--opacity", "-o", type=float, default=0.55, help="Charcoal haze opacity (default: 0.55)")
    parser.add_argument("--mode", "-m", choices=["native", "advection"], default="native", help="Smudge technique")
    parser.add_argument("--out", "-O", help="Output file path (default: <input>_smudged.svg)")
    parser.add_argument("--serve", "-S", action="store_true", help="Launch local HTTP server to receive UI variables")
    parser.add_argument("--port", "-p", type=int, default=8640, help="Server port (default: 8640)")
    parser.add_argument("--json", action="store_true", help="Output JSON response")

    parsed = parser.parse_args(args)

    if parsed.serve:
        web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "media", "visuals"))
        os.chdir(web_dir)
        server = HTTPServer(("0.0.0.0", parsed.port), SmudgeServerHandler)
        print(f"864z-smudge-filter server listening on http://localhost:{parsed.port}")
        print(f"Serving UI from: {web_dir}")
        print(f"API endpoint ready at: http://localhost:{parsed.port}/api/smudge")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
        return 0

    if not parsed.input:
        parser.print_help()
        return 1

    in_path = os.path.abspath(parsed.input)
    if not os.path.exists(in_path):
        print(f"Error: Input file not found: {in_path}", file=sys.stderr)
        return 2

    out_path = parsed.out
    if not out_path:
        base, _ = os.path.splitext(in_path)
        out_path = f"{base}_smudged.svg"
    out_path = os.path.abspath(out_path)

    if parsed.mode == "native":
        result = apply_native_svg_filter(
            in_path, out_path,
            angle=parsed.angle, dist=parsed.dist, soft=parsed.soft,
            tooth=parsed.tooth, opacity=parsed.opacity
        )
    else:
        result, _ = apply_advection_smudge(in_path, out_path, strength=parsed.dist / 10.0)

    size_kb = os.path.getsize(result) / 1024
    if parsed.json:
        print(json.dumps({
            "status": "success",
            "input": in_path,
            "output": result,
            "size_kb": round(size_kb, 1),
            "angle": parsed.angle,
            "dist": parsed.dist,
            "tooth": parsed.tooth
        }, indent=2))
    else:
        print(f"Smudged SVG created: {result} ({size_kb:.1f} KB)")
        print(f"Applied: angle={parsed.angle}° dist={parsed.dist}px soft={parsed.soft} tooth={parsed.tooth} opacity={parsed.opacity}")

    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
