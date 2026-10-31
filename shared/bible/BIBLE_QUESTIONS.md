# 864zeros Bible Question Engine - Canonical Dataset (`bible_questions.json`)

**Self-contained, translation-agnostic comprehension & Trivial Pursuit-style trivia dataset** authored in the 864zeros real-world voice across all **66 canonical books** of the Bible, balanced across **Easy (1 - ultra-simplified language)**, **Medium (2 - human motive & tension)**, and **Hard (3 - deep cross-scripture synthesis)**.

- **Master JSON Asset:** [`bible_questions.json`](bible_questions.json)
- **Interactive HTML Viewer:** [`bible_questions_viewer.html`](bible_questions_viewer.html)
- **System Prompt & Schema Spec:** [`../../_build/_src/BIBLE_QUESTION_ENGINE_PROMPT.md`](../../_build/_src/BIBLE_QUESTION_ENGINE_PROMPT.md)
- **Total Questions:** **762** (OT: 432 | NT: 330)
- **Difficulty Split:** Easy (1): **254** | Medium (2): **254** | Hard (3): **254**
- **Total Books Covered:** **66 / 66**
- **Phase 2 Roadmap Note:** Dedicated *Geography & Real-World Locations* Question Pack queued next.

## 6-Category Trivial Pursuit Distribution

| Category Enum | Count |
|---|---:|
| `GEOGRAPHY_AND_PLACES` | 90 |
| `DECISION_UNDER_PRESSURE` | 114 |
| `HUMAN_NATURE_AND_MOTIVE` | 136 |
| `PARADOX_AND_CONSEQUENCE` | 143 |
| `RELATIONAL_FRICTION` | 78 |
| `CORE_ARGUMENT_AND_LAW` | 103 |
| `BIG_PICTURE_ARC` | 98 |

## Per-Book Question & Difficulty Breakdown

| # | Book | Testament | Total | Easy (1) | Medium (2) | Hard (3) |
|---:|---|---:|---:|---:|---:|---:|
| 1 | **Genesis** | OT | **43** | 15 | 17 | 11 |
| 2 | **Exodus** | OT | **12** | 5 | 4 | 3 |
| 3 | **Leviticus** | OT | **9** | 3 | 3 | 3 |
| 4 | **Numbers** | OT | **12** | 4 | 4 | 4 |
| 5 | **Deuteronomy** | OT | **10** | 3 | 3 | 4 |
| 6 | **Joshua** | OT | **12** | 5 | 3 | 4 |
| 7 | **Judges** | OT | **10** | 3 | 4 | 3 |
| 8 | **Ruth** | OT | **10** | 4 | 3 | 3 |
| 9 | **1 Samuel** | OT | **13** | 3 | 5 | 5 |
| 10 | **2 Samuel** | OT | **10** | 4 | 3 | 3 |
| 11 | **1 Kings** | OT | **14** | 4 | 5 | 5 |
| 12 | **2 Kings** | OT | **11** | 4 | 3 | 4 |
| 13 | **1 Chronicles** | OT | **9** | 3 | 3 | 3 |
| 14 | **2 Chronicles** | OT | **10** | 3 | 3 | 4 |
| 15 | **Ezra** | OT | **9** | 3 | 3 | 3 |
| 16 | **Nehemiah** | OT | **10** | 3 | 4 | 3 |
| 17 | **Esther** | OT | **10** | 3 | 4 | 3 |
| 18 | **Job** | OT | **9** | 3 | 3 | 3 |
| 19 | **Psalms** | OT | **19** | 7 | 6 | 6 |
| 20 | **Proverbs** | OT | **12** | 4 | 4 | 4 |
| 21 | **Ecclesiastes** | OT | **9** | 3 | 3 | 3 |
| 22 | **Song of Solomon** | OT | **9** | 3 | 3 | 3 |
| 23 | **Isaiah** | OT | **9** | 3 | 3 | 3 |
| 24 | **Jeremiah** | OT | **10** | 3 | 3 | 4 |
| 25 | **Lamentations** | OT | **9** | 3 | 3 | 3 |
| 26 | **Ezekiel** | OT | **10** | 3 | 3 | 4 |
| 27 | **Daniel** | OT | **10** | 3 | 3 | 4 |
| 28 | **Hosea** | OT | **9** | 3 | 3 | 3 |
| 29 | **Joel** | OT | **9** | 3 | 3 | 3 |
| 30 | **Amos** | OT | **10** | 3 | 3 | 4 |
| 31 | **Obadiah** | OT | **10** | 3 | 3 | 4 |
| 32 | **Jonah** | OT | **11** | 4 | 3 | 4 |
| 33 | **Micah** | OT | **9** | 3 | 3 | 3 |
| 34 | **Nahum** | OT | **9** | 3 | 3 | 3 |
| 35 | **Habakkuk** | OT | **9** | 3 | 3 | 3 |
| 36 | **Zephaniah** | OT | **9** | 3 | 3 | 3 |
| 37 | **Haggai** | OT | **9** | 3 | 3 | 3 |
| 38 | **Zechariah** | OT | **9** | 3 | 3 | 3 |
| 39 | **Malachi** | OT | **9** | 3 | 3 | 3 |
| 40 | **Matthew** | NT | **21** | 9 | 6 | 6 |
| 41 | **Mark** | NT | **17** | 6 | 6 | 5 |
| 42 | **Luke** | NT | **22** | 9 | 6 | 7 |
| 43 | **John** | NT | **22** | 8 | 8 | 6 |
| 44 | **Acts** | NT | **32** | 7 | 14 | 11 |
| 45 | **Romans** | NT | **12** | 4 | 4 | 4 |
| 46 | **1 Corinthians** | NT | **13** | 4 | 4 | 5 |
| 47 | **2 Corinthians** | NT | **9** | 3 | 3 | 3 |
| 48 | **Galatians** | NT | **10** | 3 | 3 | 4 |
| 49 | **Ephesians** | NT | **9** | 3 | 3 | 3 |
| 50 | **Philippians** | NT | **9** | 3 | 3 | 3 |
| 51 | **Colossians** | NT | **9** | 3 | 3 | 3 |
| 52 | **1 Thessalonians** | NT | **9** | 3 | 3 | 3 |
| 53 | **2 Thessalonians** | NT | **9** | 3 | 3 | 3 |
| 54 | **1 Timothy** | NT | **9** | 3 | 3 | 3 |
| 55 | **2 Timothy** | NT | **9** | 3 | 3 | 3 |
| 56 | **Titus** | NT | **9** | 3 | 3 | 3 |
| 57 | **Philemon** | NT | **10** | 3 | 3 | 4 |
| 58 | **Hebrews** | NT | **12** | 4 | 4 | 4 |
| 59 | **James** | NT | **9** | 3 | 3 | 3 |
| 60 | **1 Peter** | NT | **9** | 3 | 3 | 3 |
| 61 | **2 Peter** | NT | **9** | 3 | 3 | 3 |
| 62 | **1 John** | NT | **9** | 3 | 3 | 3 |
| 63 | **2 John** | NT | **9** | 3 | 3 | 3 |
| 64 | **3 John** | NT | **9** | 3 | 3 | 3 |
| 65 | **Jude** | NT | **9** | 3 | 3 | 3 |
| 66 | **Revelation** | NT | **15** | 5 | 4 | 6 |

