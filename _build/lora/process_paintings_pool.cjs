// process_paintings_pool.cjs — Normalizes, converts TIFF/HEIC/CR3, deduplicates, and generates .txt caption pairs for paintings
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const paintingsDir = path.resolve(__dirname, '../../media/visuals/training_pools/paintings');
const archiveDir = path.resolve(__dirname, '../../sources/google_photos_inbox');

fs.mkdirSync(archiveDir, { recursive: true });

console.log('=== Step 1: Format Normalization & Previews Extraction ===');
const initialFiles = fs.readdirSync(paintingsDir).filter(f => f !== '.gitkeep');

let convertedTiffs = 0;
let convertedHeics = 0;
let extractedCr3s = 0;
let archivedRaws = 0;

initialFiles.forEach(f => {
  const ext = path.extname(f).toLowerCase();
  const base = path.basename(f, ext);
  const src = path.join(paintingsDir, f);

  if (ext === '.tiff' || ext === '.tif') {
    const destJpg = path.join(paintingsDir, `${base}.jpg`);
    if (!fs.existsSync(destJpg)) {
      try {
        execSync(`ffmpeg -y -i "${src}" -q:v 1 "${destJpg}"`, { stdio: 'pipe' });
        convertedTiffs++;
        console.log(`Converted TIFF -> JPG: ${base}.jpg`);
      } catch (e) {
        console.error(`Failed to convert TIFF ${f}:`, e.message);
      }
    }
    fs.renameSync(src, path.join(archiveDir, f));
    archivedRaws++;
  } else if (ext === '.heic') {
    const destJpg = path.join(paintingsDir, `${base}.jpg`);
    if (!fs.existsSync(destJpg)) {
      try {
        execSync(`ffmpeg -y -i "${src}" -update 1 -frames:v 1 -q:v 1 "${destJpg}"`, { stdio: 'pipe' });
        convertedHeics++;
        console.log(`Converted HEIC -> JPG: ${base}.jpg`);
      } catch (e) {
        console.error(`Failed to convert HEIC ${f}:`, e.message);
      }
    }
    fs.renameSync(src, path.join(archiveDir, f));
    archivedRaws++;
  } else if (ext === '.cr3') {
    const destJpg = path.join(paintingsDir, `${base}.jpg`);
    if (!fs.existsSync(destJpg)) {
      // Extract largest embedded JPEG stream
      const buf = fs.readFileSync(src);
      let foundJpegs = [];
      for (let i = 0; i < buf.length - 4; i++) {
        if (buf[i] === 0xFF && buf[i+1] === 0xD8 && buf[i+2] === 0xFF) {
          for (let j = i + 1000; j < buf.length - 1; j++) {
            if (buf[j] === 0xFF && buf[j+1] === 0xD9) {
              const length = (j + 2) - i;
              foundJpegs.push({ start: i, end: j + 2, length });
              break;
            }
          }
        }
      }
      foundJpegs.sort((a, b) => b.length - a.length);
      if (foundJpegs.length > 0 && foundJpegs[0].length > 10000) {
        const largest = foundJpegs[0];
        fs.writeFileSync(destJpg, buf.subarray(largest.start, largest.end));
        extractedCr3s++;
        console.log(`Extracted preview from CR3 -> JPG: ${base}.jpg (${(largest.length / 1024).toFixed(1)} KB)`);
      }
    }
    fs.renameSync(src, path.join(archiveDir, f));
    archivedRaws++;
  }
});

console.log(`\nSummary of conversions:`);
console.log(` - Converted TIFFs: ${convertedTiffs}`);
console.log(` - Converted HEICs: ${convertedHeics}`);
console.log(` - Extracted CR3 previews: ${extractedCr3s}`);
console.log(` - Archived raw files to sources/google_photos_inbox/: ${archivedRaws}`);

console.log('\n=== Step 2: Deduplication ===');
const currentFiles = fs.readdirSync(paintingsDir).filter(f => f !== '.gitkeep' && !f.endsWith('.txt'));
const seenBases = new Map();

currentFiles.forEach(f => {
  const ext = path.extname(f).toLowerCase();
  const base = path.basename(f, ext);
  if (seenBases.has(base)) {
    const existingFile = seenBases.get(base);
    const existingExt = path.extname(existingFile).toLowerCase();
    // Keep JPG/PNG over others or keep larger file
    const p1 = path.join(paintingsDir, existingFile);
    const p2 = path.join(paintingsDir, f);
    const s1 = fs.statSync(p1).size;
    const s2 = fs.statSync(p2).size;
    
    let fileToArchive = f;
    if (s2 > s1 && ext === '.jpg') {
      fileToArchive = existingFile;
      seenBases.set(base, f);
    }
    const archivePath = path.join(archiveDir, fileToArchive);
    fs.renameSync(path.join(paintingsDir, fileToArchive), archivePath);
    console.log(`Deduplicated: moved ${fileToArchive} to inbox`);
  } else {
    seenBases.set(base, f);
  }
});

console.log('\n=== Step 3: Auditing Clean Training Images ===');
const trainingImages = fs.readdirSync(paintingsDir).filter(f => {
  const ext = path.extname(f).toLowerCase();
  return ['.jpg', '.jpeg', '.png', '.webp'].includes(ext);
});

console.log(`Total valid painting images in training pool: ${trainingImages.length}`);

console.log('\n=== Step 4: Generating LoRA .txt Caption Pairs ===');
const TRIGGER_WORD = 'jeff_painting style';

const variations = [
  'expressive painterly brushwork, rich oil color layering, tactile canvas texture, dynamic tonal depth, master composition',
  'traditional acrylic painting, vibrant atmospheric palette, bold impasto strokes, soft ambient lighting, high contrast',
  'contemporary fine art painting, layered pigment glazes, organic brush textures, dramatic lighting and shadow interplay',
  'expressive figurative painting, rich chromatic harmony, painterly edges, subtle brush stroke texture, studio lighting',
  'fine art oil study, classical color temperature balance, textured brushwork on canvas, evocative tonal atmosphere',
  'expressive impressionistic painting, textured color fields, vibrant brush gestures, luminous light reflection'
];

let captionsCreated = 0;

trainingImages.forEach((imgFile, idx) => {
  const ext = path.extname(imgFile);
  const base = path.basename(imgFile, ext);
  const txtPath = path.join(paintingsDir, `${base}.txt`);

  const styleHint = variations[idx % variations.length];
  const caption = `${TRIGGER_WORD}, ${styleHint}, traditional medium fine art on canvas, professional gallery quality`;

  fs.writeFileSync(txtPath, caption, 'utf8');
  captionsCreated++;
});

console.log(`Generated ${captionsCreated} matching .txt caption files.`);

console.log('\n=== Step 5: Final Integrity Verification ===');
const finalFiles = fs.readdirSync(paintingsDir);
const finalImages = finalFiles.filter(f => ['.jpg', '.jpeg', '.png', '.webp'].includes(path.extname(f).toLowerCase()));
const finalTxts = finalFiles.filter(f => f.endsWith('.txt'));

console.log(`Images count: ${finalImages.length}`);
console.log(`Captions count: ${finalTxts.length}`);
console.log(`1-to-1 Image-Caption Pair Match: ${finalImages.length === finalTxts.length ? '100% VALIDATED' : 'MISMATCH ERROR'}`);
