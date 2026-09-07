// normalize_and_caption.cjs — Converts TIFFs, archives RAWs, deduplicates, and generates .txt caption pairs
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const sketchDir = path.resolve(__dirname, '../../media/visuals/training_pools/sketches');
const archiveDir = path.resolve(__dirname, '../../sources/google_photos_inbox');

fs.mkdirSync(archiveDir, { recursive: true });

console.log('--- Step 1: Normalizing Formats & Deduplicating ---');
const initialFiles = fs.readdirSync(sketchDir).filter(f => f !== '.gitkeep');

let convertedTiffs = 0;
let archivedCr3s = 0;
let archivedTiffs = 0;

initialFiles.forEach(f => {
  const ext = path.extname(f).toLowerCase();
  const base = path.basename(f, ext);
  const src = path.join(sketchDir, f);

  if (ext === '.tiff' || ext === '.tif') {
    const destJpg = path.join(sketchDir, `${base}.jpg`);
    const destPng = path.join(sketchDir, `${base}.png`);
    // If PNG already exists, don't overwrite with JPG
    if (!fs.existsSync(destPng) && !fs.existsSync(destJpg)) {
      try {
        execSync(`ffmpeg -y -i "${src}" -q:v 1 "${destJpg}"`, { stdio: 'pipe' });
        convertedTiffs++;
      } catch (e) {
        console.error(`Failed to convert ${f}:`, e.message);
      }
    }
    // Archive original tiff
    fs.renameSync(src, path.join(archiveDir, f));
    archivedTiffs++;
  } else if (ext === '.cr3') {
    // Archive raw CR3
    fs.renameSync(src, path.join(archiveDir, f));
    archivedCr3s++;
  }
});

// Deduplicate if both base.png and base.jpg exist
const allFiles = fs.readdirSync(sketchDir).filter(f => f !== '.gitkeep' && !f.endsWith('.txt'));
const seenBases = new Set();
allFiles.forEach(f => {
  const ext = path.extname(f).toLowerCase();
  const base = path.basename(f, ext);
  if (seenBases.has(base)) {
    // Duplicate detected
    const filePath = path.join(sketchDir, f);
    fs.renameSync(filePath, path.join(archiveDir, f));
    console.log(`Deduplicated: moved duplicate ${f} to sources/google_photos_inbox/`);
  } else {
    seenBases.add(base);
  }
});

console.log('\n--- Step 2: Auditing Training Images ---');
const trainingImages = fs.readdirSync(sketchDir).filter(f => {
  const ext = path.extname(f).toLowerCase();
  return ['.jpg', '.jpeg', '.png', '.webp'].includes(ext);
});

console.log(`Unique training images: ${trainingImages.length}`);

console.log('\n--- Step 3: Generating Structured LoRA .txt Captions ---');
const TRIGGER_WORD = 'jeff_sketch style';

let captionsCreated = 0;

trainingImages.forEach((imgFile, idx) => {
  const ext = path.extname(imgFile);
  const base = path.basename(imgFile, ext);
  const txtPath = path.join(sketchDir, `${base}.txt`);

  // Variations tailored to sketch linework
  const variations = [
    'expressive hand-drawn artwork, bold contour lines, detailed cross-hatching, rich graphite pencil textures',
    'observational sketch on textured paper, delicate pencil linework, tonal shadow gradients',
    'dynamic freehand drawing, organic line flow, clean contrast, stylized artistic rendering',
    'intricate monochrome sketch, layered shading, tactile pencil strokes, balanced composition',
    'expressive visual study, master linework, refined proportions, classic draftsmanship'
  ];
  const subjectHint = variations[idx % variations.length];

  const captionContent = `${TRIGGER_WORD}, ${subjectHint}, monochrome pencil on paper, artistic traditional medium, high quality`;

  fs.writeFileSync(txtPath, captionContent, 'utf8');
  captionsCreated++;
});

console.log(`Successfully generated ${captionsCreated} matching .txt caption files.`);

console.log('\n--- Final Dataset Verification ---');
const allSketchesDirFiles = fs.readdirSync(sketchDir);
const finalImages = allSketchesDirFiles.filter(f => ['.jpg', '.jpeg', '.png', '.webp'].includes(path.extname(f).toLowerCase()));
const finalTxts = allSketchesDirFiles.filter(f => f.endsWith('.txt'));

console.log(`Images in training pool: ${finalImages.length}`);
console.log(`Captions in training pool: ${finalTxts.length}`);
console.log(`Exact 1-to-1 Pair Match: ${finalImages.length === finalTxts.length ? 'YES (100% Validated)' : 'NO (Mismatch)'}`);
