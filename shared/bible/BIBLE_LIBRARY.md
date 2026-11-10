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
{
  "book": "...",
  "chapter": N,
  "citation": "Book C:V",
  "text": "<verbatim PD scripture>",
  "plain": "<original 864zeros 2026 rendering>",
  "visual_prompt": "<1-sentence organic biblical subject grounded in Era + Geo-Location>",
  "spec_id": "fhg_sketch_spec | fhg_sketch_people_spec",
  "humanizer": "G2+S2 | G2+S3",
  "image_file": "sketches/<filename>.jpg"
}
```
- **`text`** — the exact public-domain verse (the anchor).
- **`plain`** — an original 864zeros paraphrase in plain 2026 English (~grade 6–8). *This is the product* —
  original, owned content, not a published translation. Do not replace it with a third-party translation.
- **`visual_prompt` + `spec_id` + `humanizer` (Lean On-Device Visual Contract):**
  - To prevent mobile RAM and on-device LLM context bloat, individual verse JSON records store **only** the 1-sentence `visual_prompt`, `spec_id`, and `humanizer` stage (`"G2+S2"` for nature/objects via `fhg_sketch_spec` [~90% of verses]; `"G2+S3"` when human silhouettes seen strictly from the back are included via `fhg_sketch_people_spec` [~10% of verses]).
  - All full generation prompt templates, negative tokens, filter parameters (`G1`–`G5` per-stroke straightening + `S1`–`S5` humanizer), future medium specs (`fhg_sketch_trivia_spec`, `fhg_sketch_journal_spec`, `fhg_illustration_color_spec`, `fhg_watercolor_spec`, `fhg_painting_acrylic_color_spec`, `fhg_charcoal_spec`), and the exclusive bottom-right canonical signature rule (`media/visuals/jeff_canonical_signature.png` at `x_right=0.942w, y_bottom=0.971h`) live once in [`FHG_VISUAL_SPEC_REGISTRY.json`](FHG_VISUAL_SPEC_REGISTRY.json).
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


## FHG 19-Variation Art Studio (`V1–V19`), Component Warehouse (`bible_study_viewer.html`), & v2.0 1,189-Chapter Overviews
- **19 Studio Art Variations (`V1–V19` across 149 Plates = `2,831` Sketch Files):**
  - Every FHG plate in `shared/bible/sketches/` compiles all 19 deterministic CPU variations (`0` API calls), with **`V1 = ✨ Blotchy (B1 · Default)` (`_b1_g2_s2.jpg`)** locked at `#1`:
    - `V1–V11`: `_b1_g2_s2`, `_loop_scr`, `_xhatch_scr`, `_sub_scr`, `_c2`, `_c3`, `_g2_s2`, `_straight_g4`, `_c1`, `_c4`, `_base`.
    - `V12–V19` (Non-Blotch Line/Scribble × Palette Editions): `_nb_loop_c3`, `_nb_loop_c4`, `_nb_line_c3`, `_nb_line_c4`, `_nb_base_c3`, `_nb_base_c4`, `_nb_sub_c3`, `_nb_xhatch_g2`.
- **69 Biblical Animal & Nature Plates (`P4 · Animals` & `P2 · Nature`):**
  - Includes 23 real Gemini-drawn sliced animal plates (`study_ani_01_sheep_pasture_framed` .. `study_ani_23_fish_reeds`), 15 Fauna & Weather archetypes (`study_arch_01`..`15`), and 31 lesson plates, viewable in `shared/bible/fhg_animals_gallery.html` and governed by `media/visuals/FHG_27_BIBLICAL_ANIMALS_TAXONOMY.md`.
- **Internal Component Warehouse vs. Public Free Flagship:**
  - `shared/bible/bible_study_viewer.html` is the internal FHG Master Component & Opportunity Warehouse (`[C-*]`, `[T1–T4]`, `[O1–O3]`, `[L0–L4b]`, `[H0–H4]` HALT Check-In, `[S1–S12 / S-COMB]` Soul Sanctuary with `¹²³` citations, `[F1–F2]`, `[Q0]`, `[M1]`, `[P1–P5]`, `[V1–V19]`) with a sticky `RECIPE:` compiler bar.
  - `forhisgrace-web/framework/poc_sanctuary_reader.html` is the public free flagship Sanctuary Reader promoted on `forhisgrace.com`, powered by `sanctuary_chapter_overviews_1189.json` and `sanctuary_1189_bundle.js` (v2.0 4-Rule Gemini Editorial Standard).
- **FHG Video & Living Sanctuary Lab (`shared/bible/fhg_video_lab.html`):**
  - Showcases `Options 0–6` rendered from Google Flow `.mp4` clips (`videos_showcase/*`).

---
*Living index. Full historical session rationale: `IGNORE/SESSION_2026-08-31-content-history.md` and `IGNORE/SESSION_2026-11-09-fhg-19-art-editions-warehouse-codes-23-sliced-animals-and-video-lab.md`. Content factory principles & constraints documented in `README.md` and `index.json`.*
