// test_cr3_extract.cjs — Extracts embedded high-res JPEG previews from Canon CR3 files
const fs = require('fs');
const path = require('path');

const dir = path.resolve(__dirname, '../../media/visuals/training_pools/sketches');
const files = fs.readdirSync(dir);
const sampleCr3 = files.find(f => f.toLowerCase().endsWith('.cr3'));

if (sampleCr3) {
  const buf = fs.readFileSync(path.join(dir, sampleCr3));
  console.log(`CR3 total size: ${(buf.length / 1024 / 1024).toFixed(2)} MB`);
  
  // Look for JPEG SOI marker (0xFF, 0xD8, 0xFF)
  let foundJpegs = [];
  for (let i = 0; i < buf.length - 4; i++) {
    if (buf[i] === 0xFF && buf[i+1] === 0xD8 && buf[i+2] === 0xFF) {
      // Look for next EOI marker (0xFF, 0xD9)
      for (let j = i + 1000; j < buf.length - 1; j++) {
        if (buf[j] === 0xFF && buf[j+1] === 0xD9) {
          const length = (j + 2) - i;
          foundJpegs.push({ start: i, end: j + 2, length });
          break;
        }
      }
    }
  }

  console.log(`Found ${foundJpegs.length} embedded JPEG streams.`);
  // Find the largest one (the full-res or high-res preview)
  foundJpegs.sort((a, b) => b.length - a.length);
  if (foundJpegs.length > 0) {
    const largest = foundJpegs[0];
    console.log(`Largest embedded JPEG preview: ${(largest.length / 1024).toFixed(1)} KB`);
    const outJpg = path.join(dir, '_test_cr3_extracted.jpg');
    fs.writeFileSync(outJpg, buf.subarray(largest.start, largest.end));
    console.log(`Extracted preview saved!`);
    fs.unlinkSync(outJpg);
  }
}
