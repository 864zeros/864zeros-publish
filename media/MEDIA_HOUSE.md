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
