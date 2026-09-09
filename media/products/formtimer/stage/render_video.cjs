const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const VIDEO_DIR = __dirname;
const TEMP_RECORD_DIR = path.join(VIDEO_DIR, 'temp_record');
const HTML_FILE = path.join(VIDEO_DIR, 'video.html');
const SOUNDTRACK_FILE = path.join(VIDEO_DIR, 'audio', 'soundtrack.wav');
const FINAL_OUTPUT_MP4 = path.join(VIDEO_DIR, 'formtimer-short.mp4');

const DAM_DIR = path.resolve('C:/dev/864zeros-publish/media/products/formtimer');
const DAM_VIDEO_DIR = path.join(DAM_DIR, 'video');
const DAM_AUDIO_DIR = path.join(DAM_DIR, 'audio');
const DAM_STAGE_DIR = path.join(DAM_DIR, 'stage');
const WEB_ASSETS_DIR = path.resolve('C:/dev/864zeros-web/products/assets');
const ARTIFACT_DIR = path.resolve('C:/Users/Jeff/.gemini/antigravity-cli/brain/b339e8b3-edee-40f3-a2c6-86edd2eb2418');

fs.mkdirSync(DAM_VIDEO_DIR, { recursive: true });
fs.mkdirSync(DAM_AUDIO_DIR, { recursive: true });
fs.mkdirSync(DAM_STAGE_DIR, { recursive: true });
if (fs.existsSync(path.resolve('C:/dev/864zeros-web/products'))) {
    fs.mkdirSync(WEB_ASSETS_DIR, { recursive: true });
}

let TOTAL_DURATION_SEC = 45.0;
try {
    const timeline = JSON.parse(fs.readFileSync(path.join(VIDEO_DIR, 'audio', 'timeline.json'), 'utf8'));
    const last = timeline[timeline.length - 1];
    if (last && last.end) TOTAL_DURATION_SEC = last.end + 0.5;
} catch (e) {}

(async () => {
    console.log('--- Step 1: Preparing directories ---');
    if (fs.existsSync(TEMP_RECORD_DIR)) {
        fs.rmSync(TEMP_RECORD_DIR, { recursive: true, force: true });
    }
    fs.mkdirSync(TEMP_RECORD_DIR, { recursive: true });

    console.log('--- Step 2: Launching Chrome for 1080x1920 video recording ---');
    const browser = await chromium.launch({
        headless: true,
        executablePath: 'C:/Program Files/Google/Chrome/Application/chrome.exe',
        args: [
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding'
        ]
    });

    const context = await browser.newContext({
        recordVideo: {
            dir: TEMP_RECORD_DIR,
            size: { width: 1080, height: 1920 }
        },
        viewport: { width: 1080, height: 1920 },
        deviceScaleFactor: 1
    });

    const page = await context.newPage();
    await page.goto('file:///' + HTML_FILE.replace(/\\/g, '/'), { waitUntil: 'load' });
    await page.evaluate(async () => {
        if (document.fonts) await document.fonts.ready;
    });
    await page.waitForTimeout(500);

    await page.evaluate(() => window.startPlayback());
    const waitMs = Math.ceil((TOTAL_DURATION_SEC + 1.2) * 1000);
    console.log(`Recording animation for ${waitMs}ms (${(waitMs / 1000).toFixed(1)}s)...`);
    await page.waitForTimeout(waitMs);

    await page.close();
    await context.close();
    await browser.close();

    const videoFiles = fs.readdirSync(TEMP_RECORD_DIR).filter(f => f.endsWith('.webm'));
    if (videoFiles.length === 0) throw new Error('No recorded webm video file found.');
    const rawWebm = path.join(TEMP_RECORD_DIR, videoFiles[0]);

    console.log('--- Step 3: Muxing with soundtrack into high-res MP4 via FFmpeg ---');
    const ffmpegCmd = [
        'ffmpeg', '-y',
        '-i', `"${rawWebm}"`,
        '-i', `"${SOUNDTRACK_FILE}"`,
        '-vf', 'fps=30',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        `"${FINAL_OUTPUT_MP4}"`
    ].join(' ');

    console.log(`Executing: ${ffmpegCmd}`);
    execSync(ffmpegCmd, { stdio: 'inherit' });
    console.log(`Master MP4 created at: ${FINAL_OUTPUT_MP4}`);

    // Extract thumbnail poster at 3.0s
    console.log('--- Step 4: Extracting poster thumbnail at 3.0s ---');
    const thumbFile = path.join(VIDEO_DIR, 'thumbnail.png');
    const thumbCmd = [
        'ffmpeg', '-y',
        '-ss', '3.0',
        '-i', `"${FINAL_OUTPUT_MP4}"`,
        '-frames:v', '1',
        '-q:v', '2',
        `"${thumbFile}"`
    ].join(' ');
    execSync(thumbCmd, { stdio: 'inherit' });
    console.log(`Thumbnail extracted: ${thumbFile}`);

    // Distribute to DAM and Web
    console.log('--- Step 5: Distributing to DAM, Web, and Artifacts ---');
    fs.copyFileSync(FINAL_OUTPUT_MP4, path.join(DAM_VIDEO_DIR, 'formtimer-short.mp4'));
    fs.copyFileSync(FINAL_OUTPUT_MP4, path.join(DAM_VIDEO_DIR, 'formtimer-master.mp4'));
    fs.copyFileSync(thumbFile, path.join(DAM_VIDEO_DIR, 'formtimer-thumbnail.png'));
    if (fs.existsSync(SOUNDTRACK_FILE)) {
        fs.copyFileSync(SOUNDTRACK_FILE, path.join(DAM_AUDIO_DIR, 'soundtrack.wav'));
    }
    fs.copyFileSync(HTML_FILE, path.join(DAM_STAGE_DIR, 'video.html'));

    if (fs.existsSync(WEB_ASSETS_DIR)) {
        fs.copyFileSync(FINAL_OUTPUT_MP4, path.join(WEB_ASSETS_DIR, 'formtimer-short.mp4'));
        fs.copyFileSync(thumbFile, path.join(WEB_ASSETS_DIR, 'formtimer-thumbnail.png'));
    }

    if (fs.existsSync(ARTIFACT_DIR)) {
        fs.copyFileSync(FINAL_OUTPUT_MP4, path.join(ARTIFACT_DIR, 'formtimer-short.mp4'));
        fs.copyFileSync(thumbFile, path.join(ARTIFACT_DIR, 'formtimer-thumbnail.png'));
    }

    fs.rmSync(TEMP_RECORD_DIR, { recursive: true, force: true });
    console.log('✅ ${FINAL_OUTPUT_MP4} successfully rendered, vaulted, and distributed!');
})();
