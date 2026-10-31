# 864zeros & ForHisGrace — Master Media DAM Taxonomy, Visual Filter Definitions & Asset Metadata Schema

- **Document ID:** `DIV0-DAM-001`
- **Owners:** Zane Fields (`CTO-001`), Sloane Sterling (`STUDIO-001`), Orion Kai (`MEDIA-001`), Prya Vance (`GTM-001`)
- **Canonical Sources:**
  - [`C:\dev\864zeros-publish\media\visuals\FHG_VISUAL_SPEC_REGISTRY.json`](file:///C:/dev/864zeros-publish/media/visuals/FHG_VISUAL_SPEC_REGISTRY.json)
  - [`C:\dev\864zeros-publish\_build\tools\apply_fhg_human_filter.py`](file:///C:/dev/864zeros-publish/_build/tools/apply_fhg_human_filter.py)
  - [`C:\dev\864zeros-publish\media\products\`](file:///C:/dev/864zeros-publish/media/products/)

---

## 1. Brand & Pillar Identifiers (`brand` & `pillar`)

Every media asset, video, image, audio file, and library document in the ecosystem is tagged at the root level with a **Brand Namespace** (`[FHG]` vs `[864Z]`) and a **Division Pillar Code**:

| Brand Prefix | Brand Code | Pillar Code | Entity / Scope | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`[FHG]`** | `FHG` | `FHG-SANCTUARY` | **For His Grace (`forhisgrace.com`)** | Biblical sanctuary, 1,189-chapter Bible study & trivia, 27 Biblical Animals, 100-plate visual series (`3,760` variations), meditations, poetry, and scripture Shorts/videos. |
| **`[864Z]`** | `864Z` | `864F` | **864zeros Factory (`LLC-DIV-3-FACTORY`)** | 19 Google Workspace Add-ons, Chrome/Edge Browser Extensions (`VaultPilot`, `AutoOrganize`, `LinkLater`, `OmniClip`, `SnapLabel`, etc.). |
| **`[864Z]`** | `864Z` | `OIA` | **OIA Cognitive & Focus Suite** | Attention & neuro-divergent productivity tools (`oia-focus-note`, `oia-focus-wall`, `Time2Focus`, `TuneOut2FocusIn`, `Signal2Noise`, `DataNap`). |
| **`[864Z]`** | `864Z` | `CS` | **ClearStreak Mobile (`clearstreak`)** | Sovereign Android habit & streak tracker mobile application. |
| **`[864Z]`** | `864Z` | `864Z-CORP` | **864zeros Corporate & Executive** | Corporate website (`864zeros-web`), Pixel Office (`864zeros-pixel-office`), Executive `LIBRARY/` (`00-Kate` through `05-*`), and `LLC-DIV-0-IT-INFRASTRUCTURE`. |

---

## 2. Visual Style & Filter Pipeline Definitions (`jeff_sketch`, `B1`, `G1–G5`, `S1–S5`, `C1–C4`, `NB`)

Implemented in [`apply_fhg_human_filter.py`](file:///C:/dev/864zeros-publish/_build/tools/apply_fhg_human_filter.py) and [`FHG_VISUAL_SPEC_REGISTRY.json`](file:///C:/dev/864zeros-publish/media/visuals/FHG_VISUAL_SPEC_REGISTRY.json), the cross-division visual pipeline transforms base sketches through **6 deterministic stages**:

### 2.1 Stage 0 — Base Generation & Canonical Signature (`jeff_sketch`)

| Identifier | Name | Technical Specification |
| :--- | :--- | :--- |
| **`jeff_sketch`** | **Founder Fountain-Pen Base Style / LoRA** | Weights: [`864z_jeff_sketch_v1.safetensors`](file:///C:/dev/864zeros-publish/media/visuals/lora_weights/864z_jeff_sketch_v1.safetensors). Freehand black/sepia fountain-pen contour drawing on warm cream parchment (`#F5EFE2` / `#F5F1E8`). Expressive calligraphic line-weight modulation with bold outer silhouette contours and delicate interior lines. Humans are depicted **strictly from the back** (zero facial features). |
| **`_base`** | **Unfiltered Base Draft (`_base.jpg`)** | Raw Stage 0 generation output prior to geometry straightening, blotch prepass, or color printmaking filters. |
| **`jeff_sig`** | **Canonical Bottom-Right Signature Lock** | Asset: [`jeff_canonical_signature.png`](file:///C:/dev/864zeros-publish/media/visuals/jeff_canonical_signature.png). Always stamped **last** (Stage 5) at bottom-right (`width_ratio = 0.18w`, `x_right = 0.942w`, `y_bottom = 0.971h`) with `MaxFilter(7) + GaussianBlur(4.0)` parchment halo clearing. |

---

### 2.2 Stage 1 — Blotchy Sumi-e Ink-Wash Prepass (`B1`)

| Identifier | File Token | Function & Algorithm |
| :--- | :--- | :--- |
| **`B1`** | `_b1_g2_s2.jpg` | `apply_blotch_prepass()` — Clears the outer `5.8%` parchment margin and converts translucent washes or contour line clusters into 3-tier sumi-e charcoal brush daubs (`deep_black`, `dark_gray`, `mid_gray`, `ambient_pool`). |

---

### 2.3 Stage 2 — Geometry Stroke-Straightening Ladder (`G1` – `G5`)

Algorithm: **Vectorized Zhang-Suen 1-pixel skeletonization** followed by **Ramer-Douglas-Peucker (RDP)** per-stroke polyline chord simplification (`apply_geometric_transform()`):

| Code | RDP `epsilon` (`px`) | Corner `overshoot_px` | File Suffix | Visual Definition & Use Case |
| :--- | :---: | :---: | :--- | :--- |
| **`G1`** | `0.0 px` | `0.00 px` | `_g1.jpg` | **Natural Freehand Curves:** Unmodified organic curves (`0px` chord simplification). |
| **`G2`** | `2.5 px` | `0.15 px` | `_g2_s2.jpg` | **★ LOCKED DEFAULT — Subtle Chiseled Curves:** Retains organic contour flow while introducing subtle chiseled straight segments (`2.5px` tolerance). |
| **`G3`** | `5.5 px` | `0.35 px` | `_g3.jpg` | **Planar Straight-Line Draftsmanship:** Medium architectural planar faceting (`5.5px` tolerance). |
| **`G4`** | `9.5 px` | `0.65 px` | `_straight_g4.jpg` | **Bold Angular Straight-Edge Strokes:** Converts organic curves into bold `9.5px` straight-edge segments with crisp corner overshoots. |
| **`G5`** | `16.0 px` | `1.10 px` | `_g5.jpg` | **Architectural Straight-Chord Abstraction:** High-polygon geometric abstraction (`16.0px` chord tolerance). |

---

### 2.4 Stage 3 — Humanizer & Nib-Tooth Smudge Filter Ladder (`S1` – `S5`)

Algorithm: **Perlin/Simplex `feTurbulence` displacement** (fountain-pen nib tooth) + **anisotropic directional Gaussian charcoal blur & paper haze** (`apply_humanizer_ladder()`):

| Code | Preset Name | `freq` | `octaves` | `scale` | `blur_x, blur_y` | `haze` | `smear` | Visual Definition & Locked Standard |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S1`** | `stage1_algorithmic` | `0.045` | `1` | `0.0` | `(0.0, 0.0)` | `0.00` | `0.0` | **Pure Algorithmic Vector Line:** Zero displacement or smudge. |
| **`S2`** | `stage2_master` | `0.045` | `3` | `1.8` | `(0.0, 0.0)` | `0.00` | `0.0` | **★ LOCKED STANDARD (Nature, Architecture & Animals — `fhg_sketch_spec`):** Authentic fountain-pen nib tooth on cold-press parchment with crisp unblurred ink edges (`G2 + S2`). |
| **`S3`** | `stage3_apprentice` | `0.035` | `3` | `3.8` | `(1.5, 1.0)` | `0.35` | `0.0` | **★ LOCKED STANDARD (Humans Seen from Back — `fhg_sketch_people_spec`):** Stronger organic nib jitter plus soft directional charcoal diffusion (`G2 + S3`). |
| **`S4`** | `stage4_student` | `0.025` | `3` | `7.5` | `(5.0, 2.2)` | `0.45` | `6.0` | **Expressive Charcoal Smudge:** Heavy nib displacement with horizontal thumb-smudge trails (`smear=6.0`). |
| **`S5`** | `stage5_raw` | `0.018` | `4` | `14.5` | `(9.0, 3.8)` | `0.60` | `12.0` | **Raw Atmospheric Storm Wash:** Maximum turbulence and heavy charcoal/ink storm diffusion (`smear=12.0`). |

---

### 2.5 Stage 4 — Color Printmaking Filter Ladder (`C1` – `C4`)

Algorithm: **Morphological 3-tier tonal separation** (`MaxFilter(5)` anti-alias fringe guard) + **angled 2D Risograph halftone dot screens** (`halftone_screen`) + **automatic skyline Ukiyo-e bokashi woodblock gradient** (`compute_sky_bokashi_mask`):

| Code | Aliases | Favorite | File Suffix | Palette & Printmaking Specification |
| :--- | :--- | :---: | :--- | :--- |
| **`C1`** | `PY1`, `RISO_TERRA_PINE` | — | `_c1_riso_terra_pine.jpg` | **Dual-Tone Earth Risograph:** Angled Terracotta Clay (`35°`) & Sage-Slate (`75°`) halftone dot screens with Deep Forest Pine primary contours. |
| **`C2`** | `PY2`, `RISO_EARTH` | **★ FAV #1** | `_c2_riso_earth.jpg` | **3-Color Earth Risograph:** Golden Ochre (`18°`), Sage Olive (`52°`), and Terracotta Rust (`78°`) halftone screens with Raw Umber primary linework. |
| **`C3`** | `PY3`, `UKIYOE_RISO` | **★ FAV #2** | `_c3_ukiyoe_riso.jpg` | **Ukiyo-e Woodblock × Earth-Tone Risograph Hybrid:** Framed Terracotta-Amber skyline bokashi fade above the top contour ridge + 3-color Earth Risograph halftone screens below. |
| **`C4`** | `PY4`, `UKIYOE_PRUSSIAN` | — | `_c4_ukiyoe_prussian.jpg` | **Classic Ukiyo-e Prussian Blue Woodblock:** Top-down Hokusai Prussian Blue (`#183858`) bokashi sky fade + mineral woodblock pigment tints. |

---

### 2.6 Scribble Passes & The 8 Locked Non-Blotch (`NB`) Editions (`19` Total Variants per Plate)

Every canonical FHG visual subject generates **19 plate files** (`11` core blotch/structural passes + `8` locked Non-Blotch `NB` editions):

| Variant Code | File Suffix | Upstream Input | Filter Applied | Description |
| :--- | :--- | :--- | :--- | :--- |
| `base` | `_base.jpg` | Stage 0 | None | Raw fountain-pen & wash draft |
| `g2_s2` | `_g2_s2.jpg` | `_base.jpg` | `G2 + S2` | Chiseled contour + fountain-pen nib tooth |
| `straight_g4` | `_straight_g4.jpg` | `_base.jpg` | `G4` | Planar `9.5px` straight-edge strokes |
| `b1_g2_s2` | `_b1_g2_s2.jpg` | `_base.jpg` | `B1 + G2 + S2` | Sumi-e blotchy ink-wash + chiseled contour |
| `c1_riso_terra_pine` | `_c1_riso_terra_pine.jpg` | `_b1_g2_s2.jpg` | `C1` | Blotchy B1 × Dual-Tone Terra/Pine Risograph |
| `c2_riso_earth` | `_c2_riso_earth.jpg` | `_b1_g2_s2.jpg` | `C2` | Blotchy B1 × 3-Color Earth Risograph (★ Fav #1) |
| `c3_ukiyoe_riso` | `_c3_ukiyoe_riso.jpg` | `_b1_g2_s2.jpg` | `C3` | Blotchy B1 × Ukiyo-e Riso Hybrid (★ Fav #2) |
| `c4_ukiyoe_prussian` | `_c4_ukiyoe_prussian.jpg` | `_b1_g2_s2.jpg` | `C4` | Blotchy B1 × Prussian Blue Ukiyo-e Woodblock |
| `loop_scr` | `_loop_scr.jpg` | `G2 + B1 delta` | Loop Coils | Continuous fountain-pen circular scribble coils |
| `xhatch_scr` | `_xhatch_scr.jpg` | `G2 + B1 delta` | Cross-Hatch | 3-tier (`-48° / -132° / -12°`) cross-hatching |
| `sub_scr` | `_sub_scr.jpg` | `G2 + B1` | Subtractive P3 | Search ribbons + darkened silhouettes + negative-space erasure |
| **`nb_loop_c3`** | `_nb_loop_c3.jpg` | `_loop_scr.jpg` | **`NB + C3`** | **★ LOCKED EDITION #1 (DEFAULT HERO): Loop Scribble × Ukiyo-e Riso (`C3`)** |
| **`nb_loop_c4`** | `_nb_loop_c4.jpg` | `_loop_scr.jpg` | **`NB + C4`** | **LOCKED EDITION #2:** Loop Scribble × Prussian Woodblock (`C4`) |
| **`nb_line_c3`** | `_nb_line_c3.jpg` | `_g2_s2.jpg` | **`NB + C3`** | **LOCKED EDITION #3:** Pure Contour (`G2`) × Ukiyo-e Riso (`C3`) |
| **`nb_line_c4`** | `_nb_line_c4.jpg` | `_g2_s2.jpg` | **`NB + C4`** | **LOCKED EDITION #4:** Pure Contour (`G2`) × Prussian Woodblock (`C4`) |
| **`nb_base_c3`** | `_nb_base_c3.jpg` | `_base.jpg` | **`NB + C3`** | **LOCKED EDITION #5:** Clean Base × Ukiyo-e Riso (`C3`) |
| **`nb_base_c4`** | `_nb_base_c4.jpg` | `_base.jpg` | **`NB + C4`** | **LOCKED EDITION #6:** Clean Base × Prussian Woodblock (`C4`) |
| **`nb_sub_c3`** | `_nb_sub_c3.jpg` | `_sub_scr.jpg` | **`NB + C3`** | **LOCKED EDITION #7:** Subtractive P3 × Ukiyo-e Riso (`C3`) |
| **`nb_xhatch_g2`** | `_nb_xhatch_g2.jpg` | `_xhatch_scr.jpg` | **`NB + G2 + S2`** | **LOCKED EDITION #8:** 3-Tier Cross-Hatch × Chiseled Contour (`G2`) |

---

## 3. Product Types, Product Slugs & Names (`36` Cataloged Products + FHG Collections)

### 3.1 Product Type Identifiers (`product_type`)

| `product_type` Code | Platform / Distribution Channel | Description |
| :--- | :--- | :--- |
| `google-workspace-addon` | Google Workspace Marketplace (`Apps Script`) | 19 sovereign Workspace Add-ons for Forms, Sheets, Docs, Slides, Drive, Gmail, and YouTube. |
| `browser-extension-cws-edge` | Chrome Web Store & Microsoft Edge Add-ons (`MV3`) | Local-first Chromium browser extensions (`864F` & `OIA` pillars). |
| `mobile-app-android` | Google Play Store (`Kotlin / Android`) | Sovereign Android mobile applications (`clearstreak`). |
| `sanctuary-content-pack` | `forhisgrace.com` / YouTube / Print & Digital | FHG Bible Study, 27 Biblical Animals, 100 Visual Plates, Practice Books, Poetry, and Scripture Shorts. |
| `corporate-platform` | `864zeros.com` / Internal Operations | Corporate web presence, Pixel Office, and Executive Library. |

### 3.2 Complete Product Slug & Prefix Registry (`C:\dev\864zeros-publish\media\products\`)

| Product Slug (`product_slug`) | Product Name (`product_name`) | `product_type` | `pillar` | License Prefix |
| :--- | :--- | :--- | :--- | :---: |
| `approvalworkflow` | ApprovalWorkflow — Multi-Stage Document & Sheet Sign-Off | `google-workspace-addon` | `864F` | `AW` |
| `choiceguard` | ChoiceGuard — Dynamic Form Choice Limiter & Gatekeeper | `google-workspace-addon` | `864F` | `CG` |
| `docwatermarker` | DocWatermarker — Batch Confidential & Draft Stamp Engine | `google-workspace-addon` | `864F` | `DW` |
| `drivedrop` | DriveDrop — Secure External File Request & Intake Portal | `google-workspace-addon` | `864F` | `DD` |
| `drivesweep` | DriveSweep — Duplicate, Orphan & Quota Cleaner for Drive | `google-workspace-addon` | `864F` | `DS` |
| `drivevault` | DriveVault — Zero-Knowledge Client-Side Drive Encryption | `google-workspace-addon` | `864F` | `DV` |
| `form2docx` | Form2Docx — Instant Document & PDF Assembly from Forms | `google-workspace-addon` | `864F` | `FD` |
| `formnotifier` | FormNotifier — Conditional Multi-Recipient Routing & Alerts | `google-workspace-addon` | `864F` | `FN` |
| `formqr` | FormQR — High-Resolution Pre-Filled QR Code Generator | `google-workspace-addon` | `864F` | `FQ` |
| `formtimer` | FormTimer — Proctored Countdown & Auto-Close Gatekeeper | `google-workspace-addon` | `864F` | `FT` |
| `mailsyncshield` | MailSyncShield — Outbound Domain DLP & Attachment Guard | `google-workspace-addon` | `864F` | `MS` |
| `migration-pilot` | MigrationPilot — Cross-Tenant Drive & Permission Auditor | `google-workspace-addon` | `864F` | `MP` |
| `rowarchiver` | RowArchiver — Automated Sheet Rolling Archive & Ledger | `google-workspace-addon` | `864F` | `RA` |
| `sheet2calendar` | Sheet2Calendar — Two-Way Bulk Event & Roster Sync | `google-workspace-addon` | `864F` | `SC` |
| `sheet2webhook` | Sheet2Webhook — Outbound HMAC Webhook Dispatcher | `google-workspace-addon` | `864F` | `SW` |
| `sheetsync` | SheetSync — Cross-Workbook Master-Child Range Synchronizer | `google-workspace-addon` | `864F` | `SS` |
| `signroute` | SignRoute — Sequential Cryptographic Approval Ledger | `google-workspace-addon` | `864F` | `SR` |
| `slidebuilder` | SlideBuilder — Sheet-to-Deck Automated Presentation Engine | `google-workspace-addon` | `864F` | `SB` |
| `tubeschedule` | TubeSchedule — Sovereign YouTube Publishing & Metadata Planner | `google-workspace-addon` | `864F` | `TS` |
| `autoorganize-ytm` | AutoOrganize — YouTube Music & Playlist Intelligence | `browser-extension-cws-edge` | `864F` | `AO` |
| `vaultpilot` | VaultPilot — Local-First Bookmark & Knowledge Vault | `browser-extension-cws-edge` | `864F` | `VP` |
| `link-later` | LinkLater — Zero-Cloud Read-Later & Obsidian Clipper | `browser-extension-cws-edge` | `864F` | `LL` |
| `omniclip` | OmniClip (`clipboard`) — Universal Multi-Slot Local Clipboard | `browser-extension-cws-edge` | `864F` | `OC` |
| `snaplabel` | SnapLabel — Instant Annotated Screenshot & QA Bug Docket | `browser-extension-cws-edge` | `864F` | `SL` |
| `tab-stasher` | TabStasher — Zero-Memory Session & Workspace Freezer | `browser-extension-cws-edge` | `864F` | `TB` |
| `who-is-watching` | WhoIsWatching — Real-Time Tracker, WebRTC & Canvas Auditor | `browser-extension-cws-edge` | `864F` | `WW` |
| `864z-chronicle` | 864z Chronicle — Local Activity & Session Historian | `browser-extension-cws-edge` | `864F` | `CH` |
| `Bible-Insight` | Bible Insight — Instant Cross-Reference & Commentary Overlay | `browser-extension-cws-edge` | `FHG-SANCTUARY` | `BI` |
| `oia-focus-note` | OIA Focus Note — Distraction-Free Floating Scratchpad | `browser-extension-cws-edge` | `OIA` | `FN` |
| `oia-focus-wall` | OIA Focus Wall — Impulse Site Shield & Deep-Work Gate | `browser-extension-cws-edge` | `OIA` | `FW` |
| `Time2Focus` | Time2Focus — Visual Pomodoro & Task Timebox Engine | `browser-extension-cws-edge` | `OIA` | `TF` |
| `TuneOut2FocusIn` | TuneOut2FocusIn — Algorithmic Brown/Pink Noise & Binaural Rig | `browser-extension-cws-edge` | `OIA` | `TO` |
| `Signal2Noise` | Signal2Noise — Feed Declutterer & Algorithmic Detox | `browser-extension-cws-edge` | `OIA` | `SN` |
| `DataNap` | DataNap — Auto-Suspend Idle Tabs & RAM Reclaimer | `browser-extension-cws-edge` | `OIA` | `DN` |
| `clearstreak` | ClearStreak — Sovereign Offline Habit & Streak Tracker | `mobile-app-android` | `CS` | `CS` |

---

## 4. Media Types (`media_type`) & Functional Asset Uses (`asset_use`)

Every file in the DAM is classified by both its **Format Category (`media_type`)** and its **Functional Role (`asset_use`)**:

| `media_type` | `asset_use` Code | File Pattern / Dimensions | Functional Purpose |
| :--- | :--- | :--- | :--- |
| `image` / `vector` | `product-icon` | `<slug>.png`, `store-icon.png`, `<slug>.svg` (`128x128`, `32x32`) | Official product brand icon for CWS, Edge, GWM, and store cards. |
| `image` | `product-snapshot` | `<slug>-1.png` .. `<slug>-5.png` (`1280x800`) | Store listing UI screenshots demonstrating core product workflows. |
| `image` | `store-promo-tile` | `<slug>-promo-440x280.png`, `marquee-1400x560.png` | Chrome Web Store / Edge Add-ons promotional tiles. |
| `image` | `video-thumbnail` | `<slug>-thumbnail.png`, `thumbnail-<slug>-social-*.png` | 16:9 (`1280x720`) or 9:16 (`1080x1920`) YouTube & store poster frames. |
| `video` | `video-master-demo` | `<slug>-master.mp4` (`1920x1080`, 30–60s) | Primary widescreen product demonstration video (`RULE-017` compliant: zero prices). |
| `video` | `video-social-short-pain` | `<slug>-social-pain.mp4` (`1080x1920`, 15–30s) | Vertical 9:16 YouTube Short / Reel targeting user pain points. |
| `video` | `video-social-short-price` | `<slug>-social-price.mp4` (`1080x1920`, 15–30s) | Vertical 9:16 YouTube Short / Reel highlighting zero-subscription sovereignty. |
| `video` | `video-fhg-sanctuary` | `fhg_short_*.mp4`, `psalm*.mp4`, `animal_*.mp4` | ForHisGrace scripture meditation videos, animal Shorts, and visual loops. |
| `image` | `art-plate-variation` | `study_*_<variant>.jpg`, `verse_*_<variant>.jpg` | FHG 19-variant visual art plates (`jeff_sketch`, `B1`, `G1–G5`, `S1–S5`, `C1–C4`, `NB`). |
| `image` | `character-or-animal-pack` | `fhg-animals/*`, `practice_book/lesson_*.jpg` | Biblical animal illustrations, practice book plates, and character studies. |
| `audio` | `audio-voice-narration` | `media/audio/voices/*.wav`, `*.mp3` | Spoken TTS narration stems for product demos and scripture readings. |
| `audio` | `audio-music-bed` | `media/audio/music/*.wav`, `*.mp3` | Ambient instrumental backing tracks and sanctuary music beds. |
| `audio` | `audio-sfx` | `media/audio/sfx/*.wav`, `*.mp3` | UI transition chimes and acoustic sound effects. |
| `document` | `library-governance-doc` | `LIBRARY/**/*.md`, `*.pdf`, `youtube.md`, `manifest.json` | Executive playbooks, board decisions, YouTube metadata dockets, and DAM manifests. |

---

## 5. Custom Asset Metadata Architecture (Google Drive API + Local Catalog)

Yes — we attach **rich custom metadata** to **every single asset** in two synchronized places:

### 5.1 Google Drive v3 API Native Metadata (`appProperties` + `description`)
When [`sync-gdrive-media.mjs`](file:///C:/dev/864z-cli/scripts/sync-gdrive-media.mjs) uploads or updates any file in Google Drive, it writes:

1. **`appProperties` (Machine-Queryable Key-Value Pairs on the Drive File Object):**
   ```json
   {
     "brand": "FHG",
     "pillar": "FHG-SANCTUARY",
     "product_type": "sanctuary-content-pack",
     "product_slug": "forhisgrace-art-series",
     "media_type": "image",
     "asset_use": "art-plate-variation",
     "visual_style": "jeff_sketch",
     "filter_code": "nb_loop_c3",
     "geometry_stage": "G2",
     "humanizer_stage": "S2",
     "color_stage": "C3",
     "source_repo": "forhisgrace-web"
   }
   ```
2. **`description` (Human-Readable "Asset Passport" Indexed by Google Drive Search):**
   Every file's Google Drive Info Panel (`description`) is populated with a structured block so you can type `nb_loop_c3`, `product-snapshot`, `choiceguard`, `C3`, or `FHG` directly into the Google Drive or YouTube Studio search bar and immediately find matching assets:
   ```text
   [864zeros DAM Asset Passport]
   Brand: FHG (For His Grace) | Pillar: FHG-SANCTUARY
   Product Type: sanctuary-content-pack | Product: forhisgrace-art-series
   Media Type: image | Asset Use: art-plate-variation
   Visual Style: jeff_sketch | Variant: nb_loop_c3 (Loop Scribble x Ukiyo-e Riso C3 Hero)
   Filter Ladder: Geometry=G2 | Humanizer=S2 | Color=C3 | Blotch=NB (Non-Blotch)
   Source Path: forhisgrace-web/sketches/study_weather_05_morning_mist_dew_nb_loop_c3.jpg
   ```

### 5.2 Master Local & Cloud Asset Catalog (`DAM_ASSET_CATALOG.json`)
Every run of the DAM indexer / Google Drive sync also writes a complete JSON & Markdown summary catalog to:
- `C:\dev\864zeros-llc\LLC-DIV-0-IT-INFRASTRUCTURE\telemetry\DAM_ASSET_CATALOG_SUMMARY.md`
- `C:\dev\864zeros-llc\IGNORE\DAM_ASSET_CATALOG.json`
- Google Drive `864zeros-Ecosystem-DAM/00_DAM_TAXONOMY_AND_ASSET_CATALOG.md`
