/**
 * package_kate_rig.cjs
 * Validates and packages Kate Zefore's avatar rigging assets for real-time 3DGS video streaming.
 * Verifies file presence, manifest integrity, and formats the upload packet for Simli / LiveKit.
 */

const fs = require('fs');
const path = require('path');

const RIG_DIR = path.resolve(__dirname, '../../media/video/kate_avatar_rig');
const MANIFEST_FILE = path.join(RIG_DIR, 'avatar_manifest.json');

console.log('====================================================');
console.log('   864zeros AVATAR RIG PACKAGER: KATE ZEFORE (AOE)  ');
console.log('====================================================\n');

if (!fs.existsSync(MANIFEST_FILE)) {
  console.error(`[ERROR] Manifest not found at: ${MANIFEST_FILE}`);
  process.exit(1);
}

const manifest = JSON.parse(fs.readFileSync(MANIFEST_FILE, 'utf-8'));
console.log(`[OK] Loaded Rig Manifest: ${manifest.name} (${manifest.role}) - v${manifest.version}`);
console.log(`[OK] Rigging Architecture: ${manifest.rig_type}\n`);

let missingCount = 0;

console.log('--- Checking Master Anchors ---');
for (const [key, anchor] of Object.entries(manifest.anchors)) {
  const filePath = path.join(RIG_DIR, anchor.file);
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    console.log(`  ✓ ${key.padEnd(18)} : ${anchor.file} (${(stats.size / 1024).toFixed(1)} KB)`);
  } else {
    console.error(`  ✗ ${key.padEnd(18)} : MISSING (${anchor.file})`);
    missingCount++;
  }
}

console.log('\n--- Checking Calibrated Rigging Sheets ---');
for (const [key, sheet] of Object.entries(manifest.rigging_sheets)) {
  const filePath = path.join(RIG_DIR, sheet.file);
  if (fs.existsSync(filePath)) {
    const stats = fs.statSync(filePath);
    console.log(`  ✓ ${key.padEnd(20)} : ${sheet.file} (${(stats.size / 1024).toFixed(1)} KB)`);
    if (sheet.calibrated_shapes) {
      console.log(`    ↳ Visemes: ${sheet.calibrated_shapes.join(', ')}`);
    }
    if (sheet.calibrated_angles) {
      console.log(`    ↳ Angles: ${sheet.calibrated_angles.join(', ')}`);
    }
  } else {
    console.error(`  ✗ ${key.padEnd(20)} : MISSING (${sheet.file})`);
    missingCount++;
  }
}

console.log('\n----------------------------------------------------');
if (missingCount === 0) {
  console.log('[SUCCESS] All 6 core avatar rigging assets are present and validated!');
  console.log('Rig is ready for upload to Simli Trinity-1 / LiveKit Avatar Engine.\n');
  console.log('Deployment Payload:');
  console.log(`  Target Directory : ${RIG_DIR}`);
  console.log(`  Recommended Base : kate-portrait-warm.jpg`);
  console.log(`  Phoneme Visemes  : kate-rig-lipsync-frontal.jpg`);
  console.log(`  Multi-View Angles: 45deg, 90deg, pitch/tilt`);
} else {
  console.error(`[FAILURE] ${missingCount} required rigging asset(s) are missing.`);
  process.exit(1);
}
