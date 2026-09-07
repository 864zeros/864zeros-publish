// inspect_cr3.cjs — Check CR3 filenames and corresponding files
const fs = require('fs');
const path = require('path');

const dir = path.resolve(__dirname, '../../media/visuals/training_pools/sketches');
const files = fs.readdirSync(dir);

const cr3Files = files.filter(f => f.toLowerCase().endsWith('.cr3'));
console.log(`Found ${cr3Files.length} CR3 files:`);
cr3Files.forEach(f => {
  const base = path.basename(f, path.extname(f));
  const matches = files.filter(other => other.startsWith(base));
  console.log(` - ${f} (Matching files: ${matches.join(', ')})`);
});
