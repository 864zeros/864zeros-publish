const fs = require('fs');
const path = require('path');

const QUEUE_PATH = 'C:/dev/864zeros-llc/LLC-DIV-4-GTM/videos/PHASE_6_VIDEO_QUEUE.json';
const DAM_PRODUCTS_DIR = 'C:/dev/864zeros-publish/media/products';
const MASTER_DOCKET_PATH = 'C:/dev/864zeros-publish/YOUTUBE_UPLOAD_DOCKET.md';

const queueData = JSON.parse(fs.readFileSync(QUEUE_PATH, 'utf8'));

let masterMd = `# 864zeros — YouTube Shorts Upload Docket (All 60 Deliverables)
**Generated:** ${new Date().toISOString()}  
**Authority:** LLC-DIV-4-GTM & Central DAM (864zeros-publish)  
**Standard:** 864z-SPEC-2026-012-VIDQ (9:16 vertical, ≤60s, #Shorts eligible)

---

## Instructions for YouTube Studio Upload
1. Open [YouTube Studio](https://studio.youtube.com/) for the **@864zeros** channel.
2. Click **Create** → **Upload videos**.
3. Select the target \`.mp4\` from the DAM path indicated below.
4. Copy-paste the **Title** and **Description** directly into YouTube Studio.
5. Upload the matching **Thumbnail PNG** (if desired; YouTube mobile Shorts feeds will also generate an automatic frame preview).
6. Audience: Select **"No, it's not made for kids"**.
7. Visibility: Set to **Public**.

---
`;

let totalVideos = 0;

for (const item of queueData.queue) {
  const slug = item.slug;
  const name = item.name;
  const category = item.category;
  const price = item.decoupledPrice || 'One-time unlock';
  const damProdDir = path.join(DAM_PRODUCTS_DIR, slug);
  const manifestPath = path.join(damProdDir, 'manifest.json');
  
  let manifest = {};
  if (fs.existsSync(manifestPath)) {
    try {
      manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    } catch (e) {
      console.error('Failed to parse manifest for ' + slug, e);
    }
  }

  const webUrl = `https://864zeros.com/products/${slug}`;
  const summary = manifest.summary || item.summary || `${name} — local-first productivity tool by 864zeros.`;
  
  let prodMd = `# ${name} — YouTube Upload Metadata
**DAM Product Folder:** \`media/products/${slug}/\`  
**Web Product Page:** ${webUrl}  
**Pricing Model:** ${price} (No subscriptions)  

---
`;

  // Deliverables
  const deliverables = item.deliverables || {};

  // Custom overrides for flagship champions
  if (slug === 'autoorganize-ytm') {
    if (deliverables.tier2Master) {
      deliverables.tier2Master.title = "AutoOrganize YTM: Auto-Sort Liked Songs into Genre Playlists";
    }
    if (deliverables.tier1ShortA_Pain) {
      deliverables.tier1ShortA_Pain.title = "Is Your YouTube Music Liked Songs a Graveyard?";
      deliverables.tier1ShortA_Pain.hook = "Be honest: is your YouTube Music Liked Songs a chaotic graveyard of tracks you never actually listen to?";
    }
    if (deliverables.tier1ShortB_Price) {
      deliverables.tier1ShortB_Price.title = "Why Pay $10/Month Just to Sort Music Playlists?";
      deliverables.tier1ShortB_Price.hook = "Why are music organizers charging ten dollars every month just to sort your playlists?";
    }
  } else if (slug === 'clearstreak') {
    if (deliverables.tier2Master) {
      deliverables.tier2Master.title = "ClearStreak: Private Habit & Vice Tracker (Data Over Shame)";
    }
    if (deliverables.tier1ShortA_Pain) {
      deliverables.tier1ShortA_Pain.title = "Why Habit Trackers Make You Feel Like Trash";
      deliverables.tier1ShortA_Pain.hook = "Why does every habit tracker make you feel like trash when you slip up? Miss one day, and they wipe your entire streak to zero.";
    }
    if (deliverables.tier1ShortB_Price) {
      deliverables.tier1ShortB_Price.title = "Who Else Has Access to Habits You Want to Break?";
      deliverables.tier1ShortB_Price.hook = "Who has access to the habits you're secretly trying to break? Most wellness apps upload your struggles to cloud servers.";
    }
  }

  // 1. Tier 2 Master

  const t2 = deliverables.tier2Master;
  if (t2) {
    totalVideos++;
    const videoFile = t2.file || `${slug}-short.mp4`;
    const damVideoPath = `media/products/${slug}/video/${videoFile}`;
    const t2Title = (t2.title || `${name} Demo: ${summary.split('.')[0]}`).replace(/ — /g, ': ');
    const safeTitle = (t2Title.length > 80 ? t2Title.substring(0, 78) + '...' : t2Title) + ' #Shorts';
    
    const desc = `${summary}

🔗 Get ${name}: ${webUrl}
🛡️ 100% Local-First & Private: Runs on your device — no cloud lock-in, no tracking.
💰 Fair Pricing: ${price} (No monthly subscription fees).

#Shorts #Productivity #GoogleWorkspace #Software #LocalFirst #864zeros`;

    const tags = `${slug}, ${name.toLowerCase()}, productivity, local first, 864zeros, google workspace, software demo, no subscription`;

    const block = `### 1. Tier 2 Master Explainer
* **Video File:** \`${damVideoPath}\`
* **Suggested Thumbnail:** \`media/products/${slug}/video/thumbnail.png\` (or \`${slug}-thumbnail.png\`)
* **YouTube Title:**
\`\`\`
${safeTitle}
\`\`\`
* **YouTube Description:**
\`\`\`
${desc}
\`\`\`
* **Tags:** \`${tags}\`

---
`;
    prodMd += block;
    masterMd += `\n## ${name} (Master Explainer)\n` + block;
  }

  // 2. Tier 1 Short A (Pain Hook)
  const t1a = deliverables.tier1ShortA_Pain;
  if (t1a) {
    totalVideos++;
    const videoFile = t1a.file || `social_shorts/${slug}-social-pain.mp4`;
    const damVideoPath = `media/products/${slug}/video/${path.basename(videoFile)}`;
    const hook = t1a.hook || `Tired of broken workflows with ${name}?`;
    const rawTitle = t1a.title || `${hook.substring(0, 70)}`;
    const safeTitle = (rawTitle.length > 80 ? rawTitle.substring(0, 78) + '...' : rawTitle) + ' #Shorts';

    const desc = `${hook}

Meet ${name} — the fast, local-first solution that solves this without messy cloud tools.

🔗 Try it here: ${webUrl}
🛡️ Zero tracking, zero cloud dependency.
💰 ${price}

#Shorts #ProductivityHacks #TechTips #Workflow #864zeros`;

    const tags = `${slug}, ${name.toLowerCase()}, productivity hack, workflow tips, local first, 864zeros`;

    const block = `### 2. Tier 1 Social Short A (Pain Hook)
* **Video File:** \`${damVideoPath}\`
* **Suggested Thumbnail:** \`media/products/${slug}/video/thumbnail-${slug}-social-pain.png\`
* **YouTube Title:**
\`\`\`
${safeTitle}
\`\`\`
* **YouTube Description:**
\`\`\`
${desc}
\`\`\`
* **Tags:** \`${tags}\`

---
`;
    prodMd += block;
    masterMd += `\n## ${name} (Pain Hook Short)\n` + block;
  }

  // 3. Tier 1 Short B (Price Hook)
  const t1b = deliverables.tier1ShortB_Price;
  if (t1b) {
    totalVideos++;
    const videoFile = t1b.file || `social_shorts/${slug}-social-price.mp4`;
    const damVideoPath = `media/products/${slug}/video/${path.basename(videoFile)}`;
    const hook = t1b.hook || `Stop paying recurring subscriptions for simple tools.`;
    const rawTitle = t1b.title || `${hook.substring(0, 70)}`;
    const safeTitle = (rawTitle.length > 80 ? rawTitle.substring(0, 78) + '...' : rawTitle) + ' #Shorts';

    const desc = `${hook}

${name} gives you complete control with a single ${price} (no recurring monthly subscriptions).

🔗 Full details: ${webUrl}
🛡️ Privacy-first by design — your data stays yours.

#Shorts #AntiSaaS #NoSubscription #Productivity #864zeros`;

    const tags = `${slug}, ${name.toLowerCase()}, anti saas, no subscription, lifetime license, productivity, 864zeros`;

    const block = `### 3. Tier 1 Social Short B (Price Hook)
* **Video File:** \`${damVideoPath}\`
* **Suggested Thumbnail:** \`media/products/${slug}/video/thumbnail-${slug}-social-price.png\`
* **YouTube Title:**
\`\`\`
${safeTitle}
\`\`\`
* **YouTube Description:**
\`\`\`
${desc}
\`\`\`
* **Tags:** \`${tags}\`

---
`;
    prodMd += block;
    masterMd += `\n## ${name} (Price Hook Short)\n` + block;
  }

  // Write per-product youtube.md in DAM
  if (fs.existsSync(damProdDir)) {
    const prodYoutubeMdPath = path.join(damProdDir, 'youtube.md');
    fs.writeFileSync(prodYoutubeMdPath, prodMd, 'utf8');
    console.log(`Generated DAM YouTube docket: ${prodYoutubeMdPath}`);
  }
}

fs.writeFileSync(MASTER_DOCKET_PATH, masterMd, 'utf8');
console.log(`\nGenerated Master YouTube Docket: ${MASTER_DOCKET_PATH} (${totalVideos} deliverables)`);
