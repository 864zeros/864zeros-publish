// audit_dataset.cjs — Audits the sketch training pool images
const fs = require('fs');
const path = require('path');

const dir = path.resolve(__dirname, '../../media/visuals/training_pools/sketches');
const files = fs.readdirSync(dir).filter(f => f !== '.gitkeep');

console.log(`Total files found in sketches/: ${files.length}`);

const exts = {};
files.forEach(f => {
  const ext = path.extname(f).toLowerCase() || '(no ext)';
  exts[ext] = (exts[ext] || 0) + 1;
});

console.log('Extensions breakdown:', JSON.stringify(exts, null, 2));

console.log('\nFirst 10 sample files:');
files.slice(0, 10).forEach(f => {
  const stat = fs.statSync(path.join(dir, f));
  console.log(` - ${f} (${(stat.size / 1024).toFixed(1)} KB)`);
});
