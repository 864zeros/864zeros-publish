# ClearStreak — Affirmations Style & Sourcing Note (READ BEFORE ADDING ANY)

Affirmations are the app's **universal, always-safe encouragement layer** — distinct from the
moment-routed literature passages (`passages_core.json`) and the scripture verses
(`clearStreak-daily-verse.json`). Two pillars, two files:

- `affirmations_recovery.json` — secular, technique-aligned; derived from the 1939 Big Book (PD).
- `affirmations_spiritual.json` — faith-centered; derived from the KJV Bible (PD).

## The one rule (the whole contract)
**Authored, not quoted — but always derived and always referenced.**
Every affirmation is original 864zeros writing in our own voice (motivational author +
theologian + poet). It is *not* a quotation. But each one must be a **faithful interpretation
of one specific source passage**, and it carries that passage's exact reference. A citation is a
truth claim: the authored line must genuinely say what the cited passage says — never staple a
reference onto an unrelated thought. Creative freedom in voice; fidelity in derivation.

## Abstraction
Each affirmation stands alone. It carries **only its own text plus its source reference** — no
`moment` / `halt` / `urge_level` labels. That is deliberate: affirmations are universal and can
surface any time, which is why they stay label-free. (If routing is ever wanted, add optional
light labels then — don't retrofit the whole set.)

## Voice
- Second person, present, plain, poet's economy. Warm but not flippant — the reader may be in pain.
- 1–3 sentences. Land one durable idea, cleanly.
- **Recovery voice:** secular. No mandatory faith, no moralizing words (sin/defect/broken/insane),
  gender-neutral. Where the idea is substance-agnostic, say "use / act on the urge," not "drink."
  The Twelve Steps are never distilled into an affirmation.
- **Spiritual voice:** overtly devotional; God-language is welcome (this is the faith pillar).

## Record shape
```json
// recovery — source mirrors passages_core.json
{ "id": "aff_recovery_NNN", "text": "…", "pillar": "recovery",
  "source": { "book": "AA-1939", "chapter_id": "…", "chapter_title": "…",
              "page": 0, "paragraph_index": 0, "quote_stub": "first ~48 chars of original" } }

// spiritual — source mirrors clearStreak-daily-verse.json
{ "id": "aff_spiritual_NNN", "text": "…", "pillar": "spiritual",
  "source": { "citation": "Book C:V", "verse_text": "exact KJV text" } }
```

## Provenance discipline
- **Recovery:** anchor to a real Big Book paragraph. The v1 set was derived from passages already
  verified in `passages_core.json`, reusing their exact `page` / `paragraph_index` / `quote_stub`
  so every citation is byte-accurate. New entries must do the same (verify against
  `big_book_index.json`), never invent a page or index.
- **Spiritual:** `verse_text` must be the **exact KJV wording** (public domain). Verify before adding.

## Review gates — none
Affirmations carry **no review gates** — no `needs_clinical_review`, no `needs_theological_review`.
These are original, 864zeros-authored content; the author is the reviewer. Keep the source
provenance accurate (Big Book page/index, exact KJV verse_text) and that is the standard.

## IP posture
KJV is public domain. The 1939 Big Book is public domain (Dover reprint) but disputed by AA World
Services; re-authoring from PD ideas makes these original 864zeros content — same footnote as the
passages. A final legal read is still owed before store build.
