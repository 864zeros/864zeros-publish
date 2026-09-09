const fs = require('fs');
const path = require('path');

const PUBLISH_ROOT = path.resolve(__dirname, '..');
const LLC_ROOT = path.resolve('C:/dev/864zeros-llc');
const FACTORY = path.join(LLC_ROOT, 'LLC-DIV-3-FACTORY');
const GTM_VIDEOS = path.join(LLC_ROOT, 'LLC-DIV-4-GTM', 'videos');
const DAM_PRODUCTS = path.join(PUBLISH_ROOT, 'media', 'products');

const ADDONS = [
  { slug: 'snaplabel', factory: 'snapLabel' },
  { slug: 'choiceguard', factory: 'choiceGuard' },
  { slug: 'docwatermarker', factory: 'docWatermarker' },
  { slug: 'formtimer', factory: 'formTimer' },
  { slug: 'rowarchiver', factory: 'rowArchiver' },
  { slug: 'mailsyncshield', factory: 'mailSyncShield' },
  { slug: 'form2docx', factory: 'form2docx' },
  { slug: 'slidebuilder', factory: 'slideBuilder' },
  { slug: 'sheetsync', factory: 'sheetSync' },
  { slug: 'drivevault', factory: 'DriveVault' },
  { slug: 'approvalworkflow', factory: 'approvalWorkflow' },
  { slug: 'formnotifier', factory: 'formNotifier' },
  { slug: 'drivesweep', factory: 'driveSweep' },
  { slug: 'sheet2calendar', factory: 'sheet2Calendar' },
  { slug: 'drivedrop', factory: 'driveDrop' },
  { slug: 'formqr', factory: 'formQR' },
  { slug: 'sheet2webhook', factory: 'sheet2Webhook' },
  { slug: 'signroute', factory: 'signRoute' }
];

function copySafe(src, dest) {
  if (fs.existsSync(src)) {
    const parent = path.dirname(dest);
    if (!fs.existsSync(parent)) fs.mkdirSync(parent, { recursive: true });
    fs.copyFileSync(src, dest);
    return true;
  }
  return false;
}

function copyDir(srcDir, destDir) {
  if (!fs.existsSync(srcDir)) return 0;
  if (!fs.existsSync(destDir)) fs.mkdirSync(destDir, { recursive: true });
  let count = 0;
  for (const item of fs.readdirSync(srcDir)) {
    const s = path.join(srcDir, item);
    const d = path.join(destDir, item);
    if (fs.statSync(s).isFile()) {
      fs.copyFileSync(s, d);
      count++;
    }
  }
  return count;
}

console.log('=== Starting Full Sync of 18 Google Workspace Add-ons into Central DAM ===\n');

const stats = [];

for (const addon of ADDONS) {
  const targetDir = path.join(DAM_PRODUCTS, addon.slug);
  const iconsDir = path.join(targetDir, 'icons');
  const storeDir = path.join(targetDir, 'store');
  const audioDir = path.join(targetDir, 'audio');
  const stageDir = path.join(targetDir, 'stage');
  const videoDir = path.join(targetDir, 'video');
  const socialDir = path.join(targetDir, 'social');

  [iconsDir, storeDir, audioDir, stageDir, videoDir, socialDir].forEach(d => {
    if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });
  });

  let storeCopies = 0;
  let audioCopies = 0;
  let stageCopies = 0;
  let videoCopies = 0;

  // 1. Ingest Store Graphics from Factory
  const factoryStoreAssets = path.join(FACTORY, 'add-ons', addon.factory, 'store', 'assets');
  if (fs.existsSync(factoryStoreAssets)) {
    for (const file of fs.readdirSync(factoryStoreAssets)) {
      const srcFile = path.join(factoryStoreAssets, file);
      // Copy to store/
      fs.copyFileSync(srcFile, path.join(storeDir, file));
      // Copy to product root
      fs.copyFileSync(srcFile, path.join(targetDir, file));
      storeCopies++;

      // Copy icons/svgs to icons/
      if (file.includes('icon') || (!file.includes('-1') && !file.includes('-2') && !file.includes('-3') && !file.includes('promo'))) {
        fs.copyFileSync(srcFile, path.join(iconsDir, file));
      }
    }
  }

  // 2. Ingest Audio Stems (Master + Social)
  const videoAudioSrc = path.join(GTM_VIDEOS, addon.slug, 'audio');
  audioCopies += copyDir(videoAudioSrc, audioDir);

  const socialAudioSrc = path.join(GTM_VIDEOS, addon.slug, 'social_shorts', 'audio');
  audioCopies += copyDir(socialAudioSrc, audioDir);

  // 3. Ingest Stage Files
  const videoRoot = path.join(GTM_VIDEOS, addon.slug);
  const stageFiles = [
    { src: path.join(videoRoot, 'video.html'), dest: path.join(stageDir, 'video.html') },
    { src: path.join(videoRoot, 'generate_audio.py'), dest: path.join(stageDir, 'generate_audio.py') },
    { src: path.join(videoRoot, 'generate_music.py'), dest: path.join(stageDir, 'generate_music.py') },
    { src: path.join(videoRoot, 'render_video.cjs'), dest: path.join(stageDir, 'render_video.cjs') },
    { src: path.join(videoRoot, 'social_shorts', 'stage_pain.html'), dest: path.join(stageDir, 'stage_pain.html') },
    { src: path.join(videoRoot, 'social_shorts', 'stage_price.html'), dest: path.join(stageDir, 'stage_price.html') },
    { src: path.join(videoRoot, 'social_shorts', 'render_social_shorts.cjs'), dest: path.join(stageDir, 'render_social_shorts.cjs') },
    { src: path.join(videoRoot, 'social_shorts', 'audio', 'generate_social_audio.py'), dest: path.join(stageDir, 'generate_social_audio.py') }
  ];
  for (const sf of stageFiles) {
    if (copySafe(sf.src, sf.dest)) stageCopies++;
  }

  // 4. Ingest Master Video Deliverables
  const masterShort = path.join(videoRoot, `${addon.slug}-short.mp4`);
  const masterThumb = path.join(videoRoot, `${addon.slug}-thumbnail.png`);
  const genericThumb = path.join(videoRoot, 'thumbnail.png');

  if (fs.existsSync(masterShort)) {
    copySafe(masterShort, path.join(videoDir, `${addon.slug}-short.mp4`));
    copySafe(masterShort, path.join(videoDir, `${addon.slug}-master.mp4`));
    copySafe(masterShort, path.join(storeDir, `${addon.slug}-short.mp4`));
    copySafe(masterShort, path.join(storeDir, `${addon.slug}-master.mp4`));
    videoCopies++;
  }

  const thumbSrc = fs.existsSync(masterThumb) ? masterThumb : (fs.existsSync(genericThumb) ? genericThumb : null);
  if (thumbSrc) {
    copySafe(thumbSrc, path.join(videoDir, `${addon.slug}-thumbnail.png`));
    copySafe(thumbSrc, path.join(videoDir, 'thumbnail.png'));
    copySafe(thumbSrc, path.join(storeDir, `${addon.slug}-thumbnail.png`));
    copySafe(thumbSrc, path.join(iconsDir, `${addon.slug}-thumbnail.png`));
    copySafe(thumbSrc, path.join(targetDir, `${addon.slug}-thumbnail.png`));
  }

  // 5. Ingest Social Shorts Deliverables
  const socialRoot = path.join(videoRoot, 'social_shorts');
  const painVideo = path.join(socialRoot, `${addon.slug}-social-pain.mp4`);
  const priceVideo = path.join(socialRoot, `${addon.slug}-social-price.mp4`);
  const painThumb = path.join(socialRoot, `thumbnail-${addon.slug}-social-pain.png`);
  const priceThumb = path.join(socialRoot, `thumbnail-${addon.slug}-social-price.png`);

  if (fs.existsSync(painVideo)) {
    copySafe(painVideo, path.join(socialDir, `${addon.slug}-social-pain.mp4`));
    copySafe(painVideo, path.join(videoDir, `${addon.slug}-social-pain.mp4`));
    copySafe(painVideo, path.join(storeDir, `${addon.slug}-social-pain.mp4`));
    videoCopies++;
  }
  if (fs.existsSync(priceVideo)) {
    copySafe(priceVideo, path.join(socialDir, `${addon.slug}-social-price.mp4`));
    copySafe(priceVideo, path.join(videoDir, `${addon.slug}-social-price.mp4`));
    copySafe(priceVideo, path.join(storeDir, `${addon.slug}-social-price.mp4`));
    videoCopies++;
  }
  if (fs.existsSync(painThumb)) {
    copySafe(painThumb, path.join(socialDir, `thumbnail-${addon.slug}-social-pain.png`));
    copySafe(painThumb, path.join(videoDir, `thumbnail-${addon.slug}-social-pain.png`));
    copySafe(painThumb, path.join(storeDir, `thumbnail-${addon.slug}-social-pain.png`));
    copySafe(painThumb, path.join(iconsDir, `thumbnail-${addon.slug}-social-pain.png`));
    copySafe(painThumb, path.join(targetDir, `thumbnail-${addon.slug}-social-pain.png`));
  }
  if (fs.existsSync(priceThumb)) {
    copySafe(priceThumb, path.join(socialDir, `thumbnail-${addon.slug}-social-price.png`));
    copySafe(priceThumb, path.join(videoDir, `thumbnail-${addon.slug}-social-price.png`));
    copySafe(priceThumb, path.join(storeDir, `thumbnail-${addon.slug}-social-price.png`));
    copySafe(priceThumb, path.join(iconsDir, `thumbnail-${addon.slug}-social-price.png`));
    copySafe(priceThumb, path.join(targetDir, `thumbnail-${addon.slug}-social-price.png`));
  }

  stats.push({
    slug: addon.slug,
    storeAssets: storeCopies,
    audioStems: audioCopies,
    stageFiles: stageCopies,
    videoDeliverables: videoCopies
  });
}

console.log('--- Sync Summary ---');
console.table(stats);

// 6. Update index.json to VIDEO_COMPLETE for all 18 Google Workspace Add-ons
const indexJsonPath = path.join(PUBLISH_ROOT, 'index.json');
if (fs.existsSync(indexJsonPath)) {
  const indexData = JSON.parse(fs.readFileSync(indexJsonPath, 'utf8'));
  indexData._meta.generated = '2026-09-09';

  if (indexData.namespaces && indexData.namespaces['media/products'] && indexData.namespaces['media/products'].products_seeded) {
    let updatedCount = 0;
    for (const p of indexData.namespaces['media/products'].products_seeded) {
      if (ADDONS.some(a => a.slug === p.slug)) {
        p.status = 'VIDEO_COMPLETE';
        updatedCount++;
      }
    }
    console.log(`\n[OK] Updated ${updatedCount} add-on entries in index.json to VIDEO_COMPLETE`);
  }

  fs.writeFileSync(indexJsonPath, JSON.stringify(indexData, null, 2), 'utf8');
  console.log(`[OK] Saved updated ${indexJsonPath}`);
}

console.log('\n=== Central DAM Synchronization Complete ===');
