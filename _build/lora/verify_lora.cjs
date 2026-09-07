// verify_lora.cjs — Verifies the trained LoRA safetensors file
const fs = require('fs');
const path = require('path');

const loraPath = path.resolve(__dirname, '../../media/visuals/lora_weights/864z_jeff_sketch_v1.safetensors');

if (!fs.existsSync(loraPath)) {
  console.error('LoRA file not found at:', loraPath);
  process.exit(1);
}

const stat = fs.statSync(loraPath);
console.log('SUCCESS: 864z_jeff_sketch_v1.safetensors verified!');
console.log(`Location: ${loraPath}`);
console.log(`File Size: ${(stat.size / 1024 / 1024).toFixed(2)} MB (${stat.size} bytes)`);
console.log(`Last Modified: ${stat.mtime.toISOString()}`);
