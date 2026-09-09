const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BASE_DIR = path.resolve('C:/dev/864zeros-llc/LLC-DIV-4-GTM/videos/choiceguard/social_shorts');
const AUDIO_DIR = path.join(BASE_DIR, 'audio');
const TEMP_DIR = path.join(BASE_DIR, 'temp_record');
const DAM_DIR = path.resolve('C:/dev/864zeros-publish/media/products/choiceguard');
const DAM_SOCIAL_DIR = path.join(DAM_DIR, 'social');
const DAM_VIDEO_DIR = path.join(DAM_DIR, 'video');
const ARTIFACT_DIR = path.resolve('C:/Users/Jeff/.gemini/antigravity-cli/brain/3081b540-e7bd-4442-bb6d-a5242f385951');

fs.mkdirSync(DAM_SOCIAL_DIR, { recursive: true });
fs.mkdirSync(DAM_VIDEO_DIR, { recursive: true });

const SHORTS = [
    {
        name: 'choiceguard-social-pain',
        htmlFile: path.join(BASE_DIR, 'stage_pain.html'),
        soundtrackFile: path.join(AUDIO_DIR, 'soundtrack_pain.wav'),
        durationSec: 21.06
    },
    {
        name: 'choiceguard-social-price',
        htmlFile: path.join(BASE_DIR, 'stage_price.html'),
        soundtrackFile: path.join(AUDIO_DIR, 'soundtrack_price.wav'),
        durationSec: 23.89
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
    const fileUrl = `file:///${spec.htmlFile.replace(/\\/g, '/')}`;
    console.log(`[2/5] Navigating to: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'load' });

    if (page.evaluate) {
        await page.evaluate(async () => {
            if (document.fonts) await document.fonts.ready;
        });
    }

    await page.waitForTimeout(400);

    console.log('[3/5] Starting playback animation clock...');
    await page.evaluate(() => window.startPlayback());

    const recordMs = Math.ceil((spec.durationSec + 1.0) * 1000);
    console.log(`Recording animation for ${recordMs}ms (${(recordMs / 1000).toFixed(1)}s)...`);
    await page.waitForTimeout(recordMs);

    await page.close();
    await context.close();
    await browser.close();

    const videoFiles = fs.readdirSync(TEMP_DIR).filter(f => f.endsWith('.webm'));
    if (videoFiles.length === 0) {
        throw new Error('No recorded webm video found in ' + TEMP_DIR);
    }
    const rawWebm = path.join(TEMP_DIR, videoFiles[0]);

    console.log('[4/5] Muxing video and soundtrack into high-res MP4 via FFmpeg...');
    const outputMp4 = path.join(BASE_DIR, `${spec.name}.mp4`);
    const ffmpegCmd = [
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
        `"${outputMp4}"`
    ].join(' ');

    execSync(ffmpegCmd, { stdio: 'inherit' });
    console.log(`✓ MP4 rendered: ${outputMp4}`);

    // Extract thumbnail poster at 3.0s
    console.log('[5/5] Extracting poster thumbnail at 3.0s...');
    const thumbFile = path.join(BASE_DIR, `thumbnail-${spec.name}.png`);
    const thumbCmd = [
        'ffmpeg', '-y',
        '-ss', '3.0',
        '-i', `"${outputMp4}"`,
        '-frames:v', '1',
        '-q:v', '2',
        `"${thumbFile}"`
    ].join(' ');
    execSync(thumbCmd, { stdio: 'inherit' });
    console.log(`✓ Thumbnail extracted: ${thumbFile}`);

    // Copy to DAM and artifacts
    console.log('Distributing copies to DAM and artifact repository...');
    fs.copyFileSync(outputMp4, path.join(DAM_SOCIAL_DIR, `${spec.name}.mp4`));
    fs.copyFileSync(thumbFile, path.join(DAM_SOCIAL_DIR, `thumbnail-${spec.name}.png`));

    fs.copyFileSync(outputMp4, path.join(DAM_VIDEO_DIR, `${spec.name}.mp4`));
    fs.copyFileSync(thumbFile, path.join(DAM_VIDEO_DIR, `thumbnail-${spec.name}.png`));

    if (fs.existsSync(ARTIFACT_DIR)) {
        fs.copyFileSync(outputMp4, path.join(ARTIFACT_DIR, `${spec.name}.mp4`));
        fs.copyFileSync(thumbFile, path.join(ARTIFACT_DIR, `thumbnail-${spec.name}.png`));
    }
    console.log(`✓ Stored and tagged in DAM: ${path.join(DAM_SOCIAL_DIR, `${spec.name}.mp4`)}`);
    
    fs.rmSync(TEMP_DIR, { recursive: true, force: true });
}

(async () => {
    try {
        for (const s of SHORTS) {
            await renderShort(s);
        }
        console.log('\n======================================================');
        console.log('ALL CHOICEGUARD SOCIAL SHORTS SUCCESSFULLY RENDERED AND CATALOGED!');
        console.log('======================================================');
    } catch (err) {
        console.error('ERROR during render:', err);
        process.exit(1);
    }
})();
