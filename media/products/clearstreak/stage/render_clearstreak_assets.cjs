const { chromium } = require('C:/dev/864zeros-4review/playwright-cli-mcp/node_modules/playwright');
const path = require('path');
const fs = require('fs');

const CHROME_PATH = 'C:/Program Files/Google/Chrome/Application/chrome.exe';

const SVG_PATH = 'C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/mobile/clearstreak/store/assets/clearstreak.svg';
const SCREENSHOTS_HTML = 'C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/mobile/clearstreak/store/store-screenshots.html';

const FACTORY_ASSETS = 'C:/dev/864zeros-llc/LLC-DIV-3-FACTORY/mobile/clearstreak/store/assets';
const PUBLISH_STORE = 'C:/dev/864zeros-publish/media/products/clearstreak/store';
const PUBLISH_ICONS = 'C:/dev/864zeros-publish/media/products/clearstreak/icons';
const WEB_ASSETS = 'C:/dev/864zeros-web/products/assets';

[FACTORY_ASSETS, PUBLISH_STORE, PUBLISH_ICONS, WEB_ASSETS].forEach(dir => {
  fs.mkdirSync(dir, { recursive: true });
});

async function main() {
  console.log('Launching Chrome to render authentic ClearStreak logo & product snapshots...');
  const browser = await chromium.launch({
    executablePath: CHROME_PATH,
    headless: true
  });

  const page = await browser.newPage({
    viewport: { width: 1280, height: 800 },
    deviceScaleFactor: 2 // Crisp high-DPI rendering
  });

  // 1. Render App Icon (512x512)
  console.log('Rendering 512x512 Logo...');
  const svgContent = fs.readFileSync(SVG_PATH, 'utf-8');
  await page.setContent(`
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        body { margin: 0; padding: 0; background: transparent; display: flex; align-items: center; justify-content: center; width: 512px; height: 512px; overflow: hidden; }
      </style>
    </head>
    <body>
      ${svgContent}
    </body>
    </html>
  `);

  await page.setViewportSize({ width: 512, height: 512 });
  const iconBuffer = await page.screenshot({ omitBackground: true });

  const iconFiles = ['clearstreak.png', 'store-icon.png'];
  for (const filename of iconFiles) {
    fs.writeFileSync(path.join(FACTORY_ASSETS, filename), iconBuffer);
    fs.writeFileSync(path.join(PUBLISH_STORE, filename), iconBuffer);
    fs.writeFileSync(path.join(PUBLISH_ICONS, filename), iconBuffer);
    fs.writeFileSync(path.join(WEB_ASSETS, filename), iconBuffer);
  }
  console.log('Logo rendered and distributed to all targets: clearstreak.png & store-icon.png');

  // Also copy SVG to targets
  fs.copyFileSync(SVG_PATH, path.join(PUBLISH_ICONS, 'clearstreak.svg'));
  fs.copyFileSync(SVG_PATH, path.join(WEB_ASSETS, 'clearstreak.svg'));

  // 2. Render Product Snapshots (1280x800)
  console.log('Loading store-screenshots.html...');
  await page.setViewportSize({ width: 1400, height: 2600 });
  await page.goto(`file://${SCREENSHOTS_HTML.replace(/\\/g, '/')}`, { waitUntil: 'networkidle' });

  const slides = [
    { id: 'slide-1', name: 'clearstreak-1.png' },
    { id: 'slide-2', name: 'clearstreak-2.png' },
    { id: 'slide-3', name: 'clearstreak-3.png' },
    { id: 'feature-graphic', name: 'feature-graphic.png' }
  ];

  for (const slide of slides) {
    console.log(`Capturing ${slide.name} from #${slide.id}...`);
    const element = await page.$(`#${slide.id}`);
    if (!element) {
      throw new Error(`Element #${slide.id} not found!`);
    }

    const buf = await element.screenshot();

    fs.writeFileSync(path.join(FACTORY_ASSETS, slide.name), buf);
    fs.writeFileSync(path.join(PUBLISH_STORE, slide.name), buf);
    fs.writeFileSync(path.join(WEB_ASSETS, slide.name), buf);
    console.log(`Saved ${slide.name} (${buf.length} bytes) to Factory, Publish, and Web.`);
  }

  await browser.close();
  console.log('Successfully rendered and distributed all ClearStreak assets!');
}

main().catch(err => {
  console.error('Fatal render error:', err);
  process.exit(1);
});
