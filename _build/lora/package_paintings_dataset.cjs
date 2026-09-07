// package_paintings_dataset.cjs — Packages the 150 paintings and 150 .txt captions into a clean zip archive for LoRA training
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const paintingsDir = path.resolve(__dirname, '../../media/visuals/training_pools/paintings');
const zipOut = path.resolve(__dirname, '../../media/visuals/training_pools/864z_jeff_painting_dataset.zip');

const files = fs.readdirSync(paintingsDir).filter(f => f !== '.gitkeep' && !f.endsWith('.zip'));

console.log(`Packaging ${files.length} files (${files.filter(f => f.endsWith('.txt')).length} captions + ${files.filter(f => !f.endsWith('.txt')).length} images)...`);

// Create zip using PowerShell Compress-Archive
try {
  const psCmd = `powershell -Command "Compress-Archive -Path '${paintingsDir}/*' -DestinationPath '${zipOut}' -Force"`;
  execSync(psCmd, { stdio: 'inherit' });
  const stat = fs.statSync(zipOut);
  console.log(`\nSUCCESS: Packaged paintings training dataset to:`);
  console.log(`${zipOut} (${(stat.size / 1024 / 1024).toFixed(2)} MB)`);
} catch (e) {
  console.error('Packaging failed:', e.message);
}
