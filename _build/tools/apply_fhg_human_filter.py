#!/usr/bin/env python3
"""
864z FHG Canonical Sketch Filter Pipeline:
  - Locked Standard for Nature & Objects (`fhg_sketch_spec`):          G2 + S2
  - Locked Standard for Humans from the Back (`fhg_sketch_people_spec`): G2 + S3

Geometry Stroke-Straightening Ladder (G1-G5):
  - G1: epsilon=0.0px,  overshoot=0.00px (Unmodified freehand curves)
  - G2: epsilon=2.5px,  overshoot=0.15px (LOCKED DEFAULT — Subtle chiseled straight segments)
  - G3: epsilon=5.5px,  overshoot=0.35px (Planar straight-line draftsmanship)
  - G4: epsilon=9.5px,  overshoot=0.65px (Bold angular straight-edge strokes)
  - G5: epsilon=16.0px, overshoot=1.10px (Architectural straight-chord abstraction)

Humanization Filter Ladder (S1-S5):
  - S1 (stage1_algorithmic): scale=0.0, blur=(0.0, 0.0), haze_opacity=0.0
  - S2 (stage2_master):      baseFreq=0.045, octaves=3, scale=1.8, blur=(0.0, 0.0), haze_opacity=0.0 (LOCKED: Nature & Objects)
  - S3 (stage3_apprentice):  baseFreq=0.035, octaves=3, scale=3.8, blur=(1.5, 1.0), haze_opacity=0.35 (LOCKED: Humans from Back)
  - S4 (stage4_student):     baseFreq=0.025, octaves=3, scale=7.5, blur=(5.0, 2.2), haze_opacity=0.45, smear_scale=6.0
  - S5 (stage5_raw):         baseFreq=0.018, octaves=4, scale=14.5, blur=(9.0, 3.8), haze_opacity=0.60, smear_scale=12.0

Always applies `C:/dev/864zeros-publish/media/visuals/jeff_canonical_signature.png` in the bottom-right corner.
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

CANONICAL_SIG_PATH = r"C:\dev\864zeros-publish\media\visuals\jeff_canonical_signature.png"

STAGE_PRESETS = {
    "S1": {"freq": 0.045, "octaves": 1, "scale": 0.0,  "blur_x": 0.0, "blur_y": 0.0, "haze_opacity": 0.00, "smear_scale": 0.0},
    "S2": {"freq": 0.045, "octaves": 3, "scale": 1.8,  "blur_x": 0.0, "blur_y": 0.0, "haze_opacity": 0.00, "smear_scale": 0.0},
    "S3": {"freq": 0.035, "octaves": 3, "scale": 3.8,  "blur_x": 1.5, "blur_y": 1.0, "haze_opacity": 0.35, "smear_scale": 0.0},
    "S4": {"freq": 0.025, "octaves": 3, "scale": 7.5,  "blur_x": 5.0, "blur_y": 2.2, "haze_opacity": 0.45, "smear_scale": 6.0},
    "S5": {"freq": 0.018, "octaves": 4, "scale": 14.5, "blur_x": 9.0, "blur_y": 3.8, "haze_opacity": 0.60, "smear_scale": 12.0},
}

GEOM_PRESETS = {
    "G1": {"epsilon": 0.0,  "overshoot_px": 0.00},
    "G2": {"epsilon": 2.5,  "overshoot_px": 0.15},
    "G3": {"epsilon": 5.5,  "overshoot_px": 0.35},
    "G4": {"epsilon": 9.5,  "overshoot_px": 0.65},
    "G5": {"epsilon": 16.0, "overshoot_px": 1.10},
}

# Color Printmaking Filter Ladder (C1-C4): Deterministic Pure-Python Risograph & Ukiyo-e Woodblock Layers
# Applied after jeff_sketch + B1 (Blotchy Sumi-e Ink-Wash) + G1-G5 + S1-S5 across all Studio & Media Division pillars
COLOR_PRINT_PRESETS = {
    "C1": {
        "id": "C1",
        "aliases": ("C1", "PY1", "RISO_TERRA_PINE"),
        "label": "Dual-Tone Earth Risograph (Terracotta Clay & Deep Forest Pine)",
        "favorite": False,
    },
    "C2": {
        "id": "C2",
        "aliases": ("C2", "PY2", "RISO_EARTH", "RISO_OCHRE_OLIVE_UMBER"),
        "label": "3-Color Earth Risograph (Golden Ochre 18deg, Sage Olive 52deg, Terracotta Rust 78deg & Raw Umber)",
        "favorite": True,
    },
    "C3": {
        "id": "C3",
        "aliases": ("C3", "PY3", "UKIYOE_RISO", "UKIYOE_EARTH_RISO_HYBRID"),
        "label": "Ukiyo-e Woodblock x Earth-Tone Risograph Hybrid (Framed Terracotta-Amber Skyline Bokashi + 3-Color Earth Risograph)",
        "favorite": True,
    },
    "C4": {
        "id": "C4",
        "aliases": ("C4", "PY4", "UKIYOE_PRUSSIAN", "UKIYOE_PRUSSIAN_WOODBLOCK"),
        "label": "Classic Ukiyo-e Prussian Blue Bokashi + Earthy Woodblock Tints",
        "favorite": False,
    },
}
COLOR_ALIAS_MAP = {
    alias: code
    for code, meta in COLOR_PRINT_PRESETS.items()
    for alias in meta["aliases"]
}


def zhang_suen_thinning(mask: np.ndarray, max_iters: int = 14) -> np.ndarray:
    """
    Fast vectorized Zhang-Suen 1-pixel skeletonization in pure NumPy.
    Reduces every stroke (1px to 18px wide) to a single unbroken 8-connected centerline.
    """
    im = (mask > 0).astype(np.uint8)
    im[0, :] = 0
    im[-1, :] = 0
    im[:, 0] = 0
    im[:, -1] = 0

    for _ in range(max_iters):
        changed = False
        for step in (1, 2):
            p2 = im[:-2, 1:-1]
            p3 = im[:-2, 2:]
            p4 = im[1:-1, 2:]
            p5 = im[2:, 2:]
            p6 = im[2:, 1:-1]
            p7 = im[2:, :-2]
            p8 = im[1:-1, :-2]
            p9 = im[:-2, :-2]
            p1 = im[1:-1, 1:-1]

            A = (
                ((p2 == 0) & (p3 == 1)).astype(np.uint8)
                + ((p3 == 0) & (p4 == 1)).astype(np.uint8)
                + ((p4 == 0) & (p5 == 1)).astype(np.uint8)
                + ((p5 == 0) & (p6 == 1)).astype(np.uint8)
                + ((p6 == 0) & (p7 == 1)).astype(np.uint8)
                + ((p7 == 0) & (p8 == 1)).astype(np.uint8)
                + ((p8 == 0) & (p9 == 1)).astype(np.uint8)
                + ((p9 == 0) & (p2 == 1)).astype(np.uint8)
            )
            B = p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9

            if step == 1:
                m1 = p2 * p4 * p6
                m2 = p4 * p6 * p8
            else:
                m1 = p2 * p4 * p8
                m2 = p2 * p6 * p8

            cond = (p1 == 1) & (A == 1) & (B >= 2) & (B <= 6) & (m1 == 0) & (m2 == 0)
            if np.any(cond):
                im[1:-1, 1:-1][cond] = 0
                changed = True
        if not changed:
            break
    return im.astype(bool)


def rdp_simplify_indices(pts: np.ndarray, epsilon: float) -> np.ndarray:
    """Iterative Ramer-Douglas-Peucker returning the kept indices along `pts`."""
    n = len(pts)
    if n <= 2 or epsilon <= 0.0:
        return np.arange(n, dtype=np.int32)
    keep = np.zeros(n, dtype=bool)
    keep[0] = True
    keep[-1] = True
    stack = [(0, n - 1)]
    while stack:
        i, j = stack.pop()
        if j - i <= 1:
            continue
        p1 = pts[i]
        p2 = pts[j]
        seg = p2 - p1
        seg_len_sq = float(seg[0] * seg[0] + seg[1] * seg[1])
        sub = pts[i + 1 : j]
        if seg_len_sq < 1e-6:
            dists = np.hypot(sub[:, 0] - p1[0], sub[:, 1] - p1[1])
        else:
            cross = np.abs(seg[0] * (p1[1] - sub[:, 1]) - (p1[0] - sub[:, 0]) * seg[1])
            dists = cross / np.sqrt(seg_len_sq)
        max_idx = int(np.argmax(dists))
        max_d = float(dists[max_idx])
        if max_d > epsilon:
            split = i + 1 + max_idx
            keep[split] = True
            stack.append((i, split))
            stack.append((split, j))
    return np.nonzero(keep)[0].astype(np.int32)


def apply_geometric_transform(ink_alpha: np.ndarray, geom_stage: str, res_scale: float, seed: int = 864) -> np.ndarray:
    """
    Applies the G1-G5 Stroke-Straightening Geometry Filter Ladder to an extracted ink alpha channel.
    Extracts every ink stroke's unbroken 1px skeleton via Zhang-Suen thinning, measures local
    stroke width and darkness along the original curved chain, simplifies curves into straight-line
    chords via Ramer-Douglas-Peucker (`epsilon`), and redraws continuous variable-width straight strokes.
    """
    g_key = geom_stage.upper()
    if g_key not in GEOM_PRESETS or GEOM_PRESETS[g_key]["epsilon"] <= 0.01:
        return ink_alpha.copy()

    gcfg = GEOM_PRESETS[g_key]
    epsilon = gcfg["epsilon"] * res_scale
    overshoot_px = gcfg["overshoot_px"] * res_scale

    h, w = ink_alpha.shape
    mask = (ink_alpha > 0.16).astype(np.uint8)

    # Estimate local stroke thickness at every pixel via morphological erosion levels
    mask_pil = Image.fromarray(mask * 255, mode="L")
    thickness_map = np.ones((h, w), dtype=np.float32) * 1.35
    cur = mask_pil
    for r in range(1, 9):
        cur = cur.filter(ImageFilter.MinFilter(3))
        eroded = np.array(cur) > 127
        if not eroded.any():
            break
        thickness_map[eroded] = 1.35 + r * 1.85

    thick_pil = Image.fromarray(np.clip(thickness_map * 12.0, 0, 255).astype(np.uint8), mode="L")
    thickness_map = np.array(thick_pil.filter(ImageFilter.MaxFilter(3)), dtype=np.float32) / 12.0

    alpha_pil = Image.fromarray(np.clip(ink_alpha * 255.0, 0, 255).astype(np.uint8), mode="L")
    peak_alpha_map = np.array(alpha_pil.filter(ImageFilter.MaxFilter(3)), dtype=np.float32) / 255.0

    skeleton = zhang_suen_thinning(mask, max_iters=14)

    skel_u8 = skeleton.astype(np.uint8)
    deg = np.zeros_like(skel_u8)
    nbrs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dy, dx in nbrs:
        shifted = np.zeros_like(skel_u8)
        y0_s, y1_s = max(0, -dy), h - max(0, dy)
        x0_s, x1_s = max(0, -dx), w - max(0, dx)
        y0_d, y1_d = max(0, dy), h - max(0, -dy)
        x0_d, x1_d = max(0, dx), w - max(0, -dx)
        shifted[y0_d:y1_d, x0_d:x1_d] = skel_u8[y0_s:y1_s, x0_s:x1_s]
        deg += shifted
    deg *= skel_u8

    visited = ~skeleton
    ys_ep, xs_ep = np.nonzero(skeleton & (deg == 1))
    ys_all, xs_all = np.nonzero(skeleton & (deg != 1))
    seed_ys = np.concatenate([ys_ep, ys_all])
    seed_xs = np.concatenate([xs_ep, xs_all])

    chains = []

    def walk_from(start_y: int, start_x: int):
        path = []
        cy, cx = start_y, start_x
        while True:
            found = False
            for dy, dx in nbrs:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                    visited[ny, nx] = True
                    path.append((nx, ny))
                    cy, cx = ny, nx
                    found = True
                    break
            if not found:
                for dy, dx in nbrs:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and skeleton[ny, nx]:
                        if (len(path) == 0 and (nx != start_x or ny != start_y)) or (
                            len(path) >= 2 and (nx, ny) != path[-2]
                        ):
                            path.append((nx, ny))
                            break
                break
        return path

    for sy, sx in zip(seed_ys, seed_xs):
        if visited[sy, sx]:
            continue
        visited[sy, sx] = True
        fwd = walk_from(sy, sx)
        bwd = walk_from(sy, sx)
        full_chain = list(reversed(bwd)) + [(sx, sy)] + fwd
        if len(full_chain) >= 2:
            chains.append(np.array(full_chain, dtype=np.float32))
        elif len(full_chain) == 1:
            chains.append(np.array([full_chain[0], full_chain[0]], dtype=np.float32))

    ss = 2
    canvas = Image.new("L", (w * ss, h * ss), 0)
    draw = ImageDraw.Draw(canvas)

    for chain in chains:
        keep_idx = rdp_simplify_indices(chain, epsilon=epsilon)
        for k in range(len(keep_idx) - 1):
            i0 = int(keep_idx[k])
            i1 = int(keep_idx[k + 1])
            x0, y0 = chain[i0]
            x1, y1 = chain[i1]

            sub_pts = chain[i0 : i1 + 1].astype(np.int32)
            xs_c = np.clip(sub_pts[:, 0], 0, w - 1)
            ys_c = np.clip(sub_pts[:, 1], 0, h - 1)
            w_px = max(1, int(round(float(np.median(thickness_map[ys_c, xs_c])) * ss)))
            seg_alpha = float(np.percentile(peak_alpha_map[ys_c, xs_c], 75))
            fill_val = int(np.clip(seg_alpha * 255.0, 50, 255))

            seg_len = float(np.hypot(x1 - x0, y1 - y0))
            if overshoot_px > 0.0 and seg_len > 8.0 * res_scale:
                dx, dy = x1 - x0, y1 - y0
                ux, uy = dx / seg_len, dy / seg_len
                ox0, oy0 = x0 - ux * overshoot_px, y0 - uy * overshoot_px
                ox1, oy1 = x1 + ux * overshoot_px, y1 + uy * overshoot_px
            else:
                ox0, oy0, ox1, oy1 = x0, y0, x1, y1

            draw.line([(ox0 * ss, oy0 * ss), (ox1 * ss, oy1 * ss)], fill=fill_val, width=w_px, joint="curve")
            if w_px >= 3:
                r_cap = w_px * 0.48
                for vx, vy in ((x0 * ss, y0 * ss), (x1 * ss, y1 * ss)):
                    draw.ellipse([vx - r_cap, vy - r_cap, vx + r_cap, vy + r_cap], fill=fill_val)

    out_pil = canvas.resize((w, h), resample=Image.Resampling.BICUBIC)
    return np.array(out_pil, dtype=np.float32) / 255.0


def fractal_turbulence(h: int, w: int, base_freq: float, num_octaves: int, seed: int) -> np.ndarray:
    """Generates 2D fractalNoise matching SVG feTurbulence(type='fractalNoise'). Returns values in [-1, 1]."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), dtype=np.float32)
    total_amp = 0.0
    for octave in range(num_octaves):
        freq = base_freq * (2 ** octave)
        amp = 0.5 ** octave
        # Period in pixels = 1 / freq
        period = max(2.0, 1.0 / max(freq, 1e-4))
        gh = max(3, int(round(h / period)))
        gw = max(3, int(round(w / period)))
        grid = rng.uniform(-1.0, 1.0, size=(gh, gw)).astype(np.float32)
        up = Image.fromarray(grid, mode="F").resize((w, h), resample=Image.Resampling.BICUBIC)
        acc += np.array(up, dtype=np.float32) * amp
        total_amp += amp
    acc /= max(total_amp, 1e-6)
    return np.clip(acc * 1.35, -1.0, 1.0)


def displace_channel(channel: np.ndarray, dx: np.ndarray, dy: np.ndarray, scale: float) -> np.ndarray:
    """Applies SVG feDisplacementMap bilinearly across a 2D array."""
    if scale <= 0.0:
        return channel.copy()
    h, w = channel.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    src_x = np.clip(xx + dx * scale, 0.0, w - 1.0)
    src_y = np.clip(yy + dy * scale, 0.0, h - 1.0)

    x0 = np.floor(src_x).astype(int)
    x1 = np.clip(x0 + 1, 0, w - 1)
    y0 = np.floor(src_y).astype(int)
    y1 = np.clip(y0 + 1, 0, h - 1)
    wx = src_x - x0
    wy = src_y - y0

    return (
        (1.0 - wx) * (1.0 - wy) * channel[y0, x0]
        + wx * (1.0 - wy) * channel[y0, x1]
        + (1.0 - wx) * wy * channel[y1, x0]
        + wx * wy * channel[y1, x1]
    )


def anisotropic_gaussian_blur(arr: np.ndarray, sigma_x: float, sigma_y: float) -> np.ndarray:
    """Separable 1D Gaussian blur with independent X and Y stdDeviation matching SVG feGaussianBlur."""
    out = arr.copy()
    if sigma_x > 0.05:
        rad_x = max(1, int(np.ceil(sigma_x * 3.0)))
        kx = np.exp(-0.5 * (np.arange(-rad_x, rad_x + 1, dtype=np.float32) / sigma_x) ** 2)
        kx /= kx.sum()
        out = np.apply_along_axis(lambda m: np.convolve(m, kx, mode="same"), axis=1, arr=out)
    if sigma_y > 0.05:
        rad_y = max(1, int(np.ceil(sigma_y * 3.0)))
        ky = np.exp(-0.5 * (np.arange(-rad_y, rad_y + 1, dtype=np.float32) / sigma_y) ** 2)
        ky /= ky.sum()
        out = np.apply_along_axis(lambda m: np.convolve(m, ky, mode="same"), axis=0, arr=out)
    return out


def apply_blotch_prepass(ink_alpha: np.ndarray, res_scale: float = 1.0, seed: int = 864) -> np.ndarray:
    """
    Blotchy Sumi-e Ink-Wash Prepass (B1 / fhg_inkwash_blotch_spec):
    1. Clears any outer frame border or deckle paper shadow within the outer 6.8% canvas margin so
       the parchment margin stays 100% open #F5EFE2.
    2. If applied to an existing pure line-art sketch (where strokes are thin contour lines with no
       broad watercolor wash pools), synthesizes organic sumi-e tonal wash pools clustered around
       the interior contour forms so that subsequent G2 skeletonization converts them into layered
       grey-to-charcoal brush daubs alongside crisp fountain-pen lines.
    """
    h, w = ink_alpha.shape
    out = ink_alpha.copy()

    # 1. Clear outer 6.8% canvas border to strip any outer square ink frame or deckle paper shadow
    my = max(4, int(round(h * 0.068)))
    mx = max(4, int(round(w * 0.068)))
    out[:my, :] = 0.0
    out[h - my :, :] = 0.0
    out[:, :mx] = 0.0
    out[:, w - mx :] = 0.0

    # 2. Check if image already has broad watercolor wash pools (radius >= 4px) or is pure line-art
    fg_pil = Image.fromarray(((out > 0.14).astype(np.uint8) * 255), mode="L")
    eroded_4px = np.array(fg_pil.filter(ImageFilter.MinFilter(7)), dtype=np.uint8) > 0
    inner_eroded = eroded_4px[my : h - my, mx : w - mx]
    thick_wash_ratio = float(np.mean(inner_eroded))

    if thick_wash_ratio < 0.022:
        # Pure line-art input: synthesize organic sumi-e ink-wash brush dabs (4-10px wide) hugging contour clusters
        line_pil = Image.fromarray(np.clip(out * 255.0, 0, 255).astype(np.uint8), mode="L")
        rad_fine = max(3, int(round(5.5 * res_scale)))
        rad_broad = max(6, int(round(11.5 * res_scale)))

        dens_fine = np.array(line_pil.filter(ImageFilter.GaussianBlur(radius=rad_fine)), dtype=np.float32)
        dens_broad = np.array(line_pil.filter(ImageFilter.GaussianBlur(radius=rad_broad)), dtype=np.float32)

        active = dens_fine[dens_fine > 2.0]
        p85 = float(np.percentile(active, 85)) if active.size > 50 else 22.0
        p85 = max(p85, 7.0)

        norm_fine = np.clip(dens_fine / p85, 0.0, 1.45)
        norm_broad = np.clip(dens_broad / (p85 * 0.72), 0.0, 1.35)

        # Modulate with macro cluster field + fine brush-dab texture so daubs are 4-10px organic strokes (never giant blocks)
        blotch_macro = fractal_turbulence(h, w, base_freq=0.018, num_octaves=3, seed=seed + 313)
        dab_tex = fractal_turbulence(h, w, base_freq=0.068, num_octaves=2, seed=seed + 509)
        tone_tex = fractal_turbulence(h, w, base_freq=0.042, num_octaves=2, seed=seed + 719)

        gate = np.clip((blotch_macro + 0.32) * 1.28, 0.0, 1.35) * np.clip(dab_tex + 0.56, 0.0, 1.28)
        combined = (norm_fine * 0.72 + norm_broad * 0.38) * gate

        # Threshold into crisp 4-10px sumi-e brush dabs along the ink contours
        dab_mask = combined > 0.34
        # Vary tonal density across light grey (0.24), mid grey (0.50), and deep charcoal (0.88)
        tone_val = np.clip(0.52 + 0.36 * tone_tex + 0.16 * dab_tex, 0.22, 0.92)
        wash_alpha = np.where(dab_mask, tone_val, 0.0)

        # Keep generous negative space around outer margins
        pad_y = int(round(h * 0.095))
        pad_x = int(round(w * 0.095))
        wash_alpha[:pad_y, :] = 0.0
        wash_alpha[h - pad_y :, :] = 0.0
        wash_alpha[:, :pad_x] = 0.0
        wash_alpha[:, w - pad_x :] = 0.0

        out = np.maximum(out, wash_alpha)

    return out


# ==============================================================================
# COLOR PRINTMAKING FILTER LADDER (C1-C4): PURE-PYTHON RISOGRAPH & UKIYO-E
# Operates downstream on any rendered Blotchy (B1) or jeff_sketch RGB array
# ==============================================================================

def halftone_screen(h: int, w: int, pitch: float = 5.8, angle_deg: float = 45.0) -> np.ndarray:
    """Generates an angled 2D screenprint halftone dot threshold matrix in [0.06, 0.94]."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    theta = np.deg2rad(angle_deg)
    u = xx * np.cos(theta) + yy * np.sin(theta)
    v = -xx * np.sin(theta) + yy * np.cos(theta)
    wave = 0.5 * (np.cos(2.0 * np.pi * u / pitch) + np.cos(2.0 * np.pi * v / pitch))
    return 0.5 + 0.44 * wave


def shift_array(arr: np.ndarray, dx: int, dy: int) -> np.ndarray:
    res = np.zeros_like(arr)
    h, w = arr.shape[:2]
    src_x0, src_x1 = max(0, -dx), min(w, w - dx)
    src_y0, src_y1 = max(0, -dy), min(h, h - dy)
    dst_x0, dst_x1 = max(0, dx), min(w, w + dx)
    dst_y0, dst_y1 = max(0, dy), min(h, h + dy)
    res[dst_y0:dst_y1, dst_x0:dst_x1] = arr[src_y0:src_y1, src_x0:src_x1]
    return res


def apply_ink_layer(canvas: np.ndarray, alpha: np.ndarray, rgb: tuple[float, float, float]) -> np.ndarray:
    """Multiply-style translucent riso/woodblock ink laydown over cream paper."""
    a = np.clip(alpha, 0.0, 1.0)[:, :, None]
    ink_color = np.array(rgb, dtype=np.float32)[None, None, :]
    multiplied = (canvas * ink_color) / 245.0
    blended_ink = 0.52 * ink_color + 0.48 * multiplied
    return canvas * (1.0 - a) + blended_ink * a


def build_color_print_layers(arr: np.ndarray, seed: int = 101) -> dict:
    """
    Separates a monochrome/blotchy sketch RGB array into 3 morphological tonal tiers:
      1. deep_black: Primary crisp contour lines, heavy silhouettes & bottom-right signature
      2. dark_gray:  Broad dark-gray brush strokes / cloak stripes (50 <= lum <= 135)
      3. mid_gray:   Mid/light-gray sumi-e mist & foliage daubs (105 <= lum <= 228)
      4. ambient_pool: Soft interior drawing envelope (protected 12% outer margins)
    Includes a MaxFilter(5) anti-alias fringe guard so 1px edges of thin black ink lines stay razor-sharp.
    """
    h, w = arr.shape[:2]
    lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]

    paper_level = np.percentile(lum, 85)
    grain = fractal_turbulence(h, w, base_freq=0.14, num_octaves=2, seed=seed) * 2.2
    paper = np.zeros((h, w, 3), dtype=np.float32)
    paper[:, :, 0] = np.clip(246.0 + grain, 0, 255)
    paper[:, :, 1] = np.clip(241.0 + grain * 0.92, 0, 255)
    paper[:, :, 2] = np.clip(229.0 + grain * 0.82, 0, 255)

    ink_total = np.clip((paper_level - lum) / max(paper_level - 22.0, 1.0), 0.0, 1.0)

    deep_core_pil = Image.fromarray(((lum < 58.0) * 255).astype(np.uint8), mode="L")
    aa_fringe_guard = (
        np.array(
            deep_core_pil.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(radius=1.2)),
            dtype=np.float32,
        )
        / 255.0
    )

    raw_dark_gray = np.clip(1.0 - np.abs(lum - 88.0) / 42.0, 0.0, 1.0) * (lum >= 45.0)
    dark_gray_pil = Image.fromarray((raw_dark_gray * 255).astype(np.uint8), mode="L")
    dark_gray = (
        np.array(
            dark_gray_pil.filter(ImageFilter.MinFilter(3))
            .filter(ImageFilter.MaxFilter(3))
            .filter(ImageFilter.GaussianBlur(radius=1.0)),
            dtype=np.float32,
        )
        / 255.0
    )
    dark_gray[int(h * 0.84) :, int(w * 0.70) :] = 0.0

    raw_mid_gray = np.clip((230.0 - lum) / 95.0, 0.0, 1.0) * np.clip((lum - 85.0) / 30.0, 0.0, 1.0)
    raw_mid_gray = np.clip(raw_mid_gray - aa_fringe_guard * 0.75, 0.0, 1.0)
    mid_gray_pil = Image.fromarray((raw_mid_gray * 255).astype(np.uint8), mode="L")
    mid_gray = (
        np.array(
            mid_gray_pil.filter(ImageFilter.MinFilter(3))
            .filter(ImageFilter.MaxFilter(5))
            .filter(ImageFilter.GaussianBlur(radius=1.5)),
            dtype=np.float32,
        )
        / 255.0
    )
    mid_gray[int(h * 0.84) :, int(w * 0.70) :] = 0.0

    deep_black = np.clip(ink_total - mid_gray * 0.85 - dark_gray * 0.45, 0.0, 1.0)

    ink_no_sig = ink_total.copy()
    ink_no_sig[int(h * 0.84) :, int(w * 0.70) :] = 0.0
    ink_pil = Image.fromarray((ink_no_sig * 255).astype(np.uint8), mode="L")
    closed = ink_pil.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    envelope = np.array(closed.filter(ImageFilter.GaussianBlur(radius=28)), dtype=np.float32) / 255.0
    ambient_pool = np.clip(envelope * 2.2, 0.0, 1.0)
    pad_y, pad_x = int(h * 0.12), int(w * 0.12)
    ambient_pool[:pad_y, :] = 0.0
    ambient_pool[h - pad_y :, :] = 0.0
    ambient_pool[:, :pad_x] = 0.0
    ambient_pool[:, w - pad_x :] = 0.0

    return {
        "h": h,
        "w": w,
        "lum": lum,
        "paper": paper,
        "deep_black": deep_black,
        "dark_gray": dark_gray,
        "mid_gray": mid_gray,
        "ambient_pool": ambient_pool,
        "ink_no_sig": ink_no_sig,
    }


def compute_sky_bokashi_mask(data: dict, seed: int = 77) -> np.ndarray:
    """
    Computes a framed Ukiyo-e upper sky bokashi gradient mask with a smooth,
    streak-free skyline barrier that sits cleanly behind the top silhouette ridge.
    """
    h, w = data["h"], data["w"]
    ink = data["ink_no_sig"]

    ink_pil = Image.fromarray((ink * 255).astype(np.uint8), mode="L")
    clean_ink = (
        np.array(
            ink_pil.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(9)),
            dtype=np.float32,
        )
        / 255.0
    )

    cols_with_ink = np.where(np.max(clean_ink, axis=0) > 0.25)[0]
    if len(cols_with_ink) > 20:
        x0 = max(int(w * 0.16), int(cols_with_ink[0]) - int(w * 0.01))
        x1 = min(int(w * 0.84), int(cols_with_ink[-1]) + int(w * 0.01))
    else:
        x0, x1 = int(w * 0.18), int(w * 0.82)

    rows_with_ink = np.where(np.max(clean_ink, axis=1) > 0.25)[0]
    top_ink_y = int(rows_with_ink[0]) if len(rows_with_ink) > 0 else int(h * 0.22)
    y0 = max(int(h * 0.11), top_ink_y - int(h * 0.10))
    y1 = min(int(h * 0.54), top_ink_y + int(h * 0.28))

    barriers = np.full(w, float(y1), dtype=np.float32)
    for x in range(x0, x1):
        col_hits = np.where(clean_ink[:, x] > 0.30)[0]
        if len(col_hits) > 0:
            barriers[x] = min(float(y1), float(col_hits[0]) + h * 0.035)

    kernel_size = 35
    pad = kernel_size // 2
    padded = np.pad(barriers, pad, mode="edge")
    smooth_barriers = np.convolve(padded, np.ones(kernel_size) / kernel_size, mode="valid")

    sky_mask = np.zeros((h, w), dtype=np.float32)
    for x in range(x0, x1):
        limit_y = int(round(min(float(y1), smooth_barriers[x])))
        if limit_y > y0:
            ys = np.arange(y0, limit_y, dtype=np.float32)
            fade = np.clip(1.0 - (ys - y0) / max(float(y1 - y0), 1.0), 0.0, 1.0) ** 1.35
            sky_mask[y0:limit_y, x] = fade

    sky_pil = Image.fromarray((sky_mask * 255).astype(np.uint8), mode="L")
    sky_soft = np.array(sky_pil.filter(ImageFilter.GaussianBlur(radius=8.0)), dtype=np.float32) / 255.0

    frame = np.zeros((h, w), dtype=np.float32)
    frame[y0:y1, x0:x1] = 1.0
    wood_grain = 1.0 + fractal_turbulence(h, w, base_freq=0.09, num_octaves=2, seed=seed) * 0.05
    return np.clip(sky_soft * frame * wood_grain, 0.0, 1.0)


def apply_color_printmaking_stage(arr: np.ndarray, color_stage: str, seed: int = 864) -> np.ndarray:
    """
    Applies one of the 4 registered Pure-Python Color Printmaking stages (C1-C4)
    to a monochrome/blotchy sketch RGB array (prior to final canonical signature stamp).
    """
    code = COLOR_ALIAS_MAP.get(color_stage.upper(), color_stage.upper())
    data = build_color_print_layers(arr, seed=seed + 101)
    h, w = data["h"], data["w"]
    canvas = data["paper"].copy()
    yy = np.linspace(0.0, 1.0, h)[:, None]

    if code == "C1":
        # C1: Dual-Tone Earth Risograph (Terracotta Clay & Deep Forest Pine)
        ht_terra = halftone_screen(h, w, pitch=5.6, angle_deg=35.0)
        ht_sage = halftone_screen(h, w, pitch=6.0, angle_deg=75.0)

        sage_density = data["mid_gray"] * np.clip(1.35 - yy * 0.85, 0.25, 1.0) * 0.90
        sage_dots = shift_array(np.clip((sage_density - ht_sage * 0.68) * 3.4, 0.0, 1.0), dx=-2, dy=1)
        canvas = apply_ink_layer(canvas, sage_dots * 0.80, (104, 118, 102))

        terra_density = np.maximum(data["mid_gray"] * 0.95, data["dark_gray"] * 1.15)
        terra_dots = shift_array(np.clip((terra_density - ht_terra * 0.65) * 3.6, 0.0, 1.0), dx=3, dy=2)
        canvas = apply_ink_layer(canvas, terra_dots * 0.90, (186, 86, 52))

        canvas = apply_ink_layer(canvas, data["deep_black"], (24, 42, 32))

    elif code == "C2":
        # C2 (★ Favorite #1): 3-Color Earth Risograph (Golden Ochre 18deg, Sage Olive 52deg, Terracotta Rust 78deg & Raw Umber)
        ht_ochre = halftone_screen(h, w, pitch=5.4, angle_deg=18.0)
        ht_olive = halftone_screen(h, w, pitch=5.8, angle_deg=52.0)
        ht_rust = halftone_screen(h, w, pitch=5.0, angle_deg=78.0)

        lower_weight = np.clip((yy - 0.22) * 1.6, 0.30, 1.0)
        ochre_density = np.clip(data["ambient_pool"] * 0.82 * lower_weight + data["mid_gray"] * 0.45, 0.0, 0.92)
        ochre_dots = shift_array(np.clip((ochre_density - ht_ochre * 0.70) * 3.5, 0.0, 1.0), dx=2, dy=2)
        canvas = apply_ink_layer(canvas, ochre_dots * 0.82, (218, 160, 74))

        olive_density = np.clip(data["mid_gray"] * 1.15 + data["ambient_pool"] * 0.38 * (1.15 - lower_weight), 0.0, 0.96)
        olive_dots = shift_array(np.clip((olive_density - ht_olive * 0.65) * 3.6, 0.0, 1.0), dx=-2, dy=1)
        canvas = apply_ink_layer(canvas, olive_dots * 0.86, (108, 124, 82))

        rust_density = np.clip(data["dark_gray"] * 1.25, 0.0, 1.0)
        rust_dots = np.clip((rust_density - ht_rust * 0.58) * 4.0, 0.0, 1.0)
        canvas = apply_ink_layer(canvas, rust_dots * 0.90, (178, 82, 48))

        canvas = apply_ink_layer(canvas, data["deep_black"], (40, 27, 19))

    elif code == "C3":
        # C3 (★ Favorite #2): Ukiyo-e Woodblock x Earth-Tone Risograph Hybrid (Framed Terracotta-Amber Bokashi Sky + 3-Color Riso)
        bokashi_mask = compute_sky_bokashi_mask(data, seed=seed + 77)
        canvas = apply_ink_layer(canvas, bokashi_mask * 0.86, (179, 95, 59))

        ht_ochre = halftone_screen(h, w, pitch=5.4, angle_deg=20.0)
        ht_moss = halftone_screen(h, w, pitch=5.8, angle_deg=55.0)
        ht_terra = halftone_screen(h, w, pitch=5.0, angle_deg=80.0)

        ochre_density = np.clip(data["mid_gray"] * 0.90 + data["ambient_pool"] * 0.35, 0.0, 0.95)
        ochre_dots = shift_array(np.clip((ochre_density - ht_ochre * 0.68) * 3.5, 0.0, 1.0), dx=2, dy=2)
        canvas = apply_ink_layer(canvas, ochre_dots * 0.80, (206, 145, 66))

        moss_density = np.clip(data["mid_gray"] * 1.12, 0.0, 1.0)
        moss_dots = shift_array(np.clip((moss_density - ht_moss * 0.65) * 3.6, 0.0, 1.0), dx=-2, dy=1)
        canvas = apply_ink_layer(canvas, moss_dots * 0.84, (105, 122, 84))

        terra_density = np.clip(data["dark_gray"] * 1.25, 0.0, 1.0)
        terra_dots = np.clip((terra_density - ht_terra * 0.58) * 4.0, 0.0, 1.0)
        canvas = apply_ink_layer(canvas, terra_dots * 0.88, (173, 84, 54))

        canvas = apply_ink_layer(canvas, data["deep_black"], (34, 26, 21))

    elif code == "C4":
        # C4: Classic Ukiyo-e Prussian Blue Bokashi + Earthy Woodblock Tints
        top_fade = np.clip(1.0 - yy / 0.36, 0.0, 1.0) ** 1.65
        wood_grain = 1.0 + fractal_turbulence(h, w, base_freq=0.12, num_octaves=2, seed=seed + 55) * 0.05
        prussian_sky = np.clip(top_fade * wood_grain, 0.0, 1.0)
        canvas = apply_ink_layer(canvas, prussian_sky * 0.88, (24, 56, 88))

        lower_trail = np.clip((yy - 0.42) * 2.0, 0.0, 1.0) * data["ambient_pool"]
        canvas = apply_ink_layer(canvas, lower_trail * 0.58, (194, 122, 78))

        sage_brush = np.clip(data["mid_gray"] * 1.05, 0.0, 1.0)
        canvas = apply_ink_layer(canvas, sage_brush * 0.82, (110, 128, 96))

        rust_folds = np.clip(data["dark_gray"] * 1.25, 0.0, 1.0)
        canvas = apply_ink_layer(canvas, rust_folds * 0.88, (168, 78, 52))

        deep_pil = Image.fromarray((data["deep_black"] * 255).astype(np.uint8), mode="L")
        thick_interior = (
            np.array(deep_pil.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5)), dtype=np.float32)
            / 255.0
        )
        canvas = apply_ink_layer(canvas, thick_interior * 0.90, (30, 60, 92))

        contour_ink = np.clip(data["deep_black"] - thick_interior * 0.65, 0.0, 1.0)
        canvas = apply_ink_layer(canvas, contour_ink, (24, 21, 19))

    return np.clip(canvas, 0.0, 255.0)


def apply_humanizer_ladder(
    input_path: str,
    output_path: str,
    stage: str = "S2",
    sig_path: str = CANONICAL_SIG_PATH,
    seed: int = 864,
    geom_stage: str = "G2",
    blotch: bool = False,
    color_stage: str | None = None,
):
    st_upper = stage.upper().replace(" ", "")
    color_only_pass = False
    if "+" in st_upper:
        parts = st_upper.split("+")
        st_upper = "S2"
        for p in parts:
            if p in GEOM_PRESETS:
                geom_stage = p
            elif p in STAGE_PRESETS:
                st_upper = p
            elif p in ("B1", "BLOTCH", "INKWASH"):
                blotch = True
            elif p in COLOR_ALIAS_MAP:
                color_stage = COLOR_ALIAS_MAP[p]
    elif st_upper in COLOR_ALIAS_MAP:
        # Standalone color pass (e.g., stage="C2" or "C3") on an ALREADY rendered B1/sketch image:
        # Skip re-running geometry/humanizer wobble so existing linework stays 100% pixel-locked!
        color_stage = COLOR_ALIAS_MAP[st_upper]
        color_only_pass = True
        st_upper = "S1"
        geom_stage = "G1"
    elif st_upper in GEOM_PRESETS:
        geom_stage = st_upper
        st_upper = "S1"  # Keep straightened strokes crisp and un-wobbled by default when running G1-G5 directly
    cfg = STAGE_PRESETS[st_upper]
    img = Image.open(input_path).convert("RGB")
    w, h = img.size
    arr = np.array(img, dtype=np.float32)

    if color_only_pass:
        lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        parchment_mask = lum >= np.percentile(lum, 60)
        bg_r = float(np.median(arr[:, :, 0][parchment_mask]))
        bg_g = float(np.median(arr[:, :, 1][parchment_mask]))
        bg_b = float(np.median(arr[:, :, 2][parchment_mask]))
        tooth_r = fractal_turbulence(h, w, base_freq=0.08, num_octaves=2, seed=seed + 101) * 3.0
        paper_r = np.clip(bg_r + tooth_r, 0, 255)
        paper_g = np.clip(bg_g + tooth_r * 0.92, 0, 255)
        paper_b = np.clip(bg_b + tooth_r * 0.82, 0, 255)
        ink_rgb = (24.0, 21.0, 19.0)
        out_arr = apply_color_printmaking_stage(arr, color_stage=color_stage, seed=seed)
    else:
        # Scale factor relative to 1024x1024 SVG reference viewBox
        res_scale = w / 1024.0

        # 1. Separate warm parchment ground from black ink strokes
        lum = 0.299 * arr[:, :, 0] + 0.587 * arr[:, :, 1] + 0.114 * arr[:, :, 2]
        paper_level = np.percentile(lum, 85)
        ink_alpha = np.clip((paper_level - lum) / max(paper_level - 22.0, 1.0), 0.0, 1.0)

        # 1a. Optional Blotchy Sumi-e Ink-Wash Prepass (B1 / fhg_inkwash_blotch_spec)
        if blotch:
            ink_alpha = apply_blotch_prepass(ink_alpha, res_scale=res_scale, seed=seed)
        else:
            # When blotch=False (Pure Contour G2 / Angular G4), if the source image contains broad watercolor
            # washes, strip the broad wash fill via morphological local-background high-pass so G2/G4 renders
            # strictly the crisp fountain-pen contour linework!
            fg_pil = Image.fromarray(((ink_alpha > 0.14).astype(np.uint8) * 255), mode="L")
            eroded_4px = np.array(fg_pil.filter(ImageFilter.MinFilter(7)), dtype=np.uint8) > 0
            if float(np.mean(eroded_4px)) >= 0.022:
                lum_pil = Image.fromarray(np.clip(lum, 0, 255).astype(np.uint8), mode="L")
                local_bg = np.array(
                    lum_pil.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(radius=4.0)),
                    dtype=np.float32,
                )
                line_diff = local_bg - lum
                ink_alpha = np.clip((line_diff - 12.0) / 55.0, 0.0, 1.0)

        # 1b. Apply Geometry Filter Ladder (G1-G5) if geom_stage > G1
        if geom_stage.upper() != "G1":
            ink_alpha = apply_geometric_transform(ink_alpha, geom_stage=geom_stage, res_scale=res_scale, seed=seed)

        # Reconstruct clean warm parchment background (where ink was, fill with local parchment median)
        parchment_mask = lum >= np.percentile(lum, 60)
        bg_r = float(np.median(arr[:, :, 0][parchment_mask]))
        bg_g = float(np.median(arr[:, :, 1][parchment_mask]))
        bg_b = float(np.median(arr[:, :, 2][parchment_mask]))

        # Add subtle cold-pressed paper tooth to parchment ground
        tooth_r = fractal_turbulence(h, w, base_freq=0.08, num_octaves=2, seed=seed + 101) * 3.0
        paper_r = np.clip(bg_r + tooth_r, 0, 255)
        paper_g = np.clip(bg_g + tooth_r * 0.92, 0, 255)
        paper_b = np.clip(bg_b + tooth_r * 0.82, 0, 255)

        # 2. Generate SVG feTurbulence (R and G channels for X and Y displacement)
        noise_x = fractal_turbulence(h, w, base_freq=cfg["freq"], num_octaves=cfg["octaves"], seed=seed)
        noise_y = fractal_turbulence(h, w, base_freq=cfg["freq"], num_octaves=cfg["octaves"], seed=seed + 19)

        # 3. Fused Pipeline
        if geom_stage.upper() != "G1" and cfg["scale"] > 1.8:
            nib_x = fractal_turbulence(h, w, base_freq=0.045, num_octaves=3, seed=seed)
            nib_y = fractal_turbulence(h, w, base_freq=0.045, num_octaves=3, seed=seed + 19)
            wobble_ink = displace_channel(ink_alpha, nib_x, nib_y, scale=1.6 * res_scale)
        else:
            disp_scale = cfg["scale"] * res_scale
            wobble_ink = displace_channel(ink_alpha, noise_x, noise_y, scale=disp_scale)

        # 4. Diffusion / Haze path
        if cfg["haze_opacity"] > 0.0:
            bx = cfg["blur_x"] * res_scale
            by = cfg["blur_y"] * res_scale
            if cfg["smear_scale"] > 0.0:
                drag = anisotropic_gaussian_blur(ink_alpha, bx, by)
                haze = displace_channel(drag, noise_x, noise_y, scale=cfg["smear_scale"] * res_scale)
            else:
                haze = anisotropic_gaussian_blur(wobble_ink, bx, by)
            toned_haze_alpha = np.clip(haze * cfg["haze_opacity"], 0.0, 1.0)
        else:
            toned_haze_alpha = np.zeros_like(wobble_ink)

        # 5. feMerge
        haze_rgb = (42.0, 38.0, 34.0)
        ink_rgb = (24.0, 21.0, 19.0)

        comp_r = paper_r * (1.0 - toned_haze_alpha) + haze_rgb[0] * toned_haze_alpha
        comp_g = paper_g * (1.0 - toned_haze_alpha) + haze_rgb[1] * toned_haze_alpha
        comp_b = paper_b * (1.0 - toned_haze_alpha) + haze_rgb[2] * toned_haze_alpha

        comp_r = comp_r * (1.0 - wobble_ink) + ink_rgb[0] * wobble_ink
        comp_g = comp_g * (1.0 - wobble_ink) + ink_rgb[1] * wobble_ink
        comp_b = comp_b * (1.0 - wobble_ink) + ink_rgb[2] * wobble_ink

        out_arr = np.stack([comp_r, comp_g, comp_b], axis=-1)

        # 5b. Optional Color Printmaking Stage (C1-C4) chained after B1 + G1-G5 + S1-S5
        if color_stage:
            out_arr = apply_color_printmaking_stage(out_arr, color_stage=color_stage, seed=seed)

    # 6. Composite EXCLUSIVE Canonical Signature on the BOTTOM-RIGHT side of the canvas
    if sig_path and os.path.exists(sig_path):
        sig = Image.open(sig_path).convert("RGBA")
        sig_alpha = np.array(sig, dtype=np.float32)[:, :, 3] / 255.0

        target_w = int(w * 0.18)
        target_h = int(sig.height * (target_w / sig.width))
        sig_alpha_pil = Image.fromarray((sig_alpha * 255).astype(np.uint8), mode="L").resize(
            (target_w, target_h), resample=Image.Resampling.BICUBIC
        )
        sig_mask = np.array(sig_alpha_pil, dtype=np.float32) / 255.0

        # Apply the same S3 wobble/haze feel or clean breathing halo behind the signature
        halo_pil = sig_alpha_pil.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(radius=4.0))
        halo_mask = np.clip(np.array(halo_pil, dtype=np.float32) / 255.0 * 1.35, 0.0, 0.85)

        # Previous bottom distance from canvas bottom was 0.058 * h (py + target_h = 0.942 * h).
        # Divide that distance to the bottom of the canvas in half (0.029 * h -> py + target_h = 0.971 * h):
        px = int(w * 0.942) - target_w
        py = int(h * 0.971) - target_h
        roi = out_arr[py : py + target_h, px : px + target_w]
        roi_paper_r = paper_r[py : py + target_h, px : px + target_w]
        roi_paper_g = paper_g[py : py + target_h, px : px + target_w]
        roi_paper_b = paper_b[py : py + target_h, px : px + target_w]

        for c, (p_ch, ink_val) in enumerate([(roi_paper_r, ink_rgb[0]), (roi_paper_g, ink_rgb[1]), (roi_paper_b, ink_rgb[2])]):
            cleared = roi[:, :, c] * (1.0 - halo_mask) + p_ch * halo_mask
            roi[:, :, c] = cleared * (1.0 - sig_mask * 0.94) + ink_val * (sig_mask * 0.94)
        out_arr[py : py + target_h, px : px + target_w] = roi

    out_img = Image.fromarray(np.clip(out_arr, 0, 255).astype(np.uint8), mode="RGB")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    out_img.save(output_path, quality=95)
    print(f"[{stage}] Saved: {output_path}")


if __name__ == "__main__":
    sketches_dir = r"C:\dev\864zeros-publish\shared\bible\sketches"
    rendered_art_dir = r"C:\dev\864zeros-publish\media\visuals\rendered_art"
    targets = [
        ("verse_01_romans_10_13.jpg",    "verse_01_romans_10_13_s2_locked.jpg",    101),
        ("verse_04_acts_12_5.jpg",       "verse_04_acts_12_5_s2_locked.jpg",       404),
        ("verse_06_2samuel_22_31.jpg",   "verse_06_2samuel_22_31_s2_locked.jpg",   606),
        ("verse_08_acts_7_59.jpg",       "verse_08_acts_7_59_s2_locked.jpg",       808),
        ("verse_11_daniel_12_3.jpg",     "verse_11_daniel_12_3_s2_locked.jpg",     111),
        ("verse_16_psalm_129_2.jpg",     "verse_16_psalm_129_2_s2_locked.jpg",     161),
        ("verse_22_revelation_20_6.jpg", "verse_22_revelation_20_6_s2_locked.jpg", 222),
        ("verse_25_mark_2_17.jpg",       "verse_25_mark_2_17_s2_locked.jpg",       252),
    ]
    for src_name, dst_name, seed_val in targets:
        out_sketch = os.path.join(sketches_dir, dst_name)
        apply_humanizer_ladder(
            os.path.join(sketches_dir, src_name),
            out_sketch,
            stage="S2",
            seed=seed_val,
        )
        # Also mirror into media/visuals/rendered_art/ for the LoRA Style & Training Reference HTML
        out_art = os.path.join(rendered_art_dir, f"fhg_{dst_name}")
        if not os.path.exists(out_art):
            Image.open(out_sketch).save(out_art, quality=95)
            print(f"[MIRROR] Saved: {out_art}")

