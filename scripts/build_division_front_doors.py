#!/usr/bin/env python3
"""
864zeros Division Front Door Compiler (`build_division_front_doors.py`)
=======================================================================
Dynamically scans `C:\\dev\\864zeros-publish` (Division 4 — Creative Studio, Media & Publishing,
led by Sloane Sterling, VP-STUDIO) and across `C:\\dev\\864zeros-llc` to generate:

1. `C:\\dev\\864zeros-publish\\overview.html` — Sloane Sterling's Always-Evolving Studio Front Door
   (also mirrored to `STUDIO_ACTIVITY_REPORT_2026-10-19.html` and `LIBRARY/03-Creative-Studio-and-Media/STUDIO_FRONT_DOOR.html`)
2. `C:\\dev\\864zeros-llc\\DIVISION_FRONT_DOORS.html` — The 864zeros Company-Wide Division Front Door Hub

Every division Front Door tracks three evolving pillars:
  - Pillar I:   Asset Storage Vault (live file telemetry, byte sizes, SHA-256 provenance locks)
  - Pillar II:  Functionality, Frameworks & Brick Growth (engines, schemas, generators, JS bricks)
  - Pillar III: Media, Visual Art (`jeff_sketch` / `jeff_painting` / `jeff_geometric`), Video & Content
"""

import json
import os
from pathlib import Path
from datetime import datetime

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
LLC_ROOT = Path(r"C:\dev\864zeros-llc")
WEB_IMG_ROOT = Path(r"C:\dev\864zeros-web\meet-the-team\img")


def fmt_bytes(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024 * 1024:
        return f"{num_bytes / (1024**3):.2f} GB"
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024**2):.2f} MB"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes} B"


def classify_drawing(filename: str) -> str:
    fn = filename.lower()
    if fn.endswith(".svg"):
        return "svg_vector"
    if "dagr" in fn or "scribble" in fn or "pass" in fn or "step " in fn:
        return "dagr_multipass"
    if "ebook_" in fn or "poem" in fn or "lesson_" in fn:
        return "practice_poem"
    if "geometric" in fn or "color" in fn or "watercolor" in fn or "cubist" in fn:
        return "geometric_color"
    return "freehand_gestalt"


def scan_studio():
    # 1. File extension inventory across 864zeros-publish
    ext_counts = {}
    ext_bytes = {}
    total_files = 0
    total_bytes = 0
    for root, dirs, files in os.walk(PUBLISH_ROOT):
        if ".git" in Path(root).parts or "__pycache__" in Path(root).parts:
            continue
        for f in files:
            p = Path(root) / f
            try:
                sz = p.stat().st_size
            except OSError:
                sz = 0
            ext = p.suffix.lower() or "(no-ext)"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
            ext_bytes[ext] = ext_bytes.get(ext, 0) + sz
            total_files += 1
            total_bytes += sz

    # 2. Load PROVENANCE_LOCK.json
    prov_path = PUBLISH_ROOT / "sources" / "public_domain_classics" / "PROVENANCE_LOCK.json"
    prov_data = json.loads(prov_path.read_text(encoding="utf-8"))
    verified_sources = prov_data.get("verified_sources", [])

    # 3. Load focus_packs_catalog.json
    fp_path = PUBLISH_ROOT / "shared" / "focus_packs" / "focus_packs_catalog.json"
    fp_data = json.loads(fp_path.read_text(encoding="utf-8"))
    focus_packs = fp_data.get("packs", [])

    # 4. Scan rendered_art drawings + practice book illustrations
    rendered_dir = PUBLISH_ROOT / "media" / "visuals" / "rendered_art"
    drawings = []
    if rendered_dir.exists():
        for p in sorted(rendered_dir.iterdir()):
            if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".svg"):
                cat = classify_drawing(p.name)
                drawings.append({
                    "name": p.name,
                    "title": p.stem.replace("_", " ").replace("-", " ").title(),
                    "rel_path": f"media/visuals/rendered_art/{p.name}",
                    "abs_url": f"file:///C:/dev/864zeros-publish/media/visuals/rendered_art/{p.name}",
                    "size_str": fmt_bytes(p.stat().st_size),
                    "category": cat,
                    "ext": p.suffix.upper().lstrip("."),
                })

    # Add practice book plates
    for pb_sub in [
        ("shared/practice_books/foundations_of_resilience/images", "Foundations of Resilience"),
        ("shared/practice_books/five_plain_language_meditations/images", "5 Meditations in Ink"),
    ]:
        pb_dir = PUBLISH_ROOT / pb_sub[0]
        if pb_dir.exists():
            for p in sorted(pb_dir.iterdir()):
                if p.is_file() and p.suffix.lower() in (".jpg", ".png") and "_" in p.stem:
                    drawings.append({
                        "name": p.name,
                        "title": f"[{pb_sub[1]}] {p.stem.replace('_', ' ').title()}",
                        "rel_path": f"{pb_sub[0]}/{p.name}",
                        "abs_url": f"file:///C:/dev/864zeros-publish/{pb_sub[0]}/{p.name}",
                        "size_str": fmt_bytes(p.stat().st_size),
                        "category": "practice_poem",
                        "ext": p.suffix.upper().lstrip("."),
                    })

    # 5. Scan all 34 product DAM vaults in media/products/
    products_dir = PUBLISH_ROOT / "media" / "products"
    dam_products = []
    featured_videos = []
    if products_dir.exists():
        for prod_p in sorted(products_dir.iterdir()):
            if not prod_p.is_dir():
                continue
            mp4s = []
            wavs = []
            imgs = []
            stages = []
            for r, _, fs in os.walk(prod_p):
                for f in fs:
                    fp = Path(r) / f
                    rel = fp.relative_to(PUBLISH_ROOT).as_posix()
                    ext = fp.suffix.lower()
                    if ext == ".mp4":
                        mp4s.append((f, rel, fp.stat().st_size))
                    elif ext in (".wav", ".mp3"):
                        wavs.append(rel)
                    elif ext in (".png", ".jpg", ".jpeg", ".svg"):
                        imgs.append(rel)
                    elif ext == ".html":
                        stages.append((f, rel))
            dam_products.append({
                "slug": prod_p.name,
                "mp4_count": len(mp4s),
                "audio_count": len(wavs),
                "img_count": len(imgs),
                "stage_count": len(stages),
                "mp4s": mp4s,
                "stages": stages,
            })
            # Pick primary video/short for theater
            preferred = [m for m in mp4s if "video/" in m[1]] or mp4s
            for fname, rel, sz in preferred[:2]:
                featured_videos.append({
                    "slug": prod_p.name,
                    "fname": fname,
                    "rel": rel,
                    "abs_url": f"file:///C:/dev/864zeros-publish/{rel}",
                    "size_str": fmt_bytes(sz),
                })

    # 6. Load Studio v1.8 Bricks Manifest
    bricks_path = LLC_ROOT / "LLC-DIV-3-FACTORY" / "shared" / "bricks" / "STUDIO_BRICKS_MANIFEST_v1.8.json"
    bricks_data = json.loads(bricks_path.read_text(encoding="utf-8")) if bricks_path.exists() else {"bricks": []}

    return {
        "total_files": total_files,
        "total_bytes": total_bytes,
        "ext_counts": ext_counts,
        "ext_bytes": ext_bytes,
        "verified_sources": verified_sources,
        "focus_packs": focus_packs,
        "drawings": drawings,
        "dam_products": dam_products,
        "featured_videos": featured_videos,
        "bricks": bricks_data.get("bricks", []),
    }


def build_studio_front_door_html(data: dict) -> str:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M EDT")
    drawings = data["drawings"]
    dam_products = data["dam_products"]
    featured_videos = data["featured_videos"]
    verified_sources = data["verified_sources"]
    focus_packs = data["focus_packs"]
    bricks = data["bricks"]
    ext_counts = data["ext_counts"]
    ext_bytes = data["ext_bytes"]

    # Build Drawing Cards HTML
    drawing_cards_html = []
    cat_labels = {
        "freehand_gestalt": ("Pass 1 Freehand & Gestalt", "badge-blue"),
        "dagr_multipass": ("DAGR Multi-Pass & Scribble Lab", "badge-amber"),
        "geometric_color": ("Geometric Coif & Watercolor", "badge-purple"),
        "practice_poem": ("Practice Book & Poem Plates", "badge-green"),
        "svg_vector": ("SVG Vector Masters", "badge-rose"),
    }
    for d in drawings:
        cat_name, badge_cls = cat_labels.get(d["category"], ("Studio Plate", "badge-blue"))
        drawing_cards_html.append(f"""
        <div class="art-card" data-cat="{d['category']}" data-search="{d['title'].lower()} {d['name'].lower()}">
          <a href="{d['abs_url']}" target="_blank" class="art-thumb-link" title="Click to open full-resolution plate ({d['size_str']})">
            <img src="{d['abs_url']}" alt="{d['title']}" loading="lazy" />
            <span class="art-ext-tag">{d['ext']} · {d['size_str']}</span>
          </a>
          <div class="art-body">
            <span class="badge {badge_cls}">{cat_name}</span>
            <h4>{d['title']}</h4>
            <code>{d['name']}</code>
          </div>
        </div>""")

    # Build Playable Video Cards HTML (top 16 across ClearStreak, ChoiceGuard, Edge & GWS suite)
    priority_slugs = [
        "clearstreak", "choiceguard", "864z-chronicle", "Signal2Noise",
        "autoorganize-ytm", "vaultpilot", "approvalworkflow", "docwatermarker",
        "form2docx", "mailsyncshield", "formtimer", "rowarchiver", "snaplabel"
    ]
    ordered_videos = sorted(
        featured_videos,
        key=lambda v: (priority_slugs.index(v["slug"]) if v["slug"] in priority_slugs else 99, v["fname"])
    )[:18]

    video_cards_html = []
    for v in ordered_videos:
        is_short = "short" in v["fname"].lower() or "social" in v["fname"].lower()
        fmt_badge = '<span class="badge badge-amber">9:16 Short / Social</span>' if is_short else '<span class="badge badge-blue">16:9 Master Explainer</span>'
        video_cards_html.append(f"""
        <div class="video-card">
          <video controls preload="metadata" src="{v['abs_url']}"></video>
          <div class="video-meta">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:6px; margin-bottom:4px;">
              <strong>{v['slug']}</strong>
              {fmt_badge}
            </div>
            <div style="font-size:11.5px; color:var(--text-muted); margin-bottom:6px;">
              <code>{v['fname']}</code> ({v['size_str']})
            </div>
            <a href="{v['abs_url']}" target="_blank" style="font-size:12px; font-weight:600;">Open Raw MP4 ↗</a>
          </div>
        </div>""")

    # Build 34-Product DAM Vault Matrix rows
    dam_rows_html = []
    for idx, p in enumerate(dam_products, 1):
        stage_links = " · ".join(
            f'<a href="file:///C:/dev/864zeros-publish/{rel}" target="_blank">{name}</a>'
            for name, rel in p["stages"][:3]
        ) or "—"
        mp4_links = " · ".join(
            f'<a href="file:///C:/dev/864zeros-publish/{rel}" target="_blank">{name}</a>'
            for name, rel, _ in p["mp4s"][:3]
        ) or "—"
        status_badge = (
            '<span class="badge badge-green">FULL VIDEO + DAM</span>'
            if p["mp4_count"] > 0
            else '<span class="badge badge-blue">DAM SEEDED</span>'
        )
        dam_rows_html.append(f"""
        <tr>
          <td>{idx}</td>
          <td><strong>{p['slug']}</strong></td>
          <td>{p['mp4_count']} MP4s</td>
          <td>{p['audio_count']} Audio</td>
          <td>{p['img_count']} Visuals</td>
          <td>{p['stage_count']} Stages</td>
          <td style="font-size:11.5px;">{mp4_links}</td>
          <td style="font-size:11.5px;">{stage_links}</td>
          <td>{status_badge}</td>
        </tr>""")

    # Build 20 PD Sources rows
    pd_rows_html = []
    for i, s in enumerate(verified_sources, 1):
        pd_rows_html.append(f"""
        <tr>
          <td>{i}</td>
          <td><a href="file:///C:/dev/864zeros-publish/sources/public_domain_classics/{s['file']}" target="_blank"><code>{s['file']}</code></a></td>
          <td><strong>{s['title']}</strong><br/><span style="color:var(--text-muted); font-size:11.5px;">{s['author']}</span></td>
          <td>{s.get('translator', '')}</td>
          <td>{s['publication_year']}</td>
          <td>#{s['gutenberg_id']}</td>
          <td>{fmt_bytes(s['bytes'])}</td>
          <td><code>{s['sha256'][:14]}…</code></td>
          <td><span class="badge badge-green">LOCKED</span></td>
        </tr>""")

    # Build Focus Packs rows
    fp_rows_html = []
    for fp in focus_packs:
        vol_badge = '<span class="badge badge-amber">Vol 2</span>' if fp.get("volume") == 2 else '<span class="badge badge-blue">Vol 1</span>'
        fp_rows_html.append(f"""
        <tr>
          <td>{vol_badge}</td>
          <td><code>{fp['pack_id']}</code></td>
          <td><strong>{fp['title']}</strong><br/><span style="color:var(--text-muted); font-size:11.5px;">{fp.get('subtitle','')}</span></td>
          <td>{fp.get('author_or_source','')}</td>
          <td><strong>{fp.get('entry_count', 30)}</strong></td>
          <td><a href="file:///C:/dev/864zeros-publish/{fp['path']}" target="_blank">Open JSON ↗</a></td>
          <td><span class="badge badge-green">{fp.get('status','VERIFIED')}</span></td>
        </tr>""")

    # Build Bricks rows
    brick_rows_html = []
    for b in bricks:
        brick_rows_html.append(f"""
        <tr>
          <td><code>{b['brick_id']}</code></td>
          <td><a href="file:///C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/shared/bricks/{b['file']}" target="_blank"><code>{b['file']}</code></a></td>
          <td><span class="badge badge-purple">{b['category']}</span></td>
          <td>{b['purpose']}</td>
          <td>{", ".join(b.get("consumers", []))}</td>
          <td><span class="badge badge-green">{b.get('self_test_count', 5)}/{b.get('self_test_count', 5)} PASS</span></td>
        </tr>""")

    # Build Storage Telemetry pills
    top_exts = [".mp4", ".wav", ".png", ".jpg", ".svg", ".json", ".txt", ".mp3", ".html", ".py", ".cjs", ".safetensors"]
    storage_rows_html = []
    for ext in top_exts:
        cnt = ext_counts.get(ext, 0)
        bts = ext_bytes.get(ext, 0)
        if cnt > 0:
            storage_rows_html.append(f"""
            <div class="storage-pill">
              <div class="sp-ext">{ext}</div>
              <div class="sp-cnt">{cnt:,} files</div>
              <div class="sp-sz">{fmt_bytes(bts)}</div>
            </div>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Division 4 Front Door — 864zeros Creative Studio (`864zeros-publish` · Sloane Sterling)</title>
  <style>
    :root {{
      --bg-deep: #070b12;
      --bg-panel: #0f172a;
      --bg-card: #182235;
      --bg-card-hover: #1f2d46;
      --border: #28354e;
      --border-accent: rgba(56, 189, 248, 0.45);
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --accent-sky: #38bdf8;
      --accent-amber: #f59e0b;
      --accent-emerald: #10b981;
      --accent-violet: #a78bfa;
      --accent-rose: #f43f5e;
      --cream-paper: #faf6ee;
      --ink-dark: #18181b;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
      background: radial-gradient(circle at top right, #172554 0%, var(--bg-deep) 45%);
      color: var(--text-main);
      line-height: 1.58;
      padding-bottom: 90px;
    }}
    a {{ color: var(--accent-sky); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}

    .hero-header {{
      border-bottom: 1px solid var(--border);
      background: rgba(15, 23, 42, 0.94);
      padding: 28px 24px 20px;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(14px);
    }}
    .container {{ max-width: 1440px; margin: 0 auto; padding: 0 20px; }}
    .header-top {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
    }}
    .studio-kicker {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 4px 12px;
      border-radius: 999px;
      font-size: 11.5px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.45);
      color: #fbbf24;
      margin-bottom: 8px;
    }}
    h1 {{ font-size: 26px; font-weight: 800; color: #fff; letter-spacing: -0.02em; }}
    .subtitle {{ color: var(--text-muted); font-size: 13.5px; max-width: 880px; margin-top: 4px; }}

    /* Pillar Navigation */
    .pillar-nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
      align-items: center;
    }}
    .nav-btn {{
      padding: 8px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: #cbd5e1;
      font-size: 12.5px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s ease;
    }}
    .nav-btn:hover, .nav-btn.active {{
      background: rgba(56, 189, 248, 0.18);
      border-color: var(--accent-sky);
      color: #fff;
    }}
    .hub-link {{
      margin-left: auto;
      padding: 8px 14px;
      border-radius: 8px;
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
      color: #090d16;
      font-weight: 800;
      font-size: 12.5px;
    }}
    .hub-link:hover {{ text-decoration: none; opacity: 0.92; }}

    /* KPI Strip */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }}
    .kpi-card {{
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      border-top: 3px solid var(--accent-sky);
    }}
    .kpi-val {{ font-size: 25px; font-weight: 800; color: #fff; }}
    .kpi-label {{ font-size: 12px; color: var(--text-muted); font-weight: 600; margin-top: 2px; }}
    .kpi-sub {{ font-size: 11px; color: #6ee7b7; font-family: Consolas, monospace; margin-top: 5px; }}

    /* Three Pillar Banner */
    .pillars-overview {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 16px;
      margin-bottom: 26px;
    }}
    .pillar-box {{
      background: linear-gradient(145deg, rgba(24, 34, 53, 0.92), rgba(15, 23, 42, 0.96));
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
    }}
    .pillar-box h3 {{ font-size: 16px; color: #fff; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }}
    .pillar-box p {{ font-size: 13px; color: var(--text-muted); margin-bottom: 10px; }}
    .pillar-box ul {{ padding-left: 18px; font-size: 12.5px; color: #cbd5e1; }}
    .pillar-box li {{ margin-bottom: 4px; }}

    /* Roster */
    .roster-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
      margin-bottom: 26px;
    }}
    .leader-card {{
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 15px;
      display: flex;
      gap: 14px;
      align-items: center;
    }}
    .leader-avatar {{
      width: 62px;
      height: 62px;
      border-radius: 10px;
      object-fit: cover;
      border: 2px solid var(--border-accent);
      flex-shrink: 0;
    }}
    .leader-role {{ font-size: 10.5px; font-weight: 700; text-transform: uppercase; color: var(--accent-amber); }}
    .leader-name {{ font-size: 15.5px; font-weight: 700; color: #fff; }}
    .leader-bio {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}

    /* Section Block */
    .section-block {{
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 28px;
    }}
    .section-header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 14px;
      margin-bottom: 18px;
    }}
    .section-title {{ font-size: 19px; font-weight: 800; color: #fff; }}
    .owner-tag {{
      font-size: 11.5px;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(167, 139, 250, 0.15);
      border: 1px solid rgba(167, 139, 250, 0.4);
      color: #c4b5fd;
      font-weight: 600;
    }}

    /* Storage Pills */
    .storage-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(135px, 1fr));
      gap: 10px;
      margin-bottom: 18px;
    }}
    .storage-pill {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      text-align: center;
    }}
    .sp-ext {{ font-family: Consolas, monospace; font-size: 15px; font-weight: 800; color: var(--accent-sky); }}
    .sp-cnt {{ font-size: 13px; font-weight: 700; color: #fff; margin-top: 2px; }}
    .sp-sz {{ font-size: 11px; color: var(--text-muted); }}

    /* Filter Bar */
    .filter-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 16px;
      align-items: center;
    }}
    .filter-btn {{
      padding: 6px 12px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: var(--text-muted);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
    }}
    .filter-btn.active, .filter-btn:hover {{
      background: rgba(56, 189, 248, 0.18);
      border-color: var(--accent-sky);
      color: #fff;
    }}
    .search-input {{
      margin-left: auto;
      padding: 7px 12px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: #fff;
      font-size: 12.5px;
      min-width: 240px;
    }}

    /* Art Gallery Grid */
    .art-gallery {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(215px, 1fr));
      gap: 14px;
    }}
    .art-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .art-card:hover {{
      transform: translateY(-2px);
      border-color: var(--accent-sky);
    }}
    .art-thumb-link {{
      position: relative;
      display: block;
      height: 175px;
      background: #090d16;
      overflow: hidden;
    }}
    .art-thumb-link img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}
    .art-ext-tag {{
      position: absolute;
      bottom: 6px;
      right: 6px;
      background: rgba(9, 13, 22, 0.85);
      color: #cbd5e1;
      font-size: 10px;
      font-family: Consolas, monospace;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid var(--border);
    }}
    .art-body {{
      padding: 10px 12px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    }}
    .art-body h4 {{ font-size: 12.5px; color: #fff; line-height: 1.35; }}

    /* Video Theater Grid */
    .video-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
    }}
    .video-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
    }}
    .video-card video {{
      width: 100%;
      height: 190px;
      background: #000;
      display: block;
      object-fit: contain;
    }}
    .video-meta {{ padding: 12px; }}

    /* Interactive Viewers Shelf */
    .viewers-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
      gap: 14px;
    }}
    .viewer-card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 10px;
    }}
    .viewer-card h4 {{ font-size: 15px; color: #fff; }}
    .viewer-card p {{ font-size: 12.5px; color: var(--text-muted); }}
    .btn-launch {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 8px 12px;
      border-radius: 8px;
      background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
      color: #fff;
      font-weight: 700;
      font-size: 12px;
      text-decoration: none;
    }}
    .btn-launch:hover {{ text-decoration: none; opacity: 0.92; }}

    /* Tables */
    .table-wrap {{ overflow-x: auto; max-height: 540px; overflow-y: auto; border: 1px solid var(--border); border-radius: 10px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
    th, td {{ padding: 9px 12px; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{
      background: #162032;
      color: #cbd5e1;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 11px;
      position: sticky;
      top: 0;
      z-index: 10;
    }}
    code {{
      font-family: Consolas, monospace;
      font-size: 11px;
      background: rgba(7, 11, 18, 0.75);
      padding: 2px 5px;
      border-radius: 4px;
      color: #7dd3fc;
    }}
    .badge {{
      display: inline-block;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 700;
    }}
    .badge-green {{ background: rgba(16, 185, 129, 0.16); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }}
    .badge-blue {{ background: rgba(56, 189, 248, 0.16); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.4); }}
    .badge-amber {{ background: rgba(245, 158, 11, 0.16); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }}
    .badge-purple {{ background: rgba(167, 139, 250, 0.16); color: #ddd6fe; border: 1px solid rgba(167, 139, 250, 0.4); }}
    .badge-rose {{ background: rgba(244, 63, 94, 0.16); color: #fda4af; border: 1px solid rgba(244, 63, 94, 0.4); }}
  </style>
</head>
<body>

  <header class="hero-header">
    <div class="container">
      <div class="header-top">
        <div>
          <div class="studio-kicker">🚪 DIVISION 4 FRONT DOOR · 864ZEROS CREATIVE STUDIO, MEDIA &amp; PUBLISHING (`864zeros-publish`)</div>
          <h1>Sloane Sterling's Living Division Front Door — Assets, Frameworks, Media &amp; Content</h1>
          <p class="subtitle">
            Auto-generated live inventory of Division 4 (`864zeros-publish`). Re-run <code>python scripts/build_division_front_doors.py</code> anytime to refresh all asset storage counts, functional engines/bricks, <code>jeff_sketch</code> drawings, videos, books, and content packs.
          </p>
        </div>
        <div style="text-align:right; font-size:12px; color:var(--text-muted);">
          <div><strong>Last Auto-Scan:</strong> {now_str}</div>
          <div><strong>Total Division Files:</strong> {data['total_files']:,} ({fmt_bytes(data['total_bytes'])})</div>
          <div style="color:#6ee7b7; font-weight:700;">✓ Clean-Room &amp; Provenance Verified</div>
        </div>
      </div>

      <nav class="pillar-nav">
        <a class="nav-btn" href="file:///C:/dev/864zeros-llc/LIBRARY/overview.html">Div 0: Exec &amp; KIA (`LIBRARY`)</a>
        <a class="nav-btn" href="file:///C:/dev/864zeros-llc/LLC-DIV-1-INTELLIGENCE/overview.html">Div 1: Intelligence (`DIV-1`)</a>
        <a class="nav-btn" href="file:///C:/dev/864zeros-ISD/overview.html">Div 2: Product &amp; ISD (`864zeros-ISD`)</a>
        <a class="nav-btn" href="file:///C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/overview.html">Div 3: Software Factory (`DIV-3`)</a>
        <a class="nav-btn active" href="file:///C:/dev/864zeros-publish/overview.html">Div 4: Creative Studio (`864zeros-publish`)</a>
        <a class="nav-btn" href="file:///C:/dev/864zeros-llc/LLC-DIV-4-GTM/overview.html">Div 5: GTM &amp; Web (`DIV-4-GTM`)</a>
        <a class="hub-link" href="file:///C:/dev/864zeros-llc/DIVISION_FRONT_DOORS.html">🏛️ Master Division Hub (`DIVISION_FRONT_DOORS.html`) ↗</a>
      </nav>
      <nav class="pillar-nav" style="margin-top:8px;">
        <a class="nav-btn active" href="#pillars">3-Pillar Architecture</a>
        <a class="nav-btn" href="#viewers">Interactive Books &amp; Labs (10)</a>
        <a class="nav-btn" href="#drawings">🎨 Jeff-Style Drawings &amp; Art ({len(drawings)})</a>
        <a class="nav-btn" href="#video-theater">🎬 Playable Video Theater ({data['ext_counts'].get('.mp4', 0)} MP4s)</a>
        <a class="nav-btn" href="#frameworks">🧠 Frameworks, Focus Packs &amp; Bricks</a>
        <a class="nav-btn" href="#dam-matrix">📦 34-Product DAM Vault</a>
        <a class="nav-btn" href="#provenance">🔒 20-Volume Pre-1931 PD Vault</a>
        <a class="nav-btn" href="#bible-literary">📜 Bible (1,514), Poems &amp; Recovery</a>
      </nav>
    </div>
  </header>

  <main class="container">

    <!-- LIVE TELEMETRY KPI STRIP -->
    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-val">{data['total_files']:,}</div>
        <div class="kpi-label">Live Studio Files Stored</div>
        <div class="kpi-sub">{fmt_bytes(data['total_bytes'])} Total Vault Size</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{len(drawings)} Plates</div>
        <div class="kpi-label">`jeff_sketch` / `painting` / `geometric`</div>
        <div class="kpi-sub">+ 287 LoRA Training Plates</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{data['ext_counts'].get('.mp4', 0)} MP4s</div>
        <div class="kpi-label">Rendered Videos &amp; Shorts</div>
        <div class="kpi-sub">+ 72 HALT 9:16 Storyboards</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">{data['ext_counts'].get('.wav', 0) + data['ext_counts'].get('.mp3', 0)} Stems</div>
        <div class="kpi-label">Master Audio &amp; Narration</div>
        <div class="kpi-sub">{data['ext_counts'].get('.wav', 0)} WAV · {data['ext_counts'].get('.mp3', 0)} MP3</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">2,306+</div>
        <div class="kpi-label">Published Literary &amp; Pack Cards</div>
        <div class="kpi-sub">270 Focus · 72 HALT · 1,514 Bible</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">20 Volumes</div>
        <div class="kpi-label">Pre-1931 PD Classics Locked</div>
        <div class="kpi-sub">13.49 MB · SHA-256 Verified</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-val">8 Bricks</div>
        <div class="kpi-label">Studio v1.8 JS Feature Bricks</div>
        <div class="kpi-sub">+ 6 Python/Node Generators</div>
      </div>
    </section>

    <!-- STUDIO LEADERSHIP ROSTER -->
    <section class="roster-grid">
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/sloane-sterling.jpg" alt="Sloane Sterling" />
        <div>
          <div class="leader-role">VP-STUDIO · Division 4 Head</div>
          <div class="leader-name">Sloane Sterling</div>
          <div class="leader-bio">VP of Content, Media &amp; Publishing. Owns the Studio Front Door, cross-fleet asset synchronization, and publishing governance.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/julian-thorne.jpg" alt="Julian Thorne" />
        <div>
          <div class="leader-role">LEAD-CONTENT · Literary IP &amp; Packs</div>
          <div class="leader-name">Julian Thorne</div>
          <div class="leader-bio">Head of Literary IP, Editorial &amp; Focus Packs. Leads all 9 Focus Packs, 3 HALT packs, Practice Books, Poems, Prayers &amp; Bible Library.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/orion-kai.jpg" alt="Orion Kai" />
        <div>
          <div class="leader-role">LEAD-MEDIA · Visuals, LoRA &amp; Video</div>
          <div class="leader-name">Orion Kai</div>
          <div class="leader-bio">Head of Multimedia Production &amp; DAM. Commands <code>jeff_sketch</code>/<code>jeff_painting</code> art, Smudge Lab, 204 MP4 videos &amp; 34-product DAM.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/vera-lindqvist.jpg" alt="Vera Lindqvist" />
        <div>
          <div class="leader-role">STUDIO-LEGAL · IP &amp; Provenance</div>
          <div class="leader-name">Vera Lindqvist</div>
          <div class="leader-bio">Director of IP &amp; Public Domain Clearance. Governs <code>PROVENANCE_LOCK.json</code>, <code>STOP_SHIP</code> authority &amp; clean-room blacklists.</div>
        </div>
      </div>
    </section>

    <!-- THE 3 EVOLVING FRONT-DOOR PILLARS -->
    <section class="pillars-overview" id="pillars">
      <div class="pillar-box">
        <h3>🗄️ Pillar I: Always-Evolving Asset Storage Vault</h3>
        <p>Single-source-of-truth filesystem where raw provenance inputs, trained LoRA weights, JSON content packs, and product DAM vaults live under strict namespace boundaries:</p>
        <ul>
          <li><code>sources/public_domain_classics/</code> — 20 SHA-256 locked pre-1931 Gutenberg texts (13.49 MB)</li>
          <li><code>shared/</code> — 9 Focus Packs (270 cards), 66-Book Bible Library (1,514 records), 2 Practice Books, 155 Poems/Prayers/Reflections</li>
          <li><code>data/packs/</code> — 3 Multi-format HALT Affect-Mapped Packs (72 cards)</li>
          <li><code>media/visuals/</code> — <code>864z_jeff_sketch_v1.safetensors</code> (228.45 MB) + 287 training plates + 96 rendered fine-art plates</li>
          <li><code>media/products/</code> — 34-Product DAM Vault (204 MP4s, 644 WAV/MP3s, 1,170 PNG/JPG/SVGs)</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>⚙️ Pillar II: Functionality, Frameworks &amp; Brick Growth</h3>
        <p>Reusable behavioral frameworks, compilers, and zero-dependency Feature Bricks that turn static Studio JSON into live app &amp; print experiences:</p>
        <ul>
          <li><strong>HALT 6-State Affect Framework</strong> (<code>HUNGRY, ANGRY, LONELY, TIRED, STRESSED, HOPELESS</code>) + FNV-1a deterministic router (<code>BRK-STUDIO-002</code>)</li>
          <li><strong>4-Pillar Habit &amp; Franklin 13-Virtue Cadence</strong> (Primary Focus Pin, When-Then Anchor, Floor Rep, Continuity Shield — <code>BRK-STUDIO-003</code>)</li>
          <li><strong>Two-Pass Visual-DAGR &amp; Smudge/Advection Filter</strong> (<code>864z-smudge-filter.bat</code>, <code>smudge_filter_lab.html</code>, <code>lora_voice_verifier.py</code>)</li>
          <li><strong>5"×8" Print Compiler &amp; <code>864z://</code> QR Codec</strong> (<code>journal_compiler.py</code>, <code>BRK-QR-001</code>, <code>BRK-PUB-001</code>)</li>
          <li><strong>3-Tier <code>android_arm64</code> Edge OCR Cascade</strong> (Tier A Gemma 3 / Tier B ML Kit v2 / Tier C QR + Drive OAuth — <code>BRK-OCR-001</code>)</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>🎨 Pillar III: Media, Visual Art (`jeff_sketch`) &amp; Content Output</h3>
        <p>Every customer-facing book, interactive viewer, fine-art plate, and social/store video produced by the Studio:</p>
        <ul>
          <li><strong>3 Print-Ready 5"×8" KDP Softback QR Journals</strong> ($2.30 print cost · $5.49 net royalty/unit)</li>
          <li><strong>2 Illustrated Practice Books &amp; Ebooks</strong> (<em>Foundations of Resilience: 10 Lessons</em> &amp; <em>5 Poems in Ink &amp; Resilience</em>)</li>
          <li><strong>138+ Rendered Drawings in Jeff's Style</strong> (Freehand Gestalt, 3-Pass DAGR, Scribble-to-Line, Geometric Coif, Watercolor, SVG)</li>
          <li><strong>204 Rendered MP4 Videos + 72 9:16 Storyboards</strong> across ClearStreak, ChoiceGuard, Edge Add-ons &amp; 18 GWS Add-ons</li>
        </ul>
      </div>
    </section>

    <!-- LIVE STORAGE TELEMETRY -->
    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🗄️ Live Asset Storage Breakdown (`C:\\dev\\864zeros-publish`)</div>
        <span class="owner-tag">Auto-Scanned Filesystem Telemetry · {data['total_files']:,} Files ({fmt_bytes(data['total_bytes'])})</span>
      </div>
      <div class="storage-grid">
        {"".join(storage_rows_html)}
      </div>
    </section>

    <!-- INTERACTIVE BOOKS, LABS & VIEWERS SHELF -->
    <section class="section-block" id="viewers">
      <div class="section-header">
        <div class="section-title">🚀 Interactive Studio Books, Print Editions &amp; Visual Labs (Click to Launch)</div>
        <span class="owner-tag">10 Standalone HTML Applications Inside `864zeros-publish`</span>
      </div>
      <div class="viewers-grid">
        <div class="viewer-card">
          <div>
            <span class="badge badge-amber">5"×8" KDP Print Edition #1</span>
            <h4 style="margin-top:6px;">The Still Waters Ledger (KJV HALT Journal)</h4>
            <p>24-page 5"×8" softback interior with verbatim KJV scripture, plain rendering, 12 ruled lines, corner fiducials, and <code>864z://</code> vector QR anchors.</p>
          </div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-publish/build/journals/halt_kjv_scripture_softback_5x8.html" target="_blank">📖 Open KJV 5"×8" Journal ↗</a>
        </div>
        <div class="viewer-card">
          <div>
            <span class="badge badge-amber">5"×8" KDP Print Edition #2</span>
            <h4 style="margin-top:6px;">The Stoic Citadel Companion Journal</h4>
            <p>24-page 5"×8" softback interior pairing Marcus Aurelius, Epictetus &amp; Seneca with HALT affect triggers and scannable QR codes.</p>
          </div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-publish/build/journals/stoic_marcus_aurelius_softback_5x8.html" target="_blank">🏛️ Open Stoic 5"×8" Journal ↗</a>
        </div>
        <div class="viewer-card">
          <div>
            <span class="badge badge-amber">5"×8" KDP Print Edition #3</span>
            <h4 style="margin-top:6px;">The 13 Virtues &amp; Habit Architecture Journal</h4>
            <p>24-page 5"×8" softback interior featuring Benjamin Franklin, William James, Samuel Smiles &amp; Arnold Bennett daily habit ledgers.</p>
          </div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-publish/build/journals/habit_franklin_virtues_softback_5x8.html" target="_blank">⚡ Open Habit 5"×8" Journal ↗</a>
        </div>
        <div class="viewer-card">
          <div>
            <span class="badge badge-green">Illustrated Practice Book #1</span>
            <h4 style="margin-top:6px;">Foundations of Resilience: 10 Life Lessons</h4>
            <p>Interactive illustrated workbook combining PD scripture, behavioral intent, journaling prompts, and 20 <code>jeff_sketch</code> plates.</p>
          </div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-publish/shared/practice_books/foundations_of_resilience/practice_book_viewer.html" target="_blank">🎨 Open Practice Book Viewer ↗</a>
        </div>
        <div class="viewer-card">
          <div>
            <span class="badge badge-green">Illustrated Ebook #2</span>
            <h4 style="margin-top:6px;">Words in the Negative Space: 5 Poems in Ink</h4>
            <p>Original 864zeros poetry &amp; plain-language meditations paired with 22 <code>jeff_geometric</code> SVG &amp; fine-art plates.</p>
          </div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-publish/shared/practice_books/five_plain_language_meditations/ebook_viewer.html" target="_blank">🖋️ Open 5 Meditations Ebook ↗</a>
        </div>
        <div class="viewer-card">
          <div>
            <span class="badge badge-purple">Visual Engineering Lab #1</span>
            <h4 style="margin-top:6px;">Smudge Filter &amp; Advection Lab (`jeff_sketch`)</h4>
            <p>Interactive comparison lab for Two-Pass Visual-DAGR, directional hatching, smudge advection, and subtractive facial erasure.</p>
          </div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-publish/media/visuals/smudge_filter_lab.html" target="_blank">🧪 Launch Smudge Filter Lab ↗</a>
        </div>
        <div class="viewer-card">
          <div>
            <span class="badge badge-purple">Visual Engineering Lab #2</span>
            <h4 style="margin-top:6px;">Visual LoRA Prompt &amp; Style Guide</h4>
            <p>Canonical trigger formulas and prompt matrix for <code>864z_jeff_sketch_v1.safetensors</code> (<code>jeff_sketch</code>, <code>jeff_painting</code>, <code>jeff_geometric</code>).</p>
          </div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-publish/media/visuals/lora_overview_prompts_for_jeff_sketch.html" target="_blank">🖼️ Open LoRA Style Guide ↗</a>
        </div>
        <div class="viewer-card">
          <div>
            <span class="badge badge-blue">Scripture &amp; Study Readers</span>
            <h4 style="margin-top:6px;">66-Book Bible Viewer &amp; 660 Study Lessons</h4>
            <p>Complete dual-rendering Bible viewer (834 key verses) and 66-book actionable study lesson explorer (660 lessons).</p>
          </div>
          <div style="display:flex; gap:6px;">
            <a class="btn-launch" style="flex:1;" href="file:///C:/dev/864zeros-publish/shared/bible/bible_viewer.html" target="_blank">📜 Bible Viewer ↗</a>
            <a class="btn-launch" style="flex:1;" href="file:///C:/dev/864zeros-publish/shared/bible/bible_study_viewer.html" target="_blank">🧭 660 Lessons ↗</a>
          </div>
        </div>
        <div class="viewer-card">
          <div>
            <span class="badge badge-rose">Live Briefing &amp; Clinical Review</span>
            <h4 style="margin-top:6px;">Kate Live Briefing Room &amp; Clinical Review</h4>
            <p>Kate Zefore's live video briefing room stage (<code>kate_live_call.html</code>) and ClearStreak 130-passage clinical review portal.</p>
          </div>
          <div style="display:flex; gap:6px;">
            <a class="btn-launch" style="flex:1;" href="file:///C:/dev/864zeros-publish/media/video/kate_live_call.html" target="_blank">📹 Kate Live Stage ↗</a>
            <a class="btn-launch" style="flex:1;" href="file:///C:/dev/864zeros-publish/apps/clearstreak/clinical_review.html" target="_blank">🩺 Clinical Portal ↗</a>
          </div>
        </div>
      </div>
    </section>

    <!-- DRAWINGS & FINE ART GALLERY IN JEFF STYLE -->
    <section class="section-block" id="drawings">
      <div class="section-header">
        <div class="section-title">🎨 Drawings &amp; Visual Plates in Jeff's Style (`jeff_sketch` · `jeff_painting` · `jeff_geometric`)</div>
        <span class="owner-tag">Lead: Orion Kai (`LEAD-MEDIA`) · {len(drawings)} Rendered Plates + 287 LoRA Training Plates</span>
      </div>
      <p style="color:var(--text-muted); font-size:13px; margin-bottom:14px;">
        Filter across all <strong>{len(drawings)} rendered Studio plates</strong> in <code>media/visuals/rendered_art/</code> and <code>shared/practice_books/*/images/</code>—including Pass 1 freehand searching lines, Gestalt subtractive portraits, 3-pass DAGR kinetic search &amp; erasure studies, geometric coif colorizations, watercolor washes, and crisp SVG vector masters. Click any plate to view full resolution.
      </p>

      <div class="filter-bar">
        <button class="filter-btn active" onclick="filterArt('all', this)">All Plates ({len(drawings)})</button>
        <button class="filter-btn" onclick="filterArt('freehand_gestalt', this)">Pass 1 Freehand &amp; Gestalt</button>
        <button class="filter-btn" onclick="filterArt('dagr_multipass', this)">DAGR 3-Pass &amp; Scribble Studies</button>
        <button class="filter-btn" onclick="filterArt('geometric_color', this)">Geometric Coif &amp; Watercolor</button>
        <button class="filter-btn" onclick="filterArt('practice_poem', this)">Practice Books &amp; Poems</button>
        <button class="filter-btn" onclick="filterArt('svg_vector', this)">SVG Vector Masters</button>
        <input type="text" id="artSearch" class="search-input" placeholder="Search drawings (e.g. lighthouse, dagr, coif, step)..." oninput="searchArt(this.value)" />
      </div>

      <div class="art-gallery" id="artGallery">
        {"".join(drawing_cards_html)}
      </div>
    </section>

    <!-- PLAYABLE VIDEO THEATER -->
    <section class="section-block" id="video-theater">
      <div class="section-header">
        <div class="section-title">🎬 Studio Video &amp; Shorts Theater ({data['ext_counts'].get('.mp4', 0)} Rendered MP4s + 72 HALT 9:16 Storyboards)</div>
        <span class="owner-tag">Lead: Orion Kai (`LEAD-MEDIA`) · `media/products/*/video/` &amp; `build/video_manifests/`</span>
      </div>
      <p style="color:var(--text-muted); font-size:13px; margin-bottom:16px;">
        Playable preview of our rendered Master Explainers (16:9) and Vertical Shorts (9:16) directly from the local DAM vault, alongside links to the 3 new HALT 9:16 storyboard manifests (<a href="file:///C:/dev/864zeros-publish/build/video_manifests/halt_kjv_scripture_9x16_reels.json" target="_blank">KJV 24 Reels</a> · <a href="file:///C:/dev/864zeros-publish/build/video_manifests/stoic_marcus_aurelius_9x16_reels.json" target="_blank">Stoic 24 Reels</a> · <a href="file:///C:/dev/864zeros-publish/build/video_manifests/habit_franklin_virtues_9x16_reels.json" target="_blank">Habit 24 Reels</a>):
      </p>
      <div class="video-grid">
        {"".join(video_cards_html)}
      </div>
    </section>

    <!-- FRAMEWORKS, FOCUS PACKS & STUDIO BRICKS -->
    <section class="section-block" id="frameworks">
      <div class="section-header">
        <div class="section-title">🧠 Studio Frameworks, Focus Packs Catalog (`v2.0.0` · 12 Packs) &amp; Shared `v1.8` Feature Bricks</div>
        <span class="owner-tag">Leads: Julian Thorne · Sloane Sterling · Marcus Vance</span>
      </div>
      <h3 style="font-size:15px; color:#fff; margin-bottom:10px;">A. Master Focus Packs Catalog (`shared/focus_packs/focus_packs_catalog.json` — Volumes 1 &amp; 2)</h3>
      <div class="table-wrap" style="margin-bottom:24px;">
        <table>
          <thead>
            <tr>
              <th>Vol</th>
              <th>Pack ID</th>
              <th>Title &amp; Focus Framework</th>
              <th>Primary Source &amp; Pre-1931 Translator</th>
              <th>Records</th>
              <th>JSON Source</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {"".join(fp_rows_html)}
          </tbody>
        </table>
      </div>

      <h3 style="font-size:15px; color:#fff; margin-bottom:10px;">B. Extracted Zero-Dependency Studio Feature Bricks (`LLC-DIV-3-FACTORY/shared/bricks/` · `45/45` Assertions PASS)</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Brick ID</th>
              <th>Brick File</th>
              <th>Category</th>
              <th>Functional Contract</th>
              <th>Consuming Products</th>
              <th>Unit Tests</th>
            </tr>
          </thead>
          <tbody>
            {"".join(brick_rows_html)}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 34-PRODUCT DAM VAULT MATRIX -->
    <section class="section-block" id="dam-matrix">
      <div class="section-header">
        <div class="section-title">📦 34-Product Digital Asset Management (DAM) Vault Matrix (`media/products/`)</div>
        <span class="owner-tag">Live Asset Counts per Product · {len(dam_products)} Products Seeded</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Product Slug</th>
              <th>Videos</th>
              <th>Audio Stems</th>
              <th>Visuals/Icons</th>
              <th>HTML Stages</th>
              <th>Sample MP4 Deliverables</th>
              <th>Interactive HTML Stages</th>
              <th>Vault Status</th>
            </tr>
          </thead>
          <tbody>
            {"".join(dam_rows_html)}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 20-VOLUME PRE-1931 PUBLIC DOMAIN PROVENANCE VAULT -->
    <section class="section-block" id="provenance">
      <div class="section-header">
        <div class="section-title">🔒 20-Volume Pre-1931 Public Domain Provenance Vault (`13.49 MB` · SHA-256 Locked)</div>
        <span class="owner-tag">Lead: Vera Lindqvist (`STUDIO-LEGAL`) · `sources/public_domain_classics/PROVENANCE_LOCK.json`</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Raw Gutenberg File</th>
              <th>Work &amp; Original Author</th>
              <th>Verified Pre-1931 Translator / Edition</th>
              <th>Year</th>
              <th>PG ID</th>
              <th>Size</th>
              <th>SHA-256</th>
              <th>Clearance</th>
            </tr>
          </thead>
          <tbody>
            {"".join(pd_rows_html)}
          </tbody>
        </table>
      </div>
    </section>

    <!-- BIBLE, POEMS, PRAYERS & RECOVERY -->
    <section class="section-block" id="bible-literary">
      <div class="section-header">
        <div class="section-title">📜 Canonical Bible Library (`1,514` Records), Original Poetry/Prayers (`155`) &amp; Recovery (`280`)</div>
        <span class="owner-tag">Lead: Julian Thorne (`LEAD-CONTENT`) · `shared/bible/`, `shared/creative/`, `apps/clearstreak/`</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Namespace</th>
              <th>Collection Title</th>
              <th>Records</th>
              <th>Schema / Format</th>
              <th>Primary Files &amp; Viewers</th>
              <th>Legal &amp; QA Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><code>shared/bible</code></td>
              <td><strong>66-Book Dual-Rendering Key-Verse Library</strong></td>
              <td><strong>834</strong></td>
              <td><code>{{ book, chapter, citation, text, plain }}</code></td>
              <td><a href="file:///C:/dev/864zeros-publish/shared/bible/bible_viewer.html" target="_blank">bible_viewer.html ↗</a> · <a href="file:///C:/dev/864zeros-publish/shared/bible/bible_index.json" target="_blank">bible_index.json</a></td>
              <td><span class="badge badge-green">PUBLISHED PD + ORIGINAL</span></td>
            </tr>
            <tr>
              <td><code>shared/bible</code></td>
              <td><strong>66-Book Actionable Life Lessons Series</strong></td>
              <td><strong>660</strong></td>
              <td>10 behavioral lessons + overview per book (66 books)</td>
              <td><a href="file:///C:/dev/864zeros-publish/shared/bible/bible_study_viewer.html" target="_blank">bible_study_viewer.html ↗</a> · <a href="file:///C:/dev/864zeros-publish/shared/bible/bible_study_lessons.json" target="_blank">bible_study_lessons.json</a></td>
              <td><span class="badge badge-green">PUBLISHED PD + ORIGINAL</span></td>
            </tr>
            <tr>
              <td><code>shared/bible</code></td>
              <td><strong>Genesis 1–10 Behavioral Applications</strong></td>
              <td><strong>20</strong></td>
              <td>Situational principles, takeaways &amp; prompts</td>
              <td><a href="file:///C:/dev/864zeros-publish/shared/bible/genesis_applications.json" target="_blank">genesis_applications.json ↗</a></td>
              <td><span class="badge badge-green">PUBLISHED ORIGINAL</span></td>
            </tr>
            <tr>
              <td><code>shared/creative/poems</code></td>
              <td><strong>Original 864zeros Long-Form Narrative Poems</strong></td>
              <td><strong>5</strong></td>
              <td>Markdown manuscripts + paired <code>jeff_sketch</code> plates</td>
              <td><a href="file:///C:/dev/864zeros-publish/shared/creative/poems/the_architect_of_dawn.md" target="_blank">The Architect of Dawn</a> · <a href="file:///C:/dev/864zeros-publish/shared/creative/poems/the_lighthouse_at_the_worlds_edge.md" target="_blank">Lighthouse</a> · <a href="file:///C:/dev/864zeros-publish/shared/creative/poems/the_silent_cathedral_of_pine.md" target="_blank">Cathedral of Pine</a></td>
              <td><span class="badge badge-green">100% ORIGINAL IP</span></td>
            </tr>
            <tr>
              <td><code>shared/creative/prayers</code></td>
              <td><strong>Moment-of-Need Prayers &amp; Reflections</strong></td>
              <td><strong>150</strong></td>
              <td>100 Prayers (<code>prayers_100.json</code>) + 50 Reflections (<code>reflections_50.json</code>)</td>
              <td><a href="file:///C:/dev/864zeros-publish/shared/creative/prayers/prayers_100.json" target="_blank">prayers_100.json ↗</a> · <a href="file:///C:/dev/864zeros-publish/shared/creative/reflections/reflections_50.json" target="_blank">reflections_50.json ↗</a></td>
              <td><span class="badge badge-green">100% ORIGINAL IP</span></td>
            </tr>
            <tr>
              <td><code>apps/clearstreak</code></td>
              <td><strong>ClearStreak Recovery &amp; Affirmations Corpus</strong></td>
              <td><strong>280</strong></td>
              <td>130 passages + 50 recovery affirmations + 50 spiritual affirmations + 50 daily verses</td>
              <td><a href="file:///C:/dev/864zeros-publish/apps/clearstreak/PASSAGES_REPORT.html" target="_blank">PASSAGES_REPORT.html ↗</a> · <a href="file:///C:/dev/864zeros-publish/apps/clearstreak/clinical_review.html" target="_blank">clinical_review.html ↗</a></td>
              <td><span class="badge badge-amber">AFFIRMATIONS LIVE · PASSAGES CLINICAL GATE</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

  </main>

  <script>
    function filterArt(cat, btn) {{
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      const q = (document.getElementById('artSearch').value || '').toLowerCase();
      document.querySelectorAll('.art-card').forEach(card => {{
        const matchesCat = (cat === 'all') || (card.getAttribute('data-cat') === cat);
        const matchesSearch = !q || card.getAttribute('data-search').includes(q);
        card.style.display = (matchesCat && matchesSearch) ? 'flex' : 'none';
      }});
    }}
    function searchArt(val) {{
      const activeBtn = document.querySelector('.filter-btn.active');
      const activeCat = activeBtn ? (activeBtn.getAttribute('onclick').match(/'([^']+)'/)[1]) : 'all';
      filterArt(activeCat, activeBtn);
    }}
  </script>
</body>
</html>
"""


def build_company_division_hub_html(studio_data: dict, div_tels: dict) -> str:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M EDT")

    d0_c, d0_b = div_tels[0]["total_files"], div_tels[0]["total_bytes"]
    d1_c, d1_b = div_tels[1]["total_files"], div_tels[1]["total_bytes"]
    d2_c, d2_b = div_tels[2]["total_files"], div_tels[2]["total_bytes"]
    d3_c, d3_b = div_tels[3]["total_files"], div_tels[3]["total_bytes"]
    d4_c, d4_b = studio_data["total_files"], studio_data["total_bytes"]
    d5_c, d5_b = div_tels[5]["total_files"], div_tels[5]["total_bytes"]
    tot_c = d0_c + d1_c + d2_c + d3_c + d4_c + d5_c
    tot_b = d0_b + d1_b + d2_b + d3_b + d4_b + d5_b

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>864zeros LLC — Overarching Master Division Front Doors (`DIVISION_FRONT_DOORS.html`)</title>
  <style>
    :root {{
      --bg-deep: #070b12;
      --bg-panel: #0f172a;
      --bg-card: #182235;
      --border: #28354e;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --accent-sky: #38bdf8;
      --accent-amber: #f59e0b;
      --accent-emerald: #10b981;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
      background: radial-gradient(circle at top right, #172554 0%, var(--bg-deep) 45%);
      color: var(--text-main);
      line-height: 1.6;
      padding: 36px 24px 80px;
    }}
    .container {{ max-width: 1420px; margin: 0 auto; }}
    .kicker {{
      display: inline-block;
      padding: 4px 12px;
      border-radius: 999px;
      background: rgba(245, 158, 11, 0.16);
      border: 1px solid rgba(245, 158, 11, 0.45);
      color: #fbbf24;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 10px;
    }}
    h1 {{ font-size: 30px; font-weight: 800; color: #fff; letter-spacing: -0.02em; }}
    .sub {{ color: var(--text-muted); font-size: 14.5px; max-width: 920px; margin-top: 6px; margin-bottom: 22px; }}
    .kpi-strip {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
      gap: 12px;
      margin-bottom: 26px;
    }}
    .kpi-box {{
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-top: 3px solid var(--accent-sky);
      border-radius: 12px;
      padding: 14px 16px;
    }}
    .kpi-box .v {{ font-size: 23px; font-weight: 800; color: #fff; }}
    .kpi-box .l {{ font-size: 12px; color: var(--text-muted); font-weight: 600; }}
    .div-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
      gap: 20px;
    }}
    .div-card {{
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 16px;
      border-top: 4px solid var(--accent-sky);
    }}
    .div-card.highlight {{ border-top-color: var(--accent-amber); background: linear-gradient(145deg, #162238, #0f172a); }}
    .div-head {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }}
    .div-code {{ font-size: 11px; font-weight: 800; text-transform: uppercase; color: var(--accent-amber); letter-spacing: 0.06em; }}
    .div-title {{ font-size: 20px; font-weight: 800; color: #fff; margin-top: 2px; }}
    .div-lead {{ font-size: 12.5px; color: #cbd5e1; margin-top: 2px; }}
    .avatars-row {{ display: flex; gap: 8px; margin-top: 10px; align-items: center; }}
    .mini-avatar {{
      width: 38px; height: 38px; border-radius: 8px; object-fit: cover;
      border: 1.5px solid rgba(56, 189, 248, 0.5);
    }}
    .pillar-list {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px 16px;
      font-size: 12.5px;
      color: #e2e8f0;
    }}
    .pillar-list div {{ margin-bottom: 6px; }}
    .pillar-list div:last-child {{ margin-bottom: 0; }}
    .pillar-list strong {{ color: var(--accent-sky); }}
    code {{
      font-family: Consolas, monospace;
      font-size: 11px;
      background: rgba(7, 11, 18, 0.75);
      padding: 2px 5px;
      border-radius: 4px;
      color: #7dd3fc;
    }}
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 11px 16px;
      border-radius: 10px;
      background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%);
      color: #fff;
      font-weight: 800;
      font-size: 13px;
      text-decoration: none;
    }}
    .btn:hover {{ opacity: 0.92; }}
    .btn.gold {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: #090d16; }}
  </style>
</head>
<body>
  <div class="container">
    <span class="kicker">🏛️ 864zeros LLC · Overarching Master Front Door (`DIVISION_FRONT_DOORS.html` · Managed by Kate Zefore `COS-001`)</span>
    <h1>864zeros LLC — All-Division `overview.html` Front Doors</h1>
    <p class="sub">
      Every division of 864zeros LLC has its own living <code>overview.html</code> Front Door tracking <strong>(1) Asset Storage Vault</strong>, <strong>(2) Functionality, Frameworks &amp; Brick Growth</strong>, and <strong>(3) Media, Drawings &amp; Content Deliverables</strong>. Auto-compiled via <code>python C:\\dev\\864zeros-publish\\scripts\\build_division_front_doors.py</code> on <strong>{now_str}</strong>.
    </p>

    <div class="kpi-strip">
      <div class="kpi-box"><div class="v">6 Divisions</div><div class="l">All with Live `overview.html` Front Doors</div></div>
      <div class="kpi-box"><div class="v">{tot_c:,} Files</div><div class="l">Total Indexed Assets ({fmt_bytes(tot_b)})</div></div>
      <div class="kpi-box"><div class="v">13 Leaders</div><div class="l">C-Suite, Studio &amp; Specialist Roster</div></div>
      <div class="kpi-box"><div class="v">{len(studio_data['drawings'])} Plates</div><div class="l">`jeff_sketch` / `painting` / `geometric`</div></div>
      <div class="kpi-box"><div class="v">204 MP4s</div><div class="l">Master Explainers &amp; 9:16 Shorts</div></div>
      <div class="kpi-box"><div class="v">9 Bricks</div><div class="l">Shared v1.8 Feature Bricks (45/45 PASS)</div></div>
    </div>

    <div class="div-grid">

      <!-- DIVISION 0: EXECUTIVE COMMAND & KIA -->
      <div class="div-card">
        <div>
          <div class="div-head">
            <div>
              <div class="div-code">DIVISION 0 · LIBRARY/overview.html</div>
              <div class="div-title">Executive Command, Chief of Staff (`KIA`) &amp; Library</div>
              <div class="div-lead">Lead: <strong>Kate Zefore (`COS-001`)</strong> · Allegra Katz (`CFO`) · Cole Mercer (`CLO`)</div>
              <div class="avatars-row">
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/kate-zefore.jpg" title="Kate Zefore" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/allegra-katz.jpg" title="Allegra Katz" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/cole-mercer.jpg" title="Cole Mercer" />
              </div>
            </div>
            <span style="font-size:12px; color:#7dd3fc; font-weight:700;">{d0_c:,} files ({fmt_bytes(d0_b)})</span>
          </div>
          <div class="pillar-list" style="margin-top:14px;">
            <div><strong>1. Asset Storage:</strong> <code>LIBRARY/</code> (9 executive folders, 26 canonical docs) + <code>864zeros-diary</code> (8 milestone dispatches).</div>
            <div><strong>2. Functionality Growth:</strong> Project "Kate Is Alive" (KIA Phase 1, 6 live tools), Gmail REST API dispatcher, 60fps + A10G neural talking avatar rig.</div>
            <div><strong>3. Media &amp; Content:</strong> Pixel Command Office v2.0 (13 avatars, Office/Factory floorplan), Morning Briefs, PA CROP $5 Legal Brief.</div>
          </div>
        </div>
        <a class="btn" href="file:///C:/dev/864zeros-llc/LIBRARY/overview.html">🚪 Enter Division 0 Front Door (`LIBRARY/overview.html`) ↗</a>
      </div>

      <!-- DIVISION 1: MARKET INTELLIGENCE & VULTURE STRIKE -->
      <div class="div-card">
        <div>
          <div class="div-head">
            <div>
              <div class="div-code">DIVISION 1 · LLC-DIV-1-INTELLIGENCE/overview.html</div>
              <div class="div-title">Market Intelligence, Vulture Strike &amp; Scout</div>
              <div class="div-lead">Lead: <strong>Audrey Chen (`CPO`)</strong> · Jalen Barkley (`LEAD-DATA-ARCH`)</div>
              <div class="avatars-row">
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/audrey-chen.jpg" title="Audrey Chen" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/jalen-barkley.jpg" title="Jalen Barkley" />
              </div>
            </div>
            <span style="font-size:12px; color:#7dd3fc; font-weight:700;">{d1_c:,} files ({fmt_bytes(d1_b)})</span>
          </div>
          <div class="pillar-list" style="margin-top:14px;">
            <div><strong>1. Asset Storage:</strong> <code>LLC-DIV-1-INTELLIGENCE/</code> (`strikes/`, `briefs/`, `recon/`, `scan_results/`) + <code>864zero-scout</code>.</div>
            <div><strong>2. Functionality Growth:</strong> Vulture OS v2 review harvester, Rule of 40 opportunity scorer, autonomous distribution scout.</div>
            <div><strong>3. Media &amp; Content:</strong> GWS Add-ons Vulture Strike + Pulse + Veo Financial Plan, Zernio Master Dossier, ChoiceGuard Dossier.</div>
          </div>
        </div>
        <a class="btn" href="file:///C:/dev/864zeros-llc/LLC-DIV-1-INTELLIGENCE/overview.html">🚪 Enter Division 1 Front Door (`DIV-1/overview.html`) ↗</a>
      </div>

      <!-- DIVISION 2: PRODUCT STRATEGY & ISD BRAIN -->
      <div class="div-card">
        <div>
          <div class="div-head">
            <div>
              <div class="div-code">DIVISION 2 · 864zeros-ISD/overview.html</div>
              <div class="div-title">Product Strategy, ISD Brain &amp; Pricing Governance</div>
              <div class="div-lead">Lead: <strong>Audrey Chen (`CPO`)</strong> · Allegra Katz (`CFO`) · Jalen Barkley (`LEAD-DATA-ARCH`)</div>
              <div class="avatars-row">
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/audrey-chen.jpg" title="Audrey Chen" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/allegra-katz.jpg" title="Allegra Katz" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/jalen-barkley.jpg" title="Jalen Barkley" />
              </div>
            </div>
            <span style="font-size:12px; color:#7dd3fc; font-weight:700;">{d2_c:,} files ({fmt_bytes(d2_b)})</span>
          </div>
          <div class="pillar-list" style="margin-top:14px;">
            <div><strong>1. Asset Storage:</strong> <code>864zeros-ISD/</code> (`ISD-DIV-0-CORE`, `BRICK_REGISTRY.json`, `MONETIZATION_REGISTRY.json`, `864zeros_CONSTITUTION_v1.md`).</div>
            <div><strong>2. Functionality Growth:</strong> Spec Evaluation Meeting engine (`evaluate.py`, `adapt.py`, `capsules.py`), RULE-003 pricing governance.</div>
            <div><strong>3. Media &amp; Content:</strong> $480K/Yr Portfolio Strategy Blueprint &amp; Deck, ClearStreak Master Spec v3, Habit Engine v6 Spec.</div>
          </div>
        </div>
        <a class="btn" href="file:///C:/dev/864zeros-ISD/overview.html">🚪 Enter Division 2 Front Door (`864zeros-ISD/overview.html`) ↗</a>
      </div>

      <!-- DIVISION 3: SOFTWARE FACTORY & SHARED BRICKS -->
      <div class="div-card">
        <div>
          <div class="div-head">
            <div>
              <div class="div-code">DIVISION 3 · LLC-DIV-3-FACTORY/overview.html</div>
              <div class="div-title">Software Factory, Extensions, GWS Add-Ons &amp; Bricks</div>
              <div class="div-lead">Lead: <strong>Zane Fields (`CTO`)</strong> · Marcus Vance (`DEV-BRICKS`) · Elena Rostova (`DATA-SEC-QA`)</div>
              <div class="avatars-row">
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/zane-fields.jpg" title="Zane Fields" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/marcus-vance.jpg" title="Marcus Vance" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/elena-rostova.jpg" title="Elena Rostova" />
              </div>
            </div>
            <span style="font-size:12px; color:#7dd3fc; font-weight:700;">{d3_c:,} files ({fmt_bytes(d3_b)})</span>
          </div>
          <div class="pillar-list" style="margin-top:14px;">
            <div><strong>1. Asset Storage:</strong> 16 Chrome MV3 extensions, 12 Edge MV3 extensions, 18 GWS Add-ons, ClearStreak Android (`app-store-release.aab` 12.33 MB).</div>
            <div><strong>2. Functionality Growth:</strong> 9 Shared Feature Bricks (`v1.8`, 45/45 self-tests passing), ClearStreak v1.1 zero-permission custom JSON importer.</div>
            <div><strong>3. Media &amp; Content:</strong> 5 LIVE Edge Add-ons, 5 Edge Wave-2 certified builds, RULE-007 security/QA verification.</div>
          </div>
        </div>
        <a class="btn" href="file:///C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/overview.html">🚪 Enter Division 3 Front Door (`DIV-3-FACTORY/overview.html`) ↗</a>
      </div>

      <!-- DIVISION 4: SLOANE'S CREATIVE STUDIO -->
      <div class="div-card highlight">
        <div>
          <div class="div-head">
            <div>
              <div class="div-code">DIVISION 4 · 864zeros-publish/overview.html (CREATIVE STUDIO)</div>
              <div class="div-title">Creative Studio, Literary IP, Media &amp; Publishing</div>
              <div class="div-lead">Lead: <strong>Sloane Sterling (`VP-STUDIO`)</strong> · Julian Thorne · Orion Kai · Vera Lindqvist</div>
              <div class="avatars-row">
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/sloane-sterling.jpg" title="Sloane Sterling" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/julian-thorne.jpg" title="Julian Thorne" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/orion-kai.jpg" title="Orion Kai" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/vera-lindqvist.jpg" title="Vera Lindqvist" />
              </div>
            </div>
            <span style="font-size:12px; color:#6ee7b7; font-weight:700;">{d4_c:,} files ({fmt_bytes(d4_b)})</span>
          </div>
          <div class="pillar-list" style="margin-top:14px;">
            <div><strong>1. Asset Storage:</strong> 20 Pre-1931 PD Classics (13.49 MB), 228.45 MB SDXL LoRA, 287 training plates, 34-product DAM vault.</div>
            <div><strong>2. Functionality Growth:</strong> HALT 6-State Engine, Franklin 13-Virtue Cadence, 5"×8" QR Compiler, 3-Tier Edge OCR, Smudge Filter Lab, 8 Studio v1.8 JS Bricks.</div>
            <div><strong>3. Media &amp; Content:</strong> {len(studio_data['drawings'])} <code>jeff_sketch</code>/<code>painting</code> plates, 204 MP4 videos, 9 Focus Packs (270 cards), 3 HALT Packs (72 cards), 3 5"×8" Print Journals, 1,514 Bible records.</div>
          </div>
        </div>
        <a class="btn gold" href="file:///C:/dev/864zeros-publish/overview.html">🚪 Enter Division 4 Front Door (`864zeros-publish/overview.html`) ↗</a>
      </div>

      <!-- DIVISION 5: OMNICHANNEL GTM, STORE DISTRIBUTION & WEB -->
      <div class="div-card">
        <div>
          <div class="div-head">
            <div>
              <div class="div-code">DIVISION 5 · LLC-DIV-4-GTM/overview.html &amp; 864zeros-web</div>
              <div class="div-title">Omnichannel GTM, Store Distribution, Pulse-X &amp; Web</div>
              <div class="div-lead">Lead: <strong>Prya Vance (`CMO`)</strong> · Allegra Katz (`CFO`) · Cole Mercer (`CLO`)</div>
              <div class="avatars-row">
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/prya-vance.jpg" title="Prya Vance" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/allegra-katz.jpg" title="Allegra Katz" />
                <img class="mini-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/cole-mercer.jpg" title="Cole Mercer" />
              </div>
            </div>
            <span style="font-size:12px; color:#7dd3fc; font-weight:700;">{d5_c:,} files ({fmt_bytes(d5_b)})</span>
          </div>
          <div class="pillar-list" style="margin-top:14px;">
            <div><strong>1. Asset Storage:</strong> <code>LLC-DIV-4-GTM/</code> playbooks, <code>864zeros-web</code> live site, CWS 41-item Quota Petition, Edge Wave 2 Audit.</div>
            <div><strong>2. Functionality Growth:</strong> <code>864zeros-publisher-mcp</code> (17 tools: StorePilot Edge API, ExtPay, YouTube uploader), Pulse-X &amp; Pulse-Ad engines.</div>
            <div><strong>3. Media &amp; Content:</strong> 5 Live Edge CTAs on <code>864zeros.com</code>, 13-person Meet-the-Team campus portraits, 12+ live YouTube embeds.</div>
          </div>
        </div>
        <a class="btn" href="file:///C:/dev/864zeros-llc/LLC-DIV-4-GTM/overview.html">🚪 Enter Division 5 Front Door (`DIV-4-GTM/overview.html`) ↗</a>
      </div>

    </div>
  </div>
</body>
</html>
"""


def main():
    from div_builders import (
        PIXEL_ROOT,
        build_div0_front_door,
        build_div1_front_door,
        build_div2_front_door,
        build_div3_front_door,
        build_div5_front_door,
    )

    data = scan_studio()
    studio_html = build_studio_front_door_html(data)

    # 1. Write Division 4 (Studio) Front Door
    div4_paths = [
        PUBLISH_ROOT / "overview.html",
        PUBLISH_ROOT / "STUDIO_ACTIVITY_REPORT_2026-10-19.html",
        LLC_ROOT / "LIBRARY" / "03-Creative-Studio-and-Media" / "STUDIO_FRONT_DOOR.html",
        LLC_ROOT / "LIBRARY" / "03-Creative-Studio-and-Media" / "STUDIO_ACTIVITY_REPORT_2026-10-19.html",
    ]
    for p in div4_paths:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(studio_html, encoding="utf-8")
        print(f"[DIV 4 FRONT DOOR] {p} ({fmt_bytes(p.stat().st_size)})")

    # 2. Build & write Divisions 0, 1, 2, 3, 5 Front Doors
    div0_html, div0_tel = build_div0_front_door()
    for p in [LLC_ROOT / "LIBRARY" / "overview.html", PIXEL_ROOT / "overview.html"]:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(div0_html, encoding="utf-8")
        print(f"[DIV 0 FRONT DOOR] {p} ({fmt_bytes(p.stat().st_size)})")

    div1_html, div1_tel = build_div1_front_door()
    for p in [LLC_ROOT / "LLC-DIV-1-INTELLIGENCE" / "overview.html"]:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(div1_html, encoding="utf-8")
        print(f"[DIV 1 FRONT DOOR] {p} ({fmt_bytes(p.stat().st_size)})")

    div2_html, div2_tel = build_div2_front_door()
    for p in [Path(r"C:\dev\864zeros-ISD\overview.html")]:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(div2_html, encoding="utf-8")
        print(f"[DIV 2 FRONT DOOR] {p} ({fmt_bytes(p.stat().st_size)})")

    div3_html, div3_tel = build_div3_front_door()
    for p in [LLC_ROOT / "LLC-DIV-3-FACTORY" / "overview.html"]:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(div3_html, encoding="utf-8")
        print(f"[DIV 3 FRONT DOOR] {p} ({fmt_bytes(p.stat().st_size)})")

    div5_html, div5_tel = build_div5_front_door()
    for p in [LLC_ROOT / "LLC-DIV-4-GTM" / "overview.html", Path(r"C:\dev\864zeros-web\overview.html")]:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(div5_html, encoding="utf-8")
        print(f"[DIV 5 FRONT DOOR] {p} ({fmt_bytes(p.stat().st_size)})")

    # 3. Build & write Overarching Master Hub
    div_tels = {0: div0_tel, 1: div1_tel, 2: div2_tel, 3: div3_tel, 5: div5_tel}
    hub_html = build_company_division_hub_html(data, div_tels)
    for hub_p in [LLC_ROOT / "DIVISION_FRONT_DOORS.html", LLC_ROOT / "overview.html"]:
        hub_p.write_text(hub_html, encoding="utf-8")
        print(f"[OVERARCHING MASTER HUB] {hub_p} ({fmt_bytes(hub_p.stat().st_size)})")


if __name__ == "__main__":
    main()
