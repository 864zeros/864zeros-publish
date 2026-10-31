# 864zeros Media House — Directory & Asset Architecture

The **864zeros-publish** repository serves as the centralized content, literary IP, and multimedia production store for the entire 864zeros ecosystem.

---

## Departmental Directory Layout

```
864zeros-publish/
│
├── shared/                                 # AUTHORITATIVE LITERARY IP
│   ├── bible/                              # 66 Books Scripture, Study Lessons, Applications
│   ├── creative/                           # 100% Original 864zeros Creative Works
│   │   ├── poems/                          # 150+ Authored Poems (JSON + MD)
│   │   ├── prayers/                        # Authored Prayers (Moment/Emotion Tagged)
│   │   └── reflections/                    # Essays, Meditations, Devotionals
│   └── apps/clearstreak/                   # Recovery Passages & Affirmations
│
├── media/                                  # MULTIMEDIA ASSETS
│   │
│   ├── audio/                              # AUDIO ASSET VAULT
│   │   ├── voices/                         # Spoken word poems, prayer readings, scripture VO
│   │   ├── music/                          # Ambient beds, acoustic tracks, melodic loops
│   │   ├── sfx/                            # Sound effects (rain, pages, chimes, risers)
│   │   └── masters/                        # Final mixed audio tracks (Podcasts, Drips)
│   │
│   ├── visuals/                            # VISUAL ART & LORA VAULT
│   │   ├── training_pools/                 # Raw datasets for LoRA training
│   │   │   ├── sketches/                   # Pure sketch images dataset (157 pool)
│   │   │   ├── paintings/                  # Pure painting images dataset
│   │   │   └── illustrations/              # Digital/graphic illustration dataset
│   │   ├── lora_weights/                   # Trained .safetensors style models
│   │   └── rendered_art/                   # Generated high-res art paired to content
│   │
│   ├── graphics/                           # DESIGN & BRANDING
│   │   ├── branding/                       # Logos, watermarks, icons, badges
│   │   ├── templates/                      # Social post frames, quote templates
│   │   └── covers/                         # Book covers, album art, thumbnails
│   │
│   ├── photography/                        # STILL IMAGERY & TEXTURES
│   │   ├── references/                     # Composition reference images
│   │   └── textures/                       # Paper grains, canvas textures, overlays
│   │
│   └── video/                              # VIDEO & MOTION
│       ├── b_roll_loops/                   # Curated 9:16 vertical video loops
│       │   └── fhg_veo/                    # Veo 3/3.1 Judean loops + jesus/ character-locked motion clips
│       ├── fhg_shorts/                     # 864zGenStudioNow FHG Bible Shorts Production Vault
│       │   ├── BUILD_SPEC_FHG_SHORTS.md    # 2026 FHG Shorts Master Build Specification
│       │   ├── plates/
│       │   │   ├── jesus_character_pack/   # Locked First-Century Jesus turnaround & pose plates (a4jyww -> xyl7h6)
│       │   │   ├── sketches/               # Ink-wash & parchment outline plates
│       │   │   └── stills/                 # Jerusalem Second Temple, ancient street & Galilee keyframe stills
│       │   ├── storyboards/                # .ass active-word captions (X=468, Y<=1100) & QA milestone frames
│       │   └── rendered_reels/             # Final 1080x1920 @ 60fps (-crf 18, -14 LUFS) MP4 Shorts
│       ├── storyboards/                    # 660 JSON video scripts & timing data
│       └── rendered_reels/                 # Final compiled 9:16 MP4s
│
├── _build/                                 # AUTOMATION & PIPELINES
│   ├── lora/                               # Image captioning (.txt) & training tools
│   ├── audio/                              # Batch audio mixing & TTS generation
│   ├── video/                              # Bridge to supo-c1-p kinetic caption rendering
│   └── build_db.ps1                        # SQLite database compiler
│
└── sources/                                # RAW INGESTION & INBOX
    ├── google_photos_inbox/                # Raw sketch & photo downloads
    └── raw_writings_inbox/                 # Raw email text drops & Google Docs exports
```

---

## Canonical Linkage Standard

Every literary work (poem, prayer, lesson) links to its media siblings via structured JSON:

```json
{
  "id": "poem_042",
  "title": "Quiet Surrender",
  "author": "864zeros",
  "category": "Surrender & Peace",
  "text": "...",
  "assets": {
    "illustration": "media/visuals/rendered_art/poem_042.png",
    "narration": "media/audio/voices/poem_042_narration.wav",
    "video_reel": "media/video/rendered_reels/poem_042_reel.mp4"
  }
}
```

---

## Foundation Model Service Registry (`BRK-MEDIA-004` / `864zGenStudioNow`)

| Modality | Models | Studio Capability | Routing & Cost Governance |
|---|---|---|---|
| **Video (`Veo 3 / 3.1 / 2.0`)** | `veo-3.0-generate-preview`<br>`veo-3.1-generate-preview`<br>`veo-2.0-generate-001` | • **Image-to-Video:** `9:16` & `16:9` plate animation<br>• **First-to-Last Frame (`image` + `last_frame`):** Pose-to-pose interpolation (e.g., `a4jyww` $\rightarrow$ `xyl7h6`)<br>• **Reference Ingredients (`reference_images`):** 1–3 turnaround sheets for 100% character lock | **Google Flow Web App** (`jeff.m.conn@gmail.com` AI Ultra subscription credits = **`$0` marginal cost**) for bulk video generation; Vertex AI (`oia-age-backend`) reserved for targeted automation. |
| **Image & Retouching** | `imagen-3.0-generate-002`<br>`imagen-3.0-capability-001`<br>`gemini-2.5-flash-image-preview` | Multi-angle character turnarounds, First-Century inpainting/retouching, and photoreal-to-charcoal/ink sketch restyling | Metered Vertex AI (`project: oia-age-backend`) / Gemini API or AI Ultra Web Studio. |
| **Audio & Voice** | `lyria-002`<br>`Chirp 3 HD`<br>`Kokoro-82M` | `432Hz` instrumental ambient beds, micro-Foley layering, and `165–175 WPM` close-mic baritone narration (`-14 LUFS`) | Local `Kokoro-82M` / Neural Baritone + metered Google Cloud TTS / Vertex AI (`oia-age-backend`). |
