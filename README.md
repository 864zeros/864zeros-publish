# 864zeros-publish

**The 864zeros central content / data store.** Source-of-truth JSON assets, authored once and
*published* to consuming apps across the 864zeros ecosystem. This repo is a **data layer** — not an
app, not governance — sitting alongside the Brain (`864zeros-ISD`) and Body (`864zeros-llc`).

> Machine-readable entry point: **[`index.json`](index.json)** — lists every namespace and its assets.

## Principles

1. **JSON is the source of truth.** Any database (`db/`) is a *derived, rebuildable, git-ignored*
   artifact — never authored directly, never a second master. Rebuild it anytime from JSON.
2. **Namespace = ownership boundary.** `shared/` holds ecosystem-generic assets any app may consume;
   `apps/<name>/` holds a single app's published content. A new app is a new folder — no restructure.
3. **Provenance separated from product.** `sources/` keeps the raw public-domain inputs; `_build/`
   keeps the extractor scripts, style guides, and drafts. Neither is served to apps.
4. **Original 864zeros authorship.** All content is re-authored from public-domain sources — which
   *resolves* the copyright question rather than creating one. IP posture is documented per namespace.

## Layout

```
864zeros-publish/
├── index.json              top-level manifest (namespaces + assets)
├── shared/
│   └── bible/              public-domain Bible key-verse library (834 records, 66 books)
├── apps/
│   └── clearstreak/        ClearStreak recovery content (passages, affirmations, taxonomy, reader)
├── sources/                raw PD inputs (PDF / EPUB / docx) — provenance, not served
├── _build/                 extractor & build scripts, style guides, per-chapter drafts (_src/)
│   ├── build_db.ps1        JSON → SQLite generator (derived DB)
│   ├── extract_bigbook.ps1
│   └── build_clinical_review.ps1
├── db/                     generated SQLite (git-ignored; rebuilt from JSON)
└── overview.html           human-readable library overview
```

## Namespaces

| Namespace | What it is | Docs |
|---|---|---|
| `shared/bible` | 66-book PD Bible key-verse library. `{ book, chapter, citation, text, plain }`; KJV + WEB. | [`BIBLE_LIBRARY.md`](shared/bible/BIBLE_LIBRARY.md) · [`bible_index.json`](shared/bible/bible_index.json) |
| `apps/clearstreak` | 130 moment-of-need passages + 100 affirmations + taxonomy + full Big Book reader. **Passages gated on clinical review.** | [`PASSAGES_REPORT.md`](apps/clearstreak/PASSAGES_REPORT.md) |

## The database (SQLite)

The DB is a **build product**, not a source. To (re)generate it from the JSON:

```powershell
pwsh _build/build_db.ps1        # writes db/store.sql; builds db/store.db if sqlite3 is on PATH
```

Because `db/` is git-ignored, the DB never drifts from the JSON and is never reviewed in a diff —
the JSON is what changes and what ships.

---
*864zeros LLC · central content store · JSON is truth, the DB is derived.*
