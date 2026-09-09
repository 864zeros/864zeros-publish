const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const BASE_DIR = path.resolve('C:/dev/864zeros-llc/LLC-DIV-4-GTM/videos/docwatermarker/social_shorts');
const AUDIO_DIR = path.join(BASE_DIR, 'audio');
const TEMP_DIR = path.join(BASE_DIR, 'temp_record');
const DAM_DIR = path.resolve('C:/dev/864zeros-publish/media/products/docwatermarker');
const DAM_SOCIAL_DIR = path.join(DAM_DIR, 'social');
const DAM_VIDEO_DIR = path.join(DAM_DIR, 'video');
const ARTIFACT_DIR = path.resolve('C:/Users/Jeff/.gemini/antigravity-cli/brain/3081b540-e7bd-4442-bb6d-a5242f385951');

fs.mkdirSync(DAM_SOCIAL_DIR, { recursive: true });
fs.mkdirSync(DAM_VIDEO_DIR, { recursive: true });

const SHORTS = [
    {
        name: 'docwatermarker-social-pain',
        htmlFile: path.join(BASE_DIR, 'stage_pain.html'),
        soundtrackFile: path.join(AUDIO_DIR, 'soundtrack_pain.wav'),
        durationSec: 23.29
    },
    {
        name: 'docwatermarker-social-price',
        htmlFile: path.join(BASE_DIR, 'stage_price.html'),
        soundtrackFile: path.join(AUDIO_DIR, 'soundtrack_price.wav'),
        durationSec: 23.94
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
    const targetUrl = 'file:///' + spec.htmlFile.replace(/\\/g, '/');
    console.log(`[2/5] Navigating to: ${targetUrl}`);
    await page.goto(targetUrl, { waitUntil: 'load' });
    await page.evaluate(async () => {
        if (document.fonts) await document.fonts.ready;
    });
    await page.waitForTimeout(500);

    console.log(`[3/5] Triggering kinetic stage animation...`);
    await page.evaluate(() => window.startPlayback());

    const recordMs = Math.ceil((spec.durationSec + 1.2) * 1000);
    console.log(`Recording for ${recordMs}ms...`);
    await page.waitForTimeout(recordMs);

    await page.close();
    await context.close();
    await browser.close();

    const videoFiles = fs.readdirSync(TEMP_DIR).filter(f => f.endsWith('.webm'));
    if (videoFiles.length === 0) throw new Error(`No webm found for ${spec.name}`);
    const rawWebm = path.join(TEMP_DIR, videoFiles[0]);

    console.log(`[4/5] Muxing video with mastered audio (${spec.soundtrackFile})...`);
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
    console.log(`Master Short created: ${outputMp4}`);

    console.log(`[5/5] Extracting poster thumbnail at 3.0s...`);
    const thumbPath = path.join(BASE_DIR, `thumbnail-${spec.name}.png`);
    const thumbCmd = [
        'ffmpeg', '-y',
        '-ss', '3.0',
        '-i', `"${outputMp4}"`,
        '-frames:v', '1',
        '-update', '1',
        `"${thumbPath}"`
    ].join(' ');
    execSync(thumbCmd, { stdio: 'inherit' });

    // Distribute to DAM & Artifacts
    console.log(`Distributing ${spec.name} to Central DAM & Brain Artifacts...`);
    fs.copyFileSync(outputMp4, path.join(DAM_SOCIAL_DIR, `${spec.name}.mp4`));
    fs.copyFileSync(thumbPath, path.join(DAM_SOCIAL_DIR, `thumbnail-${spec.name}.png`));
    if (fs.existsSync(ARTIFACT_DIR)) {
        fs.copyFileSync(outputMp4, path.join(ARTIFACT_DIR, `${spec.name}.mp4`));
        fs.copyFileSync(thumbPath, path.join(ARTIFACT_DIR, `thumbnail-${spec.name}.png`));
    }

    fs.rmSync(TEMP_DIR, { recursive: true, force: true });
    console.log(`✅ ${spec.name} complete!`);
}

(async () => {
    try {
        for (const short of SHORTS) {
            await renderShort(short);
        }
        console.log(`\n🎉 All Tier 1 Social Shorts successfully rendered and vaulted!`);
    } catch (err) {
        console.error('Fatal rendering error:', err);
        process.exit(1);
    }
})();
