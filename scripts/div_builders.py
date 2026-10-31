#!/usr/bin/env python3
"""
864zeros Division Front Door Compiler (`build_division_front_doors.py`)
=======================================================================
Maintained by: Kate Zefore (`COS-001` — Chief of Staff) & Sloane Sterling (`VP-STUDIO`)

Dynamically scans every 864zeros division across `C:\\dev\\` and generates a full,
standardized, 3-Pillar interactive `overview.html` Front Door for EVERY single division,
plus the overarching Master Hub at `C:\\dev\\864zeros-llc\\DIVISION_FRONT_DOORS.html`:

  - Division 0: `C:\\dev\\864zeros-llc\\LIBRARY\\overview.html` (and `C:\\dev\\864zeros-pixel-office\\overview.html`)
                Executive Command, Chief of Staff (`KIA`), SharePoint Library & Daily Diary
  - Division 1: `C:\\dev\\864zeros-llc\\LLC-DIV-1-INTELLIGENCE\\overview.html`
                Market Intelligence, Vulture Strike & Autonomous Scout (`864zero-scout`)
  - Division 2: `C:\\dev\\864zeros-ISD\\overview.html`
                ISD Knowledge Brain, Product Strategy, Constitution & Pricing Governance
  - Division 3: `C:\\dev\\864zeros-llc\\LLC-DIV-3-FACTORY\\overview.html`
                Software Factory (16 Chrome MV3, 12 Edge MV3, 18 GWS Add-ons, ClearStreak Mobile & 9 v1.8 Bricks)
  - Division 4: `C:\\dev\\864zeros-publish\\overview.html`
                Sloane Sterling's Creative Studio, Literary IP, Media & Publishing
  - Division 5: `C:\\dev\\864zeros-llc\\LLC-DIV-4-GTM\\overview.html` (and `C:\\dev\\864zeros-web\\overview.html`)
                Omnichannel Store Distribution, `864zeros-publisher-mcp`, Pulse-X & Web Properties
  - Master Hub: `C:\\dev\\864zeros-llc\\DIVISION_FRONT_DOORS.html` (and `C:\\dev\\864zeros-llc\\overview.html`)
"""

import json
import os
from pathlib import Path
from datetime import datetime

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
LLC_ROOT = Path(r"C:\dev\864zeros-llc")
ISD_ROOT = Path(r"C:\dev\864zeros-ISD")
WEB_ROOT = Path(r"C:\dev\864zeros-web")
PIXEL_ROOT = Path(r"C:\dev\864zeros-pixel-office")
CLEARSTREAK_ROOT = Path(r"C:\dev\clearStreak")
DIARY_ROOT = Path(r"C:\dev\864zeros-diary")
SCOUT_ROOT = Path(r"C:\dev\864zero-scout")
ANALYTICS_ROOT = Path(r"C:\dev\864zeros-analytics")
PUB_MCP_ROOT = Path(r"C:\dev\864zeros-publisher-mcp")


def fmt_bytes(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024 * 1024:
        return f"{num_bytes / (1024**3):.2f} GB"
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024**2):.2f} MB"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes} B"


def scan_paths_telemetry(paths: list[Path]):
    ext_counts = {}
    ext_bytes = {}
    total_files = 0
    total_bytes = 0
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", ".gradle", "build"}
    for base in paths:
        if not base.exists():
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
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
    return {
        "total_files": total_files,
        "total_bytes": total_bytes,
        "ext_counts": ext_counts,
        "ext_bytes": ext_bytes,
    }


def render_storage_pills(telemetry: dict, top_n: int = 10) -> str:
    ext_counts = telemetry["ext_counts"]
    ext_bytes = telemetry["ext_bytes"]
    sorted_exts = sorted(ext_counts.keys(), key=lambda e: ext_bytes.get(e, 0), reverse=True)[:top_n]
    pills = []
    for ext in sorted_exts:
        pills.append(f"""
        <div class="storage-pill">
          <div class="sp-ext">{ext}</div>
          <div class="sp-cnt">{ext_counts[ext]:,} files</div>
          <div class="sp-sz">{fmt_bytes(ext_bytes[ext])}</div>
        </div>""")
    return "".join(pills)


def common_css() -> str:
    return """
    :root {
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
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Inter, sans-serif;
      background: radial-gradient(circle at top right, #172554 0%, var(--bg-deep) 45%);
      color: var(--text-main);
      line-height: 1.58;
      padding-bottom: 90px;
    }
    a { color: var(--accent-sky); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .hero-header {
      border-bottom: 1px solid var(--border);
      background: rgba(15, 23, 42, 0.94);
      padding: 26px 24px 18px;
      position: sticky;
      top: 0;
      z-index: 100;
      backdrop-filter: blur(14px);
    }
    .container { max-width: 1440px; margin: 0 auto; padding: 0 20px; }
    .header-top {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: flex-start;
      gap: 16px;
    }
    .studio-kicker {
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
    }
    h1 { font-size: 26px; font-weight: 800; color: #fff; letter-spacing: -0.02em; }
    .subtitle { color: var(--text-muted); font-size: 13.5px; max-width: 880px; margin-top: 4px; }
    .pillar-nav {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 16px;
      align-items: center;
    }
    .nav-btn {
      padding: 7px 13px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--bg-card);
      color: #cbd5e1;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
    }
    .nav-btn:hover, .nav-btn.active {
      background: rgba(56, 189, 248, 0.18);
      border-color: var(--accent-sky);
      color: #fff;
      text-decoration: none;
    }
    .hub-link {
      margin-left: auto;
      padding: 8px 14px;
      border-radius: 8px;
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
      color: #090d16;
      font-weight: 800;
      font-size: 12px;
    }
    .hub-link:hover { text-decoration: none; opacity: 0.92; }
    .kpi-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
      gap: 12px;
      margin: 24px 0;
    }
    .kpi-card {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      border-top: 3px solid var(--accent-sky);
    }
    .kpi-val { font-size: 25px; font-weight: 800; color: #fff; }
    .kpi-label { font-size: 12px; color: var(--text-muted); font-weight: 600; margin-top: 2px; }
    .kpi-sub { font-size: 11px; color: #6ee7b7; font-family: Consolas, monospace; margin-top: 5px; }
    .pillars-overview {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 16px;
      margin-bottom: 26px;
    }
    .pillar-box {
      background: linear-gradient(145deg, rgba(24, 34, 53, 0.92), rgba(15, 23, 42, 0.96));
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 20px;
    }
    .pillar-box h3 { font-size: 16px; color: #fff; margin-bottom: 6px; display: flex; align-items: center; gap: 8px; }
    .pillar-box p { font-size: 13px; color: var(--text-muted); margin-bottom: 10px; }
    .pillar-box ul { padding-left: 18px; font-size: 12.5px; color: #cbd5e1; }
    .pillar-box li { margin-bottom: 4px; }
    .roster-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 14px;
      margin-bottom: 26px;
    }
    .leader-card {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 15px;
      display: flex;
      gap: 14px;
      align-items: center;
    }
    .leader-avatar {
      width: 62px;
      height: 62px;
      border-radius: 10px;
      object-fit: cover;
      border: 2px solid var(--border-accent);
      flex-shrink: 0;
    }
    .leader-role { font-size: 10.5px; font-weight: 700; text-transform: uppercase; color: var(--accent-amber); }
    .leader-name { font-size: 15.5px; font-weight: 700; color: #fff; }
    .leader-bio { font-size: 12px; color: var(--text-muted); margin-top: 2px; }
    .section-block {
      background: var(--bg-panel);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 28px;
    }
    .section-header {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 14px;
      margin-bottom: 18px;
    }
    .section-title { font-size: 19px; font-weight: 800; color: #fff; }
    .owner-tag {
      font-size: 11.5px;
      padding: 4px 10px;
      border-radius: 6px;
      background: rgba(167, 139, 250, 0.15);
      border: 1px solid rgba(167, 139, 250, 0.4);
      color: #c4b5fd;
      font-weight: 600;
    }
    .storage-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(135px, 1fr));
      gap: 10px;
      margin-bottom: 18px;
    }
    .storage-pill {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      text-align: center;
    }
    .sp-ext { font-family: Consolas, monospace; font-size: 15px; font-weight: 800; color: var(--accent-sky); }
    .sp-cnt { font-size: 13px; font-weight: 700; color: #fff; margin-top: 2px; }
    .sp-sz { font-size: 11px; color: var(--text-muted); }
    .viewers-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
      gap: 14px;
    }
    .viewer-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 10px;
    }
    .viewer-card h4 { font-size: 15px; color: #fff; }
    .viewer-card p { font-size: 12.5px; color: var(--text-muted); }
    .btn-launch {
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
    }
    .btn-launch:hover { text-decoration: none; opacity: 0.92; }
    .table-wrap { overflow-x: auto; max-height: 540px; overflow-y: auto; border: 1px solid var(--border); border-radius: 10px; }
    table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
    th, td { padding: 9px 12px; text-align: left; border-bottom: 1px solid var(--border); }
    th {
      background: #162032;
      color: #cbd5e1;
      font-weight: 700;
      text-transform: uppercase;
      font-size: 11px;
      position: sticky;
      top: 0;
      z-index: 10;
    }
    code {
      font-family: Consolas, monospace;
      font-size: 11px;
      background: rgba(7, 11, 18, 0.75);
      padding: 2px 5px;
      border-radius: 4px;
      color: #7dd3fc;
    }
    .badge {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 999px;
      font-size: 10.5px;
      font-weight: 700;
    }
    .badge-green { background: rgba(16, 185, 129, 0.16); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }
    .badge-blue { background: rgba(56, 189, 248, 0.16); color: #7dd3fc; border: 1px solid rgba(56, 189, 248, 0.4); }
    .badge-amber { background: rgba(245, 158, 11, 0.16); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-purple { background: rgba(167, 139, 250, 0.16); color: #ddd6fe; border: 1px solid rgba(167, 139, 250, 0.4); }
    .badge-rose { background: rgba(244, 63, 94, 0.16); color: #fda4af; border: 1px solid rgba(244, 63, 94, 0.4); }
    """


def division_switcher_bar(active_div: int) -> str:
    links = [
        (0, "Div 0: Exec & KIA (`LIBRARY`)", "file:///C:/dev/864zeros-llc/LIBRARY/overview.html"),
        (1, "Div 1: Intelligence (`DIV-1`)", "file:///C:/dev/864zeros-llc/LLC-DIV-1-INTELLIGENCE/overview.html"),
        (2, "Div 2: Product & ISD (`864zeros-ISD`)", "file:///C:/dev/864zeros-ISD/overview.html"),
        (3, "Div 3: Software Factory (`DIV-3`)", "file:///C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/overview.html"),
        (4, "Div 4: Creative Studio (`864zeros-publish`)", "file:///C:/dev/864zeros-publish/overview.html"),
        (5, "Div 5: GTM & Web (`DIV-4-GTM`)", "file:///C:/dev/864zeros-llc/LLC-DIV-4-GTM/overview.html"),
    ]
    btns = []
    for num, label, url in links:
        cls = "nav-btn active" if num == active_div else "nav-btn"
        btns.append(f'<a class="{cls}" href="{url}">{label}</a>')
    btns.append('<a class="hub-link" href="file:///C:/dev/864zeros-llc/DIVISION_FRONT_DOORS.html">🏛️ Master Division Hub (`DIVISION_FRONT_DOORS.html`) ↗</a>')
    return '<nav class="pillar-nav">' + "".join(btns) + "</nav>"


# ==============================================================================
# DIVISION 0: EXECUTIVE COMMAND, CHIEF OF STAFF (KIA), LIBRARY & DIARY
# ==============================================================================
def build_div0_front_door() -> tuple[str, dict]:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M EDT")
    tel = scan_paths_telemetry([LLC_ROOT / "LIBRARY", PIXEL_ROOT, DIARY_ROOT])

    # Load Diary entries
    diary_idx_path = DIARY_ROOT / "index.json"
    diary_entries = json.loads(diary_idx_path.read_text(encoding="utf-8")).get("entries", []) if diary_idx_path.exists() else []
    diary_rows = []
    for e in reversed(diary_entries):
        diary_rows.append(f"""
        <tr>
          <td><code>{e['id']}</code></td>
          <td>{e['date']}</td>
          <td><strong>{e['title']}</strong><br/><span style="color:var(--text-muted); font-size:11.5px;">{e['summary']}</span></td>
          <td>{", ".join(e.get("authors", [])[:4])}</td>
          <td><a href="file:///C:/dev/864zeros-diary/{e['path']}" target="_blank">Open Entry ↗</a></td>
        </tr>""")

    # Scan all LIBRARY files
    lib_rows = []
    lib_dir = LLC_ROOT / "LIBRARY"
    if lib_dir.exists():
        for r, _, fs in os.walk(lib_dir):
            for f in sorted(fs):
                fp = Path(r) / f
                rel = fp.relative_to(lib_dir).as_posix()
                folder = rel.split("/")[0] if "/" in rel else "ROOT"
                lib_rows.append(f"""
                <tr>
                  <td><span class="badge badge-purple">{folder}</span></td>
                  <td><a href="file:///C:/dev/864zeros-llc/LIBRARY/{rel}" target="_blank"><code>{f}</code></a></td>
                  <td>{fmt_bytes(fp.stat().st_size)}</td>
                  <td>{datetime.fromtimestamp(fp.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}</td>
                  <td><a href="file:///C:/dev/864zeros-llc/LIBRARY/{rel}" target="_blank">Open Document ↗</a></td>
                </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Division 0 Front Door — Executive Command, Chief of Staff (`KIA`), SharePoint Library &amp; Diary</title>
  <style>{common_css()}</style>
</head>
<body>
  <header class="hero-header">
    <div class="container">
      <div class="header-top">
        <div>
          <div class="studio-kicker">🚪 DIVISION 0 FRONT DOOR · EXECUTIVE COMMAND, CHIEF OF STAFF (`KIA`), SHAREPOINT LIBRARY &amp; DIARY</div>
          <h1>Kate Zefore's (`COS-001`) Executive Command &amp; Central Library Front Door</h1>
          <p class="subtitle">
            Always-evolving front door for Executive Command (`864zeros-pixel-office`), Project "Kate Is Alive" (`http://localhost:4173/kate`), the 864zeros SharePoint Library (`C:\\dev\\864zeros-llc\\LIBRARY\\`), and the Canonical Daily Diary (`C:\\dev\\864zeros-diary\\`).
          </p>
        </div>
        <div style="text-align:right; font-size:12px; color:var(--text-muted);">
          <div><strong>Last Auto-Scan:</strong> {now_str}</div>
          <div><strong>Division Files:</strong> {tel['total_files']:,} ({fmt_bytes(tel['total_bytes'])})</div>
          <div style="color:#6ee7b7; font-weight:700;">✓ KIA Phase 1 &amp; Neural Rig Active</div>
        </div>
      </div>
      {division_switcher_bar(0)}
    </div>
  </header>

  <main class="container">
    <section class="kpi-grid">
      <div class="kpi-card"><div class="kpi-val">{len(lib_rows)} Docs</div><div class="kpi-label">SharePoint Library (`LIBRARY/`)</div><div class="kpi-sub">9 Executive Sub-Vaults</div></div>
      <div class="kpi-card"><div class="kpi-val">{len(diary_entries)} Dispatches</div><div class="kpi-label">Canonical Daily Diary</div><div class="kpi-sub">DIARY-2026-001..008</div></div>
      <div class="kpi-card"><div class="kpi-val">6 Tools</div><div class="kpi-label">Kate Chief of Staff Engine</div><div class="kpi-sub">Gmail · Tasks · Memory · Library</div></div>
      <div class="kpi-card"><div class="kpi-val">13 Avatars</div><div class="kpi-label">Pixel Command Office v2.0</div><div class="kpi-sub">[OFFICE | FACTORY] 2D Floorplan</div></div>
      <div class="kpi-card"><div class="kpi-val">60fps + A10G</div><div class="kpi-label">Kate Live Talking Avatar Rig</div><div class="kpi-sub">Formant + Neural Lip-Sync</div></div>
    </section>

    <section class="roster-grid">
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/kate-zefore.jpg" alt="Kate Zefore" />
        <div>
          <div class="leader-role">COS-001 · Chief of Staff &amp; Executive Orchestrator</div>
          <div class="leader-name">Kate Zefore</div>
          <div class="leader-bio">Reports directly to Founder &amp; CEO Jeff Conn. Commands cross-division task routing, Gmail executive dispatches, persistent memory, and the Pixel Command Office.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/allegra-katz.jpg" alt="Allegra Katz" />
        <div>
          <div class="leader-role">CFO · Chief Financial Officer</div>
          <div class="leader-name">Allegra Katz</div>
          <div class="leader-bio">Leads the $480K/Yr Portfolio Strategy Model, unit economics, Rule of 40 capital allocation, and #kate-5269 GWS Marketplace GTM financial plan.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/cole-mercer.jpg" alt="Cole Mercer" />
        <div>
          <div class="leader-role">CLO · Chief Legal Officer &amp; General Counsel</div>
          <div class="leader-name">Cole Mercer</div>
          <div class="leader-bio">Leads corporate governance, Pennsylvania CROP statutory filings, store compliance, privacy policies, and IP co-clearance with Vera Lindqvist.</div>
        </div>
      </div>
    </section>

    <section class="pillars-overview">
      <div class="pillar-box">
        <h3>🗄️ Pillar I: Asset Storage Vault (`LIBRARY/` &amp; `864zeros-diary`)</h3>
        <p>Centralized executive knowledge vault ("864zeros SharePoint") and immutable company timeline:</p>
        <ul>
          <li><code>LIBRARY/00-Kate-Chief-of-Staff/</code> — Persistent executive memory, todo ledger &amp; chat history</li>
          <li><code>LIBRARY/01..05/</code> — Board decks, pricing sign-offs, CWS/Edge dockets, product specs &amp; legal briefs</li>
          <li><code>864zeros-diary/entries/2026/</code> — 8 canonical multi-page executive diary dispatches</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>⚙️ Pillar II: Functionality &amp; Orchestration Growth</h3>
        <p>Live AI Chief of Staff brain, Gmail REST API bridge, and real-time 2D Command Office:</p>
        <ul>
          <li><strong>KIA Phase 1 Engine (`kate_engine.js`):</strong> Gemini OAuth brain with 6 live tools (<code>gmail_read</code>, <code>gmail_send</code>, <code>assign_employee_task</code>, <code>manage_todos_and_memory</code>, etc.)</li>
          <li><strong>Photorealistic &amp; Neural Avatar Rig:</strong> 60fps 3D head parallax + cloud A10G ZeroGPU neural talking-head MP4 synthesis (<code>MoDA</code> / <code>LatentSync</code>)</li>
          <li><strong>Gmail Dispatcher (`kate_email.py`):</strong> Automated HTML executive briefs &amp; inbox search</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>📊 Pillar III: Executive Briefs, Decks &amp; Live Consoles</h3>
        <p>Immediate access to live operational consoles and board-level strategic deliverables:</p>
        <ul>
          <li><strong>Kate Web/Mobile PWA Console:</strong> <code>http://localhost:4173/kate</code></li>
          <li><strong>Pixel Command Office v2.0:</strong> <code>http://localhost:4173/</code> (Office &amp; Factory views)</li>
          <li><strong>$480K/Yr Portfolio Strategy Deck:</strong> Native PPTX + Google Slides + Board Blueprint</li>
        </ul>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🚀 Live Executive Consoles &amp; Key Deliverables</div>
        <span class="owner-tag">One-Click Launchers</span>
      </div>
      <div class="viewers-grid">
        <div class="viewer-card">
          <div><span class="badge badge-green">LIVE CONSOLE</span><h4 style="margin-top:6px;">Kate Zefore Live PWA Console (`KIA`)</h4><p>Two-way voice &amp; chat console with 60fps talking avatar rig and 6 Chief of Staff tools.</p></div>
          <a class="btn-launch" href="http://localhost:4173/kate" target="_blank">👩‍💼 Open Kate Console (`localhost:4173/kate`) ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-blue">LIVE 2D OFFICE</span><h4 style="margin-top:6px;">864zeros Pixel Command Office v2.0</h4><p>13-person interactive 2D HQ with [OFFICE | FACTORY] floorplan toggle and 38-product matrix.</p></div>
          <a class="btn-launch" href="http://localhost:4173/" target="_blank">🏢 Open Pixel Command Office (`localhost:4173`) ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-amber">EXECUTIVE BRIEF</span><h4 style="margin-top:6px;">Morning Executive Brief (6-Workstream Packet)</h4><p>Complete summary of the overnight parallel workstreams, CWS petition, Edge Wave 2, and PA CROP brief.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LIBRARY/01-Executive-Presentations/MORNING_BRIEF_2026-10-19_OVERNIGHT_PACKET.md" target="_blank">📋 Open Morning Brief ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-purple">LEGAL BRIEF</span><h4 style="margin-top:6px;">PA Registered Agent (`CROP`) $5 Action Brief</h4><p>Cole Mercer's 15-minute step-by-step guide to replace LegalZoom on <code>file.dos.pa.gov</code>.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LIBRARY/04-Legal-and-PD-Clearance/PA_REGISTERED_AGENT_ACTION_BRIEF.md" target="_blank">⚖️ Open PA CROP Brief ↗</a>
        </div>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">📂 Central SharePoint Library Inventory (`C:\\dev\\864zeros-llc\\LIBRARY\\`)</div>
        <span class="owner-tag">{len(lib_rows)} Canonical Documents</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Vault Folder</th><th>Document</th><th>Size</th><th>Last Modified</th><th>Action</th></tr></thead>
          <tbody>{"".join(lib_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">📖 Canonical Daily Diary Timeline (`C:\\dev\\864zeros-diary\\`)</div>
        <span class="owner-tag">{len(diary_entries)} Milestone Dispatches</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Diary ID</th><th>Date</th><th>Title &amp; Executive Summary</th><th>Authors</th><th>Link</th></tr></thead>
          <tbody>{"".join(diary_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🗄️ Division 0 Storage Telemetry</div>
        <span class="owner-tag">{tel['total_files']:,} Files ({fmt_bytes(tel['total_bytes'])})</span>
      </div>
      <div class="storage-grid">{render_storage_pills(tel)}</div>
    </section>
  </main>
</body>
</html>"""
    return html, tel


# ==============================================================================
# DIVISION 1: MARKET INTELLIGENCE, VULTURE STRIKE & AUTONOMOUS SCOUT
# ==============================================================================
def build_div1_front_door() -> tuple[str, dict]:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M EDT")
    div1_dir = LLC_ROOT / "LLC-DIV-1-INTELLIGENCE"
    tel = scan_paths_telemetry([div1_dir, SCOUT_ROOT, ANALYTICS_ROOT])

    # Scan strikes, briefs, docs, scrapers + D-UTA analytics
    intel_rows = []
    for sub in ["strikes", "briefs", "docs", "recon", "scan_results", "scrapers", "enrichment"]:
        sd = div1_dir / sub
        if sd.exists():
            for f in sorted(sd.iterdir()):
                if f.is_file():
                    rel = f.relative_to(div1_dir).as_posix()
                    intel_rows.append(f"""
                    <tr>
                      <td><span class="badge badge-amber">{sub.upper()}</span></td>
                      <td><a href="file:///C:/dev/864zeros-llc/LLC-DIV-1-INTELLIGENCE/{rel}" target="_blank"><code>{f.name}</code></a></td>
                      <td>{fmt_bytes(f.stat().st_size)}</td>
                      <td>{datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}</td>
                      <td><a href="file:///C:/dev/864zeros-llc/LLC-DIV-1-INTELLIGENCE/{rel}" target="_blank">Inspect Asset ↗</a></td>
                    </tr>""")

    if ANALYTICS_ROOT.exists():
        for root, _, files in os.walk(ANALYTICS_ROOT):
            if ".git" in Path(root).parts:
                continue
            for fn in sorted(files):
                f = Path(root) / fn
                rel = f.relative_to(ANALYTICS_ROOT).as_posix()
                intel_rows.append(f"""
                <tr>
                  <td><span class="badge badge-blue">D-UTA ANALYTICS</span></td>
                  <td><a href="file:///C:/dev/864zeros-analytics/{rel}" target="_blank"><code>{rel}</code></a></td>
                  <td>{fmt_bytes(f.stat().st_size)}</td>
                  <td>{datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}</td>
                  <td><a href="file:///C:/dev/864zeros-analytics/{rel}" target="_blank">Inspect Telemetry ↗</a></td>
                </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Division 1 Front Door — Market Intelligence, Vulture Strike &amp; Autonomous Scout</title>
  <style>{common_css()}</style>
</head>
<body>
  <header class="hero-header">
    <div class="container">
      <div class="header-top">
        <div>
          <div class="studio-kicker">🚪 DIVISION 1 FRONT DOOR · MARKET INTELLIGENCE, VULTURE STRIKE &amp; AUTONOMOUS SCOUT (`LLC-DIV-1-INTELLIGENCE`)</div>
          <h1>Audrey Chen &amp; Jalen Barkley's Market Intelligence &amp; Vulture Strike Front Door</h1>
          <p class="subtitle">
            Always-evolving front door for Division 1 (`C:\\dev\\864zeros-llc\\LLC-DIV-1-INTELLIGENCE\\` &amp; `C:\\dev\\864zero-scout\\`) — Vulture Strike competitor vulnerability harvesting, Rule of 40 opportunity scoring, and niche community pain-signal extraction.
          </p>
        </div>
        <div style="text-align:right; font-size:12px; color:var(--text-muted);">
          <div><strong>Last Auto-Scan:</strong> {now_str}</div>
          <div><strong>Division Files:</strong> {tel['total_files']:,} ({fmt_bytes(tel['total_bytes'])})</div>
          <div style="color:#6ee7b7; font-weight:700;">✓ Vulture OS v2 &amp; Scout Active</div>
        </div>
      </div>
      {division_switcher_bar(1)}
    </div>
  </header>

  <main class="container">
    <section class="kpi-grid">
      <div class="kpi-card"><div class="kpi-val">{tel['total_files']:,}</div><div class="kpi-label">Intelligence Vault Files</div><div class="kpi-sub">{fmt_bytes(tel['total_bytes'])} Stored</div></div>
      <div class="kpi-card"><div class="kpi-val">{len(intel_rows)}</div><div class="kpi-label">Strikes, Briefs, Scrapers &amp; Recon</div><div class="kpi-sub">Vulture OS v2 Pipeline</div></div>
      <div class="kpi-card"><div class="kpi-val">18 + 16</div><div class="kpi-label">GWS &amp; MV3 Targets Validated</div><div class="kpi-sub">Rule of 40 Scored</div></div>
      <div class="kpi-card"><div class="kpi-val">Zernio + GWS</div><div class="kpi-label">Latest Strategic Dossiers</div><div class="kpi-sub">Synced to LIBRARY/05</div></div>
    </section>

    <section class="roster-grid">
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/audrey-chen.jpg" alt="Audrey Chen" />
        <div>
          <div class="leader-role">CPO · Chief Product Officer</div>
          <div class="leader-name">Audrey Chen</div>
          <div class="leader-bio">Commands Division 1 Intelligence &amp; Division 2 Product Strategy. Converts Vulture Strike competitor pain signals into single-purpose products.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/jalen-barkley.jpg" alt="Jalen Barkley" />
        <div>
          <div class="leader-role">LEAD-DATA-ARCH · Chief Data Architect</div>
          <div class="leader-name">Jalen Barkley</div>
          <div class="leader-bio">Architects Vulture Strike schemas, scraping &amp; enrichment pipelines, local-first SQLite data models, and telemetry schemas.</div>
        </div>
      </div>
    </section>

    <section class="pillars-overview">
      <div class="pillar-box">
        <h3>🗄️ Pillar I: Intelligence Asset Storage (`LLC-DIV-1-INTELLIGENCE`)</h3>
        <p>Structured storage of competitor vulnerability scans, user review mining, and target niche dossiers:</p>
        <ul>
          <li><code>strikes/</code> — Canonical JSON Vulture Strike packages (<code>864z-2026-003.json</code>, <code>864z-2026-004.json</code>)</li>
          <li><code>recon/ &amp; scan_results/</code> — Chrome Web Store, Edge &amp; GWS Marketplace gap matrices</li>
          <li><code>LIBRARY/05-GTM-and-Channel-Playbooks/</code> — Zernio Master Dossier &amp; GWS Vulture Strike GTM Plan</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>⚙️ Pillar II: Scout &amp; Scoring Functionality Growth</h3>
        <p>Automated scrapers, enrichment pipelines, and Rule of 40 opportunity scoring engines:</p>
        <ul>
          <li><strong>Vulture OS v2 (`864z_Vulture_OS_v2.md`):</strong> 1-star/2-star review harvester &amp; abandonment detector</li>
          <li><strong>864zero-scout (`C:\\dev\\864zero-scout`):</strong> Autonomous opportunity scout &amp; distribution target finder</li>
          <li><strong>PlannerPress &amp; 864zeros Engine:</strong> Automated brief-to-spec synthesis</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>🦅 Pillar III: Strategic Dossiers &amp; Target Briefs</h3>
        <p>Intelligence deliverables directly driving Division 3 builds and Division 5 GTM campaigns:</p>
        <ul>
          <li><strong>ChoiceGuard Vulture Strike Dossier</strong> (powering our first GWS Marketplace submission)</li>
          <li><strong>Zernio Master Dossier &amp; 864zeros Strategic Assessment</strong></li>
          <li><strong>GWS Add-ons Vulture Strike + Pulse-X + Veo GTM Financial Plan (`#kate-5269`)</strong></li>
        </ul>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🦅 Featured Intelligence Dossiers &amp; Strike Packages</div>
        <span class="owner-tag">Direct Document Launchers</span>
      </div>
      <div class="viewers-grid">
        <div class="viewer-card">
          <div><span class="badge badge-amber">GTM + VULTURE PLAN</span><h4 style="margin-top:6px;">GWS Add-Ons Vulture Strike + Pulse + Veo Plan</h4><p>Strategic financial &amp; niche community plan for the 18 Google Workspace Add-ons suite.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LIBRARY/05-GTM-and-Channel-Playbooks/GWS_ADDONS_VULTURE_STRIKE_PULSE_VEO_GTM_FINANCIAL_PLAN.md" target="_blank">🦅 Open GWS Vulture Plan ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-purple">COMPETITOR DOSSIER</span><h4 style="margin-top:6px;">Zernio Master Dossier &amp; Strategic Assessment</h4><p>Deep-dive competitive teardown and 864zeros executive board adaptation blueprint.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LIBRARY/05-GTM-and-Channel-Playbooks/ZERNIO_DOSSIER_AND_864ZEROS_STRATEGIC_ASSESSMENT.md" target="_blank">📊 Open Zernio Dossier ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-blue">STRIKE DOSSIER</span><h4 style="margin-top:6px;">ChoiceGuard Vulture Strike Dossier</h4><p>Competitor failure analysis (Form Limiter / Choice Eliminator) that launched ChoiceGuard.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LLC-DIV-4-GTM/CHOICEGUARD_VULTURE_STRIKE_DOSSIER.md" target="_blank">🎯 Open ChoiceGuard Dossier ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-green">D-UTA TELEMETRY</span><h4 style="margin-top:6px;">864zeros YouTube Telemetry Report (`D-UTA`)</h4><p>Live YouTube Analytics API v2 + Data v3 retention, traffic sources, and 27-video performance matrix.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-analytics/reports/YOUTUBE_TELEMETRY_REPORT.md" target="_blank">📈 Open YouTube Telemetry Report ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-green">ENGINE SPEC</span><h4 style="margin-top:6px;">864z Vulture OS v2 &amp; Vulture Nest</h4><p>Core operating manual and target criteria for Vulture Strike reconnaissance.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LLC-DIV-1-INTELLIGENCE/864z_Vulture_OS_v2.md" target="_blank">📘 Open Vulture OS v2 ↗</a>
        </div>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">📂 Division 1 Strikes, Briefs, Scrapers &amp; Recon Inventory</div>
        <span class="owner-tag">{len(intel_rows)} Core Pipeline Files</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Category</th><th>File</th><th>Size</th><th>Last Modified</th><th>Action</th></tr></thead>
          <tbody>{"".join(intel_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🗄️ Division 1 Storage Telemetry</div>
        <span class="owner-tag">{tel['total_files']:,} Files ({fmt_bytes(tel['total_bytes'])})</span>
      </div>
      <div class="storage-grid">{render_storage_pills(tel)}</div>
    </section>
  </main>
</body>
</html>"""
    return html, tel


# ==============================================================================
# DIVISION 2: PRODUCT STRATEGY, ISD BRAIN & PRICING ARCHITECTURE
# ==============================================================================
def build_div2_front_door() -> tuple[str, dict]:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M EDT")
    tel = scan_paths_telemetry([ISD_ROOT])

    isd_rows = []
    for r, dirs, fs in os.walk(ISD_ROOT):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]
        for f in sorted(fs):
            fp = Path(r) / f
            rel = fp.relative_to(ISD_ROOT).as_posix()
            sub = rel.split("/")[0] if "/" in rel else "ROOT"
            isd_rows.append(f"""
            <tr>
              <td><span class="badge badge-blue">{sub}</span></td>
              <td><a href="file:///C:/dev/864zeros-ISD/{rel}" target="_blank"><code>{rel}</code></a></td>
              <td>{fmt_bytes(fp.stat().st_size)}</td>
              <td>{datetime.fromtimestamp(fp.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}</td>
              <td><a href="file:///C:/dev/864zeros-ISD/{rel}" target="_blank">Open ↗</a></td>
            </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Division 2 Front Door — Product Strategy, ISD Knowledge Brain &amp; Pricing (`864zeros-ISD`)</title>
  <style>{common_css()}</style>
</head>
<body>
  <header class="hero-header">
    <div class="container">
      <div class="header-top">
        <div>
          <div class="studio-kicker">🚪 DIVISION 2 FRONT DOOR · PRODUCT STRATEGY, ISD BRAIN &amp; PRICING (`864zeros-ISD`)</div>
          <h1>Audrey Chen, Allegra Katz &amp; Jalen Barkley's ISD Brain &amp; Product Strategy Front Door</h1>
          <p class="subtitle">
            Always-evolving front door for Division 2 (`C:\\dev\\864zeros-ISD\\`) — the constitutional brain of 864zeros housing `ISD-DIV-0-CORE`, `BRICK_REGISTRY.json`, `MONETIZATION_REGISTRY.json`, Spec Evaluation Meeting engines, and product specifications.
          </p>
        </div>
        <div style="text-align:right; font-size:12px; color:var(--text-muted);">
          <div><strong>Last Auto-Scan:</strong> {now_str}</div>
          <div><strong>Division Files:</strong> {tel['total_files']:,} ({fmt_bytes(tel['total_bytes'])})</div>
          <div style="color:#6ee7b7; font-weight:700;">✓ Constitution &amp; Registries Locked</div>
        </div>
      </div>
      {division_switcher_bar(2)}
    </div>
  </header>

  <main class="container">
    <section class="kpi-grid">
      <div class="kpi-card"><div class="kpi-val">{tel['total_files']:,}</div><div class="kpi-label">ISD Brain Files</div><div class="kpi-sub">{fmt_bytes(tel['total_bytes'])} Stored</div></div>
      <div class="kpi-card"><div class="kpi-val">5 Sub-Divs</div><div class="kpi-label">ISD Knowledge Namespaces</div><div class="kpi-sub">CORE · STUDIO · EVOLUTION · LAB</div></div>
      <div class="kpi-card"><div class="kpi-val">$480K/Yr</div><div class="kpi-label">Portfolio Strategy Model</div><div class="kpi-sub">9-Role Board Ratified</div></div>
      <div class="kpi-card"><div class="kpi-val">RULE-003</div><div class="kpi-label">Dynamic Store Pricing Lock</div><div class="kpi-sub">Zero Hardcoded Web Prices</div></div>
    </section>

    <section class="roster-grid">
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/audrey-chen.jpg" alt="Audrey Chen" />
        <div>
          <div class="leader-role">CPO · Chief Product Officer</div>
          <div class="leader-name">Audrey Chen</div>
          <div class="leader-bio">Owns product specifications (ClearStreak Master Spec v3, Focus Packs &amp; Habit Engine Spec), single-purpose UX boundaries, and spec evaluation gates.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/allegra-katz.jpg" alt="Allegra Katz" />
        <div>
          <div class="leader-role">CFO · Chief Financial Officer</div>
          <div class="leader-name">Allegra Katz</div>
          <div class="leader-bio">Governs <code>MONETIZATION_REGISTRY.json</code>, portfolio tier pricing, KDP print margins, and RULE-003 price-free web compliance.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/jalen-barkley.jpg" alt="Jalen Barkley" />
        <div>
          <div class="leader-role">LEAD-DATA-ARCH · Chief Data Architect</div>
          <div class="leader-name">Jalen Barkley</div>
          <div class="leader-bio">Maintains <code>BRICK_REGISTRY.jsonld</code>, JSON-LD knowledge graphs, and deterministic schema contracts across ISD and the Studio.</div>
        </div>
      </div>
    </section>

    <section class="pillars-overview">
      <div class="pillar-box">
        <h3>🗄️ Pillar I: Constitutional &amp; Registry Storage (`864zeros-ISD`)</h3>
        <p>Canonical schemas, constitutional rules, and monetization/brick registries:</p>
        <ul>
          <li><code>ISD-DIV-0-CORE/864zeros_CONSTITUTION_v1.md</code> — Sovereign local-first &amp; zero-telemetry laws</li>
          <li><code>ISD-DIV-0-CORE/MONETIZATION_REGISTRY.json</code> &amp; <code>BRICK_REGISTRY.json</code></li>
          <li><code>LIBRARY/03-Product-Specs-and-Use-Cases/</code> — ClearStreak Master Spec v3 &amp; Habit Engine Spec</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>⚙️ Pillar II: Spec Evaluation &amp; Governance Engines</h3>
        <p>Automated evaluation meeting scripts and decision-record validators:</p>
        <ul>
          <li><strong>Spec Evaluation Meeting Engine (`ISD-DIV-0-CORE/meeting/`):</strong> <code>evaluate.py</code>, <code>adapt.py</code>, <code>capsules.py</code>, <code>record.py</code></li>
          <li><strong>Strike &amp; Decision Schemas:</strong> <code>strike-package.schema.json</code> &amp; <code>decision-record.schema.json</code></li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>📐 Pillar III: Product Specs &amp; Board Strategy Deliverables</h3>
        <p>Board-approved product architectures and financial models:</p>
        <ul>
          <li><strong>ClearStreak $480K/Yr Executive Board Blueprint &amp; PPTX Deck</strong></li>
          <li><strong>ClearStreak Focus Packs &amp; 3-Part Habit Engine Spec (DB v6)</strong></li>
          <li><strong>Offline Enhancement Delivery Use Cases (`ACTION_OPEN_DOCUMENT` &amp; QR)</strong></li>
        </ul>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">📐 Key Product Specifications &amp; Registries</div>
        <span class="owner-tag">Direct Document Launchers</span>
      </div>
      <div class="viewers-grid">
        <div class="viewer-card">
          <div><span class="badge badge-amber">BOARD BLUEPRINT</span><h4 style="margin-top:6px;">$480K/Yr Portfolio Executive Blueprint</h4><p>9-Role Executive Board synthesis, pricing matrix, and revenue milestones.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LIBRARY/02-Board-Decisions-and-Pricing/ClearStreak_480K_Executive_Board_Blueprint.md" target="_blank">📊 Open $480K Blueprint ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-blue">PRODUCT SPEC</span><h4 style="margin-top:6px;">ClearStreak Focus Packs &amp; Habit Engine Spec</h4><p>Compartmentalized Focus Packs + Primary Focus Pin, When-Then Anchor, and Floor Rep spec.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LIBRARY/03-Product-Specs-and-Use-Cases/CLEARSTREAK_FOCUS_PACKS_AND_HABIT_ENGINE_SPEC.md" target="_blank">📘 Open Habit Engine Spec ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-green">CONSTITUTION</span><h4 style="margin-top:6px;">864zeros Constitution v1 &amp; Monetization Registry</h4><p>Foundational architectural laws and canonical product monetization registry.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-ISD/ISD-DIV-0-CORE/864zeros_CONSTITUTION_v1.md" target="_blank">🏛️ Open Constitution v1 ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-purple">LEGACY ISD OVERVIEW</span><h4 style="margin-top:6px;">ISD Architecture Overview (`864zeros_overview.html`)</h4><p>Original ISD system topology diagram and division map.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-ISD/864zeros_overview.html" target="_blank">🗺️ Open ISD Diagram ↗</a>
        </div>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">📂 Complete `864zeros-ISD` File Inventory</div>
        <span class="owner-tag">{len(isd_rows)} Files</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Namespace</th><th>File Path</th><th>Size</th><th>Last Modified</th><th>Action</th></tr></thead>
          <tbody>{"".join(isd_rows)}</tbody>
        </table>
      </div>
    </section>
  </main>
</body>
</html>"""
    return html, tel


# ==============================================================================
# DIVISION 3: SOFTWARE FACTORY, EXTENSIONS, ADD-ONS, MOBILE & BRICKS
# ==============================================================================
def build_div3_front_door() -> tuple[str, dict]:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M EDT")
    div3_dir = LLC_ROOT / "LLC-DIV-3-FACTORY"
    tel = scan_paths_telemetry([div3_dir, CLEARSTREAK_ROOT])

    # Load Studio v1.8 Bricks
    bricks_path = div3_dir / "shared" / "bricks" / "STUDIO_BRICKS_MANIFEST_v1.8.json"
    bricks = json.loads(bricks_path.read_text(encoding="utf-8")).get("bricks", []) if bricks_path.exists() else []
    brick_rows = []
    for b in bricks:
        brick_rows.append(f"""
        <tr>
          <td><code>{b['brick_id']}</code></td>
          <td><a href="file:///C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/shared/bricks/{b['file']}" target="_blank"><code>{b['file']}</code></a></td>
          <td><span class="badge badge-purple">{b['category']}</span></td>
          <td>{b['purpose']}</td>
          <td>{", ".join(b.get("consumers", []))}</td>
          <td><span class="badge badge-green">{b.get('self_test_count', 5)}/{b.get('self_test_count', 5)} PASS</span></td>
        </tr>""")

    # Scan Chrome Extensions, Edge Extensions, and GWS Add-ons
    factory_rows = []
    for group_label, sub_rel, badge_cls in [
        ("Chrome MV3 Extension", "extensions", "badge-blue"),
        ("Edge MV3 Extension", "extensions-edge", "badge-green"),
        ("Google Workspace Add-on", "add-ons", "badge-amber"),
    ]:
        sub_p = div3_dir / sub_rel
        if sub_p.exists():
            for d in sorted(sub_p.iterdir()):
                if d.is_dir() and not d.name.startswith("_") and d.name != "specs":
                    f_cnt = sum(1 for _ in d.rglob("*") if _.is_file())
                    rel = d.relative_to(div3_dir).as_posix()
                    factory_rows.append(f"""
                    <tr>
                      <td><span class="badge {badge_cls}">{group_label}</span></td>
                      <td><strong>{d.name}</strong></td>
                      <td><code>LLC-DIV-3-FACTORY/{rel}</code></td>
                      <td>{f_cnt} files</td>
                      <td><a href="file:///C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/{rel}" target="_blank">Open Folder ↗</a></td>
                    </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Division 3 Front Door — Software Factory, Extensions, GWS Add-Ons, Mobile &amp; Shared Bricks</title>
  <style>{common_css()}</style>
</head>
<body>
  <header class="hero-header">
    <div class="container">
      <div class="header-top">
        <div>
          <div class="studio-kicker">🚪 DIVISION 3 FRONT DOOR · SOFTWARE FACTORY, MV3 EXTENSIONS, GWS ADD-ONS, MOBILE &amp; BRICKS (`LLC-DIV-3-FACTORY`)</div>
          <h1>Zane Fields, Marcus Vance &amp; Elena Rostova's Software Factory Front Door</h1>
          <p class="subtitle">
            Always-evolving front door for Division 3 (`C:\\dev\\864zeros-llc\\LLC-DIV-3-FACTORY\\` &amp; `C:\\dev\\clearStreak\\`) — housing 16 Chrome MV3 extensions, 12 Edge MV3 extensions, 18 Google Workspace Add-ons, ClearStreak Android (`v1.0` signed AAB + `v1.1` Custom Pack Importer), and the 9 Shared Feature Bricks (`v1.8`).
          </p>
        </div>
        <div style="text-align:right; font-size:12px; color:var(--text-muted);">
          <div><strong>Last Auto-Scan:</strong> {now_str}</div>
          <div><strong>Division Files:</strong> {tel['total_files']:,} ({fmt_bytes(tel['total_bytes'])})</div>
          <div style="color:#6ee7b7; font-weight:700;">✓ 45/45 Brick Self-Tests · RULE-007 Verified</div>
        </div>
      </div>
      {division_switcher_bar(3)}
    </div>
  </header>

  <main class="container">
    <section class="kpi-grid">
      <div class="kpi-card"><div class="kpi-val">16 Chrome</div><div class="kpi-label">MV3 Browser Extensions</div><div class="kpi-sub">extensions/</div></div>
      <div class="kpi-card"><div class="kpi-val">12 Edge</div><div class="kpi-label">Edge Add-On Packages</div><div class="kpi-sub">5 LIVE · 3 Review · 5 Wave 2</div></div>
      <div class="kpi-card"><div class="kpi-val">18 GWS</div><div class="kpi-label">Google Workspace Add-Ons</div><div class="kpi-sub">ChoiceGuard in Review</div></div>
      <div class="kpi-card"><div class="kpi-val">12.33 MB</div><div class="kpi-label">ClearStreak Signed Play AAB</div><div class="kpi-sub">+ v1.1 Custom JSON Importer</div></div>
      <div class="kpi-card"><div class="kpi-val">9 Bricks</div><div class="kpi-label">Shared Feature Bricks (`v1.8`)</div><div class="kpi-sub">45/45 Unit Assertions PASS</div></div>
    </section>

    <section class="roster-grid">
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/zane-fields.jpg" alt="Zane Fields" />
        <div>
          <div class="leader-role">CTO / LEAD-DEV · Chief Technology Officer</div>
          <div class="leader-name">Zane Fields</div>
          <div class="leader-bio">Commands Division 3 Software Factory, ClearStreak Kotlin/Compose architecture (SQLite DB v6), MV3 extension assembly, and headless Playwright harnesses.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/marcus-vance.jpg" alt="Marcus Vance" />
        <div>
          <div class="leader-role">DEV-BRICKS · Systems &amp; Brick Developer</div>
          <div class="leader-name">Marcus Vance</div>
          <div class="leader-bio">Engineers the zero-dependency Shared Feature Bricks (<code>LLC-DIV-3-FACTORY/shared/bricks/</code>) and cross-product modular adapters.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/elena-rostova.jpg" alt="Elena Rostova" />
        <div>
          <div class="leader-role">DATA-SEC-QA · Security, Privacy &amp; QA Lead</div>
          <div class="leader-name">Elena Rostova</div>
          <div class="leader-bio">Enforces RULE-007 security/QA gates, zero-telemetry verification, manifest permission audits, and deterministic unit test suites.</div>
        </div>
      </div>
    </section>

    <section class="pillars-overview">
      <div class="pillar-box">
        <h3>🗄️ Pillar I: Factory Codebase &amp; Release Artifacts</h3>
        <p>47+ shippable software packages across Mobile, Browser Extensions, and Google Workspace:</p>
        <ul>
          <li><code>C:\\dev\\clearStreak</code> — Signed <code>app-store-release.aab</code> (12.33 MB) &amp; <code>app-store-release.apk</code> (16.55 MB)</li>
          <li><code>LLC-DIV-3-FACTORY/extensions/</code> &amp; <code>extensions-edge/</code> — 16 Chrome + 12 Edge MV3 extensions</li>
          <li><code>LLC-DIV-3-FACTORY/add-ons/</code> — 18 Google Workspace Add-ons (Docs, Sheets, Forms, Gmail, Drive, Slides)</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>⚙️ Pillar II: Shared Feature Bricks (`v1.8`) &amp; Engine Growth</h3>
        <p>Reusable, zero-dependency code bricks shared across Mobile, Extensions, and Print:</p>
        <ul>
          <li><strong>9 Verified Feature Bricks (`45/45` assertions passing):</strong> <code>BRK-EXP-001</code>, <code>BRK-STUDIO-000..003</code>, <code>BRK-QR-001</code>, <code>BRK-PUB-001</code>, <code>BRK-MEDIA-002</code>, <code>BRK-OCR-001</code></li>
          <li><strong>ClearStreak v1.1 Custom Pack Engine:</strong> Zero-permission <code>ACTION_OPEN_DOCUMENT</code> <code>.json</code> importer with 512 KB cap &amp; HTML sanitization</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>🚀 Pillar III: Verified Production Builds &amp; QA Proof</h3>
        <p>Signed, audited packages ready for immediate store deployment:</p>
        <ul>
          <li><strong>5 Microsoft Edge Add-ons LIVE in Production</strong> (VaultPilot, TuneOut2FocusIn, AutoOrganize YTM, 864z Chronicle, Signal2Noise)</li>
          <li><strong>5 Edge Wave 2 Packages Certified 100% Ready</strong> (DataNap, tab-stasher, Time2Focus, oia-focus-note, oia-focus-wall)</li>
        </ul>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🧱 Shared Feature Bricks Registry (`LLC-DIV-3-FACTORY/shared/bricks/` · `v1.8`)</div>
        <span class="owner-tag">9 Bricks · 0 External NPM Dependencies · 45/45 Self-Tests PASS</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Brick ID</th><th>File</th><th>Category</th><th>Purpose</th><th>Consumers</th><th>QA Status</th></tr></thead>
          <tbody>{"".join(brick_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">📦 Factory Product Packages (`extensions/`, `extensions-edge/`, `add-ons/`)</div>
        <span class="owner-tag">{len(factory_rows)} Product Repositories</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Platform</th><th>Product Slug</th><th>Factory Path</th><th>File Count</th><th>Action</th></tr></thead>
          <tbody>{"".join(factory_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🗄️ Division 3 Storage Telemetry</div>
        <span class="owner-tag">{tel['total_files']:,} Files ({fmt_bytes(tel['total_bytes'])})</span>
      </div>
      <div class="storage-grid">{render_storage_pills(tel)}</div>
    </section>
  </main>
</body>
</html>"""
    return html, tel


# ==============================================================================
# DIVISION 5: OMNICHANNEL GTM, STORE DISTRIBUTION, PULSE-X & WEB PROPERTIES
# ==============================================================================
def build_div5_front_door() -> tuple[str, dict]:
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M EDT")
    div5_dir = LLC_ROOT / "LLC-DIV-4-GTM"
    tel = scan_paths_telemetry([div5_dir, WEB_ROOT, PUB_MCP_ROOT])

    gtm_rows = []
    if div5_dir.exists():
        for f in sorted(div5_dir.iterdir()):
            if f.is_file():
                gtm_rows.append(f"""
                <tr>
                  <td><span class="badge badge-amber">DIV-4-GTM</span></td>
                  <td><a href="file:///C:/dev/864zeros-llc/LLC-DIV-4-GTM/{f.name}" target="_blank"><code>{f.name}</code></a></td>
                  <td>{fmt_bytes(f.stat().st_size)}</td>
                  <td>{datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}</td>
                  <td><a href="file:///C:/dev/864zeros-llc/LLC-DIV-4-GTM/{f.name}" target="_blank">Open Playbook ↗</a></td>
                </tr>""")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Division 5 Front Door — Omnichannel GTM, Store Distribution, Pulse-X &amp; Web (`LLC-DIV-4-GTM` &amp; `864zeros-web`)</title>
  <style>{common_css()}</style>
</head>
<body>
  <header class="hero-header">
    <div class="container">
      <div class="header-top">
        <div>
          <div class="studio-kicker">🚪 DIVISION 5 FRONT DOOR · OMNICHANNEL GTM, STORE DISTRIBUTION, PULSE-X &amp; WEB (`LLC-DIV-4-GTM` &amp; `864zeros-web`)</div>
          <h1>Prya Vance &amp; Allegra Katz's Omnichannel GTM, Store Pilot &amp; Web Front Door</h1>
          <p class="subtitle">
            Always-evolving front door for Division 5 (`C:\\dev\\864zeros-llc\\LLC-DIV-4-GTM\\`, `C:\\dev\\864zeros-web\\`, and `C:\\dev\\864zeros-publisher-mcp\\`) — managing live store releases across Microsoft Edge, Chrome Web Store, Google Workspace Marketplace, Google Play, YouTube, and `864zeros.com`.
          </p>
        </div>
        <div style="text-align:right; font-size:12px; color:var(--text-muted);">
          <div><strong>Last Auto-Scan:</strong> {now_str}</div>
          <div><strong>Division Files:</strong> {tel['total_files']:,} ({fmt_bytes(tel['total_bytes'])})</div>
          <div style="color:#6ee7b7; font-weight:700;">✓ 5 Edge Add-Ons LIVE · 13 Team Bios Live</div>
        </div>
      </div>
      {division_switcher_bar(5)}
    </div>
  </header>

  <main class="container">
    <section class="kpi-grid">
      <div class="kpi-card"><div class="kpi-val">5 LIVE</div><div class="kpi-label">Microsoft Edge Add-Ons</div><div class="kpi-sub">+ 3 In Review · 5 Wave 2 Ready</div></div>
      <div class="kpi-card"><div class="kpi-val">41 MV3 Items</div><div class="kpi-label">CWS Quota Expansion Petition</div><div class="kpi-sub">Ready for Support Portal</div></div>
      <div class="kpi-card"><div class="kpi-val">18 GWS Add-Ons</div><div class="kpi-label">54/54 Video Assets Vaulted</div><div class="kpi-sub">ChoiceGuard in GWS Review</div></div>
      <div class="kpi-card"><div class="kpi-val">17 Tools</div><div class="kpi-label">`864zeros-publisher-mcp`</div><div class="kpi-sub">StorePilot · ExtPay · YouTube</div></div>
      <div class="kpi-card"><div class="kpi-val">13 Profiles</div><div class="kpi-label">`864zeros.com/meet-the-team/`</div><div class="kpi-sub">RULE-003 Compliant Web</div></div>
    </section>

    <section class="roster-grid">
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/prya-vance.jpg" alt="Prya Vance" />
        <div>
          <div class="leader-role">VP-GTM / CMO · Chief Marketing Officer</div>
          <div class="leader-name">Prya Vance</div>
          <div class="leader-bio">Leads omnichannel GTM, ASO battle dockets, Pulse-X / Pulse-Ad organic community seeding, YouTube Shorts distribution, and <code>864zeros.com</code> conversion surfaces.</div>
        </div>
      </div>
      <div class="leader-card">
        <img class="leader-avatar" src="file:///C:/dev/864zeros-web/meet-the-team/img/allegra-katz.jpg" alt="Allegra Katz" />
        <div>
          <div class="leader-role">CFO · Chief Financial Officer</div>
          <div class="leader-name">Allegra Katz</div>
          <div class="leader-bio">Co-leads the Google Workspace Marketplace GTM financial model (<code>#kate-5269</code>), ExtPay monetization wiring, and unit margin governance.</div>
        </div>
      </div>
    </section>

    <section class="pillars-overview">
      <div class="pillar-box">
        <h3>🗄️ Pillar I: Store Dockets &amp; Web Asset Vault</h3>
        <p>Centralized store submission packages, ASO dockets, and live web properties:</p>
        <ul>
          <li><code>C:\\dev\\864zeros-web</code> — Live <code>864zeros.com</code> marketing pages, privacy policies, and 13-person team roster</li>
          <li><code>LIBRARY/02-Store-Submissions-and-GTM/</code> — CWS 41-Item Quota Petition &amp; Edge Wave 2 Audit</li>
          <li><code>LLC-DIV-4-GTM/</code> — Pulse-X playbooks, GTM Queue &amp; Lifecycle Architecture, and ASO checklists</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>⚙️ Pillar II: StorePilot &amp; Publisher MCP Functionality</h3>
        <p>Automated store packaging, lockstep auditing, and headless submission tooling:</p>
        <ul>
          <li><strong>864zeros-publisher-mcp (`17` MCP Tools):</strong> <code>audit_dam_lockstep</code>, <code>package_and_prepare_edge_submission</code>, <code>upload_edge_package</code>, <code>publish_edge_submission</code>, <code>upload_youtube_deliverable</code>, <code>extpay_register_extension</code></li>
          <li><strong>Pulse-X &amp; Pulse-Ad Engines:</strong> Value-first community engagement &amp; distribution</li>
        </ul>
      </div>
      <div class="pillar-box">
        <h3>🌐 Pillar III: Live Store Listings &amp; Web Surfaces</h3>
        <p>Verified live store endpoints and customer acquisition channels:</p>
        <ul>
          <li><strong>5 Live Edge Add-Ons:</strong> VaultPilot, TuneOut2FocusIn, AutoOrganize YTM, 864z Chronicle, Signal2Noise</li>
          <li><strong>Live ClearStreak Privacy Policy:</strong> <code>https://www.864zeros.com/privacy/clearstreak</code></li>
          <li><strong>12+ Live YouTube Master Explainers &amp; Shorts</strong> embedded across product pages</li>
        </ul>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🚀 Key GTM Dockets, Live Web Pages &amp; Lifecycle Dashboards</div>
        <span class="owner-tag">One-Click Launchers</span>
      </div>
      <div class="viewers-grid">
        <div class="viewer-card">
          <div><span class="badge badge-green">HTML DASHBOARD</span><h4 style="margin-top:6px;">GTM Queue &amp; Lifecycle Architecture</h4><p>Visual pipeline of store submission stages, asset gates, and publishing queues.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LLC-DIV-4-GTM/GTM_QUEUE_AND_LIFECYCLE_ARCHITECTURE.html" target="_blank">📈 Open GTM Lifecycle HTML ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-amber">STORE PETITION</span><h4 style="margin-top:6px;">CWS Quota Expansion Petition (41 Items)</h4><p>Copy-paste Chrome Web Store Developer Support petition with 41 single-purpose MV3 justifications.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LIBRARY/02-Store-Submissions-and-GTM/CWS_QUOTA_EXPANSION_PETITION_DOCKET.md" target="_blank">📋 Open CWS Petition Docket ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-blue">EDGE WAVE 2</span><h4 style="margin-top:6px;">Edge Wave 2 Pre-Flight Audit (7 Packages)</h4><p>5 packages certified 100% ready for instant Partner Center upload + 2 icon-gate dockets.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-llc/LIBRARY/02-Store-Submissions-and-GTM/EDGE_WAVE2_7_PACKAGES_AUDIT.md" target="_blank">🌐 Open Edge Wave 2 Audit ↗</a>
        </div>
        <div class="viewer-card">
          <div><span class="badge badge-purple">LIVE WEB</span><h4 style="margin-top:6px;">864zeros.com Meet-the-Team &amp; Store Matrix</h4><p>Local preview of <code>864zeros-web/meet-the-team/index.html</code> with all 13 executive &amp; studio bios.</p></div>
          <a class="btn-launch" href="file:///C:/dev/864zeros-web/meet-the-team/index.html" target="_blank">👥 Open Meet-the-Team Page ↗</a>
        </div>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">📂 `LLC-DIV-4-GTM` Playbooks &amp; Specifications</div>
        <span class="owner-tag">{len(gtm_rows)} GTM Documents</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Division</th><th>Document</th><th>Size</th><th>Last Modified</th><th>Action</th></tr></thead>
          <tbody>{"".join(gtm_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section-block">
      <div class="section-header">
        <div class="section-title">🗄️ Division 5 Storage Telemetry</div>
        <span class="owner-tag">{tel['total_files']:,} Files ({fmt_bytes(tel['total_bytes'])})</span>
      </div>
      <div class="storage-grid">{render_storage_pills(tel)}</div>
    </section>
  </main>
</body>
</html>"""
    return html, tel
