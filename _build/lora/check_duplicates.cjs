// check_duplicates.cjs — Analyzes base names and duplicate file formats
const fs = require('fs');
const path = require('path');

const dir = path.resolve(__dirname, '../../media/visuals/training_pools/sketches');
const files = fs.readdirSync(dir).filter(f => f !== '.gitkeep');

const baseMap = {};
files.forEach(f => {
  const ext = path.extname(f).toLowerCase();
  const base = path.basename(f, ext);
  if (!baseMap[base]) baseMap[base] = [];
  baseMap[base].push(ext);
});

const uniqueBases = Object.keys(baseMap);
console.log(`Total files: ${files.length}`);
console.log(`Unique base names: ${uniqueBases.length}`);

const multiExt = uniqueBases.filter(b => baseMap[b].length > 1);
console.log(`Base names with multiple formats (e.g. raw + jpg/tiff): ${multiExt.length}`);
if (multiExt.length > 0) {
  console.log('Samples of multi-format bases:');
  multiExt.slice(0, 5).forEach(b => console.log(` - ${b}: [${baseMap[b].join(', ')}]`));
}
