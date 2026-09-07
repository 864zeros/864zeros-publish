/**
 * ClearStreak Master Explainer Video Renderer
 * Renders 60s master explainer using Playwright Chrome recordVideo + FFmpeg muxing.
 */

const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const FFMPEG = 'C:/ffmpeg/bin/ffmpeg.exe';
const STAGE_DIR = __dirname;
const AUDIO_DIR = path.join(STAGE_DIR, '..', 'audio');
const VIDEO_DIR = path.join(STAGE_DIR, '..', 'video');
const STORE_ASSETS = 'C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/mobile/clearstreak/store/assets';
const BRAIN_DIR = 'C:/Users/Jeff/.gemini/antigravity-cli/brain/3081b540-e7bd-4442-bb6d-a5242f385951';

fs.mkdirSync(VIDEO_DIR, { recursive: true });
fs.mkdirSync(STORE_ASSETS, { recursive: true });

async function render() {
  const tlData = JSON.parse(fs.readFileSync(path.join(AUDIO_DIR, 'timeline.json'), 'utf8'));
  const duration = tlData.total_duration;
  const tempDir = path.join(STAGE_DIR, 'temp_master');
  if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
  fs.mkdirSync(tempDir, { recursive: true });

  const outMp4 = path.join(VIDEO_DIR, 'clearstreak-master.mp4');
  const outThumb = path.join(VIDEO_DIR, 'clearstreak-thumbnail.png');
  const soundtrackPath = path.join(AUDIO_DIR, 'soundtrack.wav');

  console.log(`\n[ClearStreak Master Video] Recording Master Explainer (${duration.toFixed(2)}s)...`);

  const browser = await chromium.launch({
    headless: true,
    executablePath: CHROME_PATH,
    args: [
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-renderer-backgrounding'
    ]
  });

  const context = await browser.newContext({
    recordVideo: {
      dir: tempDir,
      size: { width: 1080, height: 1920 }
    },
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1
  });

  const page = await context.newPage();
  const htmlUrl = 'file:///' + path.join(STAGE_DIR, 'video.html').replace(/\\/g, '/');
  await page.goto(htmlUrl, { waitUntil: 'load' });

  await page.evaluate(async () => {
    if (document.fonts) await document.fonts.ready;
  });
  await page.waitForTimeout(400);

  // Start playback
  await page.evaluate(() => window.startPlayback());
  const waitMs = Math.ceil((duration + 1.0) * 1000);
  console.log(`  Recording for ${waitMs}ms (${(waitMs / 1000).toFixed(1)}s)...`);
  await page.waitForTimeout(waitMs);

  await page.close();
  await context.close();
  await browser.close();

  const webmFiles = fs.readdirSync(tempDir).filter(f => f.endsWith('.webm'));
  if (webmFiles.length === 0) throw new Error('No recorded webm found in ' + tempDir);
  const rawWebm = path.join(tempDir, webmFiles[0]);

  console.log(`  Muxing with soundtrack: ${soundtrackPath}`);
  const ffmpegCmd = [
    `"${FFMPEG}"`, '-y',
    '-i', `"${rawWebm}"`,
    '-i', `"${soundtrackPath}"`,
    '-vf', 'fps=30',
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-crf', '18',
    '-pix_fmt', 'yuv420p',
    '-c:a', 'aac',
    '-b:a', '192k',
    '-shortest',
    `"${outMp4}"`
  ].join(' ');

  execSync(ffmpegCmd, { stdio: 'ignore' });

  // Extract poster thumbnail at 18s (Multi-Journey Dashboard)
  const thumbCmd = [
    `"${FFMPEG}"`, '-y',
    '-ss', '18.0',
    '-i', `"${outMp4}"`,
    '-vframes', '1',
    `"${outThumb}"`
  ].join(' ');
  execSync(thumbCmd, { stdio: 'ignore' });
  console.log(`  Thumbnail saved -> ${outThumb}`);

  // Copy to store assets and brain
  fs.copyFileSync(outMp4, path.join(STORE_ASSETS, 'clearstreak-master.mp4'));
  fs.copyFileSync(outThumb, path.join(STORE_ASSETS, 'clearstreak-thumbnail.png'));

  if (fs.existsSync(BRAIN_DIR)) {
    fs.copyFileSync(outMp4, path.join(BRAIN_DIR, 'clearstreak-master.mp4'));
    fs.copyFileSync(outThumb, path.join(BRAIN_DIR, 'clearstreak-thumbnail.png'));
  }

  // Cleanup temp dir
  fs.rmSync(tempDir, { recursive: true, force: true });
  console.log(`  Successfully exported Master -> ${outMp4}`);
}

render().catch(err => {
  console.error('[ClearStreak Master Video] Render error:', err);
  process.exit(1);
});
