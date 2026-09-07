const fs = require('fs');
const path = require('path');

const PUBLISH_ROOT = path.resolve(__dirname, '..');
const LLC_ROOT = path.resolve('C:/dev/864zeros-llc');
const FACTORY = path.join(LLC_ROOT, 'LLC-DIV-3-FACTORY');
const GTM_VIDEOS = path.join(LLC_ROOT, 'LLC-DIV-4-GTM', 'videos');

const DAM_PRODUCTS = path.join(PUBLISH_ROOT, 'media', 'products');

// 1. Lock the 6 product lines into PRODUCT_TAXONOMY.json
const TAXONOMY = {
  "version": "1.0",
  "locked_date": "2026-09-06",
  "doctrine": "The 6 Commercial Form Factors of 864zeros",
  "categories": {
    "browser-extensions": {
      "title": "Browser Extensions",
      "targets": ["Chrome", "Safari", "Edge", "Firefox", "Brave"],
      "manifest_standard": "Manifest V3",
      "primary_store": "Chrome Web Store / Mac App Store / Edge Add-ons"
    },
    "google-workspace-addons": {
      "title": "Google Workspace Add-ons",
      "targets": ["Google Docs", "Google Sheets", "Google Drive", "Google Slides"],
      "manifest_standard": "appsscript.json",
      "primary_store": "Google Workspace Marketplace"
    },
    "mobile-apps": {
      "title": "Mobile Applications",
      "targets": ["iOS", "Android"],
      "stack": "Native (Flutter / Kotlin / Swift) and Wrapped Hybrids",
      "primary_store": "Google Play Store / Apple App Store"
    },
    "micro-saas": {
      "title": "Micro-SaaS (Web Applications)",
      "targets": ["Modern Web", "Mobile Web"],
      "stack": "Local-first React/TypeScript/Vite/PWA (Wrap-ready via Capacitor/Tauri)",
      "primary_store": "864zeros.com Cloudflare Pages"
    },
    "desktop-apps": {
      "title": "Desktop Applications",
      "targets": ["Windows", "macOS", "Linux"],
      "stack": "FastAPI + React / Tauri / Electron (Local AI & System engines)",
      "primary_store": "Direct Download / Microsoft Store / Mac App Store"
    },
    "agentic-developer-tools": {
      "title": "Agentic & Developer Tools",
      "targets": ["Claude", "Antigravity", "AI Coding Agents", "Terminal"],
      "stack": "Model Context Protocol (MCP) servers, Claude Code plugins, CLI tools, Skills",
      "primary_store": "GitHub / npm / PyPI / MCP Registries"
    }
  }
};

const taxonomyFile = path.join(PUBLISH_ROOT, 'PRODUCT_TAXONOMY.json');
fs.writeFileSync(taxonomyFile, JSON.stringify(TAXONOMY, null, 2), 'utf8');
console.log(`[OK] Locked product line taxonomy written to: ${taxonomyFile}`);

// 2. Discover all product candidates across LLC-DIV-3-FACTORY
const candidates = [
  // Extensions
  { slug: 'autoorganize-ytm', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'autoorganize-ytm') },
  { slug: 'link-later', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'link-later') },
  { slug: 'tab-stasher', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'tab-stasher') },
  { slug: 'migration-pilot', altSlug: 'vaultpilot', type: 'browser-extensions', pillar: '864-Flux', factoryPath: path.join(FACTORY, 'extensions', 'migration-pilot') },
  { slug: '864z-chronicle', type: 'browser-extensions', pillar: '864-Flux', factoryPath: path.join(FACTORY, 'extensions', '864z-chronicle') },
  { slug: 'DataNap', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'DataNap') },
  { slug: 'Signal2Noise', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'Signal2Noise') },
  { slug: 'Time2Focus', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'Time2Focus') },
  { slug: 'TuneOut2FocusIn', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'TuneOut2FocusIn') },
  { slug: 'who-is-watching', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'who-is-watching') },
  { slug: 'oia-focus-note', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'oia-focus-note') },
  { slug: 'oia-focus-wall', type: 'browser-extensions', pillar: 'OIA', factoryPath: path.join(FACTORY, 'extensions', 'oia-focus-wall') },
  { slug: 'clipboard', type: 'browser-extensions', pillar: '864-Flux', factoryPath: path.join(FACTORY, 'extensions', 'clipboard') },
  { slug: 'Bible-Insight', type: 'browser-extensions', pillar: 'FHG', factoryPath: path.join(FACTORY, 'extensions', 'Bible-Insight') },
  // Desktop
  { slug: 'omniclip', type: 'desktop-apps', pillar: 'CMM', factoryPath: path.join(FACTORY, 'desktop', 'omniclip') },
  // Mobile
  { slug: 'clearstreak', type: 'mobile-apps', pillar: 'FHG', factoryPath: path.join(FACTORY, 'mobile', 'clearstreak') }
];

console.log(`\n--- Seeding ${candidates.length} Products into DAM (media/products/) ---`);

const scorecard = [];

for (const prod of candidates) {
  const targetDir = path.join(DAM_PRODUCTS, prod.slug);
  const iconsDir = path.join(targetDir, 'icons');
  const storeDir = path.join(targetDir, 'store');
  const videoDir = path.join(targetDir, 'video');
  const socialDir = path.join(targetDir, 'social');

  [iconsDir, storeDir, videoDir, socialDir].forEach(d => fs.mkdirSync(d, { recursive: true }));

  let iconCount = 0;
  let storeCount = 0;
  let videoCount = 0;

  // Ingest icons
  const srcIcons = path.join(prod.factoryPath, 'icons');
  if (fs.existsSync(srcIcons)) {
    for (const file of fs.readdirSync(srcIcons)) {
      if (file.endsWith('.png') || file.endsWith('.svg')) {
        fs.copyFileSync(path.join(srcIcons, file), path.join(iconsDir, file));
        iconCount++;
      }
    }
  }

  // Ingest store assets
  const srcStoreAssets = path.join(prod.factoryPath, 'store', 'assets');
  if (fs.existsSync(srcStoreAssets)) {
    for (const file of fs.readdirSync(srcStoreAssets)) {
      fs.copyFileSync(path.join(srcStoreAssets, file), path.join(storeDir, file));
      storeCount++;
      // If store has the master icon, also copy to icons/
      if (file.includes('icon') || file.endsWith('.png') && !file.includes('-1') && !file.includes('-2') && !file.includes('-3') && !file.includes('screenshot')) {
        fs.copyFileSync(path.join(srcStoreAssets, file), path.join(iconsDir, file));
        iconCount++;
      }
    }
  }

  // Check fallback root assets/ (e.g. Bible-Insight, clipboard)
  const srcRootAssets = path.join(prod.factoryPath, 'assets');
  if (fs.existsSync(srcRootAssets) && storeCount === 0) {
    for (const file of fs.readdirSync(srcRootAssets)) {
      fs.copyFileSync(path.join(srcRootAssets, file), path.join(storeDir, file));
      storeCount++;
    }
  }

  // Ingest Video if available (AutoOrganize YTM)
  if (prod.slug === 'autoorganize-ytm') {
    const srcVideoShort = path.join(GTM_VIDEOS, 'autoorganize-ytm', 'autoorganize-ytm-short.mp4');
    const srcThumb = path.join(GTM_VIDEOS, 'autoorganize-ytm', 'thumbnail.png');
    if (fs.existsSync(srcVideoShort)) {
      fs.copyFileSync(srcVideoShort, path.join(videoDir, 'autoorganize-ytm-short.mp4'));
    }
    if (fs.existsSync(srcThumb)) {
      fs.copyFileSync(srcThumb, path.join(videoDir, 'thumbnail.png'));
    }
  }

  // Count videos in videoDir
  if (fs.existsSync(videoDir)) {
    videoCount = fs.readdirSync(videoDir).filter(f => !f.startsWith('.')).length;
  }

  // Read product.json if available
  let meta = {
    slug: prod.slug,
    category: prod.type,
    pillar: prod.pillar,
    ingested_at: new Date().toISOString()
  };

  const productJsonPath = path.join(prod.factoryPath, 'store', 'product.json');
  if (fs.existsSync(productJsonPath)) {
    try {
      const parsed = JSON.parse(fs.readFileSync(productJsonPath, 'utf8'));
      meta = { ...meta, ...parsed };
    } catch(e) {}
  }

  fs.writeFileSync(path.join(targetDir, 'manifest.json'), JSON.stringify(meta, null, 2), 'utf8');

  scorecard.push({
    slug: prod.slug,
    category: prod.type,
    pillar: prod.pillar,
    icons: iconCount,
    store: storeCount,
    video: videoCount,
    status: (iconCount > 0 && storeCount > 0) ? (videoCount > 0 ? 'VIDEO_COMPLETE' : 'MEDIA_READY') : 'PARTIAL'
  });

  console.log(`✓ Seeded ${prod.slug}: ${iconCount} icons, ${storeCount} store assets, ${videoCount} video assets`);
}

// 3. Update index.json in 864zeros-publish
const indexJsonPath = path.join(PUBLISH_ROOT, 'index.json');
const indexData = JSON.parse(fs.readFileSync(indexJsonPath, 'utf8'));

indexData.namespaces['media/products'] = {
  kind: "dam_products",
  title: "864zeros Central Product Asset Vault (DAM)",
  docs: "media/MEDIA_HOUSE.md",
  taxonomy: "PRODUCT_TAXONOMY.json",
  total_products: candidates.length,
  products_seeded: scorecard.map(s => ({
    slug: s.slug,
    category: s.category,
    pillar: s.pillar,
    status: s.status,
    vault: `media/products/${s.slug}/`
  }))
};

if (indexData.namespaces.media && indexData.namespaces.media.departments) {
  indexData.namespaces.media.departments.products = "media/products/ (canonical icons, store screenshots, promo tiles, 9:16 video shorts)";
}

fs.writeFileSync(indexJsonPath, JSON.stringify(indexData, null, 2), 'utf8');
console.log(`\n[OK] Registered 'media/products' in ${indexJsonPath}`);

// 4. Output Summary Table
console.log('\n============================================================');
console.log('       864ZEROS DAM — INITIAL FLEET SEED SCORECARD         ');
console.log('============================================================');
console.table(scorecard);
