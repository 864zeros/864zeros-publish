import os

html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>864z Smudge Filter Studio · 864zeros</title>
<style>
  :root {
    --bg: #0d0f13;
    --panel: #161920;
    --card: #1c2028;
    --border: #282d38;
    --border-focus: #d4a373;
    --text: #e6e9ef;
    --muted: #8c93a0;
    --accent: #d4a373;
    --accent-glow: rgba(212, 163, 115, 0.25);
    --gold: #e5b383;
    --green: #4ade80;
    --radius: 10px;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 0; background: var(--bg); color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.5; min-height: 100vh;
  }
  header {
    background: var(--panel); border-bottom: 1px solid var(--border);
    padding: 16px 28px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;
  }
  .badge {
    font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em;
    color: var(--accent); background: rgba(212,163,115,0.12); padding: 4px 10px; border-radius: 4px;
    border: 1px solid rgba(212,163,115,0.3); display: inline-block; margin-bottom: 4px;
  }
  h1 { font-size: 21px; font-weight: 850; margin: 0; letter-spacing: -0.01em; }
  .subtitle { font-size: 13px; color: var(--muted); margin: 0; }
  
  .actions-bar { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
  .btn {
    padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600;
    cursor: pointer; border: 1px solid var(--border); background: #222731; color: var(--text);
    transition: all 0.15s ease; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;
  }
  .btn:hover { background: #2d3442; border-color: var(--accent); }
  .btn-primary { background: var(--accent); color: #111; border-color: var(--accent); font-weight: 700; }
  .btn-primary:hover { background: #e5b383; }
  .btn-success { background: #1b3826; color: var(--green); border-color: #275938; }
  .btn-success:hover { background: #234b33; }

  .main-layout {
    display: grid; grid-template-columns: 380px 1fr;
    min-height: calc(100vh - 75px);
  }
  @media (max-width: 980px) {
    .main-layout { grid-template-columns: 1fr; }
  }

  /* Controls Sidebar */
  .sidebar {
    background: var(--panel); border-right: 1px solid var(--border);
    padding: 24px; display: flex; flex-direction: column; gap: 18px;
    overflow-y: auto; max-height: calc(100vh - 75px);
  }
  .section-title {
    font-size: 11.5px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.12em;
    color: var(--accent); margin: 0 0 10px; display: flex; align-items: center; justify-content: space-between;
  }
  .control-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 16px;
    display: flex; flex-direction: column; gap: 12px;
  }
  .control-row {
    display: flex; justify-content: space-between; align-items: center; font-size: 13px; margin-bottom: 4px;
  }
  .control-label { font-weight: 600; color: #cbd2dc; }
  .control-val { font-family: monospace; font-size: 12px; color: var(--accent); font-weight: 700; }
  input[type="range"] {
    width: 100%; height: 5px; accent-color: var(--accent); background: #2a303c;
    border-radius: 4px; outline: none; cursor: pointer;
  }
  select {
    width: 100%; padding: 8px 12px; background: #13161c; border: 1px solid var(--border);
    color: var(--text); border-radius: 6px; font-size: 13px; font-weight: 500; cursor: pointer;
    outline: none;
  }
  select:focus { border-color: var(--accent); }

  .mode-switch {
    display: grid; grid-template-columns: 1fr 1fr; gap: 6px; background: #121419;
    padding: 4px; border-radius: 8px; border: 1px solid var(--border);
  }
  .mode-btn {
    padding: 8px 10px; font-size: 12px; font-weight: 700; text-align: center;
    border-radius: 6px; cursor: pointer; color: var(--muted); border: none; background: transparent;
    transition: all 0.15s ease;
  }
  .mode-btn.active {
    background: #252b36; color: #fff; box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  }

  /* Live Terminal Snippet */
  .cli-snippet-box {
    background: #111317; border: 1px solid var(--border); border-radius: 6px; padding: 12px;
    font-family: Consolas, Monaco, "Courier New", monospace; font-size: 11.5px; color: #a6b0bf;
    position: relative; overflow-x: auto; white-space: pre-wrap; word-break: break-all;
  }
  .cli-snippet-box code { color: #e5b383; }

  /* Toast Notification */
  .toast {
    position: fixed; bottom: 24px; right: 24px; background: #1b281f; color: #4ade80;
    border: 1px solid #2e5437; padding: 12px 18px; border-radius: 8px; font-size: 13px; font-weight: 600;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: none; align-items: center; gap: 8px; z-index: 1000;
  }
  .toast.error { background: #351c1c; color: #f87171; border-color: #5e2a2a; }

  /* Canvas Stage */
  .stage-wrap {
    background: #08090c; display: flex; flex-direction: column;
    align-items: center; justify-content: center; padding: 24px; position: relative;
  }
  .canvas-card {
    background: #ffffff; border-radius: 8px; box-shadow: 0 20px 60px rgba(0,0,0,0.7);
    position: relative; width: 680px; height: 680px; max-width: 88vw; max-height: 88vw;
    overflow: hidden; user-select: none;
  }
  .canvas-card svg, .canvas-card canvas {
    width: 100%; height: 100%; display: block; position: absolute; top: 0; left: 0;
  }
  #paintCanvas {
    z-index: 10; cursor: crosshair;
  }
  .canvas-overlay-tip {
    position: absolute; bottom: 14px; left: 50%; transform: translateX(-50%);
    background: rgba(13,15,19,0.88); color: #d0d4dc; font-size: 12px; font-weight: 600;
    padding: 6px 16px; border-radius: 20px; backdrop-filter: blur(6px); pointer-events: none;
    border: 1px solid rgba(255,255,255,0.12); z-index: 20; text-align: center; white-space: nowrap;
  }
</style>
</head>
<body>

<header>
  <div>
    <div class="badge">Tool: 864z-smudge-filter · 864zeros Publish</div>
    <h1>864z Smudge Filter Studio</h1>
    <p class="subtitle">Interactive parameter receiver &amp; real-time vector advection generator.</p>
  </div>
  <div class="actions-bar">
    <button class="btn btn-success" onclick="sendVariablesToBackend()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
      Send Variables to 864z Tool
    </button>
    <button class="btn btn-primary" onclick="exportCustomSvg()">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      Download Baked SVG
    </button>
  </div>
</header>

<div class="main-layout">

  <!-- Sidebar Controls -->
  <div class="sidebar">

    <!-- Artwork Selector -->
    <div>
      <div class="section-title">Select Plate / Artwork</div>
      <select id="plateSelect" onchange="changePlate(this.value)">
        <option value="gestalt_raw_freehand_facial_master.svg">Gestalt Freehand Woman (Master)</option>
        <option value="freehand_gates_cornerstones.svg">Freehand Gates &amp; Cornerstones</option>
        <option value="portrait_raw_searching_lines.svg">Portrait Raw Searching Lines</option>
        <option value="poem_01.svg">Poem 01: Architect of Dawn</option>
        <option value="poem_02.svg">Poem 02: Lighthouse at World's Edge</option>
        <option value="cover.svg">eBook Cover: Drafting Desk &amp; Ridge</option>
      </select>
    </div>
    
    <!-- Mode Switch -->
    <div>
      <div class="section-title">Execution Mode</div>
      <div class="mode-switch">
        <button class="mode-btn active" id="btnModeSvg" onclick="setMode('svg')">1. Live SVG Filter</button>
        <button class="mode-btn" id="btnModeTouch" onclick="setMode('touch')">2. S-Pen / Touch Smudge</button>
      </div>
    </div>

    <!-- Live SVG Filter Parameters -->
    <div id="svgControlsGroup" class="control-card">
      <div class="section-title">Smudge Physics Variables</div>
      
      <div>
        <div class="control-row">
          <span class="control-label">Smudge Angle (&theta;)</span>
          <span class="control-val" id="valAngle">45&deg;</span>
        </div>
        <input type="range" id="paramAngle" min="0" max="360" value="45" oninput="updateControls()">
      </div>

      <div>
        <div class="control-row">
          <span class="control-label">Drag Distance (Strength S)</span>
          <span class="control-val" id="valDist">9.0 px</span>
        </div>
        <input type="range" id="paramDist" min="0" max="30" value="9" step="0.5" oninput="updateControls()">
      </div>

      <div>
        <div class="control-row">
          <span class="control-label">Diffusion Softness (D)</span>
          <span class="control-val" id="valSoft">3.0</span>
        </div>
        <input type="range" id="paramSoft" min="0.5" max="15" value="3" step="0.5" oninput="updateControls()">
      </div>

      <div>
        <div class="control-row">
          <span class="control-label">Paper Grain Roughness</span>
          <span class="control-val" id="valTooth">9.0</span>
        </div>
        <input type="range" id="paramTooth" min="0" max="25" value="9" step="1" oninput="updateControls()">
      </div>

      <div>
        <div class="control-row">
          <span class="control-label">Charcoal Trail Opacity</span>
          <span class="control-val" id="valOpacity">0.55</span>
        </div>
        <input type="range" id="paramOpacity" min="0" max="1" value="0.55" step="0.05" oninput="updateControls()">
      </div>

      <button class="btn" style="margin-top:4px; justify-content:center;" onclick="resetSvgParams()">Reset to Calibrated Preset</button>
    </div>

    <!-- Touch / Canvas Smudge Controls -->
    <div id="touchControlsGroup" class="control-card" style="display:none;">
      <div class="section-title">Touch / S-Pen Parameters</div>
      
      <div>
        <div class="control-row">
          <span class="control-label">Smudge Tip Radius</span>
          <span class="control-val" id="valRadius">45 px</span>
        </div>
        <input type="range" id="touchRadius" min="15" max="120" value="45" oninput="document.getElementById('valRadius').innerText = this.value + ' px'">
      </div>

      <div>
        <div class="control-row">
          <span class="control-label">Advection Strength (S)</span>
          <span class="control-val" id="valStrength">80%</span>
        </div>
        <input type="range" id="touchStrength" min="10" max="100" value="80" oninput="document.getElementById('valStrength').innerText = this.value + '%'">
      </div>

      <button class="btn" style="margin-top:4px; justify-content:center;" onclick="resetCanvasDrawing()">Reset Canvas Ink</button>
    </div>

    <!-- Live CLI Preview -->
    <div>
      <div class="section-title">Live 864z CLI Command</div>
      <div class="cli-snippet-box" id="cliCommandBox">
        <code>864z-smudge-filter input.svg --angle 45 --dist 9.0 --soft 3.0 --tooth 9.0 --opacity 0.55</code>
      </div>
    </div>

  </div>

  <!-- Stage Canvas -->
  <div class="stage-wrap">
    
    <div class="canvas-card" id="cardContainer">
      
      <!-- Native Vector SVG with Dynamic Filter -->
      <svg id="liveSvg" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
        <defs id="svgDefs">
          <filter id="charcoal_smudge" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceGraphic" id="filterBlur" stdDeviation="6.4 6.4" result="directional_smear" />
            <feTurbulence type="fractalNoise" id="filterTurb" baseFrequency="0.045" numOctaves="3" result="paper_tooth" />
            <feDisplacementMap in="directional_smear" in2="paper_tooth" id="filterDisp" scale="9" xChannelSelector="R" yChannelSelector="G" result="textured_smudge" />
            <feColorMatrix in="textured_smudge" id="filterColor" type="matrix" 
              values="0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 0.55 0" result="charcoal_haze" />
            <feMerge>
              <feMergeNode in="charcoal_haze" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        
        <g id="vectorGroup" filter="url(#charcoal_smudge)"></g>
      </svg>

      <!-- Interactive Canvas for Stylus/Mouse Advection -->
      <canvas id="paintCanvas" width="1024" height="1024" style="display:none;"></canvas>

      <div class="canvas-overlay-tip" id="overlayTip">
        Adjust sliders on the left or click "Send Variables to 864z Tool"
      </div>

    </div>

  </div>

</div>

<!-- Toast Notification -->
<div class="toast" id="toastBox">
  <span id="toastMsg">Variables saved to disk!</span>
</div>

<script>
  let currentMode = 'svg';
  let currentPlate = 'gestalt_raw_freehand_facial_master.svg';
  let canvas = document.getElementById('paintCanvas');
  let ctx = canvas.getContext('2d', { willReadFrequently: true });
  let baseImage = new Image();
  let rawSvgContent = '';

  // Load initial plate SVG
  loadPlate(currentPlate);

  function loadPlate(filename) {
    currentPlate = filename;
    fetch('tablet_vector_pack_s8_ultra/' + filename)
      .then(r => r.text())
      .then(xml => {
        rawSvgContent = xml;
        let parser = new DOMParser();
        let doc = parser.parseFromString(xml, "image/svg+xml");
        let paths = doc.querySelectorAll('path');
        let group = document.getElementById('vectorGroup');
        group.innerHTML = '';
        paths.forEach(p => group.appendChild(p.cloneNode(true)));
        updateControls();
      })
      .catch(err => console.error("Error loading SVG:", err));

    // Also load raster for touch mode
    let rasterName = filename.replace('.svg', '.jpg');
    baseImage.src = 'rendered_art/' + rasterName;
    baseImage.onload = () => { if (currentMode === 'touch') resetCanvasDrawing(); };
  }

  function changePlate(val) {
    loadPlate(val);
  }

  function setMode(mode) {
    currentMode = mode;
    document.getElementById('btnModeSvg').classList.toggle('active', mode === 'svg');
    document.getElementById('btnModeTouch').classList.toggle('active', mode === 'touch');
    document.getElementById('svgControlsGroup').style.display = mode === 'svg' ? 'flex' : 'none';
    document.getElementById('touchControlsGroup').style.display = mode === 'touch' ? 'flex' : 'none';

    let svgEl = document.getElementById('liveSvg');
    let canvasEl = document.getElementById('paintCanvas');
    let tip = document.getElementById('overlayTip');

    if (mode === 'svg') {
      svgEl.style.display = 'block';
      canvasEl.style.display = 'none';
      tip.innerText = 'Adjust sliders on the left to see the mathematical smear and paper tooth live on the vector lines.';
    } else {
      svgEl.style.display = 'none';
      canvasEl.style.display = 'block';
      tip.innerText = 'Drag with your stylus, mouse, or S-Pen across the drawing to physically smudge the ink!';
      resetCanvasDrawing();
    }
  }

  function updateControls() {
    let angleDeg = parseFloat(document.getElementById('paramAngle').value);
    let dist = parseFloat(document.getElementById('paramDist').value);
    let soft = parseFloat(document.getElementById('paramSoft').value);
    let tooth = parseFloat(document.getElementById('paramTooth').value);
    let opacity = parseFloat(document.getElementById('paramOpacity').value);

    document.getElementById('valAngle').innerText = angleDeg + '°';
    document.getElementById('valDist').innerText = dist.toFixed(1) + ' px';
    document.getElementById('valSoft').innerText = soft.toFixed(1);
    document.getElementById('valTooth').innerText = tooth.toFixed(1);
    document.getElementById('valOpacity').innerText = opacity.toFixed(2);

    let rad = angleDeg * Math.PI / 180.0;
    let dx = Math.abs(Math.cos(rad) * dist) + soft;
    let dy = Math.abs(Math.sin(rad) * dist) + soft;

    let blurEl = document.getElementById('filterBlur');
    if (blurEl) blurEl.setAttribute('stdDeviation', `${dx.toFixed(2)} ${dy.toFixed(2)}`);

    let dispEl = document.getElementById('filterDisp');
    if (dispEl) dispEl.setAttribute('scale', tooth);

    let colorEl = document.getElementById('filterColor');
    if (colorEl) colorEl.setAttribute('values', `0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 ${opacity} 0`);

    // Update CLI command preview
    let cmd = `864z-smudge-filter "${currentPlate}" --angle ${angleDeg} --dist ${dist} --soft ${soft} --tooth ${tooth} --opacity ${opacity}`;
    document.getElementById('cliCommandBox').innerHTML = `<code>${cmd}</code>`;
  }

  function resetSvgParams() {
    document.getElementById('paramAngle').value = 45;
    document.getElementById('paramDist').value = 9;
    document.getElementById('paramSoft').value = 3;
    document.getElementById('paramTooth').value = 9;
    document.getElementById('paramOpacity').value = 0.55;
    updateControls();
  }

  // Export custom SVG generated client-side
  function exportCustomSvg() {
    let angleDeg = parseFloat(document.getElementById('paramAngle').value);
    let dist = parseFloat(document.getElementById('paramDist').value);
    let soft = parseFloat(document.getElementById('paramSoft').value);
    let tooth = parseFloat(document.getElementById('paramTooth').value);
    let opacity = parseFloat(document.getElementById('paramOpacity').value);

    let rad = angleDeg * Math.PI / 180.0;
    let dx = (Math.abs(Math.cos(rad) * dist) + soft).toFixed(2);
    let dy = (Math.abs(Math.sin(rad) * dist) + soft).toFixed(2);

    let groupInner = document.getElementById('vectorGroup').innerHTML;

    let customSvg = `<?xml version="1.0" encoding="UTF-8"?>
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" style="background:#ffffff;">
<defs>
  <!-- Generated via 864z-smudge-filter: angle=${angleDeg}deg, dist=${dist}px, tooth=${tooth} -->
  <filter id="charcoal_smudge" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">
    <feGaussianBlur in="SourceGraphic" stdDeviation="${dx} ${dy}" result="directional_smear" />
    <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" result="paper_tooth" />
    <feDisplacementMap in="directional_smear" in2="paper_tooth" scale="${tooth}" xChannelSelector="R" yChannelSelector="G" result="textured_smudge" />
    <feColorMatrix in="textured_smudge" type="matrix" 
      values="0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 ${opacity} 0" result="charcoal_haze" />
    <feMerge>
      <feMergeNode in="charcoal_haze" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>
<g id="artwork" filter="url(#charcoal_smudge)">
${groupInner}
</g>
</svg>`;

    let blob = new Blob([customSvg], { type: "image/svg+xml;charset=utf-8" });
    let url = URL.createObjectURL(blob);
    let a = document.createElement("a");
    a.href = url;
    let outName = currentPlate.replace(".svg", `_smudge_a${angleDeg}_d${dist}.svg`);
    a.download = outName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    showToast(`Exported custom vector: ${outName}`);
  }

  // Send variables to 864z Backend tool API
  function sendVariablesToBackend() {
    let payload = {
      input: "media/visuals/tablet_vector_pack_s8_ultra/" + currentPlate,
      angle: parseFloat(document.getElementById('paramAngle').value),
      dist: parseFloat(document.getElementById('paramDist').value),
      soft: parseFloat(document.getElementById('paramSoft').value),
      tooth: parseFloat(document.getElementById('paramTooth').value),
      opacity: parseFloat(document.getElementById('paramOpacity').value),
      out: "media/visuals/tablet_vector_pack_s8_ultra/ui_custom_smudge.svg",
      mode: "native"
    };

    fetch('/api/smudge', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    .then(res => {
      if (!res.ok) throw new Error("HTTP error " + res.status);
      return res.json();
    })
    .then(data => {
      if (data.status === "success") {
        showToast(`Saved to disk: ${data.saved_file} (${data.size_kb} KB)`);
      } else {
        showToast("Error from 864z backend: " + data.message, true);
      }
    })
    .catch(err => {
      // If server is offline, fallback to client-side bake
      showToast("Backend server offline (run: 864z-smudge-filter --serve). Baking directly in browser!", false);
      exportCustomSvg();
    });
  }

  function showToast(msg, isError = false) {
    let t = document.getElementById('toastBox');
    let m = document.getElementById('toastMsg');
    m.innerText = msg;
    t.classList.toggle('error', isError);
    t.style.display = 'flex';
    setTimeout(() => { t.style.display = 'none'; }, 4000);
  }

  // Touch / Stylus Advection Smudge Implementation
  function resetCanvasDrawing() {
    ctx.drawImage(baseImage, 0, 0, 1024, 1024);
  }

  let isDrawing = false;
  let lastX = 0, lastY = 0;

  canvas.addEventListener('pointerdown', (e) => {
    if (currentMode !== 'touch') return;
    isDrawing = true;
    let rect = canvas.getBoundingClientRect();
    let scale = 1024 / rect.width;
    lastX = (e.clientX - rect.left) * scale;
    lastY = (e.clientY - rect.top) * scale;
  });

  window.addEventListener('pointerup', () => { isDrawing = false; });

  canvas.addEventListener('pointermove', (e) => {
    if (!isDrawing || currentMode !== 'touch') return;
    let rect = canvas.getBoundingClientRect();
    let scale = 1024 / rect.width;
    let curX = (e.clientX - rect.left) * scale;
    let curY = (e.clientY - rect.top) * scale;

    let vx = curX - lastX;
    let vy = curY - lastY;
    let vlen = Math.hypot(vx, vy);

    if (vlen > 1.5) {
      applyAdvectionSmudge(curX, curY, vx, vy);
      lastX = curX;
      lastY = curY;
    }
  });

  function applyAdvectionSmudge(cx, cy, vx, vy) {
    let radius = parseInt(document.getElementById('touchRadius').value);
    let strength = parseInt(document.getElementById('touchStrength').value) / 100.0;

    let x0 = Math.max(0, Math.floor(cx - radius));
    let y0 = Math.max(0, Math.floor(cy - radius));
    let x1 = Math.min(1024, Math.ceil(cx + radius));
    let y1 = Math.min(1024, Math.ceil(cy + radius));
    let w = x1 - x0;
    let h = y1 - y0;
    if (w <= 0 || h <= 0) return;

    let imgData = ctx.getImageData(x0, y0, w, h);
    let pixels = imgData.data;
    let copy = new Uint8ClampedArray(pixels);

    for (let py = 0; py < h; py++) {
      let worldY = y0 + py;
      let dy = worldY - cy;
      for (let px = 0; px < w; px++) {
        let worldX = x0 + px;
        let dx = worldX - cx;
        let r = Math.hypot(dx, dy);

        if (r < radius) {
          let falloff = Math.pow(1.0 - (r / radius), 1.8);
          let shiftX = strength * falloff * vx;
          let shiftY = strength * falloff * vy;

          let srcX = px - shiftX;
          let srcY = py - shiftY;

          if (srcX >= 0 && srcX < w - 1 && srcY >= 0 && srcY < h - 1) {
            let ix = Math.floor(srcX);
            let iy = Math.floor(srcY);
            let fx = srcX - ix;
            let fy = srcY - iy;

            let idx00 = (iy * w + ix) * 4;
            let idx10 = idx00 + 4;
            let idx01 = ((iy + 1) * w + ix) * 4;
            let idx11 = idx01 + 4;

            let curIdx = (py * w + px) * 4;
            for (let c = 0; c < 3; c++) {
              let val = (1 - fx) * (1 - fy) * copy[idx00 + c] +
                        fx * (1 - fy) * copy[idx10 + c] +
                        (1 - fx) * fy * copy[idx01 + c] +
                        fx * fy * copy[idx11 + c];
              pixels[curIdx + c] = val;
            }
          }
        }
      }
    }
    ctx.putImageData(imgData, x0, y0);
  }
</script>

</body>
</html>
'''

out_file = r"C:\dev\864zeros-publish\media\visuals\smudge_filter_lab.html"
with open(out_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Updated Smudge Filter Studio: {out_file} ({os.path.getsize(out_file)/1024:.1f} KB)")
