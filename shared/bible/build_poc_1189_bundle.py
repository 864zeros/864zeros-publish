#!/usr/bin/env python3
"""
Builds C:\\dev\\forhisgrace-web\\framework\\sanctuary_1189_bundle.js
so that poc_sanctuary_reader.html has an active, 100% offline/online representation
of ALL 66 Books, ALL 10 Biblical Sections/Categories, ALL 1,189 Chapter Overviews,
ALL 660 4-Layer Study Lessons + Studio Art, and ALL 834 Sanctuary Plain Key Verses!
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(r"C:\dev\864zeros-publish\shared\bible")
WEB_DIR = Path(r"C:\dev\forhisgrace-web")

OVERVIEWS_PATH = BASE_DIR / "sanctuary_chapter_overviews_1189.json"
LESSONS_PATH = WEB_DIR / "bible_study_lessons.json"
BIBLE_DATA_JS_PATH = WEB_DIR / "bible_data.js"
BSB_PATH = BASE_DIR / "pd_sources" / "BSB_cc0_full.json"
KJV_PATH = BASE_DIR / "pd_sources" / "AKJV_1769_full.json"

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


def norm_book(name: str) -> str:
    if name == "Psalm":
        return "Psalms"
    if name == "Revelation of John":
        return "Revelation"
    name = re.sub(r"^III\s+", "3 ", name)
    name = re.sub(r"^II\s+", "2 ", name)
    name = re.sub(r"^I\s+", "1 ", name)
    return name


def clean_bsb_text(t: str) -> str:
    return (
        t.replace("?o", "“")
        .replace("??", "”")
        .replace('?"', "—")
        .replace("?s", "’s")
        .replace("?t", "’t")
    )


def synthesize_sanctuary_plain(bsb_txt: str, cur_plain: str = "") -> str:
    if cur_plain and cur_plain.strip():
        return cur_plain.strip()
    txt = clean_bsb_text(bsb_txt).strip()
    # Apply gentle FHG Sanctuary Plain nomenclature & cadence
    replacements = [
        (r"\bLORD\b", "Lord"),
        (r"\bBehold,\s*", "Look closely — "),
        (r"\bbehold,\s*", "look closely — "),
        (r"\bTruly, truly, I tell you\b", "Hear this steady truth"),
        (r"\bVerily, verily\b", "Truly"),
        (r"\bBlessed are\b", "Held in quiet grace are"),
        (r"\bFear not\b", "Do not be afraid"),
        (r"\bWait for the Lord\b", "Rest quietly and wait for the Lord"),
        (r"\bwalked with God\b", "walked faithfully in quiet step with God"),
        (r"\blovingkindness\b", "steadfast covenant love"),
        (r"\btransgressions\b", "wanderings and failures"),
        (r"\biniquity\b", "brokenness"),
    ]
    for pat, rep in replacements:
        txt = re.sub(pat, rep, txt)
    return txt


def main():
    print("Loading 1,189 Chapter Overviews, 660 Study Lessons, 834 Key Verses, and BSB/KJV anchors...")
    ov_data = json.loads(OVERVIEWS_PATH.read_text(encoding="utf-8"))
    lessons_data = json.loads(LESSONS_PATH.read_text(encoding="utf-8"))
    bsb_data = json.loads(BSB_PATH.read_text(encoding="utf-8"))
    kjv_data = json.loads(KJV_PATH.read_text(encoding="utf-8"))

    # Parse window.BIBLE from bible_data.js
    bible_js_raw = BIBLE_DATA_JS_PATH.read_text(encoding="utf-8")
    bible_json_str = re.sub(r"^window\.BIBLE\s*=\s*", "", bible_js_raw.strip()).rstrip(";")
    bible_data = json.loads(bible_json_str)

    # Index curated plain verses from bible_data.js by (book, ch, v)
    curated_plain = {}
    extra_chapter_vnums = {}
    for b in bible_data.get("books", []):
        b_name = norm_book(b.get("book", ""))
        for v_rec in b.get("verses", []):
            cite = v_rec.get("citation", "")
            m = re.search(r":(\d+)", cite)
            if m:
                v_num = int(m.group(1))
                c_num = int(v_rec.get("chapter") or 1)
                curated_plain[(b_name, c_num, v_num)] = v_rec.get("plain", "")
                extra_chapter_vnums.setdefault((b_name, c_num), set()).add(v_num)

    # Also track lesson citation verses so every lesson's anchor verse is in chapterVerses
    for b in lessons_data.get("books", []):
        b_name = norm_book(b.get("book", ""))
        for l in b.get("lessons", []):
            cite = l.get("citation", "")
            m = re.search(r"(\d+):(\d+)", cite)
            if m:
                c_num = int(m.group(1))
                v_num = int(m.group(2))
                extra_chapter_vnums.setdefault((b_name, c_num), set()).add(v_num)

    # Index KJV verses by (book, ch, v)
    kjv_lookup = {}
    for b in kjv_data.get("books", []):
        b_name = norm_book(b.get("name", ""))
        for ch in b.get("chapters", []):
            c_num = ch.get("chapter")
            for v in ch.get("verses", []):
                kjv_lookup[(b_name, c_num, v.get("verse"))] = v.get("text", "")

    # Index BSB verses by (book, ch)
    bsb_chapters = {}
    for b in bsb_data.get("books", []):
        b_name = norm_book(b.get("name", ""))
        for ch in b.get("chapters", []):
            c_num = ch.get("chapter")
            bsb_chapters[(b_name, c_num)] = ch.get("verses", [])

    # Build compact 66-book metadata + lessons
    books_meta = []
    for b in lessons_data.get("books", []):
        b_name = b.get("book")
        usfm = BOOK_TO_USFM.get(b_name, b_name[:3].upper())
        rep_sketch_prefix = "../sketches/study_gen_01_genesis_1_3"
        rep_sketch_mode = "s2"
        rep_caption = f"Quiet contemplation in the Book of {b_name} — Walking in God’s grace."
        for l in b.get("lessons", []):
            img_c2 = l.get("image_file_c2") or ""
            if img_c2:
                m = re.match(r"^(sketches/study_[a-z0-9_]+?)_b1_g2_(s[23])_c2\.jpg$", img_c2)
                if m:
                    rep_sketch_prefix = "../" + m.group(1)
                    rep_sketch_mode = m.group(2)
                    rep_caption = l.get("visual_prompt") or rep_caption
                    break

        ch_nums = sorted([
            rec["chapter"] for k, rec in ov_data["chapters"].items()
            if rec["book"] == b_name
        ])

        books_meta.append({
            "order": b.get("order"),
            "book": b_name,
            "usfm": usfm,
            "testament": b.get("testament"),
            "category": b.get("category"),
            "chapterCount": len(ch_nums),
            "bookOverview": b.get("overview", ""),
            "keyThemes": b.get("key_themes", []),
            "sketchPrefix": rep_sketch_prefix,
            "sketchMode": rep_sketch_mode,
            "visualCaption": rep_caption,
            "lessons": [
                {
                    "number": l.get("number"),
                    "title": l.get("title"),
                    "citation": l.get("citation"),
                    "scripture_text": l.get("scripture_text"),
                    "lesson": l.get("lesson"),
                    "application": l.get("application"),
                    "relational_outflow": l.get("relational_outflow", ""),
                    "stillness_communion": l.get("stillness_communion", ""),
                    "quiet_prayer": l.get("quiet_prayer", ""),
                    "visual_prompt": l.get("visual_prompt", ""),
                    "image_file_c2": l.get("image_file_c2", "")
                }
                for l in b.get("lessons", [])
            ]
        })

    # Store opening 6 verses + any curated/lesson key verses of every chapter across all 1,189 chapters
    chapter_head_verses = {}
    for (b_name, c_num), v_list in bsb_chapters.items():
        usfm = BOOK_TO_USFM.get(b_name, b_name[:3].upper())
        key = f"{usfm}.{c_num}"
        extra_v = extra_chapter_vnums.get((b_name, c_num), set())
        selected_v_objs = []
        for idx, v_obj in enumerate(v_list):
            vn = v_obj.get("verse")
            if idx < 6 or vn in extra_v:
                selected_v_objs.append(v_obj)

        chapter_head_verses[key] = [
            {
                "v": v_obj.get("verse"),
                "BSB": clean_bsb_text(v_obj.get("text", "")),
                "KJV": kjv_lookup.get((b_name, c_num, v_obj.get("verse")), clean_bsb_text(v_obj.get("text", ""))),
                "PLAIN": synthesize_sanctuary_plain(
                    v_obj.get("text", ""),
                    curated_plain.get((b_name, c_num, v_obj.get("verse")), "")
                )
            }
            for v_obj in selected_v_objs
        ]

    bundle = {
        "schema_version": "1.0.0",
        "sanctuary_plain_provenance": "FHG Sanctuary Plain is our original interpretation of scripture. It is enhanced with AI models trained on the author's 'real' poems and prayers. Original tonality and nomenclature are applied. No interpretation arrives unapproved. — JMC",
        "artist_provenance": "Artwork is original and enhanced with AI models trained on the artist's 'real' sketches. No artwork arrives unapproved. — JMC",
        "books": books_meta,
        "chapters": ov_data["chapters"],
        "chapterVerses": chapter_head_verses
    }

    js_content = "window.FHG_SANCTUARY_1189 = " + json.dumps(bundle, ensure_ascii=False, separators=(",", ":")) + ";\n"
    out_js = WEB_DIR / "framework" / "sanctuary_1189_bundle.js"
    out_js.write_text(js_content, encoding="utf-8")
    print(f"SUCCESS: Wrote {out_js} ({out_js.stat().st_size:,} bytes) covering {len(books_meta)} books and {len(ov_data['chapters'])} chapters!")


if __name__ == "__main__":
    main()
