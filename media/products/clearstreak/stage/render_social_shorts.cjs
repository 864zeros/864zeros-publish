/**
 * ClearStreak Social Micro-Shorts Renderer
 * Renders both sub-20s social shorts using Playwright Chrome recordVideo + FFmpeg muxing:
 *   1. Variant A (Shame / Data Over Shame): clearstreak-social-shame.mp4
 *   2. Variant B (Privacy / Biometrics): clearstreak-social-privacy.mp4
 */

const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const FFMPEG = 'C:/ffmpeg/bin/ffmpeg.exe';
const STAGE_DIR = __dirname;
const AUDIO_DIR = path.join(STAGE_DIR, '..', 'audio');
const SOCIAL_DIR = path.join(STAGE_DIR, '..', 'social');
const STORE_ASSETS = 'C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/mobile/clearstreak/store/assets';
const BRAIN_DIR = 'C:/Users/Jeff/.gemini/antigravity-cli/brain/3081b540-e7bd-4442-bb6d-a5242f385951';

fs.mkdirSync(SOCIAL_DIR, { recursive: true });
fs.mkdirSync(STORE_ASSETS, { recursive: true });

const VARIANTS = [
  {
    id: 'shame',
    name: 'clearstreak-social-shame',
    html: 'stage_shame.html',
    timeline: 'timeline_shame.json',
    soundtrack: 'soundtrack_shame.wav',
    thumbSec: 8.5
  },
  {
    id: 'privacy',
    name: 'clearstreak-social-privacy',
    html: 'stage_privacy.html',
    timeline: 'timeline_privacy.json',
    soundtrack: 'soundtrack_privacy.wav',
    thumbSec: 8.0
  }
];

async function renderVariant(browser, variant) {
  const tlData = JSON.parse(fs.readFileSync(path.join(AUDIO_DIR, variant.timeline), 'utf8'));
  const duration = tlData.total_duration;
  const tempDir = path.join(STAGE_DIR, 'temp_' + variant.id);
  if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
  fs.mkdirSync(tempDir, { recursive: true });

  const outMp4 = path.join(SOCIAL_DIR, `${variant.name}.mp4`);
  const outThumb = path.join(SOCIAL_DIR, `thumbnail-${variant.name}.png`);
  const soundtrackPath = path.join(AUDIO_DIR, variant.soundtrack);

  console.log(`\n[ClearStreak Social] Recording ${variant.name} (${duration.toFixed(2)}s)...`);

  const context = await browser.newContext({
    recordVideo: {
      dir: tempDir,
      size: { width: 1080, height: 1920 }
    },
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1
  });

  const page = await context.newPage();
  const htmlUrl = 'file:///' + path.join(STAGE_DIR, variant.html).replace(/\\/g, '/');
  await page.goto(htmlUrl, { waitUntil: 'load' });

  await page.evaluate(async () => {
    if (document.fonts) await document.fonts.ready;
  });
  await page.waitForTimeout(400);

  // Start playback
  await page.evaluate(() => window.startPlayback());
  const waitMs = Math.ceil((duration + 0.8) * 1000);
  console.log(`  Recording for ${waitMs}ms...`);
  await page.waitForTimeout(waitMs);

  await page.close();
  await context.close();

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

  // Extract poster thumbnail at thumbSec
  const thumbCmd = [
    `"${FFMPEG}"`, '-y',
    '-ss', String(variant.thumbSec),
    '-i', `"${outMp4}"`,
    '-vframes', '1',
    `"${outThumb}"`
  ].join(' ');
  execSync(thumbCmd, { stdio: 'ignore' });
  console.log(`  Thumbnail saved -> ${outThumb}`);

  // Copy to store assets and brain
  fs.copyFileSync(outMp4, path.join(STORE_ASSETS, `${variant.name}.mp4`));
  fs.copyFileSync(outThumb, path.join(STORE_ASSETS, `thumbnail-${variant.name}.png`));

  if (fs.existsSync(BRAIN_DIR)) {
    fs.copyFileSync(outMp4, path.join(BRAIN_DIR, `${variant.name}.mp4`));
    fs.copyFileSync(outThumb, path.join(BRAIN_DIR, `thumbnail-${variant.name}.png`));
  }

  // Cleanup temp dir
  fs.rmSync(tempDir, { recursive: true, force: true });
  console.log(`  Successfully exported -> ${outMp4}`);
}

async function main() {
  const browser = await chromium.launch({
    headless: true,
    executablePath: CHROME_PATH,
    args: [
      '--disable-background-timer-throttling',
      '--disable-backgrounding-occluded-windows',
      '--disable-renderer-backgrounding'
    ]
  });

  for (const v of VARIANTS) {
    await renderVariant(browser, v);
  }

  await browser.close();
  console.log('\n[ClearStreak Social] All social shorts rendered successfully!');
}

main().catch(err => {
  console.error('[ClearStreak Social] Render error:', err);
  process.exit(1);
});
