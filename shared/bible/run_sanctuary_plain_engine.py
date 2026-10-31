#!/usr/bin/env python3
"""
Sanctuary Plain-Language Engine (v2.0 — 4-Rule Gemini Editorial Standard)
Transforms the 3-Input Public Domain Corpus:
  1. Matthew Henry's Concise Commentary on the Whole Bible (1706/1811 PD)
  2. F.B. Meyer's Through the Bible Day by Day (1914 PD)
  3. Berean Standard Bible (BSB, CC0) + 1769 KJV (Deterministic Lexical & Structural Stats)
into clean-room Sanctuary Plain-Language Chapter Overviews across all 66 books / 1,189 chapters.

v2.0 Upgrades (Aligned with Jeff's Gemini 1 John 4 Editorial Standard):
  - Rule 1 (Freed Narrative): No redundant "Chapter Movements (...):" speed bump in Paragraph 1;
    outlines are parsed into structured {range, summary} chips while the prose opens directly
    with the biblical movement.
  - Rule 2 (Smart Casing & Smooth Transitions): Proper nouns (God, Christ, Adam, Satan, Moses,
    Christians, Israel, etc.) stay capitalized after introductory clauses while common words
    lowercase naturally; no jarring capitalized words after mid-sentence commas.
  - Rule 3 (Strict Plain-Language Theological Dictionary): Replaces 17th/19th-century terms
    (propitiation -> atoning sacrifice, slavish dread/fear -> dread of judgment, begat -> fathered,
    chastened -> lovingly corrected, apostacy -> turning away from God, enervates -> weakens, etc.).
  - Rule 4 (Pastoral Daily-Walk Filter + Revelation 1-22 Full Unlock): Normalizes "Revelation of John"
    -> "Revelation" so all 22 chapters of Revelation pull full Matthew Henry + F.B. Meyer commentary,
    and filters out dry structural/academic sentences from the closing devotional movement.
"""

import hashlib
import json
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path(r"C:\dev\864zeros-publish\shared\bible")
PD_DIR = BASE_DIR / "pd_sources"
MHC_ROOT = PD_DIR / "matthew_henry_concise" / "mhenry-concise-main"
FBMEYER_ROOT = PD_DIR / "pillar_pd_commentaries" / "pillar-commentary-data-main" / "c" / "fbmeyer"
BSB_PATH = PD_DIR / "BSB_cc0_full.json"
LESSONS_PATH = BASE_DIR / "bible_study_lessons.json"

BOOK_TO_USFM = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM", "Deuteronomy": "DEU",
    "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT", "1 Samuel": "1SA", "2 Samuel": "2SA",
    "1 Kings": "1KI", "2 Kings": "2KI", "1 Chronicles": "1CH", "2 Chronicles": "2CH",
    "Ezra": "EZR", "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalms": "PSA",
    "Proverbs": "PRO", "Ecclesiastes": "ECC", "Song of Solomon": "SNG", "Isaiah": "ISA",
    "Jeremiah": "JER", "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN",
    "Hosea": "HOS", "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON",
    "Micah": "MIC", "Nahum": "NAM", "Habakkuk": "HAB", "Zephaniah": "ZEP", "Haggai": "HAG",
    "Zechariah": "ZEC", "Malachi": "MAL",
    "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK", "John": "JHN", "Acts": "ACT",
    "Romans": "ROM", "1 Corinthians": "1CO", "2 Corinthians": "2CO", "Galatians": "GAL",
    "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL", "1 Thessalonians": "1TH",
    "2 Thessalonians": "2TH", "1 Timothy": "1TI", "2 Timothy": "2TI", "Titus": "TIT",
    "Philemon": "PHM", "Hebrews": "HEB", "James": "JAS", "1 Peter": "1PE", "2 Peter": "2PE",
    "1 John": "1JN", "2 John": "2JN", "3 John": "3JN", "Jude": "JUD", "Revelation": "REV"
}

BOOK_TO_MHC_SLUG = {
    name: name.lower().replace(" ", "-") for name in BOOK_TO_USFM
}
BOOK_TO_MHC_SLUG["Song of Solomon"] = "song-of-solomon"

THEME_WORDS = {
    "love", "grace", "peace", "faith", "trust", "rest", "light", "life", "truth", "spirit",
    "heart", "mercy", "joy", "hope", "praise", "prayer", "pray", "wisdom", "covenant",
    "forgive", "forgiveness", "strength", "refuge", "salvation", "deliver", "humble",
    "kindness", "righteous", "righteousness", "glory", "holy", "walk", "abide", "fear",
    "promise", "blessing", "bless", "blessed", "heal", "comfort", "patient", "steadfast"
}

# Comprehensive 17th/19th-Century -> FHG Sanctuary Plain Lexical Modernization Table
PLAIN_REPLACEMENTS = [
    (r"\bpropitiation for our sins\b", "atoning sacrifice for our sins"),
    (r"\bpropitiation\b", "atoning sacrifice"),
    (r"\bslavish dread and fear\b", "dread of judgment"),
    (r"\bslavish fear\b", "dread of judgment"),
    (r"\bslavish dread\b", "dread of judgment"),
    (r"\bchastened of the Lord\b", "lovingly corrected by the Lord"),
    (r"\bchastened\b", "corrected in love"),
    (r"\bapostacy\b", "turning away from God"),
    (r"\bapostasy\b", "turning away from God"),
    (r"\bSoft comfort enervates\.", "Easy comfort alone cannot build a resilient faith."),
    (r"\benervates\b", "weakens"),
    (r"\bbid man go out\b", "sent humanity out"),
    (r"\bbegat\b", "fathered"),
    (r"\bhearken to\b", "listen closely to"),
    (r"\bhearken\b", "listen"),
    (r"\bamanuensis\b", "scribe"),
    (r"\bsabbatic\b", "Sabbath"),
    (r"\bJehovah\b", "the Lord"),
    (r"\bworldlings\b", "those absorbed in the world"),
    (r"\bconverted sinner\b", "redeemed believer"),
    (r"\bheathenism\b", "life apart from God"),
    (r"\balmsgiving\b", "charitable giving"),
    (r"\bregenerating Spirit\b", "renewing Spirit"),
    (r"\bordinance of true religion\b", "sacred practice of true worship"),
    (r"\bbullock\b", "young ox"),
    (r"\bturtle-dove\b", "turtledove"),
    (r"\bspake\b", "spoke"),
    (r"\bSpake\b", "Spoke"),
    (r"\bshew\b", "show"),
    (r"\bshewed\b", "showed"),
    (r"\bshewing\b", "showing"),
    (r"\bbrethren\b", "brothers and sisters"),
    (r"\bBrethren\b", "Brothers and sisters"),
    (r"\bwhosoever\b", "anyone who"),
    (r"\bWhosoever\b", "Anyone who"),
    (r"\bwhatsoever\b", "whatever"),
    (r"\bwherefore\b", "therefore"),
    (r"\bWherefore\b", "Therefore"),
    (r"\btherein\b", "in it"),
    (r"\bthereof\b", "of it"),
    (r"\bwhereby\b", "by which"),
    (r"\bunto\b", "to"),
    (r"\bUnto\b", "To"),
    (r"\bdoth\b", "does"),
    (r"\bhath\b", "has"),
    (r"\bsaith\b", "says"),
    (r"\bdwelleth\b", "dwells"),
    (r"\bloveth\b", "loves"),
    (r"\bknoweth\b", "knows"),
    (r"\bkeepeth\b", "keeps"),
    (r"\bwalketh\b", "walks"),
    (r"\bcometh\b", "comes"),
    (r"\bgiveth\b", "gives"),
    (r"\bmaketh\b", "makes"),
    (r"\bseeketh\b", "seeks"),
    (r"\bjudgeth\b", "judges"),
    (r"\bworketh\b", "works"),
    (r"\bbringeth\b", "brings"),
    (r"\bpasseth\b", "passes"),
    (r"\bleadeth\b", "leads"),
    (r"\bstandeth\b", "stands"),
    (r"\bliveth\b", "lives"),
    (r"\bthee\b", "you"),
    (r"\bthou\b", "you"),
    (r"\bThou\b", "You"),
    (r"\bthy\b", "your"),
    (r"\bThy\b", "Your"),
    (r"\bthine\b", "yours"),
    (r"\bThine\b", "Yours"),
    (r"\bye\b", "you"),
    (r"\bYe\b", "You"),
    (r"\bwouldst you\b", "if you want to"),
    (r"\bWouldst you\b", "If you want to"),
    (r"\bwilt\b", "will"),
    (r"\bshalt\b", "shall"),
    (r"\bart\b", "are"),
    (r"\bhast\b", "have"),
    (r"\bcanst\b", "can"),
    (r"\bdidst\b", "did"),
    (r"\blovest\b", "love"),
    (r"\bknowest\b", "know"),
    (r"\bHoly Ghost\b", "Holy Spirit"),
    (r"\bcarnal men\b", "worldly-minded people"),
    (r"\bprofessors\b", "professing believers"),
]

PROPER_PREFIXES = (
    "God", "Lord", "Christ", "Jesus", "Spirit", "Holy", "Father", "Son", "Savior", "Messiah",
    "Adam", "Eve", "Cain", "Abel", "Seth", "Enoch", "Noah", "Abram", "Abraham", "Sarah", "Isaac",
    "Jacob", "Esau", "Joseph", "Moses", "Aaron", "Pharaoh", "Israel", "Israelites", "Egypt",
    "Sinai", "Canaan", "Joshua", "Caleb", "Gideon", "Samson", "Ruth", "Boaz", "Samuel", "Saul",
    "David", "Solomon", "Elijah", "Elisha", "Hezekiah", "Josiah", "Ezra", "Nehemiah", "Esther",
    "Mordecai", "Job", "Isaiah", "Jeremiah", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "John", "Peter", "Paul", "James", "Jude", "Luke", "Mark", "Matthew", "Stephen", "Barnabas",
    "Timothy", "Titus", "Philemon", "Mary", "Martha", "Lazarus", "Pilate", "Herod", "Satan",
    "Christian", "Christians", "Jews", "Gentiles", "Jerusalem", "Zion", "Babylon", "Rome",
    "Ephesus", "Corinth", "Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "Thessalonians", "Hebrews", "Scripture", "Scriptures", "Bible", "I ", "I,"
)

DRY_STRUCTURAL_PATTERNS = [
    r"^The first paragraph belongs to the previous chapter",
    r"^Note the curious similarity in the names",
    r"^Compare\s+[A-Z0-9]",
    r"^See\s+also\s+",
    r"^This chapter is nearly identical",
    r"^The genealogy here",
]

FEATURED_GOLD_OVERVIEWS = {
    "1JN.4": {
        "overview": [
            'The apostle John opens this chapter by counseling believers not to trust every spiritual claim blindly, but to examine teachers by one clear standard: whether they confess that Jesus Christ has truly come in the flesh (vv. 1–6).¹ Writing from Ephesus to a church surrounded by competing philosophies, John reassures them that they do not stand on their own strength: "Greater is He that is in you, than he that is in the world" (v. 4).²',
            'From verse 7 to 21, the chapter unfolds its deepest truth: "God is love."³ God did not wait for us to become worthy or to love Him first. Instead, He demonstrated His love by sending His Son to be the atoning sacrifice for our sins while we were still deeply in need (vv. 9–10).⁴ Because God’s love toward us is complete and unshakeable, it casts out all dread of judgment, freeing us to walk in quiet peace before Him and to love one another with open hands (vv. 17–21).⁵'
        ],
        "footnotes": [
            '1. KJV 1769 Chapter Argument & Matthew Henry (1706, PD) on 1 John 4:1–3 — Sound discernment tests every spirit by the incarnation of Jesus Christ.',
            '2. Jamieson-Fausset-Brown Commentary (1871, PD) on 1 John 4:4 — The indwelling Spirit of God is the believer’s quiet safeguard against deception.',
            '3. Matthew Henry (1706, PD) on 1 John 4:7–8 — Brotherly love flows directly from the nature of God Himself ("God is love").',
            '4. Treasury of Scripture Knowledge (1836, PD) on 1 John 4:10, 19 — Compare Romans 5:8; divine grace always precedes and awakens human love.',
            '5. Jamieson-Fausset-Brown (1871, PD) on 1 John 4:17–18 — Dread of punishment vanishes where the heart rests in God’s reconciling love.'
        ]
    },
    "GEN.5": {
        "overview": [
            'Across the long generations from Adam to Noah where every other life closes with the solemn refrain “and he died” (vv. 1–20),¹ Enoch’s story breaks the rhythm twice with a quiet, breathtaking testimony: “Enoch walked with God” (vv. 21–24).²',
            'Walking with God means setting the Lord before us and living under His gracious eye in unhurried communion across ordinary family days.³ Where Cain’s line sought worldly renown, Seth’s line in Enoch reveals that steady, daily companionship with our Creator is the true reality and peace of faith (vv. 25–32).⁴'
        ]
    },
    "GEN.12": {
        "overview": [
            'God calls Abram to step out from his familiar country and kindred toward a land He promises to show him along the way, pairing every call of faith with an overflowing covenant of blessing (vv. 1–3).¹ Trusting God’s word, Abram departs from Haran at seventy-five years of age and journeys into Canaan, building quiet altars of gratitude wherever he pitches his tent (vv. 4–9).²',
            'Abram trusted that the blessing of the Almighty would more than make up for everything he left behind.³ In our own walk, God rarely shows us the entire ten-year map at once; He blesses and guides us one trusting step at a time so our lives become a shelter of blessing to others.⁴'
        ]
    },
    "EXO.14": {
        "overview": [
            'Hemmed in between Pharaoh’s pursuing chariots behind and the deep waters of the sea ahead (vv. 1–9),¹ Israel cries out in fear until Moses steadies them with one of Scripture’s greatest sanctuary promises: “Do not be afraid. Stand still, and see the salvation of the Lord... The Lord will fight for you, and you shall hold your peace” (vv. 10–14).²',
            'As the angel of God moves the protective cloud between the camps and parts the waters through the night (vv. 15–31),³ we see that when no path remains open around us, our Shepherd opens a dry path right through the impossible sea.⁴'
        ]
    },
    "DEU.15": {
        "overview": [
            'Moses establishes the Sabbath year of release and calls God’s people to care for neighbors in need with an ungrudging heart and an open hand (vv. 1–11).¹ Even when servants are released into freedom, they are to be sent out generously supplied from the flock, the threshing floor, and the winepress (vv. 12–18).²',
            'God’s covenant looks past outward rules to the quiet attitude of the heart, inviting us to loosen the grip of scarcity and give gladly—knowing that the Lord blesses every work of an open hand (vv. 19–23).³'
        ]
    }
}


def clean_encoding_and_modernize(text: str) -> str:
    if not text:
        return ""
    text = text.replace('?"', "–").replace("?o", "“").replace("??", "”").replace("?T", "’")
    text = text.replace("\u2013", "–").replace("\u2014", "—")
    text = re.sub(r"\s+", " ", text).strip()
    for pat, repl in PLAIN_REPLACEMENTS:
        text = re.sub(pat, repl, text)
    return text


def smart_clause_join(prefix: str, sentence: str) -> str:
    """Joins an introductory clause like 'In verses 1–5, ' with a sentence, preserving Proper Nouns."""
    sentence = sentence.strip()
    if not sentence:
        return prefix.strip()
    if any(sentence.startswith(p) for p in PROPER_PREFIXES):
        return f"{prefix}{sentence}"
    if len(sentence) > 1 and sentence[0].isupper() and sentence[1].islower():
        return f"{prefix}{sentence[0].lower() + sentence[1:]}"
    return f"{prefix}{sentence}"


def first_n_sentences(text: str, n: int = 3, filter_dry: bool = False) -> str:
    text = clean_encoding_and_modernize(text)
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text)
    cleaned_parts = []
    for p in parts:
        p_str = p.strip()
        if len(p_str) <= 15:
            continue
        if filter_dry and any(re.search(pat, p_str, flags=re.I) for pat in DRY_STRUCTURAL_PATTERNS):
            continue
        cleaned_parts.append(p_str)
    return " ".join(cleaned_parts[:n])


def parse_outline_item(raw_item: str) -> dict:
    """Converts 'The creation of light. (3–5)' into {'range': '3–5', 'summary': 'The creation of light'}."""
    m = re.match(r"^(.*?)\s*\(([^)]+)\)\.?\s*$", raw_item.strip())
    if m:
        summary = m.group(1).strip().rstrip(".,;")
        rng = m.group(2).strip()
        return {"range": rng, "summary": summary}
    return {"range": "", "summary": raw_item.strip().rstrip(".")}


def format_sec_ref(sec_title: str) -> str:
    """Converts 'Verses 1–6' -> 'vv. 1–6' or 'Verse 31' -> 'v. 31'."""
    m = re.match(r"^Verses\s+(.*)$", sec_title.strip(), flags=re.I)
    if m:
        return f"vv. {m.group(1)}"
    m2 = re.match(r"^Verse\s+(.*)$", sec_title.strip(), flags=re.I)
    if m2:
        return f"v. {m2.group(1)}"
    return sec_title.lower()


def parse_mhc_chapter(book_name: str, chapter_num: int):
    slug = BOOK_TO_MHC_SLUG.get(book_name)
    if not slug:
        return [], [], ""
    md_path = MHC_ROOT / slug / f"chapter-{chapter_num}.md"
    if not md_path.exists():
        return [], [], ""
    raw = md_path.read_text(encoding="utf-8", errors="replace")
    raw_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

    outlines = []
    sections = []

    outline_match = re.search(r"## Chapter Outline\s+(.*?)(?=\n## |\Z)", raw, flags=re.S)
    if outline_match:
        for line in outline_match.group(1).splitlines():
            line = line.strip()
            if line.startswith("- "):
                outlines.append(parse_outline_item(clean_encoding_and_modernize(line[2:])))

    for sec_match in re.finditer(r"## (Verses?\s+[^\n]+)\n+(.*?)(?=\n## |\Z)", raw, flags=re.S):
        sec_title = clean_encoding_and_modernize(sec_match.group(1))
        sec_body = clean_encoding_and_modernize(sec_match.group(2))
        if sec_body:
            sections.append((sec_title, sec_body))

    return outlines, sections, raw_hash


def parse_fbmeyer_chapter(book_name: str, chapter_num: int):
    usfm = BOOK_TO_USFM.get(book_name)
    if not usfm:
        return [], ""
    json_path = FBMEYER_ROOT / usfm / f"{chapter_num}.json"
    if not json_path.exists():
        return [], ""
    raw = json_path.read_text(encoding="utf-8", errors="replace")
    raw_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    try:
        data = json.loads(raw)
    except Exception:
        return [], raw_hash

    blocks = []
    content_list = data.get("chapter", {}).get("content", [])
    for item in content_list:
        v_num = item.get("number", 1)
        texts = []
        for c in item.get("content", []):
            if isinstance(c, dict) and c.get("text"):
                texts.append(c["text"])
            elif isinstance(c, str):
                texts.append(c)
        joined = "\n".join(texts).strip()
        if joined:
            lines = [l.strip() for l in joined.splitlines() if l.strip()]
            heading = clean_encoding_and_modernize(lines[0]) if lines else f"Verse {v_num}"
            body = clean_encoding_and_modernize(" ".join(lines[1:])) if len(lines) > 1 else heading
            blocks.append((v_num, heading, body))
    return blocks, raw_hash


def compute_chapter_lexical_stat(book_name: str, chapter_num: int, verses: list) -> str:
    total_verses = len(verses)
    full_text = " ".join(v.get("text", "") for v in verses)
    words = re.findall(r"[A-Za-z']+", full_text.lower())
    total_words = len(words)

    theme_counts = Counter(w for w in words if w in THEME_WORDS)
    love_family = sum(1 for w in words if w.startswith("lov") or w == "beloved")
    if love_family >= 4:
        theme_counts["love / beloved"] = love_family

    if theme_counts:
        top_theme, top_count = theme_counts.most_common(1)[0]
        return (
            f"BSB / KJV Chapter Fact: {book_name} {chapter_num} spans {total_verses} verses "
            f"({total_words:,} words), anchored by the recurring theme of “{top_theme}” "
            f"(appearing {top_count} time{'s' if top_count != 1 else ''} in this chapter)."
        )
    return (
        f"BSB / KJV Chapter Fact: {book_name} {chapter_num} contains {total_verses} verses "
        f"({total_words:,} words in the Berean Standard Bible)."
    )


def build_sanctuary_overview_for_chapter(book_name: str, chapter_num: int, verses: list, book_lessons: list):
    usfm = BOOK_TO_USFM.get(book_name, "")
    ch_key = f"{usfm}.{chapter_num}"

    outlines, mhc_sections, mhc_hash = parse_mhc_chapter(book_name, chapter_num)
    fbm_blocks, fbm_hash = parse_fbmeyer_chapter(book_name, chapter_num)
    word_stat = compute_chapter_lexical_stat(book_name, chapter_num, verses)

    # Match an FHG Sanctuary Plain lesson for this book/chapter as our pastoral anchor
    matched_lesson = None
    for l in book_lessons:
        m = re.search(r"(\d+):", l.get("citation", ""))
        if m and int(m.group(1)) == chapter_num:
            matched_lesson = l
            break
    if not matched_lesson and book_lessons:
        matched_lesson = book_lessons[(chapter_num - 1) % len(book_lessons)]

    overview_paragraphs = []
    footnotes = []

    outline_str = "; ".join(
        f"{o['summary']} ({o['range']})" if o.get("range") else o["summary"]
        for o in outlines[:4]
    )

    # Paragraph 1: Freed Narrative (Opens directly with the active biblical movement — no speed bump)
    if mhc_sections:
        first_sec_title, first_sec_body = mhc_sections[0]
        s1 = first_n_sentences(first_sec_body, 2)
        ref_tag = format_sec_ref(first_sec_title)
        p1 = smart_clause_join(f"In the opening movement ({ref_tag}), ", s1) + "¹"
        if len(mhc_sections) > 2:
            mid_title, mid_body = mhc_sections[1]
            s_mid = first_n_sentences(mid_body, 1)
            if s_mid:
                p1 += f" {s_mid} ({format_sec_ref(mid_title)}).²"
        overview_paragraphs.append(p1.strip())

        if outline_str:
            footnotes.append(
                f"1. 1769 KJV Summary & Matthew Henry’s Concise Commentary (1706, PD) · {book_name} {chapter_num} — {outline_str}."
            )
        else:
            footnotes.append(
                f"1. Matthew Henry’s Concise Commentary (1706, PD) on {book_name} {chapter_num} ({first_sec_title})."
            )
        footnotes.append(
            f"2. Matthew Henry (1706, PD) on {book_name} {chapter_num} ({first_sec_title}) — {first_n_sentences(first_sec_body, 1)}"
        )

    # Paragraph 2: Closing Movement + Pastoral Sanctuary Plain Takeaway
    if len(mhc_sections) > 1:
        last_sec_title, last_sec_body = mhc_sections[-1]
        s2 = first_n_sentences(last_sec_body, 2)
        ref_last = format_sec_ref(last_sec_title)
        fbm_s = ""
        fbm_head = ""
        if fbm_blocks:
            _, fbm_head, fbm_body = fbm_blocks[0]
            fbm_s = first_n_sentences(fbm_body, 2, filter_dry=True)

        if fbm_s:
            p2 = smart_clause_join(f"As the chapter unfolds ({ref_last}), ", s2) + f"³ {fbm_s}⁴"
            overview_paragraphs.append(p2.strip())
            footnotes.append(
                f"3. Matthew Henry (1706, PD) on {book_name} {chapter_num} ({last_sec_title}) — {first_n_sentences(last_sec_body, 1)}"
            )
            footnotes.append(
                f"4. F.B. Meyer’s Through the Bible Day by Day (1914, PD) on {book_name} {chapter_num} ({fbm_head})."
            )
        elif matched_lesson:
            p2 = smart_clause_join(f"As the chapter concludes ({ref_last}), ", s2) + f"³ {matched_lesson.get('lesson', '')}⁴"
            overview_paragraphs.append(p2.strip())
            footnotes.append(
                f"3. Matthew Henry (1706, PD) on {book_name} {chapter_num} ({last_sec_title})."
            )
            footnotes.append(
                f"4. FHG Sanctuary Plain Study Anchor ({matched_lesson.get('citation')}) — {matched_lesson.get('title')}."
            )
        else:
            p2 = smart_clause_join(f"In the closing verses ({ref_last}), ", s2) + "³"
            overview_paragraphs.append(p2.strip())
            footnotes.append(
                f"3. Matthew Henry (1706, PD) on {book_name} {chapter_num} ({last_sec_title})."
            )
    elif fbm_blocks:
        _, fbm_head, fbm_body = fbm_blocks[0]
        fbm_s = first_n_sentences(fbm_body, 3, filter_dry=True) or first_n_sentences(fbm_body, 2)
        clean_head = re.sub(r"\s*--.*$", "", fbm_head).strip()
        p_fbm = f"{fbm_s}¹"
        if matched_lesson and len(overview_paragraphs) == 0:
            overview_paragraphs.append(p_fbm)
            overview_paragraphs.append(f"{matched_lesson.get('lesson', '')} {matched_lesson.get('stillness_communion', '')}²")
            footnotes.append(f"1. F.B. Meyer’s Through the Bible Day by Day (1914, PD) · {book_name} {chapter_num} ({clean_head}).")
            footnotes.append(f"2. FHG Sanctuary Plain Devotional Anchor ({matched_lesson.get('citation')}) — {matched_lesson.get('title')}.")
        else:
            overview_paragraphs.append(p_fbm)
            footnotes.append(f"2. F.B. Meyer’s Through the Bible Day by Day (1914, PD) · {book_name} {chapter_num} ({clean_head}).")

    if not overview_paragraphs and verses:
        v1 = clean_encoding_and_modernize(verses[0].get("text", ""))
        l_txt = matched_lesson.get("lesson", "") if matched_lesson else "This chapter invites quiet reflection and faithful stewardship before God."
        overview_paragraphs.append(
            f"{book_name} {chapter_num} opens with the words: “{v1}”¹ {l_txt}²"
        )
        footnotes.append(f"1. Berean Standard Bible (CC0 Public Domain) · {book_name} {chapter_num}:1–{len(verses)}.")
        if matched_lesson:
            footnotes.append(f"2. FHG Sanctuary Plain Study Anchor ({matched_lesson.get('citation')}).")

    # Apply gold-standard hand-crafted overrides for featured chapters (e.g., 1JN.4, GEN.5, GEN.12, EXO.14, DEU.15)
    if ch_key in FEATURED_GOLD_OVERVIEWS:
        gold = FEATURED_GOLD_OVERVIEWS[ch_key]
        overview_paragraphs = gold["overview"]
        if "footnotes" in gold:
            footnotes = gold["footnotes"]

    return {
        "book": book_name,
        "usfm": usfm,
        "chapter": chapter_num,
        "verse_count": len(verses),
        "outline": outlines,
        "word_stat": word_stat,
        "overview": overview_paragraphs,
        "footnotes": footnotes[:5],
        "pd_provenance": {
            "mhc_1706_sha256_prefix": mhc_hash,
            "fbmeyer_1914_sha256_prefix": fbm_hash,
            "scripture_base": "BSB (CC0 1.0 Public Domain) + KJV (1769 Public Domain)"
        }
    }


def main():
    print("Loading BSB_cc0_full.json and bible_study_lessons.json (66 books / 1,189 chapters)...")
    bsb_data = json.loads(BSB_PATH.read_text(encoding="utf-8", errors="replace"))
    lessons_data = json.loads(LESSONS_PATH.read_text(encoding="utf-8", errors="replace"))
    book_lessons_map = {
        b.get("book"): b.get("lessons", [])
        for b in lessons_data.get("books", [])
    }

    books = bsb_data.get("books", [])
    all_chapters = {}
    total_chapters = 0

    for b in books:
        b_name = b.get("name", "")
        if b_name == "Psalm":
            b_name = "Psalms"
        elif b_name == "Revelation of John":
            b_name = "Revelation"
        b_name = re.sub(r"^III\s+", "3 ", b_name)
        b_name = re.sub(r"^II\s+", "2 ", b_name)
        b_name = re.sub(r"^I\s+", "1 ", b_name)
        usfm = BOOK_TO_USFM.get(b_name, b_name[:3].upper())
        b_lessons = book_lessons_map.get(b_name, [])
        for ch in b.get("chapters", []):
            ch_num = ch.get("chapter")
            verses = ch.get("verses", [])
            key = f"{usfm}.{ch_num}"
            rec = build_sanctuary_overview_for_chapter(b_name, ch_num, verses, b_lessons)
            all_chapters[key] = rec
            total_chapters += 1

    output_payload = {
        "schema_version": "2.0.0",
        "engine": "For His Grace — Sanctuary Plain-Language Engine v2.0 (4-Rule Gemini Editorial Standard)",
        "canonical_logo": "images/fig-001-jeff-style.jpg",
        "canonical_slogan": "Solitude isn’t lonely when it’s the gift He gave.",
        "sanctuary_plain_provenance": "FHG Sanctuary Plain is our original interpretation of scripture. It is enhanced with AI models trained on the author's 'real' poems and prayers. Original tonality and nomenclature are applied. No interpretation arrives unapproved. — JMC",
        "artist_provenance": "Artwork is original and enhanced with AI models trained on the artist's 'real' sketches. No artwork arrives unapproved. — JMC",
        "legal_clearance": "100% Public Domain (Matthew Henry 1706/1811 + F.B. Meyer 1914 + BSB CC0 + KJV 1769)",
        "total_books": len(books),
        "total_chapters": total_chapters,
        "chapters": all_chapters
    }

    out_shared = BASE_DIR / "sanctuary_chapter_overviews_1189.json"
    out_web = Path(r"C:\dev\forhisgrace-web\sanctuary_chapter_overviews_1189.json")

    out_json = json.dumps(output_payload, ensure_ascii=False, indent=2)
    out_shared.write_text(out_json, encoding="utf-8")
    out_web.write_text(out_json, encoding="utf-8")

    print(f"SUCCESS: Generated {total_chapters} v2.0 Sanctuary Plain-Language Chapter Overviews!")
    for sample_key in ["GEN.1", "GEN.2", "GEN.3", "PSA.23", "ROM.8", "1JN.4", "REV.21"]:
        rec = all_chapters.get(sample_key)
        if rec:
            print(f"\n=== SAMPLE: {sample_key} ({rec['book']} {rec['chapter']}) ===")
            print("Outlines:", rec["outline"][:3])
            for p in rec["overview"]:
                print("Overview:", p)


if __name__ == "__main__":
    main()
