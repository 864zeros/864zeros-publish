# 864zeros Modular Content Engine & ClearStreak Companion Architecture

**Version:** `1.0.0`  
**Owner:** 864zeros Publishing House & ClearStreak Engineering  
**Governance:** 100% Local-First Sovereignty · Clean-Room Public Domain Provenance · Zero Metered Cloud Dependencies

---

## 1. System Overview

The **864zeros Modular Content Engine** is a single-source-of-truth publishing and behavioral coaching pipeline that compiles verified pre-1931 Public Domain wisdom and King James Version scripture into three synchronized surfaces:

1. **ClearStreak Affect-Mapped Focus Packs (`data/packs/*.json`)**: Validated against `data/schemas/content_pack.schema.json`, organizing passages across the 6 extended HALT affect states (`HUNGRY`, `ANGRY`, `LONELY`, `TIRED`, `STRESSED`, `HOPELESS`).
2. **5"×8" KDP Softback Companion Journals (`build/journals/*_softback_5x8.html`)**: Physical paperback editions featuring `jeff_sketch style` vector plates, verbatim passages, 864zeros clean-room plain distillations, 12 ruled handwriting lines, optical corner fiducials, and deterministic `864z://cs/entry` QR anchors.
3. **9:16 Vertical Kinetic Video Manifests (`build/video_manifests/*_9x16_reels.json`)**: Two-Pass Visual-DAGR (`jeff_sketch style` → `jeff_painting style`) storyboard and narration timelines.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    864ZEROS MODULAR CONTENT ENGINE                      │
│  sources/public_domain_classics/ + shared/bible/ + shared/creative/     │
└───────────────────┬─────────────────────────┬───────────────────────────┘
                    │                         │
                    ▼                         ▼
     ┌────────────────────────────┐  ┌──────────────────────────────────┐
     │  data/packs/*.json         │  │  Visual LoRA & Voice Verifier    │
     │  (6 HALT Affect Triggers)  │  │  864z_jeff_sketch_v1.safetensors │
     └──────┬──────────────┬──────┘  └────────────────┬─────────────────┘
            │              │                          │
            ▼              ▼                          ▼
┌───────────────────┐ ┌──────────────────────┐ ┌──────────────────────────┐
│ 5"x8" Print Book  │ │ 9:16 Video Reels     │ │ ClearStreak Edge App     │
│ + Vector QR Codes │ │ Storyboard Manifests │ │ Offline QR + 3-Tier OCR  │
└─────────┬─────────┘ └──────────────────────┘ └────────────▲─────────────┘
          │                                                 │
          └────── Physical Handwritten Page Scan ───────────┘
            864z://cs/entry?book=...&page=...&trigger=...&ref=...
```

---

## 2. Clean-Room & Provenance Architecture

All content packs enforce strict separation between **Public Domain Verbatim Text** (`text`) and **Original 2026 864zeros Authorship** (`plain`, `reflection_prompt`, `micro_action`):

- **Pre-1931 Public Domain Lock**: Only editions published prior to January 1, 1931 (17 U.S.C. Public Domain) or Crown/Public Domain KJV (1611/1769) are ingested.
- **Zero Prohibited Translators**: Modern copyrighted translators (e.g., Gregory Hays, Robin Waterfield, Ryan Holiday) are strictly blocked at build time.
- **Zero Pop-Habit Jargon**: Banned commercial buzzwords, mythical day-count tropes, and prohibited terms are rejected automatically by `src/generators/pack_builder.py`.

---

## 3. Physical-to-Digital Bridge & Sovereign Data Custody

When a reader scans a physical 5"×8" Companion Journal page with the ClearStreak mobile app:

1. **Offline QR Resolution (`< 18 ms`)**: Extracts `book`, `page`, `trigger`, and `ref` directly from the printed `29×29` vector QR code without network calls.
2. **Perspective Homography (`< 12 ms`)**: Aligns the four corner fiducials (`fid-tl`, `fid-tr`, `fid-bl`, `fid-br`) to crop the 12 ruled handwriting lines (`y = 3.40in .. 6.25in`).
3. **3-Tier Hardware Capability Cascade (`src/ocr/litert_pipeline.py`)**: Routes handwriting extraction based on physical device RAM and NPU/GPU availability (`Tier A >= 8GB RAM`, `Tier B 4GB–6GB RAM`, `Tier C < 4GB RAM`).
4. **Sovereign Cloud Offload (User-Owned Google Drive Only)**: Backups and Tier C asynchronous image storage use the user's own Google account via OAuth (`drive.appdata` / user folder)—never touching 864zeros servers or metered third-party APIs.
