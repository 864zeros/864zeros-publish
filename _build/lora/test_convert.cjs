// test_convert.cjs — Tests conversion of TIFF and CR3 files via ffmpeg
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const dir = path.resolve(__dirname, '../../media/visuals/training_pools/sketches');
const files = fs.readdirSync(dir);

const tiff = files.find(f => f.endsWith('.tiff'));
const cr3 = files.find(f => f.endsWith('.cr3'));

if (tiff) {
  const src = path.join(dir, tiff);
  const out = path.join(dir, '_test_tiff.jpg');
  try {
    execSync(`ffmpeg -y -i "${src}" "${out}"`, { stdio: 'pipe' });
    if (fs.existsSync(out)) {
      console.log(`TIFF conversion succeeded! Size: ${(fs.statSync(out).size / 1024).toFixed(1)} KB`);
      fs.unlinkSync(out);
    }
  } catch (e) {
    console.error('TIFF conversion failed:', e.message);
  }
}

if (cr3) {
  const src = path.join(dir, cr3);
  const out = path.join(dir, '_test_cr3.jpg');
  try {
    execSync(`ffmpeg -y -i "${src}" "${out}"`, { stdio: 'pipe' });
    if (fs.existsSync(out)) {
      console.log(`CR3 conversion succeeded! Size: ${(fs.statSync(out).size / 1024).toFixed(1)} KB`);
      fs.unlinkSync(out);
    }
  } catch (e) {
    console.log('CR3 conversion via ffmpeg: not supported directly (raw camera format).');
  }
}
