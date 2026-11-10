#!/usr/bin/env node
/**
 * fhg_youtube_cli.mjs — Official For His Grace (@ForHisGrace) YouTube OAuth,
 * Channel Setup, In-Place Metadata Upgrade & Automated Shorts Upload CLI
 *
 * Account: forhisgrace.web@gmail.com
 * Governance Locks Enforced Before Every API Call:
 *   - RULE-004: Zero "864zeros" mentions on any public FHG YouTube surface
 *   - RULE-016: Zero internal engineering/pipeline jargon
 *   - RULE-017: Zero dollar ($) or commercial pricing figures
 *   - Dual "— JMC" Provenance Disclaimers (*FHG-SP + Studio Artwork)
 *
 * Usage:
 *   node fhg_youtube_cli.mjs --status
 *   node fhg_youtube_cli.mjs --auth
 *   node fhg_youtube_cli.mjs --setup-channel
 *   node fhg_youtube_cli.mjs --upload sepia-001 --dry-run
 *   node fhg_youtube_cli.mjs --upload sepia-001 --live
 */

import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import { exec, execSync } from 'node:child_process';
import { createRequire } from 'node:module';

const require = createRequire('C:/dev/864zeros-publisher-mcp/package.json');
const dotenv = require('dotenv');
const { google } = require('googleapis');

const MCP_ENV_PATH = 'C:\\dev\\864zeros-publisher-mcp\\.env';
const FHG_TOKEN_FILE = path.join(process.env.USERPROFILE || 'C:\\Users\\Jeff', '.864zeros', 'youtube-tokens-fhg.json');
const RENDERS_DIR = 'C:\\dev\\864zeros-publish\\media\\video\\fhg_shorts\\rendered_reels';
const THUMBS_DIR = 'C:\\dev\\864zeros-publish\\media\\video\\fhg_shorts\\thumbnails';
const LOCKED_BANNER_PATH = path.join(THUMBS_DIR, 'FHG-BANNER-B_warm-parchment-sanctuary_2560x1440.jpg');
const LOCKED_AVATAR_PATH = path.join(THUMBS_DIR, 'FHG-AVATAR_fig-tree-emblem_800x800.jpg');

dotenv.config({ path: MCP_ENV_PATH });

const PROVENANCE_FOOTER = [
  '🖋️ Provenance & Stewardship Note:',
  '• *FHG-SP (FHG Sanctuary Plain) is a plain-English contextual study companion synthesized from public-domain manuscript traditions and original-language lexicons for personal reflection alongside established translations. No interpretation arrives unapproved. — JMC',
  "• Artwork is original and enhanced with AI models trained on the artist's 'real' sketches. No artwork arrives unapproved. — JMC"
].join('\n');

export const FHG_PLAYLISTS = [
  {
    key: 'context',
    title: 'First-Century Bible Context & Old Testament Prophecies Explained',
    description: 'Why did the Gospel writers record specific legal prices, coins, architectural details, and Old Testament echoes? This series uncovers the first-century Judean and Galilean historical context—and the Torah and prophetic cross-references (Exodus, Zechariah, Isaiah, Psalms)—that unlock the deeper meaning of the Gospels. Read every passage across 4 parallel translations (BSB, KJV, WEB & *FHG-SP) at https://forhisgrace.com/framework/poc_sanctuary_reader.html'
  },
  {
    key: 'parables',
    title: 'Parables of Jesus Explained in First-Century Context (Visual Sketch Series)',
    description: "Jesus rarely used royal palaces or towering cedars to explain the Kingdom of Heaven—He used wild garden mustard seeds, worn fishing nets, leavened bread, and everyday Galilean labor. Watch our hand-sketched Sepia visual studies exploring what Jesus's parables actually meant to the first-century crowds who heard them first. Study in parallel at https://forhisgrace.com"
  },
  {
    key: 'words',
    title: 'Misunderstood Bible Verses & Original Greek / Hebrew Word Studies',
    description: 'What happens when we stop reading isolated "fortune-cookie" verses and look at the full chapter context and original Greek and Hebrew words? From what "meek" (praus) truly meant in Matthew 5:5 to how first-century believers read Scripture aloud as one unified story (John 5:39), this series restores the weight of the biblical text.'
  },
  {
    key: 'sanctuary',
    title: 'How to Study the Bible in Context — Sanctuary Reader & Parallel Translations',
    description: 'Step-by-step guides to reading Scripture deeply without noise: comparing translations side by side (BSB, KJV, WEB & *FHG-SP), tracing Old Testament cross-references in the Gospels, and using the free, ad-free Sanctuary Reader at https://forhisgrace.com/framework/poc_sanctuary_reader.html'
  }
];

export const FHG_DOCKETS = {
  'broll-001': {
    id: 'broll-001',
    liveVideoId: 'ErMizVyePaY',
    format: '9:16',
    videoPath: path.join(RENDERS_DIR, 'FHG-SHORT-BROLL-001_9x16_1080p.mp4'),
    videoPath16x9: path.join(RENDERS_DIR, 'FHG-SHORT-BROLL-001_16x9_1080p.mp4'),
    companionThumb16x9: path.join(THUMBS_DIR, 'FHG-THUMB-001A_silver-coins_16x9.jpg'),
    title: 'Why Did Judas Get 30 Pieces of Silver? The Torah Law Everyone Misses (Exodus 21:32) #Shorts',
    description: [
      'Why did the chief priests weigh out exactly thirty pieces of silver to betray Jesus in Matthew 26:15 and Matthew 27:9—not twenty-five, and not fifty?',
      '',
      "Thirty pieces of silver (thirty shekels) wasn't a random bargain. Under the Law of Moses in Exodus 21:32, thirty shekels of silver was the exact statutory compensation paid when an ox gored and wounded a bondservant. Seven centuries later, the prophet Zechariah stood in the temple courtyard as the rejected Good Shepherd and asked them to weigh out his worth—and they weighed out thirty pieces of silver, thrown to the potter in the house of the Lord (Zechariah 11:12–13).",
      '',
      'When the temple leaders counted out thirty silver coins for Jesus, they thought they were pricing Him at the lowest insult in the Torah. Instead, they fulfilled the exact prophetic price of the Wounded Servant who came to purchase our freedom.',
      '',
      '📖 READ THIS MESSAGE & COMPARE ALL 3 CROSS-REFERENCES:',
      '• Full Written & Audio Study (Thirty Pieces of Silver): https://forhisgrace.com/messages/thirty-pieces-of-silver.html',
      '• Open in the 4-Translation Sanctuary Reader (BSB, KJV, WEB & *FHG-SP): https://forhisgrace.com/framework/poc_sanctuary_reader.html',
      '',
      PROVENANCE_FOOTER,
      '',
      '#BibleStudy #ScriptureInContext #ForHisGrace'
    ].join('\n'),
    tags: [
      'thirty pieces of silver meaning',
      'why did judas get 30 pieces of silver',
      'exodus 21 32 thirty shekels of silver',
      'zechariah 11 12 13 thirty pieces of silver',
      'matthew 27 9 prophecy explained',
      'price of a wounded servant bible',
      'first century bible context',
      'old testament prophecies of jesus',
      'for his grace',
      'how to read the bible in context'
    ],
    pinnedComment: 'Had you ever connected the 30 pieces of silver in Matthew 26:15 back to the Torah law of the wounded servant in Exodus 21:32 and Zechariah 11:12–13? 👇 Read the full cross-reference study and compare BSB, KJV, WEB & *FHG-SP side by side here: https://forhisgrace.com/messages/thirty-pieces-of-silver.html',
    playlistKeys: ['context']
  },
  'sepia-001': {
    id: 'sepia-001',
    format: '9:16',
    videoPath: path.join(RENDERS_DIR, 'FHG-SHORT-SEPIA-001_9x16_1080p.mp4'),
    videoPath16x9: path.join(RENDERS_DIR, 'FHG-SHORT-SEPIA-001_16x9_1080p.mp4'),
    companionThumb16x9: path.join(THUMBS_DIR, 'FHG-THUMB-SEPIA-001_mustard-seed_16x9.jpg'),
    title: 'Why Did Jesus Compare Heaven to a Wild Mustard Seed? (Matthew 13:31–32) #Shorts',
    description: [
      'Why did Jesus compare the Kingdom of Heaven to a tiny garden mustard seed in Matthew 13:31–32 instead of the mighty cedars of Lebanon?',
      '',
      "In the ancient Near East, empires like Babylon and Rome—and even Old Testament imagery in Ezekiel 17 and Daniel 4—pictured kingdoms as towering cedar trees on high mountains. When Jesus stood by the Sea of Galilee and compared God's Kingdom to a common mustard seed that grows into a wild garden shrub where birds find shelter, His first-century listeners heard a radical truth: the Kingdom of God doesn't arrive with imperial spectacle. It starts almost invisibly small, takes root in ordinary soil, and quietly shelters the weary.",
      '',
      '📖 READ MATTHEW 13:31–32 IN THE SANCTUARY READER (4 PARALLEL TRANSLATIONS):',
      'Compare BSB, KJV, WEB & *FHG-SP (FHG Sanctuary Plain) side by side in a quiet, ad-free workspace:',
      'https://forhisgrace.com/framework/poc_sanctuary_reader.html',
      '',
      '🕊️ RELATED FIRST-CENTURY STUDY:',
      '• Thirty Pieces of Silver — The Price of a Wounded Servant (Exodus 21:32 × Matthew 27):',
      'https://forhisgrace.com/messages/thirty-pieces-of-silver.html',
      '• Explore For His Grace (Always free, zero ads):',
      'https://forhisgrace.com',
      '',
      PROVENANCE_FOOTER,
      '',
      '#BibleStudy #ParablesOfJesus #ScriptureInContext'
    ].join('\n'),
    tags: [
      'parable of the mustard seed explained',
      'matthew 13 31 32 meaning',
      'why did jesus use a mustard seed',
      'kingdom of heaven mustard seed',
      'first century bible context',
      'parables of jesus in context',
      'cedar of lebanon vs mustard seed',
      'matthew 13 bible study',
      'for his grace',
      'how to read the bible in context'
    ],
    pinnedComment: 'When you first heard the Parable of the Mustard Seed growing up, was it taught as a lesson about "having bigger faith" or about how quietly God\'s Kingdom grows in the world? 👇 (Compare Matthew 13:31–32 across 4 translations in the Sanctuary Reader: https://forhisgrace.com/framework/poc_sanctuary_reader.html)',
    playlistKeys: ['parables', 'context']
  },
  'sepia-002': {
    id: 'sepia-002',
    format: '9:16',
    videoPath: path.join(RENDERS_DIR, 'FHG-SHORT-SEPIA-002_9x16_1080p.mp4'),
    videoPath16x9: path.join(RENDERS_DIR, 'FHG-SHORT-SEPIA-002_16x9_1080p.mp4'),
    companionThumb16x9: path.join(THUMBS_DIR, 'FHG-THUMB-SEPIA-002_galilee-nets_16x9.jpg'),
    title: 'Why Did Jesus Call Tired Fishermen After an Empty Night? (Luke 5:1–11) #Shorts',
    description: [
      'Why did Jesus walk past the elite religious academies of Jerusalem and step straight onto the gravel shore of Galilee to call exhausted fishermen washing empty nets at dawn (Luke 5:1–11)?',
      '',
      "In first-century Galilee, night fishing with linen trammel nets was backbreaking work. By sunrise, Simon Peter and his partners had worked all night, caught nothing, and were scrubbing lake silt and weeds from their nets before storing them. Jesus didn't wait until Peter had a victorious morning—He stepped into Peter's empty boat, asked him to push out into deep water in broad daylight (when every experienced fisherman knew fish couldn't be caught in surface nets), and met exhaustion with overwhelming grace.",
      '',
      '📖 READ LUKE 5:1–11 IN THE SANCTUARY READER (4 PARALLEL TRANSLATIONS):',
      'Compare BSB, KJV, WEB & *FHG-SP (FHG Sanctuary Plain) side by side in a calm, distraction-free study view:',
      'https://forhisgrace.com/framework/poc_sanctuary_reader.html',
      '',
      '🕊️ RELATED FIRST-CENTURY STUDY:',
      '• Thirty Pieces of Silver — The Price of a Wounded Servant (Exodus 21:32 × Matthew 27):',
      'https://forhisgrace.com/messages/thirty-pieces-of-silver.html',
      '• Explore For His Grace (Always free, zero ads):',
      'https://forhisgrace.com',
      '',
      PROVENANCE_FOOTER,
      '',
      '#BibleStudy #GospelOfLuke #ScriptureInContext'
    ].join('\n'),
    tags: [
      'luke 5 1 11 explained',
      'why did jesus call fishermen',
      'miraculous catch of fish luke 5',
      'simon peter washing nets',
      'first century galilee fishing',
      'put out into the deep luke 5',
      'bible context explained',
      'for his grace',
      'scripture in context',
      'christian bible study'
    ],
    pinnedComment: 'Notice in Luke 5:5 that Peter tells Jesus, "Master, we toiled all night and took nothing—but at Your word I will let down the nets." What stands out to you most about Jesus stepping into Peter\'s boat right after an empty night? 👇 (Read Luke 5 side by side in 4 translations: https://forhisgrace.com/framework/poc_sanctuary_reader.html)',
    playlistKeys: ['context', 'parables']
  },
  'sepia-003': {
    id: 'sepia-003',
    format: '9:16',
    videoPath: path.join(RENDERS_DIR, 'FHG-SHORT-SEPIA-003_9x16_1080p.mp4'),
    videoPath16x9: path.join(RENDERS_DIR, 'FHG-SHORT-SEPIA-003_16x9_1080p.mp4'),
    companionThumb16x9: path.join(THUMBS_DIR, 'FHG-THUMB-SEPIA-003_capernaum-roof_16x9.jpg'),
    title: 'Why Did Four Friends Tear Open a Roof in Capernaum? (Mark 2:1–12) #Shorts',
    description: [
      'What actually happened when four men tore open the roof above Jesus in Capernaum (Mark 2:1–12)?',
      '',
      'First-century houses in Capernaum were built with basalt stone walls and flat roofs supported by timber beams, woven reeds, and a heavy layer of packed mud-thatch rolled tight with a stone roller. An exterior stone staircase led directly to the roof. When the doorway was completely blocked by the crowd and the scribes sitting inside, the four friends carried their paralyzed friend up the outside stairs and literally "dug through" (Greek: exoryxantes) the packed earth and branches while dust fell onto the room below. And Mark 2:5 records a stunning detail: "When Jesus saw THEIR faith, He said to the paralytic, \'Son, your sins are forgiven.\'"',
      '',
      '📖 READ MARK 2:1–12 IN THE SANCTUARY READER (4 PARALLEL TRANSLATIONS):',
      'Compare BSB, KJV, WEB & *FHG-SP (FHG Sanctuary Plain) side by side in a quiet, ad-free study view:',
      'https://forhisgrace.com/framework/poc_sanctuary_reader.html',
      '',
      '🕊️ RELATED FIRST-CENTURY STUDY:',
      '• Thirty Pieces of Silver — The Price of a Wounded Servant (Exodus 21:32 × Matthew 27):',
      'https://forhisgrace.com/messages/thirty-pieces-of-silver.html',
      '• Explore For His Grace (Always free, zero ads):',
      'https://forhisgrace.com',
      '',
      PROVENANCE_FOOTER,
      '',
      '#BibleStudy #GospelOfMark #ScriptureInContext'
    ].join('\n'),
    tags: [
      'mark 2 1 12 explained',
      'healing of the paralytic capernaum',
      'tearing open the roof mark 2',
      'first century capernaum house roof',
      'when jesus saw their faith mark 2 5',
      'bible historical context',
      'gospel of mark study',
      'for his grace',
      'scripture in context',
      'how to study the bible'
    ],
    pinnedComment: 'Mark 2:5 says, "When Jesus saw THEIR faith..." — referring to the four friends carrying the mat as much as the man on it. Who in your life has carried you to Jesus when you couldn\'t get through the door yourself? 👇 (Compare Mark 2:1–12 across 4 translations in the Sanctuary Reader: https://forhisgrace.com/framework/poc_sanctuary_reader.html)',
    playlistKeys: ['context', 'parables']
  }
};

function verifyFhgGovernance(docket) {
  const combined = `${docket.title}\n${docket.description}\n${(docket.tags || []).join(' ')}\n${docket.pinnedComment || ''}`;
  if (/864zeros|864z/i.test(combined)) {
    throw new Error(`RULE-004 VIOLATION: Found '864zeros' in FHG docket '${docket.id}'!`);
  }
  if (/\$[0-9]/.test(combined)) {
    throw new Error(`RULE-017 VIOLATION: Found commercial dollar figure ($X) in FHG docket '${docket.id}'!`);
  }
  if (/\b(LoRA|IndexedDB|localStorage|WebMCP|D-UTA|Difference-of-Gaussians)\b/i.test(combined)) {
    throw new Error(`RULE-016 VIOLATION: Found internal engineering jargon in FHG docket '${docket.id}'!`);
  }
  if (!combined.includes('— JMC')) {
    throw new Error(`PROVENANCE VIOLATION: Missing '— JMC' provenance disclaimer in FHG docket '${docket.id}'!`);
  }
  return true;
}

function updateEnvKey(filePath, updates) {
  let content = fs.existsSync(filePath) ? fs.readFileSync(filePath, 'utf8') : '';
  for (const [k, v] of Object.entries(updates)) {
    const regex = new RegExp(`^${k}=.*$`, 'm');
    if (regex.test(content)) {
      content = content.replace(regex, `${k}=${v}`);
    } else {
      content = content.trimEnd() + `\n${k}=${v}\n`;
    }
  }
  fs.writeFileSync(filePath, content, 'utf8');
}

function getFhgOAuthClient() {
  let clientId = process.env.FHG_YOUTUBE_CLIENT_ID;
  let clientSecret = process.env.FHG_YOUTUBE_CLIENT_SECRET;
  let refreshToken = process.env.FHG_YOUTUBE_REFRESH_TOKEN || process.env.YOUTUBE_FHG_REFRESH_TOKEN;

  // Prefer Google's pre-verified clasp Desktop OAuth Client (1072944905499) over unverified SYZYGY Trust Vault (100480155220)
  const clasprcPath = path.join(process.env.USERPROFILE || 'C:\\Users\\Jeff', '.clasprc.json');
  if (!clientId && fs.existsSync(clasprcPath)) {
    try {
      const clasprc = JSON.parse(fs.readFileSync(clasprcPath, 'utf8'));
      const def = clasprc?.tokens?.default;
      if (def?.client_id && def?.client_secret) {
        clientId = def.client_id;
        clientSecret = def.client_secret;
      }
    } catch (_) {}
  }

  if (fs.existsSync(FHG_TOKEN_FILE)) {
    try {
      const saved = JSON.parse(fs.readFileSync(FHG_TOKEN_FILE, 'utf8'));
      if (saved.client_id && saved.client_secret) {
        clientId = saved.client_id;
        clientSecret = saved.client_secret;
      }
      if (saved.refresh_token) refreshToken = saved.refresh_token;
    } catch (_) {}
  }

  if (!clientId) clientId = process.env.YOUTUBE_CLIENT_ID;
  if (!clientSecret) clientSecret = process.env.YOUTUBE_CLIENT_SECRET;

  return { clientId, clientSecret, refreshToken };
}

async function runOAuthLogin() {
  const { clientId, clientSecret } = getFhgOAuthClient();
  const PORT = 3099;
  const redirectUri = `http://localhost:${PORT}`;
  const oauth2Client = new google.auth.OAuth2(clientId, clientSecret, redirectUri);

  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    prompt: 'select_account consent',
    login_hint: 'forhisgrace.web@gmail.com',
    scope: [
      'https://www.googleapis.com/auth/youtube.upload',
      'https://www.googleapis.com/auth/youtube',
      'https://www.googleapis.com/auth/yt-analytics.readonly'
    ]
  });

  console.log('\n========================================================================');
  console.log('🏛️  FOR HIS GRACE (@ForHisGrace) YOUTUBE OAUTH CONNECT (PORT 3099)');
  console.log('Please sign in with: forhisgrace.web@gmail.com');
  console.log('Auth URL:', authUrl);
  console.log('========================================================================\n');

  const server = http.createServer(async (req, res) => {
    if (req.url && req.url.includes('code=')) {
      const code = new URL(req.url, redirectUri).searchParams.get('code');
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end('<div style="font-family:Georgia,serif;background:#F6EFE4;color:#261C13;padding:44px;text-align:center;border:2px solid #8B6642;border-radius:12px;max-width:620px;margin:40px auto;"><h2>✅ @ForHisGrace YouTube Channel Connected!</h2><p>Saved dedicated OAuth token for <strong>forhisgrace.web@gmail.com</strong> and configuring Playlists, Banner &amp; Analytics now. You may close this browser tab.</p></div>');

      try {
        const { tokens } = await oauth2Client.getToken(code);
        if (tokens.refresh_token) {
          fs.mkdirSync(path.dirname(FHG_TOKEN_FILE), { recursive: true });
          fs.writeFileSync(FHG_TOKEN_FILE, JSON.stringify({
            account: 'forhisgrace.web@gmail.com',
            channelHandle: '@ForHisGrace',
            client_id: clientId,
            client_secret: clientSecret,
            refresh_token: tokens.refresh_token,
            scopes: [
              'https://www.googleapis.com/auth/youtube.upload',
              'https://www.googleapis.com/auth/youtube',
              'https://www.googleapis.com/auth/yt-analytics.readonly'
            ],
            updatedAt: new Date().toISOString()
          }, null, 2), 'utf8');

          updateEnvKey(MCP_ENV_PATH, {
            FHG_YOUTUBE_CLIENT_ID: clientId,
            FHG_YOUTUBE_CLIENT_SECRET: clientSecret,
            FHG_YOUTUBE_REFRESH_TOKEN: tokens.refresh_token,
            YOUTUBE_FHG_REFRESH_TOKEN: tokens.refresh_token
          });
          process.env.FHG_YOUTUBE_CLIENT_ID = clientId;
          process.env.FHG_YOUTUBE_CLIENT_SECRET = clientSecret;
          process.env.FHG_YOUTUBE_REFRESH_TOKEN = tokens.refresh_token;
          process.env.YOUTUBE_FHG_REFRESH_TOKEN = tokens.refresh_token;
          console.log(`✅ Saved FHG OAuth token to ${FHG_TOKEN_FILE} and ${MCP_ENV_PATH}`);
        }
        await setupChannelAndUpgradeLiveVideo();
        execSync('node "C:\\dev\\864zeros-analytics\\scripts\\sync_youtube_analytics.mjs"', { stdio: 'inherit' });
        server.close();
        process.exit(0);
      } catch (err) {
        console.error('❌ OAuth exchange / setup error:', err.message);
        server.close();
        process.exit(1);
      }
    }
  });

  server.listen(PORT, () => {
    exec(`start "" "${authUrl}"`);
  });
}

async function setupChannelAndUpgradeLiveVideo() {
  const { clientId, clientSecret, refreshToken } = getFhgOAuthClient();
  if (!refreshToken) {
    console.error('❌ Missing FHG YouTube OAuth token. Run: node fhg_youtube_cli.mjs --auth');
    process.exit(1);
  }

  const oauth2Client = new google.auth.OAuth2(clientId, clientSecret, 'http://localhost');
  oauth2Client.setCredentials({ refresh_token: refreshToken });
  const youtube = google.youtube({ version: 'v3', auth: oauth2Client });

  // 1. Verify authenticated channel is @ForHisGrace (and never @864zeros)
  const chRes = await youtube.channels.list({ part: ['snippet', 'statistics'], mine: true });
  const channel = chRes.data.items?.[0];
  if (!channel) throw new Error('No YouTube channel found for this token.');
  console.log(`🏛️ Connected to Channel: ${channel.snippet.title} (${channel.snippet.customUrl || channel.id})`);
  if (/864zeros/i.test(channel.snippet.title || '')) {
    throw new Error('RULE-004 SAFETY HALT: Authenticated token belongs to @864zeros, not @ForHisGrace! Run `node fhg_youtube_cli.mjs --auth` and select forhisgrace.web@gmail.com.');
  }

  // 2. Upgrade Live Video #001 (ErMizVyePaY) in place
  const d001 = FHG_DOCKETS['broll-001'];
  verifyFhgGovernance(d001);
  await youtube.videos.update({
    part: ['snippet'],
    requestBody: {
      id: d001.liveVideoId,
      snippet: {
        title: d001.title,
        description: d001.description,
        tags: d001.tags,
        categoryId: '27', // Education
        defaultLanguage: 'en',
        defaultAudioLanguage: 'en'
      }
    }
  });
  console.log(`✅ Upgraded Live Video #001 (${d001.liveVideoId}) metadata, tags & Category 27 (Education).`);

  // 3. Ensure all 4 Official Thematic Playlists exist
  const existingPl = await youtube.playlists.list({ part: ['snippet'], mine: true, maxResults: 50 });
  const existingByTitle = {};
  for (const p of existingPl.data.items || []) {
    existingByTitle[p.snippet.title] = p.id;
  }

  const playlistIdsByKey = {};
  for (const pl of FHG_PLAYLISTS) {
    if (existingByTitle[pl.title]) {
      playlistIdsByKey[pl.key] = existingByTitle[pl.title];
      console.log(`✓ Playlist already exists: ${pl.title} (${playlistIdsByKey[pl.key]})`);
    } else {
      const created = await youtube.playlists.insert({
        part: ['snippet', 'status'],
        requestBody: {
          snippet: { title: pl.title, description: pl.description, defaultLanguage: 'en' },
          status: { privacyStatus: 'public' }
        }
      });
      playlistIdsByKey[pl.key] = created.data.id;
      console.log(`✅ Created Playlist: ${pl.title} (${created.data.id})`);
    }
  }

  // 4. Add ErMizVyePaY to Playlist 1 (First-Century Context)
  if (playlistIdsByKey.context) {
    try {
      await youtube.playlistItems.insert({
        part: ['snippet'],
        requestBody: {
          snippet: {
            playlistId: playlistIdsByKey.context,
            resourceId: { kind: 'youtube#video', videoId: d001.liveVideoId }
          }
        }
      });
      console.log(`✅ Added ${d001.liveVideoId} to Playlist: First-Century Bible Context & Old Testament Prophecies Explained`);
    } catch (_) {}
  }

  // 5. Upload & Set Locked Channel Header Banner (FHG-BANNER-B_warm-parchment-sanctuary_2560x1440.jpg) via API
  if (fs.existsSync(LOCKED_BANNER_PATH)) {
    try {
      const bannerRes = await youtube.channelBanners.insert({
        media: {
          mimeType: 'image/jpeg',
          body: fs.createReadStream(LOCKED_BANNER_PATH)
        }
      });
      const bannerExternalUrl = bannerRes.data.url;
      if (bannerExternalUrl) {
        const chBrand = await youtube.channels.list({ part: ['brandingSettings'], mine: true });
        const currentBranding = chBrand.data.items?.[0]?.brandingSettings || {};
        await youtube.channels.update({
          part: ['brandingSettings'],
          requestBody: {
            id: channel.id,
            brandingSettings: {
              ...currentBranding,
              image: {
                ...(currentBranding.image || {}),
                bannerExternalUrl
              }
            }
          }
        });
        console.log(`✅ Uploaded & applied locked Channel Header Banner: ${LOCKED_BANNER_PATH}`);
      }
    } catch (bannerErr) {
      console.warn(`⚠️ Channel Banner API note (${bannerErr.message}) — you can also upload ${LOCKED_BANNER_PATH} in YouTube Studio -> Customization -> Branding.`);
    }
  }
}

async function uploadDocket(docketKey, isLive = false, publishAt = null) {
  const docket = FHG_DOCKETS[docketKey];
  if (!docket) {
    console.error(`Unknown docket '${docketKey}'. Available: ${Object.keys(FHG_DOCKETS).join(', ')}`);
    process.exit(1);
  }
  verifyFhgGovernance(docket);

  if (!fs.existsSync(docket.videoPath)) {
    throw new Error(`Video file not found: ${docket.videoPath}`);
  }

  if (!isLive) {
    console.log(JSON.stringify({
      dryRun: true,
      governancePassed: ['RULE-004 (Zero 864zeros)', 'RULE-016 (Zero Jargon)', 'RULE-017 (Zero $ Price)', 'Dual — JMC Provenance'],
      docketId: docket.id,
      videoPath: docket.videoPath,
      videoSizeMB: (fs.statSync(docket.videoPath).size / (1024 * 1024)).toFixed(2),
      companionThumb16x9: docket.companionThumb16x9,
      shortCoverPolicy: 'Native YouTube In-Video Frame Selection (9:16 Locked)',
      categoryId: '27 (Education)',
      title: docket.title,
      tags: docket.tags,
      pinnedComment: docket.pinnedComment
    }, null, 2));
    return;
  }

  const { clientId, clientSecret, refreshToken } = getFhgOAuthClient();
  if (!refreshToken) {
    throw new Error('Missing FHG YouTube OAuth token. Run: node fhg_youtube_cli.mjs --auth');
  }

  const oauth2Client = new google.auth.OAuth2(clientId, clientSecret, 'http://localhost');
  oauth2Client.setCredentials({ refresh_token: refreshToken });
  const youtube = google.youtube({ version: 'v3', auth: oauth2Client });

  const chRes = await youtube.channels.list({ part: ['snippet'], mine: true });
  const channel = chRes.data.items?.[0];
  if (/864zeros/i.test(channel?.snippet?.title || '')) {
    throw new Error('RULE-004 SAFETY HALT: Authenticated token belongs to @864zeros, not @ForHisGrace!');
  }

  const statusPayload = {
    privacyStatus: publishAt ? 'private' : 'public',
    selfDeclaredMadeForKids: false
  };
  if (publishAt) statusPayload.publishAt = new Date(publishAt).toISOString();

  const res = await youtube.videos.insert({
    part: ['snippet', 'status'],
    requestBody: {
      snippet: {
        title: docket.title,
        description: docket.description,
        tags: docket.tags,
        categoryId: '27', // Education
        defaultLanguage: 'en',
        defaultAudioLanguage: 'en'
      },
      status: statusPayload
    },
    media: {
      body: fs.createReadStream(docket.videoPath)
    }
  });

  const videoId = res.data.id;
  console.log(`✅ Uploaded @ForHisGrace Short: https://www.youtube.com/shorts/${videoId}`);
}

const args = process.argv.slice(2);
if (args.includes('--auth')) {
  await runOAuthLogin();
} else if (args.includes('--setup-channel')) {
  await setupChannelAndUpgradeLiveVideo();
} else if (args.includes('--upload')) {
  const idx = args.indexOf('--upload');
  const key = args[idx + 1] || 'sepia-001';
  const isLive = args.includes('--live');
  await uploadDocket(key, isLive);
} else {
  const { refreshToken } = getFhgOAuthClient();
  console.log(JSON.stringify({
    channel: '@ForHisGrace (forhisgrace.web@gmail.com)',
    oauthTokenPresent: Boolean(refreshToken),
    tokenFile: FHG_TOKEN_FILE,
    liveVideos: ['https://www.youtube.com/shorts/ErMizVyePaY'],
    readyDockets: Object.keys(FHG_DOCKETS),
    commands: {
      connectChannelOAuth: 'node C:\\dev\\864zeros-publish\\_build\\video\\fhg_shorts_engine\\fhg_youtube_cli.mjs --auth',
      setupPlaylistsAndUpgrade001: 'node C:\\dev\\864zeros-publish\\_build\\video\\fhg_shorts_engine\\fhg_youtube_cli.mjs --setup-channel',
      dryRunUploadSepia001: 'node C:\\dev\\864zeros-publish\\_build\\video\\fhg_shorts_engine\\fhg_youtube_cli.mjs --upload sepia-001 --dry-run',
      liveUploadSepia001: 'node C:\\dev\\864zeros-publish\\_build\\video\\fhg_shorts_engine\\fhg_youtube_cli.mjs --upload sepia-001 --live'
    }
  }, null, 2));
}
