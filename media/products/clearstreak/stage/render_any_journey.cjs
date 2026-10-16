const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

(async () => {
  const stageDir = 'C:/dev/864zeros-publish/media/products/clearstreak/stage';
  const audioDir = 'C:/dev/864zeros-publish/media/products/clearstreak/audio';
  const socialDir = 'C:/dev/864zeros-publish/media/products/clearstreak/social';
  const videoDir = 'C:/dev/864zeros-publish/media/products/clearstreak/video';
  const iconsDir = 'C:/dev/864zeros-publish/media/products/clearstreak/icons';
  const storeAssets = 'C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/mobile/clearstreak/store/assets';
  const ffmpeg = 'C:/ffmpeg/bin/ffmpeg.exe';

  const tl = JSON.parse(fs.readFileSync(path.join(audioDir, 'timeline_any.json'), 'utf8'));
  const duration = tl.total_duration;
  const t1 = tl.scenes[0].end;
  const t2 = tl.scenes[1].end;

  const tempDir = path.join(stageDir, 'temp_any');
  if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
  fs.mkdirSync(tempDir, { recursive: true });

  const browser = await chromium.launch({
    headless: true,
    executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
    args: ['--disable-background-timer-throttling', '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding']
  });

  const context = await browser.newContext({
    recordVideo: { dir: tempDir, size: { width: 1080, height: 1920 } },
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1
  });

  const page = await context.newPage();
  await page.goto('file:///' + path.join(stageDir, 'stage_any_journey.html').replace(/\\/g, '/'), { waitUntil: 'load' });
  await page.waitForTimeout(400);
  await page.evaluate(({ t1, t2 }) => window.startPlayback(t1, t2), { t1, t2 });
  await page.waitForTimeout(Math.ceil((duration + 0.8) * 1000));
  await page.close();
  await context.close();
  await browser.close();

  const webm = fs.readdirSync(tempDir).find(f => f.endsWith('.webm'));
  const rawWebm = path.join(tempDir, webm);
  const outMp4 = path.join(socialDir, 'clearstreak-social-any-journey.mp4');
  const outThumb = path.join(socialDir, 'thumbnail-clearstreak-social-any-journey.png');
  const soundtrack = path.join(audioDir, 'soundtrack_any.wav');

  execSync(`"${ffmpeg}" -y -i "${rawWebm}" -i "${soundtrack}" -vf fps=30 -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest "${outMp4}"`, { stdio: 'ignore' });
  execSync(`"${ffmpeg}" -y -ss 2.5 -i "${outMp4}" -vframes 1 "${outThumb}"`, { stdio: 'ignore' });

  fs.copyFileSync(outMp4, path.join(videoDir, 'clearstreak-social-any-journey.mp4'));
  fs.copyFileSync(outThumb, path.join(iconsDir, 'thumbnail-clearstreak-social-any-journey.png'));
  fs.copyFileSync(outMp4, path.join(storeAssets, 'clearstreak-social-any-journey.mp4'));
  fs.copyFileSync(outThumb, path.join(storeAssets, 'thumbnail-clearstreak-social-any-journey.png'));
  fs.rmSync(tempDir, { recursive: true, force: true });
  console.log('Rendered clearstreak-social-any-journey.mp4 (' + duration + 's)');
})();
