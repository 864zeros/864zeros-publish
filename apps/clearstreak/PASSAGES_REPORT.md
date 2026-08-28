# ClearStreak — Literature Content Pipeline Report

**Product:** ClearStreak (864zeros · Faith, Health & Growth pillar)
**Scope:** Modernizing the public-domain 1939 *Alcoholics Anonymous* ("Big Book") into help content for the app.
**Status:** Draft content complete — **awaiting clinical review** before any ship.
**Date:** 2026-08-19

---

## 1. What this is

We extracted the public-domain 1939 first edition of the Big Book and mined its most useful passages into **modernized, 2026-appropriate help content** for the ClearStreak recovery app — both a book reader and a moment-of-need surfacing system. Nothing here ships without a licensed clinical review pass.

The deliverable is **`content/passages_core.json`** — 130 passages, each with two full-fidelity renderings, rich labels, an optional faith layer, and exact source provenance.

---

## 2. Decisions locked (the working contract)

| Decision | Choice |
|---|---|
| **Framework stance** | **Technique-only + optional faith.** Keep only universally-safe, evidence-aligned techniques (urge-surfing, HALT, delay, expressive writing, reach-out). AA doctrine is **re-mapped into our framework, not deleted**. Faith is opt-in, never mandatory. |
| **Fidelity over brevity** | Never abbreviate the message to fit a UI shape. Preserve the full meaning. `reading_time` is a surfacing hint only, never a reason to trim. |
| **The Twelve Steps** | **Untouchable.** Never mined, reworded, or labeled. Fenced at Chapter 5, paragraphs 6–17. If shown in the reader, they appear verbatim. (Note: the 1939 Step 12 reads *"spiritual experience,"* not the later *"awakening"* — preserved.) |
| **Two renderings** | `reader_text` = light-touch (keeps the 1939 voice; only dated/exclusionary words changed + doctrine re-mapped + faith made optional). `surface_text` = re-voiced plain 2026 (same complete meaning, warm and grounded). |
| **IP posture** | Re-authoring from public-domain ideas makes the cards **original 864zeros content** — which *resolves* the copyright concern rather than creating one, and matches spec §9.1 ("100% original or properly licensed"). |
| **Scope** | Tier 1 mined fully; Tier 2 mined selectively; the 29 personal stories **dropped** for v1 (rewriting testimony destroys authenticity — revisit with real modern voices post-launch). |

### Doctrine → our framework (re-map, do not delete)

| Source doctrine | Re-mapped to | Technique | Faith layer |
|---|---|---|---|
| powerless over alcohol | "you can't out-willpower a craving — but you can outlast it" | urge-surfing, self-efficacy | optional |
| allergy / disease | "it's wiring, not willpower; one use flips a craving switch" | non-moral condition framing | — |
| life unmanageable | "when it runs the show, life gets unmanageable — that's data, not shame" | functional analysis | — |
| Higher Power / God | "something bigger than the urge" (people, values, future self) | social support / meaning | ← the faith toggle |
| moral inventory | "honest self-review, written down" | expressive writing | — |
| character defects / sin | "patterns that don't serve you" | habit reframing | — |
| confession | "saying it out loud to one person drains its power" | shame-reduction / disclosure | — |
| amends | "repair" | relational repair | — |
| spiritual malady | "the restless, never-enough feeling" | affect regulation | — |

---

## 3. The deliverable — `passages_core.json` (130 passages)

Every passage carries `reader_text` + `surface_text` (**both full-fidelity, nothing abbreviated**), plus `faith_optional`, labels, `framework_map`, `reading_time`, exact `source` provenance, and `needs_clinical_review: true`.

### Passage record shape
```json
{
  "id": "lit_ch05_7",
  "reader_text": "…full light-touch (1939 voice) message…",
  "surface_text": "…full re-voiced 2026 message…",
  "faith_optional": "…opt-in faith line, shown only in faith mode, or null…",
  "labels": {
    "moment": ["resentment", "fear"],
    "halt": "GENERAL",
    "urge_level": "WHITE_KNUCKLING",
    "stage": "action",
    "function": "instructional"
  },
  "applies_to": ["UNIVERSAL"],
  "framework_map": "which doctrine was re-mapped",
  "reading_time": "medium",
  "source": {
    "book": "AA-1939",
    "chapter_id": "ch05",
    "chapter_title": "V. How It Works",
    "page": 76,
    "paragraph_index": 36,
    "quote_stub": "Resentment is the “number one” offender…"
  },
  "needs_clinical_review": true
}
```

### Coverage

| Tier | Chapters | Passages |
|---|---|---|
| Tier 1 (full) | The Doctor's Opinion, Chapters I–VII, XI | 118 |
| Tier 2 (selective) | Chapters VIII–X (universal nuggets only) | 12 |
| **Total** | | **130** |

Per-chapter: Doctor's Opinion 12 · Ch I 18 · Ch II 23 · Ch III 9 · Ch IV 8 · Ch V 16 · Ch VI 12 · Ch VII 9 · Ch VIII 4 · Ch IX 4 · Ch X 4 · Ch XI 11.

### Distribution

- **Faith:** 31 / 130 have an opt-in `faith_optional` line; **0** God/Higher-Power references leaked into user-facing text.
- **Journeys:** 125 `UNIVERSAL` (serve all journey types), 5 alcohol-specific.
- **Moment** (primary router): staying-the-course 39 · doubt-higher-power 35 · is-this-me 31 · starting-out 29 · after-a-slip 27 · craving-now 21 · helping-others 21 · resentment 15 · family-strain 14 · lonely 8 · hopelessness 7 · fear 7 · work-strain 5.
- **Urge tier:** PASSING 57 · CLEAR 32 · WHITE_KNUCKLING 32 · CRITICAL 9.
- **HALT:** GENERAL 73 · HOPELESS 27 · ANGRY 12 · STRESSED 9 · LONELY 7 · TIRED 2 · HUNGRY 0 *(correct — the book doesn't speak to hunger; that stays a pure HALT-basic card).*

### Guardrails verified programmatically

- 🔒 Twelve Steps (ch05 ¶6–17) never mined — 0 leaks.
- Doctrine re-mapped, not deleted (`framework_map` records each).
- No moralizing terms; gender-neutral throughout.
- 0 God/Higher-Power references in user-facing text (faith isolated to `faith_optional`).
- Provenance exact: page / paragraph-index / quote-stub cross-checked against source; 4 off-by-one pages auto-corrected.

---

## 4. How the content is organized (taxonomy)

Canonical vocabulary lives in **`content/taxonomy.json`**. Two content layers share one label vocabulary.

- **Layer 1 — the Reader:** `big_book.json`, the 42 ordered sections (front / main / stories). Full read experience at `reader_text` fidelity.
- **Layer 2 — Moment-of-need:** the passages, which point back into the reader via `source{chapter_id, page, paragraph_index}`.

### Label axes

**App-native (reuse code enums verbatim, so the DB queries them directly):**
- `halt` → `HaltTrigger` (incl. `GENERAL`)
- `urge_level` → `UrgeLevel`
- `applies_to` → `JourneyCategory` + a `UNIVERSAL` flag *(the axis the multi-journey design required)*

**Content-native (new, for filing + surfacing):**
- `moment` — the **primary router** (13 values incl. `hopelessness`)
- `stage` — contemplation / decision / action / maintenance / relapse-recovery
- `function` — foundational / instructional / identification / relational / spiritual
- `reading_time` — surfacing hint **only** (never a trim trigger)

### Surfacing — live state → content
`moment` is derived from the two taps the user already makes (urge tier + HALT):

| User state (urge × HALT) | → moment(s) | → example |
|---|---|---|
| 🟠 White-Knuckling + 😡 Angry | `resentment` | How It Works, p.76 |
| 🟠 White-Knuckling + 😞 Hopeless | `after-a-slip`, `staying-the-course` | the Promises, p.96 |
| 🟡 Passing + any | `craving-now`, `is-this-me` | Doctor's Opinion, p.5 |
| 🔴 Critical + any | Crisis Intercept **first**; optional `quick` grounding passage | — |

---

## 5. Notes & risks

1. **ch01 (18) and ch02 (23) are over-mined** relative to the rest. Not harmful — more raw material for the clinical reviewer — but a dedupe/quality-rank pass can tighten the set.
2. **`needs_clinical_review: true` on all 130.** These are strong drafts; per spec, nothing ships without an LCSW/CADC pass. This file is what the reviewer receives.
3. **Public-domain posture still needs a final legal read before store build.** The 1939 first-edition PD basis is real (Dover reprint) but disputed by AA World Services. Re-authoring reduces exposure; a definitive read is still owed before shipping.

---

## 6. Artifacts on disk

```
content/
  PASSAGES_REPORT.md      ← this report
  PASSAGES_REPORT.html    ← HTML version (864zeros design)
  passages_core.json      ← THE DELIVERABLE (130 passages)
  taxonomy.json           ← controlled vocab + state→content routing
  big_book.json           ← full 42-section reader text (archive / provenance source)
  big_book_index.json     ← page-per-paragraph provenance
  _src/                   ← per-chapter drafts + STYLE_GUIDE.md (reproducibility; gitignore-able)
  passages_sample.json    ← 3-passage calibration file (superseded — safe to delete)
  extract_bigbook.ps1     ← re-runnable extractor
```

---

## 7. Next steps

- **(A) Trim / rank** — resolve ch01–ch02 over-mining into a tighter curated set.
- **(B) Wire into the app** — author the `BookPassage` Kotlin model + a loader (mirroring `daily_verses.json`), and a first reader / surfacing screen.
- **(C) Clinical-review handoff** — export a reviewer-friendly view (original ↔ reader ↔ surface + provenance) as CSV/HTML for passage-by-passage sign-off.

**Recommendation: (C) then (B)** — get clinical sign-off before building UI on top of unreviewed content.

---

*864zeros LLC · ClearStreak content pipeline · code wins.*
