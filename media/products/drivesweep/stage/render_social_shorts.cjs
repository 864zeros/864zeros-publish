const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BASE_DIR = path.resolve('C:/dev/864zeros-llc/LLC-DIV-4-GTM/videos/drivesweep/social_shorts');
const AUDIO_DIR = path.join(BASE_DIR, 'audio');
const TEMP_DIR = path.join(BASE_DIR, 'temp_record');
const DAM_DIR = path.resolve('C:/dev/864zeros-publish/media/products/drivesweep');
const DAM_SOCIAL_DIR = path.join(DAM_DIR, 'social');
const DAM_VIDEO_DIR = path.join(DAM_DIR, 'video');
const WEB_ASSETS_DIR = path.resolve('C:/dev/864zeros-web/products/assets');
const ARTIFACT_DIR = path.resolve('C:/Users/Jeff/.gemini/antigravity-cli/brain/b339e8b3-edee-40f3-a2c6-86edd2eb2418');

fs.mkdirSync(DAM_SOCIAL_DIR, { recursive: true });
fs.mkdirSync(DAM_VIDEO_DIR, { recursive: true });
if (fs.existsSync(WEB_ASSETS_DIR)) {
    fs.mkdirSync(WEB_ASSETS_DIR, { recursive: true });
}

const SHORTS = [
    {
        name: 'drivesweep-social-pain',
        htmlFile: path.join(BASE_DIR, 'stage_pain.html'),
        soundtrackFile: path.join(AUDIO_DIR, 'soundtrack_pain.wav'),
        durationSec: 24.43
    },
    {
        name: 'drivesweep-social-price',
        htmlFile: path.join(BASE_DIR, 'stage_price.html'),
        soundtrackFile: path.join(AUDIO_DIR, 'soundtrack_price.wav'),
        durationSec: 26.14
    }
];

async function renderShort(spec) {
    console.log(`\n======================================================`);
    console.log(`Rendering Social Short: ${spec.name} (${spec.durationSec}s)`);
    console.log(`======================================================`);

    if (fs.existsSync(TEMP_DIR)) {
        fs.rmSync(TEMP_DIR, { recursive: true, force: true });
    }
    fs.mkdirSync(TEMP_DIR, { recursive: true });

    console.log('[1/5] Launching Chrome headless (1080x1920)...');
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
            dir: TEMP_DIR,
            size: { width: 1080, height: 1920 }
        },
        viewport: { width: 1080, height: 1920 },
        deviceScaleFactor: 1
    });

    const page = await context.newPage();
    const fileUrl = 'file:///' + spec.htmlFile.replace(/\\/g, '/');
    console.log(`[2/5] Navigating to: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'load' });
    await page.evaluate(async () => {
        if (document.fonts) await document.fonts.ready;
    });
    await page.waitForTimeout(400);

    console.log(`[3/5] Starting playback and recording for ${(spec.durationSec + 1.2).toFixed(1)}s...`);
    await page.evaluate(() => window.startPlayback());
    const waitMs = Math.ceil((spec.durationSec + 1.2) * 1000);
    await page.waitForTimeout(waitMs);

    await page.close();
    await context.close();
    await browser.close();

    const videoFiles = fs.readdirSync(TEMP_DIR).filter(f => f.endsWith('.webm'));
    if (videoFiles.length === 0) throw new Error('No webm video recorded!');
    const rawWebm = path.join(TEMP_DIR, videoFiles[0]);

    const finalMp4 = path.join(BASE_DIR, `${spec.name}.mp4`);
    console.log(`[4/5] Muxing video with soundtrack via FFmpeg -> ${finalMp4}...`);
    const muxCmd = [
        'ffmpeg', '-y',
        '-i', `"${rawWebm}"`,
        '-i', `"${spec.soundtrackFile}"`,
        '-vf', 'fps=30',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-shortest',
        `"${finalMp4}"`
    ].join(' ');
    execSync(muxCmd, { stdio: 'inherit' });

    console.log('[5/5] Extracting thumbnail & distributing assets...');
    const thumbFile = path.join(BASE_DIR, `thumbnail-${spec.name}.png`);
    const thumbCmd = [
        'ffmpeg', '-y',
        '-ss', '3.0',
        '-i', `"${finalMp4}"`,
        '-frames:v', '1',
        '-q:v', '2',
        `"${thumbFile}"`
    ].join(' ');
    execSync(thumbCmd, { stdio: 'inherit' });

    fs.copyFileSync(finalMp4, path.join(DAM_SOCIAL_DIR, `${spec.name}.mp4`));
    fs.copyFileSync(thumbFile, path.join(DAM_SOCIAL_DIR, `thumbnail-${spec.name}.png`));

    if (fs.existsSync(WEB_ASSETS_DIR)) {
        fs.copyFileSync(finalMp4, path.join(WEB_ASSETS_DIR, `${spec.name}.mp4`));
        fs.copyFileSync(thumbFile, path.join(WEB_ASSETS_DIR, `thumbnail-${spec.name}.png`));
    }

    if (fs.existsSync(ARTIFACT_DIR)) {
        fs.copyFileSync(finalMp4, path.join(ARTIFACT_DIR, `${spec.name}.mp4`));
        fs.copyFileSync(thumbFile, path.join(ARTIFACT_DIR, `thumbnail-${spec.name}.png`));
    }

    fs.rmSync(TEMP_DIR, { recursive: true, force: true });
    console.log(`✅ ${spec.name} complete: ${finalMp4}`);
}

(async () => {
    try {
        for (const spec of SHORTS) {
            await renderShort(spec);
        }
        console.log('\n🎉 ALL DRIVESWEEP LOCAL SOCIAL SHORTS SUCCESSFULLY RENDERED & DISTRIBUTED!');
    } catch (err) {
        console.error('Fatal render error:', err);
        process.exit(1);
    }
})();
