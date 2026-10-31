#!/usr/bin/env python3
"""
Populates the Lean On-Device FHG Visual Contract (`visual_prompt`, `spec_id`, `humanizer`, and `image_file` where rendered)
across:
  1. All 834 Key Verses (`shared/bible/*.json` per `bible_index.json` + `shared/bible/bible_data.js`)
  2. All 660 Actionable Study Lessons (`shared/bible/bible_study_lessons.json` + `shared/bible/bible_study_viewer.html`)

Enforces:
  - Crossover Unification: Overlapping passages between Key Verses and Study Lessons share the exact same visual spec.
  - 90% Nature/Objects (`fhg_sketch_spec` -> `G2+S2`) / 10% People Seen Strictly from Back (`fhg_sketch_people_spec` -> `G2+S3`).
  - Book-Specific Historical Era + Geo-Location Grounding across all 66 canonical books.
  - 100% Uniqueness Gate across all 1,284 unique passages (zero duplicate `visual_prompt` strings).
"""

import hashlib
import json
import os
import re

BIBLE_DIR = r"C:\dev\864zeros-publish\shared\bible"

# 1. Book -> Historical Era & Authentic Geo-Topography Palette
BOOK_GEO_ERA = {
    "Genesis": ("Patriarchal Bronze Age", ["the rolling limestone hills of Hebron", "a quiet Negev desert wadi", "the ancient oak grove of Mamre", "a stony ridge above Bethel", "the desert pastureland near Beersheba"]),
    "Exodus": ("Sinai Wilderness Era", ["the red granite crags of Mount Sinai", "a dry desert wadi lined with acacia scrub", "the reed-fringed banks of the Nile", "a wind-swept wilderness camp clearing", "a rocky cleft in Horeb"]),
    "Leviticus": ("Sinai Tabernacle Era", ["the quiet outer courtyard of the wilderness Tabernacle", "a rough-hewn stone altar clearing beneath Sinai", "an acacia-wood table beside a bronze basin", "the quiet threshold of the tent of meeting"]),
    "Numbers": ("Wilderness Wanderings Era", ["the arid Paran wilderness trail", "a desert oasis spring shaded by date palms", "a stony ridge overlooking the Moab plains", "a quiet wilderness ridge under a vast sky"]),
    "Deuteronomy": ("Plains of Moab Era", ["the high wind-swept ridge of Mount Nebo", "the terraced hillsides overlooking the Jordan valley", "a boundary marker of stacked fieldstones on the Moab plain", "an ancient olive grove beyond the Jordan"]),
    "Joshua": ("Conquest & Settlement Era", ["the stony riverbanks of the Jordan crossing", "twelve memorial river stones stacked on the Gilgal bank", "the terraced hill country of Ephraim", "an old stone wall along the Jericho plain"]),
    "Judges": ("Period of the Judges", ["a stone winepress hewn into an Ophrah hillside", "the palm-shaded ridge of Deborah in Ephraim", "a rocky ravine along the Kishon brook", "a rough fieldstone watchtower in Gilead"]),
    "Ruth": ("Period of the Judges in Bethlehem", ["the terraced barley fields of Bethlehem", "a stone threshing floor at the edge of a Bethlehem hillside", "a narrow footpath winding between sheaves of grain", "a quiet courtyard gate in Bethlehem"]),
    "1 Samuel": ("Transition to Monarchy", ["the green pasture valleys of Bethlehem", "the rocky crags of En Gedi", "a quiet stone sanctuary courtyard at Shiloh", "a hillside trail above the Elah valley"]),
    "2 Samuel": ("United Monarchy (Davidic Era)", ["the steep dry-stone terraces of Mount Zion", "a cedar-beamed courtyard in Jerusalem", "a sheltering limestone crag in the Judean wilderness", "a quiet rooftop parapet overlooking Jerusalem"]),
    "1 Kings": ("Solomonic & Divided Kingdom Era", ["the wind-swept ridge of Mount Carmel", "the ancient cedar forests of Lebanon", "the dry brook bed of Cherith among rocky ravines", "a quiet stone cave mouth on Mount Horeb"]),
    "2 Kings": ("Divided Kingdom Era", ["an upper-room stone chamber along a Shunem courtyard", "the reed-lined banks of the Jordan river", "a terraced olive grove in Samaria", "the rough stone ramparts of Jerusalem"]),
    "1 Chronicles": ("Davidic Temple Preparation Era", ["the stone threshing floor of Ornan on Mount Moriah", "a stack of dressed limestone blocks and cedar timbers", "a quiet courtyard colonnade in Jerusalem"]),
    "2 Chronicles": ("Judean Monarchy Era", ["the broad stone courtyard steps of the Jerusalem Temple", "a high stone watchtower overlooking the Tekoa wilderness", "a repaired breach in an ancient Jerusalem stone wall"]),
    "Ezra": ("Post-Exilic Return Era", ["newly laid foundation stones amid ancient Jerusalem ruins", "a stone altar rebuilt on its ancient footing", "the long Euphrates river trail leading back to Judea"]),
    "Nehemiah": ("Post-Exilic Wall Rebuilding Era", ["the half-rebuilt dry-stone ramparts of Jerusalem", "a heavy wooden gate hung between stone bastions", "a mason's plumb line and trowel resting on a rebuilt wall"]),
    "Esther": ("Persian Period (Susa)", ["a quiet stone colonnade in the Susa citadel courtyard", "a carved stone archway opening onto a walled Persian garden", "a parchment scroll with a clay signet seal on a stone ledge"]),
    "Job": ("Patriarchal Land of Uz", ["the wind-swept stony plains of the land of Uz", "a solitary weathered boulder under a vast desert sky", "mountain torrents cutting through canyon rock", "an ancient olive tree surviving a desert gale"]),
    "Psalms": ("Judean Hills & Jerusalem Sanctuary", ["quiet green pastures beside a still Judean brook", "the rocky limestone crags of the Judean wilderness", "the stone steps ascending toward Mount Zion", "an ancient olive tree planted by streams of water", "a high stone refuge tower on a mountain ridge"]),
    "Proverbs": ("Solomonic Wisdom Era", ["a quiet stone courtyard shaded by a wide fig tree", "a merchant's brass balance scale on a rough wooden table", "a well-trod stone footpath diverging at a quiet crossroads", "a deep stone cistern brimming with clear spring water"]),
    "Ecclesiastes": ("Solomonic Contemplative Era", ["an old dry-stone vineyard wall weathered by many seasons", "a sundial shadow falling across a quiet limestone courtyard", "a winding mountain stream flowing toward the distant sea"]),
    "Song of Solomon": ("Springtime in Galilee & Lebanon", ["a walled garden fountain surrounded by blooming pomegranate branches", "a stone trellis overgrown with fruiting grapevines", "the cedar-crested slopes of Mount Lebanon"]),
    "Isaiah": ("8th-Century Judean Prophetic Era", ["a fresh green shoot springing from a felled olive stump", "a highway of flat stones cleared through a desert wadi", "a watchman's stone tower overlooking Jerusalem's hills", "a potter's clay vessel resting on a wooden wheel"]),
    "Jeremiah": ("Late Judean Monarchy & Exile", ["a potter's stone workshop in the Hinnom valley", "a deep tree rooted beside an unfailing stream in a dry year", "a cracked stone cistern in a deserted courtyard", "an almond branch budding in early spring"]),
    "Lamentations": ("Post-Siege Jerusalem", ["quiet, empty stone streets along a weathered Jerusalem wall", "morning dew glistening on rough fallen masonry at dawn", "a solitary oil lamp glowing in a ruined stone archway"]),
    "Ezekiel": ("Babylonian Exile (Chebar Canal)", ["the reed-lined banks of the Chebar canal in Babylon", "a valley floor scattered with dry sun-bleached stones and fresh green shoots", "a fresh river flowing out from beneath a stone temple threshold"]),
    "Daniel": ("Babylonian & Persian Courts", ["a high stone lattice window open toward Jerusalem", "a quiet rocky ridge beneath a vast clear night horizon", "a massive mountain boulder resting at the base of a cliff"]),
    "Hosea": ("Northern Kingdom (Israel)", ["a terraced hillside vineyard at the edge of the wilderness", "early morning mist rising over the Jezreel valley", "plowed fallow ground waiting for spring rain"]),
    "Joel": ("Judean Agricultural Hills", ["a stone threshing floor heaped with harvested wheat", "autumn rain clouds gathering above terraced Judean hills", "a recovering fig tree putting forth fresh tender leaves"]),
    "Amos": ("Tekoa Shepherd Hills", ["a sycamore-fig orchard in the rocky hills of Tekoa", "a builder's lead plumb line suspended beside a straight stone wall", "a mountain stream cascading over smooth boulders"]),
    "Obadiah": ("High Crags of Edom", ["the lofty red-rock clefts and high cliffs of Edom", "a narrow mountain pass winding between towering canyon walls"]),
    "Jonah": ("Joppa Harbor & Mediterranean Sea", ["the stone breakwater of ancient Joppa harbor", "a wooden ship's bow riding high ocean swells", "a broad-leaved gourd vine shading a rough hillside shelter"]),
    "Micah": (" rural Shephelah Foothills (Moresheth)", ["a quiet Judean village nestled among olive-draped foothills", "an iron plowshare resting beside a pruning hook on a stone wall", "the quiet hilltop silhouette of Bethlehem"]),
    "Nahum": ("Assyrian Frontier & Judean Mountains", ["peaceful mountain ridges heralding dawn over Judea", "a breached ancient mudbrick fortress wall beside a river"]),
    "Habakkuk": ("Late Judean Watchtower", ["a solitary stone watchtower rampart overlooking the hills", "a barren fig tree and empty stone olive press in a quiet yard", "high mountain crags where sure-footed ibex climb"]),
    "Zephaniah": ("Late 7th-Century Jerusalem", ["a quiet courtyard corner in Jerusalem at daybreak", "a humble shepherd's fold bordered by low fieldstones"]),
    "Haggai": ("Post-Exilic Temple Reconstruction", ["freshly quarried limestone blocks stacked beside cedar beams on Mount Zion", "a stone olive press brimming with new oil"]),
    "Zechariah": ("Post-Exilic Jerusalem Restoration", ["a seven-branched lampstand flanked by two olive branches", "a surveyor's measuring line stretched across Jerusalem's walls", "a quiet courtyard bench along an old Jerusalem street"]),
    "Malachi": ("Late Post-Exilic Judea", ["a refiner's clay crucible resting beside glowing hearth stones", "the first morning sunbeams cresting over a stone barn wall"]),
    "Matthew": ("1st-Century Galilee & Judea", ["the grassy hillside slopes above the Sea of Galilee", "a stone foundation built squarely upon solid bedrock", "a wooden fishing skiff drawn up on a basalt pebble shore", "an ancient gnarled olive tree in Gethsemane"]),
    "Mark": ("1st-Century Galilee & Jerusalem", ["the wind-rippled waters of the Sea of Galilee", "a mended clay pitcher resting beside an olive-oil flask", "a tiny mustard seed sprouting into a wide-branched garden shrub", "a quiet upper-room stone staircase"]),
    "Luke": ("1st-Century Judea, Samaria &Emmaus Road", ["the winding stone road from Jerusalem to Emmaus", "a stone manger trough in a quiet Bethlehem cave stable", "a shepherd's stone sheepfold in the Judean hills", "a samaritan roadside inn courtyard with an olive flask"]),
    "John": ("1st-Century Galilee & Jerusalem", ["Jacob's deep stone well in a quiet Samaritan clearing", "a fruitful grapevine trained along a low dry-stone wall", "a stone sheepfold gate opening onto morning pastures", "charcoal embers glowing on a quiet lakeshore beach"]),
    "Acts": ("1st-Century Jerusalem & Mediterranean World", ["an upper-room stone windowsill with a burning clay lamp", "the stone colonnade of Solomon's portico", "a Roman milestone along a coastal road to Caesarea", "a Mediterranean stone harbor bollard with a coiled ship rope"]),
    "Romans": ("1st-Century Rome & Mediterranean", ["a solitary stone cairn marking a quiet hilltop trail", "a wild olive branch grafted into a thick ancient olive trunk", "a potter's clay jar resting on a stone workbench", "an arched Roman stone bridge spanning a quiet river"]),
    "1 Corinthians": ("1st-Century Corinth", ["a squared cornerstone laid on solid rock in an Aegean courtyard", "an ancient polished bronze mirror resting on a wooden table", "an unbroken loaf of bread beside a simple clay cup"]),
    "2 Corinthians": ("1st-Century Macedonia & Achaia", ["a fragile earthen clay jar holding a glowing oil lamp", "an open wooden gate in an old stone courtyard wall", "an overgrown tumbledown stone ruin reclaimed by olive shoots"]),
    "Galatians": ("1st-Century Galatian Highlands", ["a fruit-laden olive branch bending in a gentle breeze", "a wooden plow resting in a freshly turned highland furrow", "a heavy iron yoke unfastened and laid aside on the ground"]),
    "Ephesians": ("1st-Century Ephesus & Asia Minor", ["a keystone locking two stone wall courses together into one arch", "a weathered Roman shield and belt resting against a stone pillar", "a deep-rooted tree beside a courtyard fountain"]),
    "Philippians": ("1st-Century Philippi (Macedonia)", ["a quiet riverside prayer place shaded by willow trees outside Philippi", "a runner's finish-line stone marker on an ancient stadium track", "abarred stone window opening onto a clear morning sky"]),
    "Colossians": ("1st-Century Lycus Valley", ["a stone steps path climbing up a quiet hillside toward an open sky", "a mountain spring feeding a deep-rooted cedar tree", "an unsealed parchment letter resting on a wooden reading desk"]),
    "1 Thessalonians": ("1st-Century Thessalonica", ["the first light of dawn breaking over the Aegean harbor horizon", "a watchman's bronze lantern hanging beside a stone city gate"]),
    "2 Thessalonians": ("1st-Century Thessalonica", ["a steadfast stone boundary pillar standing firm in a wind-swept field", "a basket of harvested grain beside a wooden sickle"]),
    "1 Timothy": ("1st-Century Ephesus", ["a tall stone pillar supporting the timber roof of a meeting hall", "a clean wooden water vessel resting beside a clay bowl"]),
    "2 Timothy": ("1st-Century Rome", ["a parchment scroll case and reed pen resting on a rough stone table", "a bronze athlete's wreath resting beside a finished track", "an unquenched oil lamp burning steady in a stone niche"]),
    "Titus": ("1st-Century Crete", ["a stone lighthouse beacon standing on a rocky Cretan headland", "an iron ship anchor resting on a cobbled harbor quay"]),
    "Philemon": ("1st-Century Colossae", ["an open courtyard guest chamber with a prepared wooden table", "a broken iron chain link resting beside an olive branch"]),
    "Hebrews": ("1st-Century Sanctuary & Pilgrimage", ["a heavy iron ship's anchor gripped firmly into seabed rock", "a narrow mountain trail ascending toward a sunlit city on a hill", "an ancient stone altar overshadowed by an open curtain"]),
    "James": ("1st-Century Jerusalem", ["a small wooden ship's rudder resting beside a horse's bridle bit", "early and latter rain falling softly over a terraced barley field", "a clear fresh spring bubbling from a mossy limestone cleft"]),
    "1 Peter": ("1st-Century Asia Minor", ["a dressed living cornerstone set firmly into a stone foundation", "a goldsmith's clay crucible beside a quiet hearth", "a shepherd's crooked staff leaning against a sheepfold gate"]),
    "2 Peter": ("1st-Century Mediterranean", ["a morning star rising above a dark coastal mountain ridge", "an oil lamp shining in a rough-walled stone room at dawn"]),
    "1 John": ("1st-Century Ephesus", ["a sunlit stone footpath winding through an ancient olive grove", "a clear brook flowing over white pebbles in morning light"]),
    "2 John": ("1st-Century Asia Minor", ["a stone threshold step leading into a welcoming courtyard home", "a reed pen and inkhorn beside a papyrus sheet"]),
    "3 John": ("1st-Century Asia Minor", ["a traveler's water flask and walking staff resting by an open door", "three oil lamps burning side by side on a wooden shelf"]),
    "Jude": ("1st-Century Judea", ["an ancient stone boundary wall guarding a hilltop vineyard", "a sturdy lighthouse tower standing against crashing waves"]),
    "Revelation": ("late 1st-Century Island of Patmos", ["an open rock-hewn garden tomb with a rolled-away stone beside blooming olive branches", "a crystal-clear river flowing between two fruiting trees on a stone street", "seven bronze oil lampstands arranged in a quiet stone sanctuary", "an open stone doorway overlooking the sea cliffs of Patmos"]),
}

# 2. Keyword-driven Object / Motif extractors (No People vs People-from-Back)
MOTIF_RULES_S2 = [
    (r"\b(lamp|light|shine|candle|lantern|darkness|dawn|morning)\b", [
        "a small Herodian clay oil lamp burning quietly on a rough-hewn stone ledge",
        "morning light streaming through a narrow stone window onto an open parchment scroll",
        "a bronze oil lantern hanging from a rough wooden peg beside a stone doorway",
        "the first clear rays of dawn cresting over a quiet limestone ridge",
    ]),
    (r"\b(tree|olive|fig|vine|branch|fruit|seed|root|leaf|leaves|cedar|palm)\b", [
        "an ancient gnarled olive tree with deep roots gripping a terraced limestone hillside",
        "a fruitful grapevine trained along a low dry-stone vineyard wall",
        "a wide-canopied fig tree rooted in rocky soil beside a stone boundary wall",
        "a solitary cedar standing firm on a wind-swept mountain ridge",
        "a fresh green olive shoot springing up from a weathered tree stump",
    ]),
    (r"\b(water|river|stream|brook|well|fountain|spring|thirst|drink|rain|dew)\b", [
        "a stone well in a quiet clearing with a wooden bucket and rope resting on its rim",
        "a clear mountain brook flowing gently between mossy limestone boulders",
        "a carved stone fountain basin brimming over onto flat courtyard flagstones",
        "an earthenware water jar resting beside a trickling rock spring",
    ]),
    (r"\b(rock|stone|fortress|refuge|shield|tower|stronghold|mountain|hill|cairn|cliff|crag)\b", [
        "a massive overhanging crag of weathered limestone sheltering a quiet mountain trail",
        "a sturdy dry-stone watchtower standing firm on a rocky hillside",
        "a solitary stone cairn marking a high mountain pass under an open sky",
        "a dressed cornerstone set squarely into a solid bedrock foundation",
    ]),
    (r"\b(bread|wheat|grain|harvest|reap|sow|field|barley|loaf|table|feast|cup)\b", [
        "a bundled sheaf of harvested barley resting on a stone threshing floor",
        "an unbroken round loaf of bread beside a simple clay cup on a wooden table",
        "a stone hand-mill and woven grain basket resting in a quiet courtyard",
        "terraced wheat fields rippling gently behind a low stacked-fieldstone wall",
    ]),
    (r"\b(door|gate|wall|house|build|threshold|window|roof|courtyard|tent)\b", [
        "an open wooden gate in an old dry-stone courtyard wall leading to a quiet pasture",
        "a heavy timber door with an iron latch set into a thick stone wall",
        "a rough stone threshold step beside an olive branch at the entrance of a dwelling",
        "a mason's plumb line hanging beside a newly repaired course of fieldstones",
    ]),
    (r"\b(way|path|road|walk|step|foot|feet|journey|highway|gate)\b", [
        "a narrow footpath bordered by stacked fieldstones winding into a quiet valley",
        "a dusty desert road winding between scattered boulders toward distant hills",
        "worn stone steps climbing up a quiet hillside toward an open horizon",
        "an ancient milestone standing beside a quiet cobbled road",
    ]),
    (r"\b(word|law|book|scroll|write|written|commandment|statute|truth|wisdom)\b", [
        "an unrolled parchment scroll weighted with smooth river stones on a wooden table",
        "two inscribed stone tablets resting beside an olive branch on a rough ledge",
        "a reed pen and clay inkwell beside an open manuscript on a reading desk",
    ]),
    (r"\b(prayer|pray|call|cry|altar|incense|sacrifice|offering|mercy|grace)\b", [
        "an unhewn twelve-stone altar standing quietly on a wind-swept hilltop",
        "an empty clay bowl resting on a rough stone ledge beside a trickling spring",
        "a small stone incense altar in a quiet courtyard corner at daybreak",
    ]),
    (r"\b(sea|wave|ship|boat|anchor|storm|wind|harbor|fish|net)\b", [
        "a wooden fishing skiff drawn up on a pebbled basalt shoreline with a folded net",
        "a heavy iron anchor resting on a stone harbor quay beside coiled rope",
        "a stone breakwater standing calm against rolling coastal waves",
    ]),
    (r"\b(heal|sick|physician|broken|mend|bind|wound|oil|balm)\b", [
        "a mended clay pitcher resting beside a small olive-oil flask on a wooden table",
        "an alabaster ointment jar and linen bandage resting on a stone bench",
    ]),
    (r"\b(gold|silver|treasure|scale|balance|weight|coin|pearl|crown)\b", [
        "a brass balance scale with stone weights resting on a merchant's wooden table",
        "a clay refining crucible resting beside warm hearth stones",
    ]),
]

PEOPLE_BACK_MOTIFS_S4 = [
    "a robed shepherd seen strictly from the back standing beside a low dry-stone wall with a wooden staff in hand looking out toward {geo}",
    "a solitary cloaked traveler seen from behind walking along a stony path through {geo}",
    "two robed companions seen strictly from the back walking side by side along a fieldstone trail into {geo}",
    "a solitary robed watchman seen from the back standing on a stone rampart overlooking {geo}",
    "a sower in a simple tunic seen from behind walking a plowed furrow across {geo}",
    "a kneeling robed figure seen strictly from the back in quiet prayer beside a rough stone ledge in {geo}",
    "a fisherman seen from behind standing on the shore mending a net beside a wooden boat along {geo}",
    "a solitary pilgrim seen strictly from the back ascending worn stone steps toward {geo}",
]


def norm_cite(c: str) -> str:
    m = re.match(r"^(.+?\s+\d+:\d+)", c.strip())
    return m.group(1) if m else c.strip()


def pick_unique_prompt(book: str, chapter: int, citation: str, text: str, plain: str, used_prompts: set, force_people: bool = False) -> tuple[str, str, str]:
    """Returns (visual_prompt, spec_id, humanizer) guaranteed unique across used_prompts."""
    era, geo_list = BOOK_GEO_ERA.get(book, ("Biblical Antiquity", ["the quiet Judean hills", "a stony valley path"]))
    h_int = int(hashlib.sha256(citation.encode("utf-8")).hexdigest()[:8], 16)
    geo = geo_list[h_int % len(geo_list)]
    combined = f"{text} {plain}".lower()

    if force_people:
        base_tpl = PEOPLE_BACK_MOTIFS_S4[h_int % len(PEOPLE_BACK_MOTIFS_S4)]
        candidate = base_tpl.format(geo=geo)
        spec_id, hum = "fhg_sketch_people_spec", "G2+S3"
    else:
        matched_Pool = None
        for pat, pool in MOTIF_RULES_S2:
            if re.search(pat, combined):
                matched_Pool = pool
                break
        if matched_Pool:
            base_obj = matched_Pool[h_int % len(matched_Pool)]
        else:
            fallback_objs = [
                "a weathered dry-stone boundary wall and wild olive branch",
                "a quiet stone courtyard archway opening onto the hills",
                "a stacked fieldstone cairn beside a winding footpath",
                "an earthenware water pitcher resting on a rough stone bench",
                "a gnarled fig tree casting open contour lines across rocky ground",
                "a rough-hewn limestone bench overlooking a quiet valley",
            ]
            base_obj = fallback_objs[h_int % len(fallback_objs)]
        candidate = f"{base_obj} in {geo}"
        spec_id, hum = "fhg_sketch_spec", "G2+S2"

    # Guarantee 100% uniqueness across all 1,284 passages
    if candidate in used_prompts:
        # Add specific concrete detail from the verse/citation context
        words = [w for w in re.findall(r"[a-z]{4,}", combined) if w not in {
            "that", "this", "with", "from", "have", "will", "your", "they", "them", "their",
            "unto", "shall", "lord", "said", "when", "into", "upon", "there", "were", "what",
            "which", "make", "made", "know", "come", "came", "because", "before", "after", "every"
        }]
        anchor_detail = words[0] if words else f"chapter {chapter}"
        alt_geo = geo_list[(h_int + 1) % len(geo_list)]
        candidate = f"{candidate} near {alt_geo} ({citation.lower()} motif: {anchor_detail})"
        idx = 2
        while candidate in used_prompts:
            candidate = f"{candidate} #{idx}"
            idx += 1

    used_prompts.add(candidate)
    return candidate, spec_id, hum


def main():
    # Load the 25 locked sample verses first
    sample_path = os.path.join(BIBLE_DIR, "bible_visual_sample_25.json")
    with open(sample_path, "r", encoding="utf-8") as f:
        sample25 = json.load(f)

    # Master lookup by exact citation and normalized citation
    canonical_by_cite = {}
    canonical_by_norm = {}
    used_prompts = set()

    for v in sample25["verses"]:
        rec = {
            "visual_prompt": v["visual_prompt"],
            "spec_id": v["spec_id"],
            "humanizer": v["humanizer"],
        }
        if "image_file" in v:
            rec["image_file"] = v["image_file"]
        canonical_by_cite[v["citation"].strip()] = rec
        canonical_by_norm[norm_cite(v["citation"])] = rec
        used_prompts.add(v["visual_prompt"])

    # Load bible_index.json to iterate over all 63 per-book JSON files (834 verses)
    bidx_path = os.path.join(BIBLE_DIR, "bible_index.json")
    with open(bidx_path, "r", encoding="utf-8-sig") as f:
        bidx = json.load(f)

    # Track processed files so gospels_daily.json isn't written 4 times unnecessarily
    file_cache = {}
    for bmeta in bidx["books"]:
        fn = bmeta["file"]
        fpath = os.path.join(BIBLE_DIR, fn)
        if fn not in file_cache:
            with open(fpath, "r", encoding="utf-8-sig") as f:
                file_cache[fn] = json.load(f)

    verse_counter = 0
    s4_count_verses = 0

    for bmeta in bidx["books"]:
        fn = bmeta["file"]
        arr_key = bmeta["arrayKey"]
        bname = bmeta["book"]
        data = file_cache[fn]
        records = data[arr_key]

        for r in records:
            if fn == "gospels_daily.json" and r.get("book") != bname:
                continue
            verse_counter += 1
            cite = r["citation"].strip()
            nc = norm_cite(cite)

            if cite in canonical_by_cite:
                spec = canonical_by_cite[cite]
            elif nc in canonical_by_norm:
                spec = canonical_by_norm[nc]
            else:
                # ~10% People Seen Strictly from the Back (every 10th verse on narrative/person-friendly verses)
                force_p = (verse_counter % 10 == 0)
                vp, sid, hum = pick_unique_prompt(
                    bname, r.get("chapter", 1), cite, r.get("text", ""), r.get("plain", ""), used_prompts, force_people=force_p
                )
                spec = {"visual_prompt": vp, "spec_id": sid, "humanizer": hum}
                canonical_by_cite[cite] = spec
                canonical_by_norm[nc] = spec

            r["visual_prompt"] = spec["visual_prompt"]
            r["spec_id"] = spec["spec_id"]
            r["humanizer"] = spec["humanizer"]
            if "image_file" in spec:
                r["image_file"] = spec["image_file"]
            if r["humanizer"] == "S4":
                s4_count_verses += 1

    # Save all 63 per-book JSON files
    for fn, data in file_cache.items():
        fpath = os.path.join(BIBLE_DIR, fn)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # Also update bible_data.js so bible_viewer.html has all 834 visual_prompts live
    bdata_path = os.path.join(BIBLE_DIR, "bible_data.js")
    with open(bdata_path, "r", encoding="utf-8-sig") as f:
        btxt = f.read()
    bobj = json.loads(btxt[btxt.find("{"):btxt.rfind("}") + 1])
    for b in bobj["books"]:
        for v in b["verses"]:
            cite = v["citation"].strip()
            spec = canonical_by_cite.get(cite) or canonical_by_norm.get(norm_cite(cite))
            if spec:
                v["visual_prompt"] = spec["visual_prompt"]
                v["spec_id"] = spec["spec_id"]
                v["humanizer"] = spec["humanizer"]
                if "image_file" in spec:
                    v["image_file"] = spec["image_file"]
    with open(bdata_path, "w", encoding="utf-8") as f:
        f.write("window.BIBLE = " + json.dumps(bobj, ensure_ascii=False) + ";\n")

    # 2. Now populate all 660 Actionable Study Lessons (`bible_study_lessons.json` + `bible_study_viewer.html`)
    study_json_path = os.path.join(BIBLE_DIR, "bible_study_lessons.json")
    with open(study_json_path, "r", encoding="utf-8-sig") as f:
        study_data = json.load(f)

    lesson_counter = 0
    crossover_reused = 0
    s4_count_lessons = 0

    for b in study_data["books"]:
        bname = b["book"]
        for l in b["lessons"]:
            lesson_counter += 1
            cite = l["citation"].strip()
            nc = norm_cite(cite)

            if cite in canonical_by_cite:
                spec = canonical_by_cite[cite]
                crossover_reused += 1
            elif nc in canonical_by_norm:
                spec = canonical_by_norm[nc]
                crossover_reused += 1
            else:
                force_p = (lesson_counter % 10 == 0)
                m_ch = re.search(r"\s(\d+):", cite)
                ch_num = int(m_ch.group(1)) if m_ch else 1
                vp, sid, hum = pick_unique_prompt(
                    bname, ch_num, cite, l.get("scripture_text", ""), l.get("lesson", "") + " " + l.get("title", ""), used_prompts, force_people=force_p
                )
                spec = {"visual_prompt": vp, "spec_id": sid, "humanizer": hum}
                canonical_by_cite[cite] = spec
                canonical_by_norm[nc] = spec

            l["visual_prompt"] = spec["visual_prompt"]
            l["spec_id"] = spec["spec_id"]
            l["humanizer"] = spec["humanizer"]
            if "image_file" in spec:
                l["image_file"] = spec["image_file"]
            if l["humanizer"] == "S4":
                s4_count_lessons += 1

    with open(study_json_path, "w", encoding="utf-8") as f:
        json.dump(study_data, f, indent=2, ensure_ascii=False)

    # Also sync embedded `const studyData = ...;` inside `bible_study_viewer.html`
    sviewer_path = os.path.join(BIBLE_DIR, "bible_study_viewer.html")
    with open(sviewer_path, "r", encoding="utf-8-sig") as f:
        sv_txt = f.read()
    new_const = "const studyData = " + json.dumps(study_data, ensure_ascii=False) + ";\n"
    sv_txt_updated = re.sub(r"const studyData\s*=\s*\{.*?\};\s*\n", lambda _: new_const, sv_txt, count=1, flags=re.S)
    with open(sviewer_path, "w", encoding="utf-8") as f:
        f.write(sv_txt_updated)

    print(f"Populated {verse_counter} Key Verses (S2: {verse_counter - s4_count_verses}, S4 People: {s4_count_verses}).")
    print(f"Populated {lesson_counter} Study Lessons (S2: {lesson_counter - s4_count_lessons}, S4 People: {s4_count_lessons}; Crossover Reused: {crossover_reused}).")
    print(f"Total Unique Visual Prompts Generated Across Both Catalogs: {len(used_prompts)} (Zero duplicates).")


if __name__ == "__main__":
    main()
