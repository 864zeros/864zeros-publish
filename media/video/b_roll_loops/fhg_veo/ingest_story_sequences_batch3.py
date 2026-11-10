#!/usr/bin/env python3
r"""
1. Masters the 9 new Biblical Jesus Story videos in `C:\dev\fhg-videos\` (Paralytic Lowered Through the Roof
   & Ten Lepers Healed from Afar) into `1080p` (`16:9`, `9:16`, `1:1`) as `FHG-BR-059` .. `FHG-BR-067`.
2. Updates `FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv`, `FHG_BROLL_DAM_CATALOG.json`, and `FHG_MASTER_MEANING_GRAPH.json`.
3. Builds the interactive local web app `C:\dev\fhg-videos\fhg_video_metadata_studio.html` so Jeff can view
   every video & image across `C:\dev\fhg-videos\`, group them into multi-shot Biblical Stories, edit descriptions,
   Scripture anchors, HALT tags, and sequence order, and save/export directly.
"""

import csv
import json
import shutil
from pathlib import Path
from ingest_and_master_fhg_brole_batch2 import (
    CATALOG_JSON,
    CSV_PATH,
    DAM_BROLL_LIB,
    WS_VIDEOS_DIR,
    master_clip_1080p,
)
from build_fhg_meaning_graph import build_master_meaning_graph

STORY_CLIPS_ROOT = [
    # STORY 1: THE PARALYTIC LOWERED THROUGH THE ROOF (Mark 2:1-12 / Luke 5:17-26)
    {
        "broll_id": "FHG-BR-059",
        "story_group": "Story: The Paralytic Lowered Through the Roof (Mark 2:1-12)",
        "story_beat": 1,
        "title": "Crowd Gathering at Capernaum Stone House Doorway",
        "src_16x9": "Crowd_gathering_at_stone_house_747d5c85.mp4",
        "prompt": "A large first-century Judean crowd pressing outside the doorway of a stone house in Capernaum so no one can enter, cutting to the packed timber-ceiling room inside.",
        "visual_search_terms": "first-century crowd gathered outside stone house doorway, packed room inside, timber reed ceiling, Capernaum",
        "thematic_tags": "paralytic lowered through roof, Mark 2, Luke 5, barriers to Jesus, crowded doorway, seeking healing",
        "scripture_anchors": "Mark 2:1-2; Luke 5:17-19; Matthew 9:1-2",
        "soul_halt_tags": "Blocked & Discouraged, Seeking God, Perseverance",
        "short_hook_archetypes": "Story Beat 1 (The Obstacle), 1st-Century Capernaum House Architecture",
    },
    {
        "broll_id": "FHG-BR-060",
        "story_group": "Story: The Paralytic Lowered Through the Roof (Mark 2:1-12)",
        "story_beat": 2,
        "title": "Four Friends Carrying Paralyzed Man Up Roof Steps",
        "src_16x9": "Four_men_carrying_paralyzed_man_0f8d8d6f.mp4",
        "prompt": "Four first-century men carrying a paralyzed friend on a woven reed mat up the exterior stone staircase onto the flat roof of a Judean house ('Keep it steady, I have this corner').",
        "visual_search_terms": "four men carrying paralyzed man on woven reed stretcher mat up stone steps onto flat roof",
        "thematic_tags": "faith of friends, carrying one another's burdens, intercession, brotherhood, refusing to give up, Mark 2:3",
        "scripture_anchors": "Mark 2:3-4; Luke 5:18-19; Galatians 6:2; Ecclesiastes 4:9-10",
        "soul_halt_tags": "Tired & Exhausted, Lonely & Abandoned, Fellowship & Support, Hope & Courage",
        "short_hook_archetypes": "Story Beat 2 (Faith in Action), Personal Application (Who Carries Your Mat?)",
    },
    {
        "broll_id": "FHG-BR-061",
        "story_group": "Story: The Paralytic Lowered Through the Roof (Mark 2:1-12)",
        "story_beat": 3,
        "title": "Four Men Digging Through the Mud-and-Thatch Roof",
        "src_16x9": "Men_tearing_open_roof_e35017dc.mp4",
        "prompt": "Four men on a flat first-century Judean roof digging with their hands through dried mud and reed thatch between wooden roof beams as dust and sunlight break into the room below.",
        "visual_search_terms": "four men tearing open dried mud and reed thatch roof, dust falling between wooden ceiling beams, sunlight shaft",
        "thematic_tags": "unstoppable faith, digging through the roof, Mark 2:4, bold intercession, breaking through obstacles",
        "scripture_anchors": "Mark 2:4; Luke 5:19; Matthew 7:7-8; Hebrews 11:6",
        "soul_halt_tags": "Desperate Faith, Perseverance, Courage",
        "short_hook_archetypes": "Story Beat 3 (1st-Century Mud-and-Wattle Roofs), Hook_0_3s",
    },
    {
        "broll_id": "FHG-BR-062",
        "story_group": "Story: The Paralytic Lowered Through the Roof (Mark 2:1-12)",
        "story_beat": 4,
        "title": "Lowering the Paralyzed Man on Ropes Before Jesus",
        "src_16x9": "Men_lowering_paralyzed_man_on_1ff01283.mp4",
        "prompt": "Inside the dim stone house, the paralyzed man on his woven mat is lowered by ropes through a blinding shaft of sunlight from the opened ceiling directly to the feet of Jesus.",
        "visual_search_terms": "paralyzed man lowered on ropes through hole in ceiling, sunbeam shaft, crowd watching in awe, Jesus looking down with compassion",
        "thematic_tags": "your sins are forgiven, healing the paralytic, seeing their faith, authority of Jesus, Mark 2:5-12",
        "scripture_anchors": "Mark 2:4-12; Luke 5:19-25; Matthew 9:2-7; Psalm 103:2-3",
        "soul_halt_tags": "Ashamed & Guilty, Healing & Comfort, Grace & Forgiveness",
        "short_hook_archetypes": "Story Beat 4 (Climax Reveal — 'When Jesus Saw Their Faith')",
    },
    # STORY 2: THE TEN LEPERS HEALED FROM AFAR & THE ONE WHO RETURNED (Luke 17:11-19)
    {
        "broll_id": "FHG-BR-063",
        "story_group": "Story: The Ten Lepers Healed from Afar (Luke 17:11-19)",
        "story_beat": 1,
        "title": "Ten Lepers Crying Out to Jesus from Afar ('Jesus, Master, Look Upon Us!')",
        "src_16x9": "Figures_walking_on_dusty_trail_c17b6e5a.mp4",
        "prompt": "Jesus walking with His disciples near the border village as ten leprous men standing at a distance raise their hands and cry out, 'Jesus, Master, look upon us!' and Jesus answers.",
        "visual_search_terms": "Jesus walking in village, ten lepers standing at a distance raising hands crying out, Luke 17",
        "thematic_tags": "ten lepers, crying out from afar, outcasts, mercy of Jesus, Levitical quarantine, Luke 17:12-14",
        "scripture_anchors": "Luke 17:11-14; Leviticus 13:45-46; Psalm 34:6; Psalm 107:13",
        "soul_halt_tags": "Lonely & Isolated, Ashamed & Outcast, Crying Out for Mercy",
        "short_hook_archetypes": "Story Beat 1 (Why Lepers Had to Stand 100 Paces Away), Spoken Dialogue",
    },
    {
        "broll_id": "FHG-BR-064",
        "story_group": "Story: The Ten Lepers Healed from Afar (Luke 17:11-19)",
        "story_beat": 2,
        "title": "Ten Lepers Walking Down the Road as Their Skin Is Cleansed",
        "src_16x9": "Men_walking_down_dusty_road_303896c3.mp4",
        "prompt": "Ten lepers walking away down a sunlit dusty road toward the priests; as they walk in obedience, the leprous sores vanish from their arms and faces and they gasp in joy.",
        "visual_search_terms": "ten lepers walking down dusty road, leprous sores disappearing from arms as they walk, rejoicing",
        "thematic_tags": "healed as they went, obedience before seeing, cleansing of the ten lepers, faith in motion, Luke 17:14",
        "scripture_anchors": "Luke 17:14; 2 Kings 5:14; Isaiah 65:24; Hebrews 11:8",
        "soul_halt_tags": "Patience & Waiting, Guidance & Trust, Healing & Joy",
        "short_hook_archetypes": "Story Beat 2 ('As They Went, They Were Cleansed' — Why Healing Happened Mid-Step)",
    },
    {
        "broll_id": "FHG-BR-065",
        "story_group": "Story: The Ten Lepers Healed from Afar (Luke 17:11-19)",
        "story_beat": 3,
        "title": "Macro Close-Up of Leprous Forearm Miraculously Healed in Sunlight",
        "src_16x9": "Man_healing_leprous_forearm_ecc492fb.mp4",
        "prompt": "Extreme close-up of a man's outstretched leprous forearm in warm sunlight as the lesions dissolve into a golden dust mist, leaving completely whole, healthy skin.",
        "visual_search_terms": "extreme close-up leprous arm and hand dissolving into golden light particles, skin restored clean and whole",
        "thematic_tags": "miraculous healing, cleansing from leprosy, restoration, made whole, touch of God, Luke 17:14-15",
        "scripture_anchors": "Luke 17:14-15; Mark 1:41-42; Psalm 103:3; Jeremiah 30:17",
        "soul_halt_tags": "Healing & Comfort, Hope & Courage, Freedom from Shame",
        "short_hook_archetypes": "Story Beat 3 (Macro Miracle Reveal), Hook_0_3s",
    },
    {
        "broll_id": "FHG-BR-066",
        "story_group": "Story: The Ten Lepers Healed from Afar (Luke 17:11-19)",
        "story_beat": 4,
        "title": "The One Healed Samaritan Running Back to Fall at Jesus's Feet",
        "src_16x9": "Man_bowing_at_Jesus_feet_81e9a2df.mp4",
        "prompt": "One healed man runs back down the dusty village road shouting 'Praise God! Thank You!' and falls face-down in the dust at Jesus's sandaled feet while the other nine walk away.",
        "visual_search_terms": "one healed man running back shouting praise God thank you, falling face down at Jesus feet in dust",
        "thematic_tags": "gratitude, the one who returned, Samaritan leper, worship at Jesus's feet, your faith has made you well, Luke 17:15-19",
        "scripture_anchors": "Luke 17:15-19; Psalm 103:2; 1 Thessalonians 5:18; Colossians 3:15",
        "soul_halt_tags": "Joy & Gratitude, Wholehearted Devotion, Returning to God",
        "short_hook_archetypes": "Story Beat 4 ('Were Not All Ten Cleansed? Where Are the Other Nine?')",
    },
    {
        "broll_id": "FHG-BR-067",
        "story_group": "Story: The Ten Lepers Healed from Afar (Luke 17:11-19)",
        "story_beat": 5,
        "title": "Jesus Lowering His Hood and Smiling Warmly",
        "src_16x9": "Man_lowering_hood_and_smiling_bb9a05d7.mp4",
        "prompt": "Intimate close-up of first-century Jesus reaching up with both hands to lower His dark wool hood and smiling warmly into the camera ('Rise and go; your faith has made you well').",
        "visual_search_terms": "close-up first-century Jesus lowering wool hood with both hands, warm gentle smile, direct eye contact",
        "thematic_tags": "joy of Jesus, your faith has made you whole, face of grace, welcome, intimacy with Christ, Zephaniah 3:17",
        "scripture_anchors": "Luke 17:19; Numbers 6:25-26; Zephaniah 3:17; John 15:11",
        "soul_halt_tags": "Joy & Gratitude, Peace & Calm, Seen & Loved",
        "short_hook_archetypes": "Story Beat 5 (Final Resolution — The Smile of the Savior), Climax_Reveal",
    },
]


def main() -> None:
    catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8-sig"))
    items_by_id = {it["broll_id"]: it for it in catalog.get("items", [])}

    print("=== Mastering 9 New Biblical Story Clips in C:\\dev\\fhg-videos (FHG-BR-059..067) ===")
    for clip in STORY_CLIPS_ROOT:
        bid = clip["broll_id"]
        src16 = WS_VIDEOS_DIR / clip["src_16x9"]
        # Also copy into fhg-brole so all raw clips live together
        brole_copy = WS_VIDEOS_DIR / "fhg-brole" / clip["src_16x9"]
        if src16.exists() and not brole_copy.exists():
            shutil.copy2(src16, brole_copy)

        masters = master_clip_1080p(bid, clip["title"], src16, None)
        entry = {
            "broll_id": bid,
            "story_group": clip["story_group"],
            "story_beat": clip["story_beat"],
            "title": clip["title"],
            "prompt": clip["prompt"],
            "source_filename": clip["src_16x9"],
            "status": "MASTERED_1080P_ALL_CHANNELS",
            "thematic_tags": clip["thematic_tags"],
            "visual_search_terms": clip["visual_search_terms"],
            "scripture_anchors": clip["scripture_anchors"],
            "soul_halt_tags": clip["soul_halt_tags"],
            "short_hook_archetypes": clip["short_hook_archetypes"],
            "dam_master_16x9_1080p": masters.get("master_16x9_1080p", ""),
            "dam_vertical_9x16_1080p": masters.get("vertical_9x16_1080p", ""),
            "dam_square_1x1_1080p": masters.get("square_1x1_1080p", ""),
        }
        items_by_id[bid] = entry

    ordered_items = [items_by_id[k] for k in sorted(items_by_id.keys())]
    catalog["items"] = ordered_items
    catalog["total_prompts"] = len(ordered_items)
    catalog["total_rendered_1080p_items"] = sum(
        1 for x in ordered_items if x.get("dam_master_16x9_1080p") or x.get("dam_vertical_9x16_1080p")
    )
    CATALOG_JSON.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")

    # Update CSV
    fieldnames = [
        "DAM_ID", "Concept", "Prompt_16x9_Master", "Visual_Search_Terms",
        "Theological_Themes", "Scripture_Anchors", "Emotional_HALT_Tone",
        "Short_Hook_Archetype", "Render_Status", "DAM_Master_16x9_1080p",
        "DAM_Vertical_9x16_1080p", "DAM_Square_1x1_1080p", "QA_Notes",
    ]
    with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({
            "DAM_ID": "GLOBAL_RULES",
            "Concept": "GLOBAL CONTEXT & RULES",
            "Prompt_16x9_Master": catalog.get("global_context_and_rules", ""),
            "Visual_Search_Terms": "1st century levant, judea, galilee, ancient near east, olive skin, homespun wool, rough linen, leather sandals",
            "Theological_Themes": "biblical authenticity, historical grounding, sanctuary plain aesthetic",
            "Scripture_Anchors": "All 66 Books",
            "Emotional_HALT_Tone": "Sacred, Authentic, Grounded",
            "Short_Hook_Archetype": "Global Style Rule",
            "Render_Status": "LOCKED_16x9_1080P_STANDARD",
            "DAM_Master_16x9_1080p": "1920x1080 (YouTube / Web / TV)",
            "DAM_Vertical_9x16_1080p": "1080x1920 (Shorts / Reels / TikTok)",
            "DAM_Square_1x1_1080p": "1080x1080 (Social Feed)",
            "QA_Notes": "Create in 16:9 (>=1080p); FFmpeg produces 9:16 & 1:1 channel masters in ZeroCloudDAM.",
        })
        for it in ordered_items:
            writer.writerow({
                "DAM_ID": it.get("broll_id", ""),
                "Concept": it.get("title", ""),
                "Prompt_16x9_Master": it.get("prompt", ""),
                "Visual_Search_Terms": it.get("visual_search_terms", ""),
                "Theological_Themes": it.get("thematic_tags", ""),
                "Scripture_Anchors": it.get("scripture_anchors", ""),
                "Emotional_HALT_Tone": it.get("soul_halt_tags", ""),
                "Short_Hook_Archetype": it.get("short_hook_archetypes", ""),
                "Render_Status": it.get("status", ""),
                "DAM_Master_16x9_1080p": it.get("dam_master_16x9_1080p", ""),
                "DAM_Vertical_9x16_1080p": it.get("dam_vertical_9x16_1080p", ""),
                "DAM_Square_1x1_1080p": it.get("dam_square_1x1_1080p", ""),
                "QA_Notes": it.get("story_group", "1080p All-Channel Ready") if it.get("dam_master_16x9_1080p") else "Pending 16:9 1080p render.",
            })

    build_master_meaning_graph()
    build_metadata_studio_html(ordered_items, catalog.get("unique_reference_stills", []))
    print(f"Mastered all 9 Story Clips! Total cataloged items: {len(ordered_items)} ({catalog['total_rendered_1080p_items']} rendered 1080p)")


def build_metadata_studio_html(items: list[dict], stills: list[dict]) -> None:
    """Build C:\\dev\\fhg-videos\\fhg_video_metadata_studio.html for reviewing & editing story metadata."""
    broll_rel_prefix = "file:///C:/dev/864zeros-publish/media/video/b_roll_loops/fhg_veo/broll_library/"
    rendered_items = [it for it in items if it.get("dam_master_16x9_1080p") or it.get("dam_vertical_9x16_1080p")]
    data_json = json.dumps(rendered_items, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>For His Grace — Biblical Story &amp; Video Metadata Studio</title>
<style>
  :root {{
    --bg: #EFE8DC;
    --parchment: #DBCEB8;
    --card: #FAF6EE;
    --ink: #1E1914;
    --muted: #5C5146;
    --pine: #2E6245;
    --pine-soft: #EAF2EC;
    --umber: #6E4D2C;
    --line: #D5C7B2;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: "Nunito", "Inter", system-ui, -apple-system, sans-serif;
  }}
  header {{
    background: var(--parchment);
    border-bottom: 1px solid var(--umber);
    padding: 18px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    position: sticky;
    top: 0;
    z-index: 50;
  }}
  header h1 {{
    margin: 0;
    font-size: 22px;
    font-weight: 800;
  }}
  .header-sub {{
    font-size: 13px;
    color: var(--muted);
    margin-top: 2px;
  }}
  .toolbar {{
    display: flex;
    gap: 10px;
    align-items: center;
    flex-wrap: wrap;
  }}
  .btn {{
    background: var(--pine);
    color: #fff;
    border: none;
    padding: 9px 16px;
    border-radius: 999px;
    font-weight: 800;
    font-size: 13px;
    cursor: pointer;
  }}
  .btn.secondary {{
    background: var(--card);
    color: var(--ink);
    border: 1px solid var(--umber);
  }}
  .wrap {{
    max-width: 1440px;
    margin: 0 auto;
    padding: 24px;
  }}
  /* Story Sequence Theater */
  .story-theater {{
    background: var(--card);
    border: 2px solid var(--pine);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 28px;
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 24px;
  }}
  @media (max-width: 960px) {{
    .story-theater {{ grid-template-columns: 1fr; }}
  }}
  .theater-video-box {{
    background: #120f0c;
    border-radius: 12px;
    overflow: hidden;
  }}
  .theater-video-box video {{
    width: 100%;
    max-height: 460px;
    display: block;
  }}
  .story-pills {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }}
  .story-pill {{
    background: var(--bg);
    border: 1px solid var(--line);
    padding: 7px 14px;
    border-radius: 999px;
    font-size: 12.5px;
    font-weight: 800;
    cursor: pointer;
  }}
  .story-pill.active {{
    background: var(--pine);
    color: #fff;
    border-color: var(--pine);
  }}
  /* Filter Bar */
  .filter-bar {{
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }}
  .filter-bar input, .filter-bar select {{
    padding: 10px 14px;
    border-radius: 10px;
    border: 1px solid var(--line);
    background: var(--card);
    font-size: 14px;
    color: var(--ink);
  }}
  .filter-bar input {{ flex: 1; min-width: 260px; }}
  /* Cards Grid */
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(410px, 1fr));
    gap: 20px;
  }}
  .clip-card {{
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }}
  .clip-card video {{
    width: 100%;
    height: 230px;
    object-fit: cover;
    background: #120f0c;
  }}
  .clip-body {{
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }}
  .clip-meta-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }}
  .badge {{
    font-size: 11px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 6px;
    background: var(--pine-soft);
    color: var(--pine);
  }}
  .field-group {{
    display: flex;
    flex-direction: column;
    gap: 3px;
  }}
  .field-group label {{
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--umber);
  }}
  .field-group input, .field-group textarea, .field-group select {{
    width: 100%;
    padding: 7px 10px;
    border-radius: 7px;
    border: 1px solid var(--line);
    background: #fff;
    font-family: inherit;
    font-size: 13px;
    color: var(--ink);
  }}
  .field-group textarea {{
    min-height: 58px;
    resize: vertical;
  }}
  .row-2 {{
    display: grid;
    grid-template-columns: 1fr 90px;
    gap: 8px;
  }}
</style>
</head>
<body>

<header>
  <div>
    <h1>🎬 For His Grace — Biblical Story &amp; Video Metadata Studio</h1>
    <div class="header-sub">Review all {len(rendered_items)} mastered 1080p clips (Google Flow + ZeroCloudDAM), play multi-shot Biblical Jesus Stories in sequence, and edit descriptions &amp; Scripture tags.</div>
  </div>
  <div class="toolbar">
    <span id="saveToast" style="font-size:12.5px;font-weight:800;color:var(--pine);"></span>
    <button class="btn secondary" onclick="exportMetadataJSON()">⬇️ Export Updated JSON Catalog</button>
    <button class="btn" onclick="exportMetadataCSV()">⬇️ Export Updated Master CSV</button>
  </div>
</header>

<div class="wrap">
  <!-- Multi-Shot Biblical Story Sequence Player -->
  <section class="story-theater">
    <div>
      <div class="story-pills">
        <button class="story-pill active" onclick="playStorySequence('Story: The Paralytic Lowered Through the Roof (Mark 2:1-12)', this)">
          ▶ Story 1: The Paralytic Lowered From the Roof (Mark 2:1–12 · 4 Clips)
        </button>
        <button class="story-pill" onclick="playStorySequence('Story: The Ten Lepers Healed from Afar (Luke 17:11-19)', this)">
          ▶ Story 2: The Ten Lepers Healed From Afar (Luke 17:11–19 · 5 Clips)
        </button>
        <button class="story-pill" onclick="playStorySequence('Encounters', this)">
          ▶ Encounters: Blind Man, Hem of Garment, Good Shepherd &amp; Olive Grove
        </button>
      </div>
      <div class="theater-video-box">
        <video id="theaterPlayer" controls preload="metadata"></video>
      </div>
    </div>
    <div id="theaterInfo" style="display:flex;flex-direction:column;justify-content:space-between;">
      <div>
        <div class="badge" id="thBadge" style="display:inline-block;margin-bottom:8px;">STORY SEQUENCE PLAYER</div>
        <h2 id="thTitle" style="margin:0 0 8px;font-size:22px;">Select or Play Any Biblical Story Sequence</h2>
        <p id="thPrompt" style="font-size:14px;line-height:1.55;color:var(--muted);"></p>
        <div id="thPlaylist" style="margin-top:14px;display:flex;flex-direction:column;gap:6px;"></div>
      </div>
      <div style="font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:10px;margin-top:12px;">
        💡 All edits you type in the cards below auto-save in your browser immediately and can be exported to <code>FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv</code> with one click.
      </div>
    </div>
  </section>

  <div class="filter-bar">
    <input type="text" id="searchInput" placeholder="Search by ID (FHG-BR-062), story (paralytic, lepers, blind, shepherd), Scripture (Luke 17, Mark 2), or keyword..." oninput="renderGrid()" />
    <select id="groupFilter" onchange="renderGrid()">
      <option value="ALL">All Videos ({len(rendered_items)} Mastered 1080p Clips)</option>
      <option value="Story: The Paralytic Lowered Through the Roof (Mark 2:1-12)">Story: Paralytic Lowered Through Roof (Mark 2:1-12)</option>
      <option value="Story: The Ten Lepers Healed from Afar (Luke 17:11-19)">Story: Ten Lepers Healed From Afar (Luke 17:11-19)</option>
      <option value="NEW_SCENES">New Biblical Scenes &amp; Miracles (FHG-BR-034..067)</option>
      <option value="BROLL_SYMBOLS">Tactile 1st-Century Symbols (FHG-BR-002..033)</option>
    </select>
  </div>

  <div class="grid" id="cardsGrid"></div>
</div>

<script>
const BASE_LIB = "{broll_rel_prefix}";
let CLIPS = {data_json};

// Load any user edits from localStorage
try {{
  const saved = JSON.parse(localStorage.getItem("fhg_video_metadata_edits_v1") || "{{}}");
  CLIPS.forEach(c => {{
    if (saved[c.broll_id]) Object.assign(c, saved[c.broll_id]);
  }});
}} catch (e) {{}}

function saveEdit(id, field, val) {{
  const item = CLIPS.find(c => c.broll_id === id);
  if (!item) return;
  item[field] = val;
  try {{
    const saved = JSON.parse(localStorage.getItem("fhg_video_metadata_edits_v1") || "{{}}");
    saved[id] = saved[id] || {{}};
    saved[id][field] = val;
    localStorage.setItem("fhg_video_metadata_edits_v1", JSON.stringify(saved));
    const t = document.getElementById("saveToast");
    t.textContent = "✓ Saved " + id + " (" + field + ")";
    clearTimeout(window._st);
    window._st = setTimeout(() => t.textContent = "", 2200);
  }} catch (e) {{}}
}}

let currentPlaylist = [];
let currentPlayIdx = 0;

function playStorySequence(groupName, btnEl) {{
  if (btnEl) {{
    document.querySelectorAll(".story-pill").forEach(b => b.classList.remove("active"));
    btnEl.classList.add("active");
  }}
  if (groupName === "Encounters") {{
    currentPlaylist = CLIPS.filter(c => ["FHG-BR-037","FHG-BR-038","FHG-BR-040","FHG-BR-041","FHG-BR-047"].includes(c.broll_id));
  }} else {{
    currentPlaylist = CLIPS.filter(c => c.story_group === groupName).sort((a,b) => (a.story_beat||99) - (b.story_beat||99));
  }}
  if (!currentPlaylist.length) return;
  currentPlayIdx = 0;
  playTheaterIndex(0);
}}

function playTheaterIndex(idx) {{
  currentPlayIdx = idx;
  const clip = currentPlaylist[idx];
  if (!clip) return;
  const v = document.getElementById("theaterPlayer");
  const file = clip.dam_master_16x9_1080p || clip.dam_vertical_9x16_1080p;
  v.src = BASE_LIB + file;
  v.play().catch(() => {{}});
  document.getElementById("thBadge").textContent = clip.broll_id + (clip.story_beat ? " · BEAT " + clip.story_beat : "");
  document.getElementById("thTitle").textContent = clip.title;
  document.getElementById("thPrompt").textContent = (clip.user_story_notes || clip.prompt) + " — [" + clip.scripture_anchors + "]";

  const listEl = document.getElementById("thPlaylist");
  listEl.innerHTML = currentPlaylist.map((c, i) => `
    <div onclick="playTheaterIndex(${{i}})" style="padding:8px 11px;border-radius:8px;cursor:pointer;font-size:13px;font-weight:${{i===idx?'800':'600'}};background:${{i===idx?'var(--pine-soft)':'var(--bg)'}};border:1px solid ${{i===idx?'var(--pine)':'var(--line)'}};">
      ${{i+1}}. <strong>${{c.broll_id}}</strong> — ${{c.title}} <span style="color:var(--umber);font-size:11.5px;">(${{c.scripture_anchors.split(';')[0]}})</span>
    </div>
  `).join("");
}}

document.getElementById("theaterPlayer").addEventListener("ended", () => {{
  if (currentPlayIdx + 1 < currentPlaylist.length) {{
    playTheaterIndex(currentPlayIdx + 1);
  }}
}});

function renderGrid() {{
  const q = (document.getElementById("searchInput").value || "").toLowerCase().trim();
  const gf = document.getElementById("groupFilter").value;
  const grid = document.getElementById("cardsGrid");

  const filtered = CLIPS.slice().reverse().filter(c => {{
    if (gf === "NEW_SCENES" && parseInt(c.broll_id.split("-")[2], 10) < 34) return false;
    if (gf === "BROLL_SYMBOLS" && parseInt(c.broll_id.split("-")[2], 10) >= 34) return false;
    if (gf.startsWith("Story:") && c.story_group !== gf) return false;
    if (q) {{
      const hay = `${{c.broll_id}} ${{c.title}} ${{c.story_group||''}} ${{c.prompt||''}} ${{c.user_story_notes||''}} ${{c.scripture_anchors||''}} ${{c.thematic_tags||''}} ${{c.soul_halt_tags||''}}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }}
    return true;
  }});

  grid.innerHTML = filtered.map(c => {{
    const file = c.dam_master_16x9_1080p || c.dam_vertical_9x16_1080p;
    return `
      <article class="clip-card">
        <video controls preload="metadata" src="${{BASE_LIB + file}}"></video>
        <div class="clip-body">
          <div class="clip-meta-top">
            <span class="badge">${{c.broll_id}}</span>
            <span style="font-size:11.5px;color:var(--muted);font-weight:700;">16:9 + 9:16 + 1:1 (1080p) · Google Flow</span>
          </div>
          <div class="field-group">
            <label>Clip Title</label>
            <input type="text" value="${{(c.title||'').replace(/"/g,'&quot;')}}" oninput="saveEdit('${{c.broll_id}}','title',this.value)" />
          </div>
          <div class="row-2">
            <div class="field-group">
              <label>Biblical Story / Series Group</label>
              <input type="text" placeholder="e.g. Story: The Paralytic Lowered Through the Roof (Mark 2:1-12)" value="${{(c.story_group||'').replace(/"/g,'&quot;')}}" oninput="saveEdit('${{c.broll_id}}','story_group',this.value)" />
            </div>
            <div class="field-group">
              <label>Story Beat #</label>
              <input type="number" min="1" max="20" value="${{c.story_beat||''}}" oninput="saveEdit('${{c.broll_id}}','story_beat',parseInt(this.value,10)||null)" />
            </div>
          </div>
          <div class="field-group">
            <label>Your Story Description / Meaning &amp; Dialogue Notes</label>
            <textarea oninput="saveEdit('${{c.broll_id}}','prompt',this.value)">${{c.prompt||''}}</textarea>
          </div>
          <div class="field-group">
            <label>Scripture Anchors</label>
            <input type="text" value="${{(c.scripture_anchors||'').replace(/"/g,'&quot;')}}" oninput="saveEdit('${{c.broll_id}}','scripture_anchors',this.value)" />
          </div>
          <div class="field-group">
            <label>Theological Themes &amp; Meaning</label>
            <input type="text" value="${{(c.thematic_tags||'').replace(/"/g,'&quot;')}}" oninput="saveEdit('${{c.broll_id}}','thematic_tags',this.value)" />
          </div>
          <div class="field-group">
            <label>Emotional / HALT Soul Tags</label>
            <input type="text" value="${{(c.soul_halt_tags||'').replace(/"/g,'&quot;')}}" oninput="saveEdit('${{c.broll_id}}','soul_halt_tags',this.value)" />
          </div>
        </div>
      </article>
    `;
  }}).join("");
}}

function exportMetadataJSON() {{
  const blob = new Blob([JSON.stringify(CLIPS, null, 2)], {{ type: "application/json;charset=utf-8" }});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "FHG_BROLL_DAM_CATALOG_UPDATED.json";
  a.click();
}}

function exportMetadataCSV() {{
  const headers = ["DAM_ID","Story_Group","Story_Beat","Concept","Prompt_16x9_Master","Visual_Search_Terms","Theological_Themes","Scripture_Anchors","Emotional_HALT_Tone","Short_Hook_Archetype","DAM_Master_16x9_1080p","DAM_Vertical_9x16_1080p"];
  const esc = v => '"' + String(v ?? "").replace(/"/g, '""') + '"';
  const rows = [headers.join(",")];
  CLIPS.forEach(c => {{
    rows.push([
      esc(c.broll_id), esc(c.story_group||""), esc(c.story_beat||""), esc(c.title),
      esc(c.prompt), esc(c.visual_search_terms), esc(c.thematic_tags),
      esc(c.scripture_anchors), esc(c.soul_halt_tags), esc(c.short_hook_archetypes),
      esc(c.dam_master_16x9_1080p), esc(c.dam_vertical_9x16_1080p)
    ].join(","));
  }});
  const blob = new Blob([rows.join("\\r\\n")], {{ type: "text/csv;charset=utf-8" }});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "FHG_Biblical_Shorts_B_Roll_Master_Catalog_UPDATED.csv";
  a.click();
}}

renderGrid();
playStorySequence("Story: The Paralytic Lowered Through the Roof (Mark 2:1-12)");
</script>
</body>
</html>
"""
    out_html = WS_VIDEOS_DIR / "fhg_video_metadata_studio.html"
    out_html.write_text(html, encoding="utf-8")
    print(f"Built Interactive Video Metadata Studio UI: {out_html}")



if __name__ == "__main__":
    main()
