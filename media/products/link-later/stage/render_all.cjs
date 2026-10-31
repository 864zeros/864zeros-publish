const { chromium } = require('C:/dev/864zeros-publisher-mcp/node_modules/playwright');
const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const PY_EXE = 'C:/Users/Jeff/AppData/Local/Programs/Python/Python313/python.exe';
const FFMPEG_PATH = execSync(`"${PY_EXE}" -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"`)
  .toString()
  .trim();

const BASE_DIR = __dirname;
const LLC_ROOT = path.resolve(BASE_DIR, '..', '..', '..');
const EXT_CHROME = path.join(LLC_ROOT, 'LLC-DIV-3-FACTORY', 'extensions', 'link-later');
const EXT_EDGE = path.join(LLC_ROOT, 'LLC-DIV-3-FACTORY', 'extensions-edge', 'link-later');
const DAM_DIR = path.resolve(LLC_ROOT, '..', '864zeros-publish', 'media', 'products', 'link-later');
const WEB_ASSETS = path.resolve(LLC_ROOT, '..', '864zeros-web', 'products', 'assets');

function ensureDir(d) {
  fs.mkdirSync(d, { recursive: true });
}

function copyFileSafe(src, dst) {
  ensureDir(path.dirname(dst));
  fs.copyFileSync(src, dst);
}

async function renderStageVideo(browser, {
  htmlPath,
  audioPath,
  outMp4Path,
  thumbPath,
  thumbTime = 4.5,
  width = 1080,
  height = 1920,
  durationSec,
  fps = 15,
}) {
  ensureDir(path.dirname(outMp4Path));
  ensureDir(path.dirname(thumbPath));

  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: 1,
  });

  const fileUrl = 'file:///' + htmlPath.replace(/\\/g, '/');
  await page.goto(fileUrl, { waitUntil: 'networkidle' });
  await page.waitForTimeout(250);

  await page.evaluate((t) => window.renderAtTime(t), thumbTime);
  await page.screenshot({ path: thumbPath, type: 'png' });
  console.log(`  [thumb] ${path.basename(thumbPath)}`);

  const totalFrames = Math.ceil((durationSec + 0.35) * fps);
  const ffmpegArgs = [
    '-y',
    '-f', 'image2pipe',
    '-vcodec', 'mjpeg',
    '-r', String(fps),
    '-i', '-',
    '-i', audioPath,
    '-c:v', 'libx264',
    '-preset', 'veryfast',
    '-crf', '20',
    '-r', '30',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    '-movflags', '+faststart',
    outMp4Path,
  ];

  const ff = spawn(FFMPEG_PATH, ffmpegArgs, { stdio: ['pipe', 'ignore', 'pipe'] });
  let stderrLog = '';
  ff.stderr.on('data', (d) => { stderrLog += d.toString(); });

  for (let frame = 0; frame < totalFrames; frame++) {
    const t = frame / fps;
    await page.evaluate((timeSec) => window.renderAtTime(timeSec), t);
    const buf = await page.screenshot({ type: 'jpeg', quality: 88 });
    const ok = ff.stdin.write(buf);
    if (!ok) {
      await new Promise((r) => ff.stdin.once('drain', r));
    }
  }
  ff.stdin.end();

  await new Promise((resolve, reject) => {
    ff.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`FFmpeg exited ${code}: ${stderrLog.slice(-400)}`));
    });
  });

  await page.close();
  const sz = (fs.statSync(outMp4Path).size / (1024 * 1024)).toFixed(2);
  console.log(`  [video] ${path.basename(outMp4Path)} (${sz} MB)`);
}

async function captureStoreScreenshots(browser) {
  console.log('[1/3] Capturing 1280x800 FHG Store Screenshots...');
  const page = await browser.newPage({
    viewport: { width: 1400, height: 2600 },
    deviceScaleFactor: 1,
  });
  const htmlPath = path.join(EXT_CHROME, 'store', 'store-screenshots.html');
  await page.goto('file:///' + htmlPath.replace(/\\/g, '/'), { waitUntil: 'networkidle' });
  await page.waitForTimeout(200);

  const assetsDir = path.join(BASE_DIR, 'assets');
  ensureDir(assetsDir);

  for (let i = 1; i <= 3; i++) {
    const el = page.locator(`#slide${i}`);
    const outPng = path.join(assetsDir, `link-later-${i}.png`);
    await el.screenshot({ path: outPng, type: 'png' });
    console.log(`  [shot] link-later-${i}.png`);
  }
  await page.close();
}

(async () => {
  const iconB64 = 'data:image/png;base64,' + fs.readFileSync(path.join(EXT_CHROME, 'icons', 'icon128.png')).toString('base64');
  const stageFiles = [
    path.join(BASE_DIR, 'video.html'),
    path.join(BASE_DIR, 'video_v2.html'),
    path.join(BASE_DIR, 'live_ui_demo.html'),
    path.join(BASE_DIR, 'social_shorts', 'stage_pain.html'),
    path.join(BASE_DIR, 'social_shorts', 'stage_price.html'),
    path.join(BASE_DIR, 'social_shorts', 'stage_speed.html'),
  ];
  for (const sf of stageFiles) {
    let html = fs.readFileSync(sf, 'utf8');
    html = html.replace(/src="(?:\.\.\/)+LLC-DIV-3-FACTORY\/extensions\/link-later\/icons\/icon128\.png"/g, `src="${iconB64}"`);
    html = html.replace(/transition:\s*opacity\s+0\.28s\s+ease,\s*transform\s+0\.28s\s+ease;/g, 'transition: none;');
    fs.writeFileSync(sf, html, 'utf8');
  }

  const browser = await chromium.launch({ headless: true, channel: 'msedge' });

  await captureStoreScreenshots(browser);

  console.log('[2/3] Rendering FHG Master Explainer, 3 Social Micro-Shorts & 1080p Live-UI Walkthrough...');
  const masterTl = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'audio', 'timeline.json'), 'utf8'));
  const painTl = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'social_shorts', 'audio', 'timeline_pain.json'), 'utf8'));
  const priceTl = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'social_shorts', 'audio', 'timeline_price.json'), 'utf8'));
  const speedTl = JSON.parse(fs.readFileSync(path.join(BASE_DIR, 'social_shorts', 'audio', 'timeline_speed.json'), 'utf8'));

  // 1. Master Explainer (9:16)
  await renderStageVideo(browser, {
    htmlPath: path.join(BASE_DIR, 'video.html'),
    audioPath: path.join(BASE_DIR, 'audio', 'soundtrack.wav'),
    outMp4Path: path.join(BASE_DIR, 'link-later-short.mp4'),
    thumbPath: path.join(BASE_DIR, 'thumbnail.png'),
    thumbTime: 5.0,
    width: 1080,
    height: 1920,
    durationSec: masterTl.total_duration,
    fps: 15,
  });
  copyFileSafe(path.join(BASE_DIR, 'link-later-short.mp4'), path.join(BASE_DIR, 'link-later-short-v2.mp4'));
  copyFileSafe(path.join(BASE_DIR, 'thumbnail.png'), path.join(BASE_DIR, 'thumbnail-v2.png'));

  // 2. Social Micro-Short A: Pain
  await renderStageVideo(browser, {
    htmlPath: path.join(BASE_DIR, 'social_shorts', 'stage_pain.html'),
    audioPath: path.join(BASE_DIR, 'social_shorts', 'audio', 'soundtrack_pain.wav'),
    outMp4Path: path.join(BASE_DIR, 'social_shorts', 'link-later-social-pain.mp4'),
    thumbPath: path.join(BASE_DIR, 'social_shorts', 'thumbnail-link-later-social-pain.png'),
    thumbTime: 4.0,
    width: 1080,
    height: 1920,
    durationSec: painTl.total_duration,
    fps: 15,
  });

  // 3. Social Micro-Short B: Price
  await renderStageVideo(browser, {
    htmlPath: path.join(BASE_DIR, 'social_shorts', 'stage_price.html'),
    audioPath: path.join(BASE_DIR, 'social_shorts', 'audio', 'soundtrack_price.wav'),
    outMp4Path: path.join(BASE_DIR, 'social_shorts', 'link-later-social-price.mp4'),
    thumbPath: path.join(BASE_DIR, 'social_shorts', 'thumbnail-link-later-social-price.png'),
    thumbTime: 4.0,
    width: 1080,
    height: 1920,
    durationSec: priceTl.total_duration,
    fps: 15,
  });

  // 4. Social Micro-Short C: Speed
  await renderStageVideo(browser, {
    htmlPath: path.join(BASE_DIR, 'social_shorts', 'stage_speed.html'),
    audioPath: path.join(BASE_DIR, 'social_shorts', 'audio', 'soundtrack_speed.wav'),
    outMp4Path: path.join(BASE_DIR, 'social_shorts', 'link-later-social-speed.mp4'),
    thumbPath: path.join(BASE_DIR, 'social_shorts', 'thumbnail-link-later-social-speed.png'),
    thumbTime: 4.0,
    width: 1080,
    height: 1920,
    durationSec: speedTl.total_duration,
    fps: 15,
  });

  // 5. Tier 0: 1080p Live-UI Walkthrough (16:9)
  await renderStageVideo(browser, {
    htmlPath: path.join(BASE_DIR, 'live_ui_demo.html'),
    audioPath: path.join(BASE_DIR, 'audio', 'soundtrack.wav'),
    outMp4Path: path.join(BASE_DIR, 'link-later-live-ui-demo.mp4'),
    thumbPath: path.join(BASE_DIR, 'thumbnail-live-ui.png'),
    thumbTime: 6.0,
    width: 1920,
    height: 1080,
    durationSec: masterTl.total_duration,
    fps: 15,
  });

  await browser.close();

  console.log('[3/3] Syncing rendered videos, thumbnails, screenshots & DAM stems across fleet...');
  const storeTargets = [
    path.join(EXT_CHROME, 'store', 'assets'),
    path.join(EXT_EDGE, 'store', 'assets'),
    WEB_ASSETS,
  ];

  for (const targetDir of storeTargets) {
    ensureDir(targetDir);
    copyFileSafe(path.join(BASE_DIR, 'link-later-short.mp4'), path.join(targetDir, 'link-later-short.mp4'));
    copyFileSafe(path.join(BASE_DIR, 'link-later-live-ui-demo.mp4'), path.join(targetDir, 'link-later-live-ui-demo.mp4'));
    copyFileSafe(path.join(BASE_DIR, 'thumbnail.png'), path.join(targetDir, 'link-later-thumbnail.png'));
    for (let i = 1; i <= 3; i++) {
      copyFileSafe(path.join(BASE_DIR, 'assets', `link-later-${i}.png`), path.join(targetDir, `link-later-${i}.png`));
    }
    for (const kind of ['pain', 'price', 'speed']) {
      copyFileSafe(
        path.join(BASE_DIR, 'social_shorts', `link-later-social-${kind}.mp4`),
        path.join(targetDir, `link-later-social-${kind}.mp4`)
      );
      copyFileSafe(
        path.join(BASE_DIR, 'social_shorts', `thumbnail-link-later-social-${kind}.png`),
        path.join(targetDir, `thumbnail-link-later-social-${kind}.png`)
      );
    }
  }

  // Sync to DAM (864zeros-publish/media/products/link-later/)
  copyFileSafe(path.join(BASE_DIR, 'link-later-short.mp4'), path.join(DAM_DIR, 'video', 'link-later-short.mp4'));
  copyFileSafe(path.join(BASE_DIR, 'link-later-short-v2.mp4'), path.join(DAM_DIR, 'video', 'link-later-short-v2.mp4'));
  copyFileSafe(path.join(BASE_DIR, 'link-later-live-ui-demo.mp4'), path.join(DAM_DIR, 'video', 'link-later-live-ui-demo.mp4'));
  copyFileSafe(path.join(BASE_DIR, 'thumbnail.png'), path.join(DAM_DIR, 'video', 'link-later-thumbnail.png'));

  for (let i = 1; i <= 3; i++) {
    copyFileSafe(path.join(BASE_DIR, 'assets', `link-later-${i}.png`), path.join(DAM_DIR, 'store', `link-later-${i}.png`));
  }

  for (const kind of ['pain', 'price', 'speed']) {
    copyFileSafe(
      path.join(BASE_DIR, 'social_shorts', `link-later-social-${kind}.mp4`),
      path.join(DAM_DIR, 'social', `link-later-social-${kind}.mp4`)
    );
    copyFileSafe(
      path.join(BASE_DIR, 'social_shorts', `thumbnail-link-later-social-${kind}.png`),
      path.join(DAM_DIR, 'social', `thumbnail-link-later-social-${kind}.png`)
    );
  }

  // Copy stage & audio stems into DAM
  copyFileSafe(path.join(BASE_DIR, 'video.html'), path.join(DAM_DIR, 'stage', 'video.html'));
  copyFileSafe(path.join(BASE_DIR, 'social_shorts', 'stage_pain.html'), path.join(DAM_DIR, 'stage', 'stage_pain.html'));
  copyFileSafe(path.join(BASE_DIR, 'social_shorts', 'stage_price.html'), path.join(DAM_DIR, 'stage', 'stage_price.html'));
  copyFileSafe(path.join(BASE_DIR, 'social_shorts', 'stage_speed.html'), path.join(DAM_DIR, 'stage', 'stage_speed.html'));
  copyFileSafe(path.join(BASE_DIR, 'generate_all_audio.py'), path.join(DAM_DIR, 'stage', 'generate_audio.py'));
  copyFileSafe(path.join(BASE_DIR, 'audio', 'timeline.json'), path.join(DAM_DIR, 'audio', 'timeline.json'));
  copyFileSafe(path.join(BASE_DIR, 'audio', 'soundtrack.wav'), path.join(DAM_DIR, 'audio', 'soundtrack.wav'));
  copyFileSafe(path.join(BASE_DIR, 'audio', 'voiceover_full.wav'), path.join(DAM_DIR, 'audio', 'voiceover_full.wav'));
  copyFileSafe(path.join(BASE_DIR, 'audio', 'music_bed.wav'), path.join(DAM_DIR, 'audio', 'music_bed.wav'));

  console.log('ALL LINK-LATER VIDEOS, SCREENSHOTS & DAM STEMS SYNCED SUCCESSFULLY!');
})();
