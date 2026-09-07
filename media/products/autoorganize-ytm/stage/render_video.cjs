const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const VIDEO_DIR = path.resolve('C:/dev/864zeros-llc/LLC-DIV-4-GTM/videos/autoorganize-ytm');
const TEMP_RECORD_DIR = path.join(VIDEO_DIR, 'temp_record');
const HTML_FILE = path.join(VIDEO_DIR, 'video.html');
const SOUNDTRACK_FILE = path.join(VIDEO_DIR, 'audio', 'soundtrack.wav');
const FINAL_OUTPUT_MP4 = path.join(VIDEO_DIR, 'autoorganize-ytm-short.mp4');
const WEB_OUTPUT_MP4 = path.resolve('C:/dev/864zeros-web/products/assets/autoorganize-ytm-short.mp4');
const ARTIFACT_DIR = path.resolve('C:/Users/Jeff/.gemini/antigravity-cli/brain/3081b540-e7bd-4442-bb6d-a5242f385951');
const ARTIFACT_MP4 = path.join(ARTIFACT_DIR, 'autoorganize-ytm-short.mp4');

const TOTAL_DURATION_SEC = 56.89;

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

    console.log(`--- Step 3: Navigating to video stage: ${HTML_FILE} ---`);
    await page.goto(`file:///${HTML_FILE.replace(/\\/g, '/')}`, { waitUntil: 'load' });

    // Wait for fonts to be completely ready
    await page.evaluate(async () => {
        if (document.fonts) {
            await document.fonts.ready;
        }
    });

    // Small warmup pause
    await page.waitForTimeout(500);

    console.log('--- Step 4: Starting playback animation clock ---');
    await page.evaluate(() => window.startPlayback());

    // Record for the total duration plus a brief cushion
    const waitMs = Math.ceil((TOTAL_DURATION_SEC + 1.2) * 1000);
    console.log(`Recording animation for ${waitMs}ms (${(waitMs / 1000).toFixed(1)}s)...`);
    await page.waitForTimeout(waitMs);

    console.log('--- Step 5: Closing page and browser to finalize WebM video ---');
    await page.close();
    await context.close();
    await browser.close();

    const videoFiles = fs.readdirSync(TEMP_RECORD_DIR).filter(f => f.endsWith('.webm'));
    if (videoFiles.length === 0) {
        throw new Error('No recorded webm video file found in ' + TEMP_RECORD_DIR);
    }
    const rawWebm = path.join(TEMP_RECORD_DIR, videoFiles[0]);
    console.log(`Raw video recorded: ${rawWebm}`);

    console.log('--- Step 6: Muxing with soundtrack into high-res MP4 via FFmpeg ---');
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

    // Step 7: Distribute copies
    console.log('--- Step 7: Distributing copies to web assets and artifact dir ---');
    fs.copyFileSync(FINAL_OUTPUT_MP4, WEB_OUTPUT_MP4);
    console.log(`Copied to Web assets: ${WEB_OUTPUT_MP4}`);

    if (fs.existsSync(ARTIFACT_DIR)) {
        fs.copyFileSync(FINAL_OUTPUT_MP4, ARTIFACT_MP4);
        console.log(`Copied to Artifact dir: ${ARTIFACT_MP4}`);
    }

    console.log('--- COMPLETE: Product Video Short is ready! ---');
})();
