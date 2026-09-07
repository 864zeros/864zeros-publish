// init_media_house.cjs — Initializes the complete Media House directory structure
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');

const dirs = [
  'shared/creative/poems',
  'shared/creative/prayers',
  'shared/creative/reflections',
  'media/audio/voices',
  'media/audio/music',
  'media/audio/sfx',
  'media/audio/masters',
  'media/visuals/training_pools/sketches',
  'media/visuals/training_pools/paintings',
  'media/visuals/training_pools/illustrations',
  'media/visuals/lora_weights',
  'media/visuals/rendered_art',
  'media/graphics/branding',
  'media/graphics/templates',
  'media/graphics/covers',
  'media/photography/references',
  'media/photography/textures',
  'media/video/b_roll_loops',
  'media/video/storyboards',
  'media/video/rendered_reels',
  '_build/lora',
  '_build/audio',
  '_build/video',
  'sources/google_photos_inbox',
  'sources/raw_writings_inbox'
];

dirs.forEach(d => {
  const fullPath = path.join(root, d);
  fs.mkdirSync(fullPath, { recursive: true });
  const gitkeep = path.join(fullPath, '.gitkeep');
  if (!fs.existsSync(gitkeep)) {
    fs.writeFileSync(gitkeep, '', 'utf8');
  }
});

console.log(`Successfully initialized ${dirs.length} Media House directories.`);
