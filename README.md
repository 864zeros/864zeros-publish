# 864zeros-publish — The 864zeros Studio

**The 864zeros central content, literary IP, and multimedia vault.** Source-of-truth JSON assets, verified Public Domain provenance locks, and DAM deliverables authored once and *published* to consuming apps across the 864zeros ecosystem (`ClearStreak`, `OIA` Focus Extensions, Practice Books, and standalone products). This repo is the **Studio & Data Layer** sitting alongside the Brain (`864zeros-ISD`) and Body (`864zeros-llc`).

> Machine-readable entry point: **[`index.json`](index.json)** — lists every namespace, provenance lock, and published asset.

## Studio Leadership (`864zeros-publish`)

| Role Code | Executive / Lead | Charter & Responsibility |
|---|---|---|
| **`VP-STUDIO`** | **Sloane Sterling** | VP of Content, Media & Publishing — overall Studio governance, release readiness, and cross-fleet publishing lockstep |
| **`LEAD-MEDIA`** | **Orion Kai** | Head of Multimedia Production — `media/` visual, audio, LoRA, video reels, and product DAM vault |
| **`LEAD-CONTENT`** | **Julian Thorne** | Head of Literary IP, Editorial & Focus Packs — `shared/focus_packs/`, `shared/bible/`, `shared/practice_books/`, `apps/clearstreak/` |
| **`STUDIO-LEGAL`** | **Vera Lindqvist** | Director of IP, Public Domain Clearance & Provenance — `sources/public_domain_classics/PROVENANCE_LOCK.json`, SHA-256 source verification, and clean-room guardrails |

## Principles

1. **JSON is the source of truth.** Any database (`db/`) is a *derived, rebuildable, git-ignored*
   artifact — never authored directly, never a second master. Rebuild it anytime from JSON.
2. **Namespace = ownership boundary.** `shared/` holds ecosystem-generic assets any app may consume;
   `apps/<name>/` holds a single app's published content. A new app is a new folder — no restructure.
3. **Provenance separated from product.** `sources/` keeps the raw public-domain inputs locked by SHA-256 in [`sources/public_domain_classics/PROVENANCE_LOCK.json`](sources/public_domain_classics/PROVENANCE_LOCK.json); `_build/`
   keeps the extractor scripts, style guides, and drafts. Neither is served to apps.
4. **Original 864zeros authorship & Clean-Room Clearance.** All content is re-authored from verified pre-1931 public-domain sources (`17 U.S.C. Public Domain`) and empirical behavioral science (`17 U.S.C. § 102(b)`), enforcing a strict clean-room blacklist against copyrighted modern translations and trademarked pop-book jargon.

## Layout

```
864zeros-publish/
├── index.json                          top-level manifest (Studio leadership, namespaces + assets)
├── shared/
│   ├── focus_packs/                    5 Philosophy & Habit Focus Packs (150 records) + master catalog
│   ├── bible/                          public-domain Bible key-verse library (834 records) + study lessons
│   ├── creative/                       original 864zeros poems, prayers & reflections
│   └── practice_books/                 illustrated daily practice books & workbooks
├── apps/
│   └── clearstreak/                    ClearStreak recovery content (passages, affirmations, taxonomy, reader)
├── media/                              864zeros Central Multimedia & Product DAM Vault (34 products)
├── sources/                            raw PD inputs (not served)
│   └── public_domain_classics/         verified pre-1931 Project Gutenberg texts + PROVENANCE_LOCK.json
├── _build/                             extractor & build scripts, style guides, per-chapter drafts (_src/)
│   ├── build_db.ps1                    JSON → SQLite generator (derived DB)
│   ├── extract_bigbook.ps1
│   └── build_clinical_review.ps1
├── db/                                 generated SQLite (git-ignored; rebuilt from JSON)
└── overview.html                       human-readable library overview
```

## Namespaces

| Namespace | What it is | Docs / Manifest |
|---|---|---|
| `sources/public_domain_classics` | 6 verified pre-1931 Project Gutenberg classic texts (Marcus Aurelius, Epictetus, Seneca, Benjamin Franklin, Aristotle, William James) locked with SHA-256 hashes & clean-room blacklist rules. | [`PROVENANCE_LOCK.json`](sources/public_domain_classics/PROVENANCE_LOCK.json) |
| `shared/focus_packs` | 5 compartmentalized Philosophy & Habit Focus Packs (`30` entries each = `150` curated entries) using `{ id, citation, text, plain, application, focus_theme }` + master catalog indexing all 8 Focus Packs. | [`focus_packs_catalog.json`](shared/focus_packs/focus_packs_catalog.json) |
| `shared/bible` | Complete PD Bible key-verse library. `{ book, chapter, citation, text, plain }`; KJV + WEB, plus Genesis applications & study lessons. | [`BIBLE_LIBRARY.md`](shared/bible/BIBLE_LIBRARY.md) · [`bible_index.json`](shared/bible/bible_index.json) |
| `shared/creative` | 150+ original authored poems, prayers, and reflections with emotional/moment taxonomy. | `shared/creative/` |
| `shared/practice_books` | Illustrated practice workbooks combining PD texts, plain-language renderings, and behavioral reflections. | `shared/practice_books/` |
| `apps/clearstreak` | 130 moment-of-need passages + 100 affirmations + taxonomy + full Big Book reader. **Passages gated on clinical review.** | [`PASSAGES_REPORT.md`](apps/clearstreak/PASSAGES_REPORT.md) |
| `media` & `media/products` | Central Multimedia & Product Asset Vault (DAM) across 34 ecosystem products. | [`MEDIA_HOUSE.md`](media/MEDIA_HOUSE.md) |

## Compartmentalized Focus Packs (`shared/focus_packs/`)

| Pack ID | Title | Entries | Provenance Source |
|---|---|---|---|
| `marcus_aurelius_meditations` | *The Citadel Within: Marcus Aurelius on Daily Self-Command* | 30 | [`marcus_aurelius_meditations.json`](shared/focus_packs/marcus_aurelius_meditations.json) |
| `stoic_masters_epictetus_seneca` | *Sovereign Will: Epictetus & Seneca on Time, Agency, and Focus* | 30 | [`stoic_masters_epictetus_seneca.json`](shared/focus_packs/stoic_masters_epictetus_seneca.json) |
| `ben_franklin_virtues` | *The 13 Virtues Ledger: Benjamin Franklin's Sequential Focus Method* | 30 | [`ben_franklin_virtues.json`](shared/focus_packs/ben_franklin_virtues.json) |
| `aristotle_character` | *Excellence by Repetition: Aristotle's Nicomachean Ethics in Practice* | 30 | [`aristotle_character.json`](shared/focus_packs/aristotle_character.json) |
| `william_james_habit` | *The Neuroplastic Groove: William James's 1890 Maxims of Habit* | 30 | [`william_james_habit.json`](shared/focus_packs/william_james_habit.json) |

## The database (SQLite)

The DB is a **build product**, not a source. To (re)generate it from the JSON:

```powershell
pwsh _build/build_db.ps1        # writes db/store.sql; builds db/store.db if sqlite3 is on PATH
```

Because `db/` is git-ignored, the DB never drifts from the JSON and is never reviewed in a diff —
the JSON is what changes and what ships.

---
*864zeros LLC · The 864zeros Studio · JSON is truth, the DB is derived.*
