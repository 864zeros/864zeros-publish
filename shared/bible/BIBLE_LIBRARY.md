# Bible Content Library — index & conventions

**What this is:** a complete, public-domain **Bible key-verse library** curated for the 864zeros central content store
for reuse across the whole 864zeros ecosystem (not tied to any one app). Every one of the 66 books is
represented. Total: **834 records** across **63 files**.

> **Machine-readable manifest:** [`bible_index.json`](bible_index.json) — the single entry point. It lists all
> 66 books in canonical order with, per book: `file`, `arrayKey`, `translation`, `shape`, and `records`.
> Load flow: read `bible_index.json` → pick a book → load its `file` → read the `[arrayKey]` array.
> (This Markdown doc is the human-readable companion; the JSON manifest is authoritative for counts/paths.)

## Record schema
Every scripture record is:
```json
{ "book": "...", "chapter": N, "citation": "Book C:V", "text": "<verbatim PD scripture>", "plain": "<original 864zeros 2026 rendering>" }
```
- **`text`** — the exact public-domain verse (the anchor).
- **`plain`** — an original 864zeros paraphrase in plain 2026 English (~grade 6–8). *This is the product* —
  original, owned content, not a published translation. Do not replace it with a third-party translation.
- The three `_daily` files add a shape field (`day` for Proverbs; `psalm`/`day` for Psalms). Each file has a
  `_meta` block: title, translation, license, source, selection policy, `count`.

## Conventions
- **Translations:** **KJV** for the NT and most of the OT; **WEB** (World English Bible) for **Psalms &
  Proverbs only** (a known, deliberate inconsistency — WEB was chosen before KJV became the standard).
- **Divine name:** KJV (via getbible) already reads "the Lord". WEB "Yahweh"/"Yah" was adapted → "the Lord"
  (subject/possessive) and "Lord" (vocative).
- **Normalization:** straight ASCII quotes/apostrophes; proper-name en-dashes → hyphens; wrapping parentheses,
  editorial colophons, and "Selah" dropped for standalone display; UTF-8, no BOM.
- **No review gates** — author is reviewer.
- **Coverage:** NT epistle books cover 100% of chapters; OT narrative books cover devotional high points
  (pure-genealogy and graphic-only chapters intentionally skipped — see each file's `_meta.selection`).

## Sourcing recipe (to add/verify verses)
`curl https://api.getbible.net/v2/kjv/<n>.json` — n = book number 1–66 (Genesis=1 … Malachi=39,
Matthew=40 … Revelation=66) — returns the whole book as clean JSON. Select verses locally; cross-check
against `sources/The-Holy-Bible-King-James-Version.pdf`. Note: `bible-api.com` rate-limits (~16/window) — prefer bulk getbible.

## Content-filter note
Anthropic's API output filter (`400 Output blocked by content filtering policy`) can fire on Revelation's
graphic imagery **if raw scripture is re-sent through a live API call**. Shipping these files as **static JSON
assets at runtime** avoids it entirely.

---

## Files (record counts)

### Old Testament — 388 records, 39 books
| Book | File | n | | Book | File | n |
|---|---|--:|---|---|---|--:|
| Genesis | genesis.json | 55 | | Ecclesiastes | ecclesiastes.json | 3 |
| Exodus | exodus.json | 27 | | Song of Solomon | songofsolomon.json | 2 |
| Leviticus | leviticus.json | 7 | | Isaiah | isaiah.json | 17 |
| Numbers | numbers.json | 7 | | Jeremiah | jeremiah.json | 6 |
| Deuteronomy | deuteronomy.json | 10 | | Lamentations | lamentations.json | 3 |
| Joshua | joshua.json | 5 | | Ezekiel | ezekiel.json | 3 |
| Judges | judges.json | 2 | | Daniel | daniel.json | 4 |
| Ruth | ruth.json | 2 | | Hosea | hosea.json | 2 |
| 1 Samuel | 1samuel.json | 8 | | Joel | joel.json | 3 |
| 2 Samuel | 2samuel.json | 3 | | Amos | amos.json | 1 |
| 1 Kings | 1kings.json | 3 | | Obadiah | obadiah.json | 1 |
| 2 Kings | 2kings.json | 1 | | Jonah | jonah.json | 1 |
| 1 Chronicles | 1chronicles.json | 3 | | Micah | micah.json | 3 |
| 2 Chronicles | 2chronicles.json | 4 | | Nahum | nahum.json | 1 |
| Ezra | ezra.json | 2 | | Habakkuk | habakkuk.json | 4 |
| Nehemiah | nehemiah.json | 2 | | Zephaniah | zephaniah.json | 1 |
| Esther | esther.json | 1 | | Haggai | haggai.json | 1 |
| Job | job.json | 6 | | Zechariah | zechariah.json | 1 |
| **Psalms** | psalms_daily.json | 150 | | Malachi | malachi.json | 2 |
| **Proverbs** | proverbs_daily.json | 31 | | | | |

(Psalms = one verse per psalm; Proverbs = Proverb-a-Day, day→chapter. Both WEB anchor.)

### New Testament — 446 records, 27 books
| Book | File | n | | Book | File | n |
|---|---|--:|---|---|---|--:|
| Gospels (Mt/Mk/Lk/Jn) | gospels_daily.json | 89 | | 1 Timothy | 1timothy.json | 11 |
| Acts | acts.json | 71 | | 2 Timothy | 2timothy.json | 7 |
| Romans | romans.json | 42 | | Titus | titus.json | 4 |
| 1 Corinthians | 1corinthians.json | 32 | | Philemon | philemon.json | 2 |
| 2 Corinthians | 2corinthians.json | 25 | | Hebrews | hebrews.json | 22 |
| Galatians | galatians.json | 13 | | James | james.json | 11 |
| Ephesians | ephesians.json | 12 | | 1 Peter | 1peter.json | 12 |
| Philippians | philippians.json | 13 | | 2 Peter | 2peter.json | 5 |
| Colossians | colossians.json | 11 | | 1 John | 1john.json | 13 |
| 1 Thessalonians | 1thessalonians.json | 10 | | 2 John | 2john.json | 1 |
| 2 Thessalonians | 2thessalonians.json | 6 | | 3 John | 3john.json | 2 |
| | | | | Jude | jude.json | 2 |
| | | | | Revelation | revelation.json | 30 |

(Gospels = one verse per chapter; all other NT books = several key verses per chapter.)

---
*Living index. Full historical session rationale: `IGNORE/SESSION_2026-08-31-content-history.md`. Content factory principles & constraints documented in `README.md` and `index.json`.*
