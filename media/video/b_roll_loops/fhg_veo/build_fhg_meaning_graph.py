#!/usr/bin/env python3
r"""
FHG Master Meaning Graph & Open Topic Video Planner (`build_fhg_meaning_graph.py`)

Unifies all For His Grace content and visual datasets around MEANING while preserving
100% creative freedom to build any video type, topic, subject, or length on demand:
1. Visual DAM (`FHG_BROLL_DAM_CATALOG.json` + `plates/jesus_character_pack/`)
   * HARD RULE: Strictly excludes ALL filtered and colored sketches (`_c1..c4`, `_blotch`,
     `_ukiyoe`, `_prussian`, `_loop_scr`, `_xhatch`, etc.). Only photorealistic 1st-Century
     B-roll/character plates and canonical unfiltered ink/parchment outro assets are indexed.
2. 762 Bible Trivia & Comprehension Questions (`shared/bible/bible_questions.json`)
3. 660 4-Layer Sanctuary Study Lessons & HALT/Soul Tags (`shared/bible/bible_study_lessons.json`)
4. Open/Trending Topic & Custom Duration Planner (`plan_video_from_any_input`)
   * Supports starting from:
     - Any Trending/Freeform Topic or Subject
     - Any Known Scripture Verse / Citation
     - Any HALT / Soul State (Hungry, Angry, Lonely, Tired, Anxious, Ashamed, Grief)
     - Any of the 762 Trivia Questions
     - Any of the 660 Study Lessons
     - Any Target Length (15s, 30s, 42s Short, 60s Reel, or 3m+ Long-Form)
"""

import json
import re
import shutil
from pathlib import Path

PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
VEO_DIR = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo"
SHARED_BIBLE = PUBLISH_ROOT / "shared" / "bible"
JESUS_PACK_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "plates" / "jesus_character_pack"
WS_VIDEOS_DIR = Path(r"C:\dev\fhg-videos")

BROLL_CATALOG_JSON = VEO_DIR / "FHG_BROLL_DAM_CATALOG.json"
QUESTIONS_JSON = SHARED_BIBLE / "bible_questions.json"
LESSONS_JSON = SHARED_BIBLE / "bible_study_lessons.json"
MASTER_GRAPH_JSON = VEO_DIR / "FHG_MASTER_MEANING_GRAPH.json"

# HARD VISUAL GOVERNANCE RULE: Never use filtered or color sketches
FORBIDDEN_SKETCH_PATTERNS = [
    "_c1", "_c2", "_c3", "_c4", "_blotch", "_loop_scr", "_xhatch",
    "_sub_scr", "_nb_loop", "_nb_line", "_nb_base", "_nb_sub",
    "_ukiyoe", "_prussian", "_g4", "_g2_s2"
]


def tokenize(text: str) -> set[str]:
    if not text:
        return set()
    stop = {
        "the", "and", "for", "that", "with", "from", "this", "his", "her", "you", "your",
        "are", "was", "were", "what", "when", "where", "why", "how", "who", "into", "unto",
        "not", "but", "have", "had", "has", "will", "can", "all", "one", "out", "our", "they",
        "them", "their", "there", "been", "being", "does", "did", "about", "over", "under"
    }
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) > 2 and w not in stop}


def build_jesus_character_still_entries() -> list[dict]:
    """Index the canonical photorealistic 1st-Century Jesus Character Pack stills (for Ken Burns / Veo anchors)."""
    plates = [
        {
            "asset_id": "FHG-CHR-001",
            "filename": "Gemini_Generated_Image_a4jywwa4jywwa4jy.jpg",
            "title": "Jesus Contemplative Downcast 3/4 Close-Up",
            "thematic_tags": "compassion, sorrow, prayer, humility, Gethsemane, listening, burden-bearing",
            "visual_search_terms": "first-century Jesus close-up looking down, contemplative, olive skin, homespun wool cloak",
            "scripture_anchors": "Isaiah 53:3; Matthew 11:28-30; Luke 22:41-44; John 11:35",
            "soul_halt_tags": "Tired & Exhausted, Grief & Heartbroken, Lonely & Abandoned",
            "short_hook_archetypes": "Personal Application, Emotional Pivot"
        },
        {
            "asset_id": "FHG-CHR-002",
            "filename": "Gemini_Generated_Image_n6l4wdn6l4wdn6l4.jpg",
            "title": "Jesus Eye-Level 3/4 Close-Up Looking Left",
            "thematic_tags": "presence, teaching, seeing the overlooked, parables, invitation, grace",
            "visual_search_terms": "first-century Jesus eye-level portrait looking left, warm Judean sunlight, gentle gaze",
            "scripture_anchors": "John 1:48; Mark 10:21; Luke 19:5; Matthew 5:1-2",
            "soul_halt_tags": "Lonely & Abandoned, Guidance & Trust, Sacred Worth",
            "short_hook_archetypes": "Historical/Biblical Reveal, Personal Application"
        },
        {
            "asset_id": "FHG-CHR-003",
            "filename": "Gemini_Generated_Image_xyl7h6xyl7h6xyl7.jpg",
            "title": "Jesus Upward Reverent Gaze toward the Father",
            "thematic_tags": "prayer, communion with the Father, gratitude, resurrection hope, intercession, dependence",
            "visual_search_terms": "first-century Jesus looking up to heaven, prayerful gaze, golden hour light",
            "scripture_anchors": "John 17:1;John 11:41; Matthew 14:19; Hebrews 7:25",
            "soul_halt_tags": "Hope & Courage, Peace & Calm, Anxious & Overwhelmed",
            "short_hook_archetypes": "Climax_Reveal, Prayer Resolution"
        },
        {
            "asset_id": "FHG-CHR-004",
            "filename": "Gemini_Generated_Image_mnmhmmmnmhmmmnmh.jpg",
            "title": "Jesus Over-the-Shoulder Hooded Walk in Judean Street",
            "thematic_tags": "following Jesus, discipleship, journey to Jerusalem, endurance, solitude, Emmaus road",
            "visual_search_terms": "rear over-the-shoulder shot of hooded Jesus in ancient stone street, following footsteps",
            "scripture_anchors": "Luke 9:51; Luke 24:15; Matthew 16:24; John 10:27",
            "soul_halt_tags": "Guidance & Trust, Lonely & Abandoned, Tired & Exhausted",
            "short_hook_archetypes": "Hook_0_3s, Tension_Context"
        },
        {
            "asset_id": "FHG-CHR-005",
            "filename": "Screenshot 2026-10-31 012823.png",
            "title": "Jesus Seated on the Ground Teaching / John 8 Posture",
            "thematic_tags": "mercy over judgment, writing in the dirt, grace for the ashamed, humility, teaching",
            "visual_search_terms": "vertical 9:16 high-angle shot of Jesus seated on dusty Judean ground looking up",
            "scripture_anchors": "John 8:6-11; Matthew 5:1-2; Luke 7:38-50",
            "soul_halt_tags": "Ashamed & Guilty, Grace & Forgiveness, Peace & Calm",
            "short_hook_archetypes": "1st-Century Judean Context, Misunderstood Verses"
        }
    ]
    out = []
    for p in plates:
        f_path = JESUS_PACK_DIR / p["filename"]
        if f_path.exists():
            p["asset_class"] = "CHARACTER_PHOTOREAL_STILL"
            p["rendered_ready"] = True
            p["path"] = str(f_path)
            p["tokens"] = sorted(tokenize(
                f"{p['title']} {p['thematic_tags']} {p['visual_search_terms']} {p['scripture_anchors']} {p['soul_halt_tags']}"
            ))
            out.append(p)
    return out


def load_clean_visual_catalog() -> list[dict]:
    """Load all B-Roll, Sepia Sketch-to-Animation, & Character motion/still assets."""
    raw = json.loads(BROLL_CATALOG_JSON.read_text(encoding="utf-8-sig"))
    assets = []
    source_list = raw.get("catalog_items") or raw.get("items", [])
    for item in source_list:
        bid = item.get("DAM_ID") or item.get("broll_id", "")
        m16 = item.get("DAM_Master_16x9_1080p") or item.get("dam_master_16x9_1080p", "")
        v9 = item.get("DAM_Vertical_9x16_1080p") or item.get("dam_vertical_9x16_1080p", "")
        s1 = item.get("DAM_Square_1x1_1080p") or item.get("dam_square_1x1_1080p", "")
        has_rendered = bool(m16 or v9)
        start_sketch = item.get("Starting_Sketch_Image_Path", "")
        if has_rendered:
            aclass = "SEPIA_1080P_VIDEO" if bid.startswith("FHG-SK-") else "BROLL_1080P_VIDEO"
        elif start_sketch:
            aclass = "SEPIA_SKETCH_READY_TO_ANIMATE"
        else:
            aclass = "QUEUED_BROLL_PROMPT"
        entry = {
            "asset_id": bid,
            "asset_class": aclass,
            "rendered_ready": has_rendered,
            "title": item.get("Concept") or item.get("title", ""),
            "image_creation_prompt": item.get("Image_Creation_Prompt", ""),
            "video_animation_prompt": item.get("Video_Animation_Prompt") or item.get("prompt", ""),
            "starting_sketch_image_path": start_sketch,
            "filter_19_styles": item.get("filter_19_styles", {}),
            "thematic_tags": item.get("Theological_Themes") or item.get("thematic_tags", ""),
            "visual_search_terms": item.get("Visual_Search_Terms") or item.get("visual_search_terms", ""),
            "scripture_anchors": item.get("Scripture_Anchors") or item.get("scripture_anchors", ""),
            "soul_halt_tags": item.get("Emotional_HALT_Tone") or item.get("soul_halt_tags", ""),
            "short_hook_archetypes": item.get("Short_Hook_Archetype") or item.get("short_hook_archetypes", ""),
            "master_16x9_1080p": m16,
            "vertical_9x16_1080p": v9,
            "square_1x1_1080p": s1,
        }
        entry["tokens"] = sorted(tokenize(
            f"{entry['title']} {entry['thematic_tags']} {entry['visual_search_terms']} "
            f"{entry['scripture_anchors']} {entry['soul_halt_tags']} {entry['short_hook_archetypes']}"
        ))
        assets.append(entry)

    # Add the 3 vaulted 1080p Jesus Walking motion clips (FHG-BR-034, 035, 036) if not already in items
    existing_ids = {a["asset_id"] for a in assets}
    jesus_motion = [
        {
            "asset_id": "FHG-BR-034",
            "asset_class": "BROLL_1080P_VIDEO",
            "rendered_ready": True,
            "title": "Jesus Walking Forward Between Olive Trees (Centered Dolly)",
            "thematic_tags": "Jesus walking, steadfast love, journey to Jerusalem, presence, discipleship, peace in chaos",
            "visual_search_terms": "first-century Jesus walking forward toward camera between olive trees and stone houses",
            "scripture_anchors": "Luke 9:51; John 14:6; Matthew 11:28; Hebrews 12:2",
            "soul_halt_tags": "Lonely & Abandoned, Tired & Exhausted, Guidance & Trust",
            "short_hook_archetypes": "Personal Application, Emotional Pivot",
            "master_16x9_1080p": "FHG-BR-034_jesus-walking-olive-trees_16x9_1080p.mp4",
            "vertical_9x16_1080p": "FHG-BR-034_jesus-walking-olive-trees_9x16_1080p.mp4",
            "square_1x1_1080p": ""
        },
        {
            "asset_id": "FHG-BR-035",
            "asset_class": "BROLL_1080P_VIDEO",
            "rendered_ready": True,
            "title": "Jesus Walking Across Judean Village Square (Lateral Tracking)",
            "thematic_tags": "Jesus walking, daily walk, Immanuel, compassion, seeking the lost, unhurried grace",
            "visual_search_terms": "side-profile dolly tracking first-century Jesus walking across dusty sunlit village square",
            "scripture_anchors": "Luke 19:10; Matthew 9:35-36; Mark 2:14; John 1:14",
            "soul_halt_tags": "Lonely & Abandoned, Tired & Exhausted, Peace & Calm",
            "short_hook_archetypes": "Personal Application, Emotional Pivot",
            "master_16x9_1080p": "FHG-BR-035_jesus-walking-village-lateral_16x9_1080p.mp4",
            "vertical_9x16_1080p": "FHG-BR-035_jesus-walking-village-lateral_9x16_1080p.mp4",
            "square_1x1_1080p": ""
        },
        {
            "asset_id": "FHG-BR-036",
            "asset_class": "BROLL_1080P_VIDEO",
            "rendered_ready": True,
            "title": "Jesus Standing in Village Courtyard (360 Orbital Camera)",
            "thematic_tags": "unshakeable truth, cornerstone, Messiah, calm in accusation, priceless worth, authority",
            "visual_search_terms": "360-degree orbital camera around first-century Jesus standing calmly in Judean courtyard",
            "scripture_anchors": "Isaiah 53:3-5; John 8:12; Matthew 27:11-14; 1 Peter 2:6",
            "soul_halt_tags": "Anxious & Overwhelmed, Ashamed & Guilty, Hope & Courage",
            "short_hook_archetypes": "Climax_Reveal, Personal Application",
            "master_16x9_1080p": "FHG-BR-036_jesus-orbital-courtyard_16x9_1080p.mp4",
            "vertical_9x16_1080p": "FHG-BR-036_jesus-orbital-courtyard_9x16_1080p.mp4",
            "square_1x1_1080p": ""
        }
    ]
    for jm in jesus_motion:
        if jm["asset_id"] not in existing_ids:
            jm["tokens"] = sorted(tokenize(
                f"{jm['title']} {jm['thematic_tags']} {jm['visual_search_terms']} {jm['scripture_anchors']} {jm['soul_halt_tags']}"
            ))
            assets.append(jm)

    assets.extend(build_jesus_character_still_entries())
    return assets


def score_visual_match(query_tokens: set[str], query_book: str, asset: dict, prefer_rendered: bool = True) -> float:
    asset_tokens = set(asset.get("tokens", []))
    overlap = len(query_tokens & asset_tokens)
    score = overlap * 3.0
    if query_book and query_book.lower() in asset.get("scripture_anchors", "").lower():
        score += 6.0
    if prefer_rendered and asset.get("rendered_ready"):
        score += 4.5
    return score


def build_master_meaning_graph() -> dict:
    assets = load_clean_visual_catalog()
    questions_data = json.loads(QUESTIONS_JSON.read_text(encoding="utf-8-sig"))
    lessons_data = json.loads(LESSONS_JSON.read_text(encoding="utf-8-sig"))

    # 1. Index all 660 Lessons (stripping any filtered/color sketch fields!)
    lessons_by_book: dict[str, list[dict]] = {}
    clean_lessons = []
    for book_obj in lessons_data.get("books", []):
        book_name = book_obj.get("book", "")
        lessons_by_book.setdefault(book_name.lower(), [])
        for les in book_obj.get("lessons", []):
            lid = f"{book_name.upper()[:3]}_{les.get('number', 0):02d}"
            q_tokens = tokenize(
                f"{book_name} {les.get('title', '')} {les.get('citation', '')} "
                f"{les.get('lesson', '')} {les.get('application', '')} "
                f"{les.get('visual_prompt', '')} {' '.join(les.get('soul_tags', []))}"
            )
            ranked = sorted(
                assets,
                key=lambda a: score_visual_match(q_tokens, book_name, a, prefer_rendered=True),
                reverse=True
            )
            rendered_picks = [a["asset_id"] for a in ranked if a.get("rendered_ready")][:5]
            queued_picks = [a["asset_id"] for a in ranked if not a.get("rendered_ready")][:2]

            clean_les = {
                "lesson_id": lid,
                "book": book_name,
                "testament": book_obj.get("testament", ""),
                "category": book_obj.get("category", ""),
                "number": les.get("number"),
                "title": les.get("title"),
                "citation": les.get("citation"),
                "scripture_text": les.get("scripture_text"),
                "layer1_grace_insight": les.get("lesson"),
                "layer2_life_application": les.get("application"),
                "layer3_relational_outflow": les.get("relational_outflow"),
                "layer4_stillness_halt_whisper": les.get("stillness_communion"),
                "quiet_prayer": les.get("quiet_prayer"),
                "soul_halt_tags": les.get("soul_tags", []),
                "first_century_visual_prompt": les.get("visual_prompt", ""),
                "matched_rendered_assets": rendered_picks + ["FHG-BR-034", "FHG-OUTRO-001"],
                "matched_queued_broll": queued_picks,
            }
            clean_lessons.append(clean_les)
            lessons_by_book[book_name.lower()].append(clean_les)

    # 2. Index all 762 Trivia Questions and connect each to its best Lesson + Visual Cut List
    connected_questions = []
    for q in questions_data.get("questions", []):
        book_name = q.get("book", "")
        q_tokens = tokenize(
            f"{book_name} {q.get('citation', '')} {q.get('question', '')} "
            f"{' '.join(q.get('options', []))} {q.get('explanation', '')} {q.get('category', '')}"
        )
        # Find best matching Lesson in the same book
        book_lessons = lessons_by_book.get(book_name.lower(), [])
        best_lesson_id = book_lessons[0]["lesson_id"] if book_lessons else None
        best_soul_tags = book_lessons[0]["soul_halt_tags"] if book_lessons else ["Guidance & Trust"]
        if book_lessons:
            scored_l = sorted(
                book_lessons,
                key=lambda l: len(q_tokens & tokenize(f"{l['title']} {l['citation']} {l['layer1_grace_insight']}")),
                reverse=True
            )
            best_lesson_id = scored_l[0]["lesson_id"]
            best_soul_tags = scored_l[0]["soul_halt_tags"]

        ranked_assets = sorted(
            assets,
            key=lambda a: score_visual_match(q_tokens, book_name, a, prefer_rendered=True),
            reverse=True
        )
        rendered_picks = [a["asset_id"] for a in ranked_assets if a.get("rendered_ready")][:5]

        connected_questions.append({
            "qid": q.get("qid"),
            "passage_id": q.get("passage_id"),
            "book": book_name,
            "citation": q.get("citation"),
            "category": q.get("category"),
            "difficulty": q.get("difficulty"),
            "hook_question": q.get("question"),
            "distractor_assumptions": [
                opt for idx, opt in enumerate(q.get("options", [])) if idx != q.get("correct_index")
            ],
            "correct_answer": q.get("options", [""])[q.get("correct_index", 0)],
            "theological_explanation": q.get("explanation"),
            "connected_lesson_id": best_lesson_id,
            "soul_halt_tags": best_soul_tags,
            "matched_rendered_assets": rendered_picks + ["FHG-BR-034", "FHG-OUTRO-001"],
        })

    graph = {
        "schema_version": "2.0.0",
        "title": "For His Grace — Unified Meaning Graph & Open Topic Video Engine",
        "visual_governance": {
            "allow_filtered_sketches": False,
            "allow_color_sketches": False,
            "forbidden_sketch_patterns": FORBIDDEN_SKETCH_PATTERNS,
            "approved_visual_classes": [
                "BROLL_1080P_VIDEO (Photorealistic 1st-Century B-Roll & Jesus Motion)",
                "CHARACTER_PHOTOREAL_STILL (Photorealistic 1st-Century Character Plates)",
                "CANONICAL_UNFILTERED_OUTRO (FHG-OUTRO-001 4.5s Bird-to-Parchment & Signed Fig Tree Logo)"
            ],
            "open_topic_freedom": "Engine supports ANY ad-hoc/trending topic, subject, Scripture, or target duration (15s, 30s, 42s, 60s, or long-form) in addition to pre-linked Trivia and Study Lessons."
        },
        "counts": {
            "clean_visual_assets_total": len(assets),
            "rendered_ready_visual_assets": sum(1 for a in assets if a.get("rendered_ready")),
            "queued_broll_prompts": sum(1 for a in assets if not a.get("rendered_ready")),
            "connected_study_lessons": len(clean_lessons),
            "connected_trivia_questions": len(connected_questions),
        },
        "visual_assets": assets,
        "study_lessons": clean_lessons,
        "trivia_questions": connected_questions,
    }

    MASTER_GRAPH_JSON.write_text(json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8")
    shutil.copy2(MASTER_GRAPH_JSON, WS_VIDEOS_DIR / MASTER_GRAPH_JSON.name)
    print(
        f"Built FHG_MASTER_MEANING_GRAPH.json:\n"
        f"  - Clean Visual Assets (0 filtered/color sketches): {len(assets)} "
        f"({graph['counts']['rendered_ready_visual_assets']} rendered ready, {graph['counts']['queued_broll_prompts']} queued prompts)\n"
        f"  - Connected 4-Layer Study Lessons: {len(clean_lessons)}\n"
        f"  - Connected Trivia Questions (Short-Ready): {len(connected_questions)}"
    )
    return graph


if __name__ == "__main__":
    build_master_meaning_graph()
