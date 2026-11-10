#!/usr/bin/env python3
r"""
Ingest, Catalog, Tag, and Master (`1080p` 16:9, 9:16, 1:1) all new B-Roll & Scene Videos
and Reference Images in `C:\dev\fhg-videos\fhg-brole\`.

1. Maps newly generated CSV B-roll clips directly onto their existing `FHG-BR-xxx` IDs:
   - FHG-BR-005 (Potter's Clay) <- gemini_generated_video_76dc9cba.mp4
   - FHG-BR-007 (Teardrop in Dust) <- gemini_generated_video_f8e34814.mp4
   - FHG-BR-008 (Water Washing Feet) <- Water_poured_over_dusty_feet_3850944d.mp4
   - FHG-BR-009 (Twisting Thorns) <- gemini_generated_video_1ab7ea3a.mp4
   - FHG-BR-013 (Wool on Briar) <- gemini_generated_video_e4883373.mp4
   - FHG-BR-019 (Fishing Net Underwater) <- Net_trapping_fish_underwater_edfe6e79.mp4
   - FHG-BR-024 (Washing Hands in Basin) <- Water_pouring_over_hands_38ac84e7.mp4
   - FHG-BR-033 (Hauling Fishing Net Rope 16:9) <- gemini_generated_video_0e73a3ef.mp4
2. Catalogs and masters all new 1st-Century Biblical Scene / Narrative clips (`FHG-BR-037`..`055`)
   into `1080p` (`16:9` 1920x1080, `9:16` 1080x1920, `1:1` 1080x1080) in ZeroCloudDAM (`broll_library/`),
   using native `9:16` source files whenever present (e.g., `*_3823b70c.mp4`, `*_19ab5e0b.mp4`, `*_4f7579d6.mp4`)!
3. Catalogs all unique `.jpg` still plates in `C:\dev\fhg-videos\fhg-brole\` into `plates/brole_stills/`.
4. Rebuilds `FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv`, `FHG_BROLL_DAM_CATALOG.json`, and `FHG_MASTER_MEANING_GRAPH.json`.
"""

import csv
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BROLE_DIR = Path(r"C:\dev\fhg-videos\fhg-brole")
WS_VIDEOS_DIR = Path(r"C:\dev\fhg-videos")
PUBLISH_ROOT = Path(r"C:\dev\864zeros-publish")
VEO_DIR = PUBLISH_ROOT / "media" / "video" / "b_roll_loops" / "fhg_veo"
DAM_BROLL_LIB = VEO_DIR / "broll_library"
DAM_STILLS_DIR = PUBLISH_ROOT / "media" / "video" / "fhg_shorts" / "plates" / "brole_stills"
CSV_PATH = WS_VIDEOS_DIR / "FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv"
CATALOG_JSON = VEO_DIR / "FHG_BROLL_DAM_CATALOG.json"

DAM_BROLL_LIB.mkdir(parents=True, exist_ok=True)
DAM_STILLS_DIR.mkdir(parents=True, exist_ok=True)


def probe_media(path: Path) -> dict:
    out = json.loads(
        subprocess.check_output(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration",
                "-show_entries", "format=duration",
                "-of", "json",
                str(path),
            ],
            text=True,
        )
    )
    st = (out.get("streams") or [{}])[0]
    fmt = out.get("format") or {}
    w = int(st.get("width") or 0)
    h = int(st.get("height") or 0)
    dur = float(st.get("duration") or fmt.get("duration") or 0.0)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "width": w,
        "height": h,
        "aspect": "9:16" if h > w else ("16:9" if w > h else "1:1"),
        "duration_s": round(dur, 2),
        "size_bytes": path.stat().st_size,
        "sha256": sha,
    }


def slugify(text: str) -> str:
    return "-".join("".join(c.lower() if c.isalnum() else " " for c in text).split())


def master_clip_1080p(
    dam_id: str,
    title: str,
    src_16x9: Path | None,
    src_9x16: Path | None = None,
) -> dict:
    """Master a clip into 1080p (16:9 1920x1080, 9:16 1080x1920, 1:1 1080x1080) in ZeroCloudDAM."""
    slug = slugify(title)
    out_16x9 = DAM_BROLL_LIB / f"{dam_id}_{slug}_16x9_1080p.mp4"
    out_9x16 = DAM_BROLL_LIB / f"{dam_id}_{slug}_9x16_1080p.mp4"
    out_1x1 = DAM_BROLL_LIB / f"{dam_id}_{slug}_1x1_1080p.mp4"

    # Copy raw source(s) into DAM_BROLL_LIB for archival
    if src_16x9 and src_16x9.exists():
        raw_16 = DAM_BROLL_LIB / f"{dam_id}_{slug}_16x9_raw.mp4"
        if not raw_16.exists():
            shutil.copy2(src_16x9, raw_16)
    if src_9x16 and src_9x16.exists():
        raw_9 = DAM_BROLL_LIB / f"{dam_id}_{slug}_9x16_raw.mp4"
        if not raw_9.exists():
            shutil.copy2(src_9x16, raw_9)

    primary_src = src_16x9 if (src_16x9 and src_16x9.exists()) else src_9x16
    if not primary_src or not primary_src.exists():
        return {}

    # 1. Build 16:9 1080p (1920x1080) if we have a 16:9 source
    if src_16x9 and src_16x9.exists() and not out_16x9.exists():
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(src_16x9),
                "-vf", "scale=1920:1080:flags=lanczos,setsar=1,format=yuv420p",
                "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                str(out_16x9),
            ],
            check=True,
            capture_output=True,
        )

    # 2. Build 9:16 1080p (1080x1920) — prefer native 9:16 source if available, else center-crop from 16:9
    if not out_9x16.exists():
        if src_9x16 and src_9x16.exists():
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(src_9x16),
                    "-vf", "scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p",
                    "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    str(out_9x16),
                ],
                check=True,
                capture_output=True,
            )
        elif src_16x9 and src_16x9.exists():
            subprocess.run(
                [
                    "ffmpeg", "-y", "-i", str(src_16x9),
                    "-vf", "scale=-1:1920:flags=lanczos,crop=1080:1920:(iw-1080)/2:0,setsar=1,format=yuv420p",
                    "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    str(out_9x16),
                ],
                check=True,
                capture_output=True,
            )

    # 3. Build 1:1 1080p (1080x1080)
    if not out_1x1.exists():
        if src_16x9 and src_16x9.exists():
            vf_sq = "scale=-1:1080:flags=lanczos,crop=1080:1080:(iw-1080)/2:0,setsar=1,format=yuv420p"
            src_sq = src_16x9
        else:
            vf_sq = "scale=1080:-1:flags=lanczos,crop=1080:1080:0:(ih-1080)/2,setsar=1,format=yuv420p"
            src_sq = src_9x16
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", str(src_sq),
                "-vf", vf_sq,
                "-r", "30", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                str(out_1x1),
            ],
            check=True,
            capture_output=True,
        )

    print(f"  [Mastered 1080p] {dam_id} ({title})")
    return {
        "master_16x9_1080p": out_16x9.name if out_16x9.exists() else "",
        "vertical_9x16_1080p": out_9x16.name if out_9x16.exists() else "",
        "square_1x1_1080p": out_1x1.name if out_1x1.exists() else "",
    }


# 1. Existing CSV Queued Prompts now fulfilled in C:\dev\fhg-videos\fhg-brole\
CSV_FULFILLMENTS = {
    "FHG-BR-005": {
        "title": "Potter's Clay",
        "src_16x9": "gemini_generated_video_76dc9cba.mp4",
        "src_9x16": None,
    },
    "FHG-BR-007": {
        "title": "Teardrop in Dust",
        "src_16x9": "gemini_generated_video_f8e34814.mp4",
        "src_9x16": None,
    },
    "FHG-BR-008": {
        "title": "Water Washing Feet",
        "src_16x9": "Water_poured_over_dusty_feet_3850944d.mp4",
        "src_9x16": None,
    },
    "FHG-BR-009": {
        "title": "Twisting Thorns",
        "src_16x9": "gemini_generated_video_1ab7ea3a.mp4",
        "src_9x16": None,
    },
    "FHG-BR-013": {
        "title": "Wool on Briar",
        "src_16x9": "gemini_generated_video_e4883373.mp4",
        "src_9x16": None,
    },
    "FHG-BR-019": {
        "title": "Fishing Net Underwater",
        "src_16x9": "Net_trapping_fish_underwater_edfe6e79.mp4",
        "src_9x16": None,
    },
    "FHG-BR-024": {
        "title": "Washing Hands in Basin",
        "src_16x9": "Water_pouring_over_hands_38ac84e7.mp4",
        "src_9x16": None,
    },
    "FHG-BR-033": {
        "title": "Hauling Fishing Net Rope",
        "src_16x9": "gemini_generated_video_0e73a3ef.mp4",
        "src_9x16": "gemini_generated_video_fbcc0a19.mp4",
    },
}

# 2. Brand-new 1st-Century Biblical Scene & Symbol Clips in C:\dev\fhg-videos\fhg-brole\
NEW_BROLL_CLIPS = [
    {
        "broll_id": "FHG-BR-037",
        "title": "Sheep Eye Reflecting the Good Shepherd",
        "src_16x9": "gemini_generated_video_caeb9887.mp4",
        "src_9x16": "gemini_generated_video_caeb9887_19ab5e0b.mp4",
        "prompt": "Cinematic 1st-century Judean hillside flock of sheep grazing among olive trees, smooth zoom into a single sheep's eye reflecting the Good Shepherd holding His wooden staff.",
        "visual_search_terms": "flock of sheep on rocky Judean hillside, olive trees, macro zoom into sheep eye reflection, Good Shepherd with staff",
        "thematic_tags": "Good Shepherd, Psalm 23, known by name, watchful care, lost sheep found, protection, guidance",
        "scripture_anchors": "John 10:11-14; Psalm 23:1-4; Luke 15:4-6; Ezekiel 34:11-12; Isaiah 40:11",
        "soul_halt_tags": "Lonely & Abandoned, Anxious & Overwhelmed, Guidance & Trust, Sacred Worth",
        "short_hook_archetypes": "1st-Century Shepherd Context, Hook_0_3s, Climax_Reveal",
    },
    {
        "broll_id": "FHG-BR-038",
        "title": "Jesus Healing the Blind Man's Eyes",
        "src_16x9": "gemini_generated_video_b6a18f6f.mp4",
        "src_9x16": "gemini_generated_video_b6a18f6f_4f7579d6.mp4",
        "prompt": "First-century blind beggar kneeling in a dusty Jerusalem stone street with hands raised, as Jesus's hands gently touch his clouded eyes and restore his sight.",
        "visual_search_terms": "blind man Bartimaeus kneeling in dusty stone street, clouded eyes healed, Jesus hands touching eyes, sight restored",
        "thematic_tags": "healing the blind, Bartimaeus, John 9, spiritual sight, mercy, compassion, miracles of Jesus, crying out to God",
        "scripture_anchors": "John 9:1-7; Mark 10:46-52; Luke 18:35-43; Isaiah 35:5; Psalm 146:8",
        "soul_halt_tags": "Hopeless & Desperate, Grief & Healing, Grace & Forgiveness, Faith & Courage",
        "short_hook_archetypes": "1st-Century Judean Context, Miracles & Compassion, Climax_Reveal",
    },
    {
        "broll_id": "FHG-BR-039",
        "title": "Fish Rising from Deep to Joyful Fisherman",
        "src_16x9": "gemini_generated_video_427c8f88.mp4",
        "src_9x16": "gemini_generated_video_427c8f88_3823b70c.mp4",
        "prompt": "Underwater POV following a fish rising into sunlit surface ripples on the Sea of Galilee as a bearded first-century fisherman in a wooden boat smiles in joy.",
        "visual_search_terms": "underwater fish rising to surface sunlight, wooden boat on Sea of Galilee, smiling bearded fisherman, coin in fish mouth",
        "thematic_tags": "miraculous provision, temple tax coin in fish mouth, calling of Peter, joy after night of toil, Sea of Galilee",
        "scripture_anchors": "Matthew 17:24-27; Luke 5:4-9; John 21:6; Matthew 4:19",
        "soul_halt_tags": "Anxious & Overwhelmed, Joy & Gratitude, Provision & Trust",
        "short_hook_archetypes": "Hook_0_3s, Misunderstood Verses (Matthew 17 Coin in the Fish's Mouth)",
    },
    {
        "broll_id": "FHG-BR-040",
        "title": "Woman Touching the Fringe of Jesus's Garment",
        "src_16x9": "Woman_touching_garment_in_crowd_c1af2598.mp4",
        "src_9x16": None,
        "prompt": "Low ground-level shot in a dusty Judean crowd as a trembling woman's hand reaches out and grasps the tassels (tzitzit) at the hem of Jesus's cloak.",
        "visual_search_terms": "woman hand reaching in dusty crowd, touching hem fringe tzitzit of Jesus garment cloak, leather sandals stopping",
        "thematic_tags": "woman with issue of blood, healing in the wings, tzitzit tassels, desperate faith, unseen suffering, Mark 5",
        "scripture_anchors": "Mark 5:25-34; Luke 8:43-48; Matthew 9:20-22; Malachi 4:2; Numbers 15:38-39",
        "soul_halt_tags": "Tired & Exhausted, Ashamed & Guilty, Healing & Comfort, Lonely & Overlooked",
        "short_hook_archetypes": "1st-Century Judean Context (Why She Reached for the Tzitzit Fringe), Personal Application",
    },
    {
        "broll_id": "FHG-BR-041",
        "title": "Jesus Lifting His Head with Compassionate Gaze",
        "src_16x9": "Man_lifting_head_and_looking_614b39c1.mp4",
        "src_9x16": None,
        "prompt": "Close-up portrait of first-century Jesus in a dark homespun wool hood slowly lifting His head from prayerful contemplation to look directly into the lens with quiet compassion.",
        "visual_search_terms": "close-up first-century Jesus lifting head, looking directly at camera, compassionate eyes, hooded wool cloak",
        "thematic_tags": "seen by Jesus, compassion, Man of Sorrows, grace over condemnation, John 8, personal invitation",
        "scripture_anchors": "John 8:10-11; Luke 22:61; Matthew 11:28-30; Isaiah 53:3; Hebrews 4:15",
        "soul_halt_tags": "Ashamed & Guilty, Lonely & Abandoned, Tired & Exhausted, Seen & Loved",
        "short_hook_archetypes": "Personal Application, Emotional Pivot, Climax_Reveal",
    },
    {
        "broll_id": "FHG-BR-042",
        "title": "Removing Sandals & Washing at Stone Threshold",
        "src_16x9": "Removing_sandals_at_stone_entrance_87568130.mp4",
        "src_9x16": None,
        "prompt": "Close-up of weathered hands untying dusty leather sandals at a sunlit stone threshold and dipping fingers into a brass water basin.",
        "visual_search_terms": "untying dusty leather sandals, bare feet on stone threshold, brass water basin, washing hands at entrance",
        "thematic_tags": "holy ground, preparation for worship, humility, hospitality, leaving the world's dust behind, Exodus 3",
        "scripture_anchors": "Exodus 3:5; Joshua 5:15; Luke 7:44; John 13:4-10; Ecclesiastes 5:1",
        "soul_halt_tags": "Rest & Fatigue, Peace & Calm, Sacred Stillness",
        "short_hook_archetypes": "1st-Century Hospitality & Sanctuary Context, Hook_0_3s",
    },
    {
        "broll_id": "FHG-BR-043",
        "title": "Pouring Red Communion Wine into Clay Cup",
        "src_16x9": "Woman_pouring_red_wine_2e66bae9.mp4",
        "src_9x16": None,
        "prompt": "Close-up of a rustic earthenware pitcher pouring deep red wine into an unglazed clay cup on a weathered wooden table lit by warm candlelight.",
        "visual_search_terms": "pouring red wine from clay pitcher into earthenware cup, wooden table, candlelight, communion cup",
        "thematic_tags": "New Covenant in My blood, Last Supper, Passover cup of redemption, communion, wedding at Cana, Psalm 23",
        "scripture_anchors": "Luke 22:20; Matthew 26:27-28; 1 Corinthians 11:25; John 2:7-10; Psalm 23:5",
        "soul_halt_tags": "Grace & Forgiveness, Gratitude & Fellowship, Sacred Worth",
        "short_hook_archetypes": "1st-Century Passover & Communion Context, Climax_Reveal",
    },
    {
        "broll_id": "FHG-BR-044",
        "title": "Pouring Red Wine into Cup (Alternate Angle)",
        "src_16x9": "Woman_pouring_red_wine_2ba45bdc.mp4",
        "src_9x16": None,
        "prompt": "Warm candlelight close-up of hands pouring red wine from a clay jug into a simple pottery cup on an ancient wooden table.",
        "visual_search_terms": "clay jug pouring red wine into pottery cup, warm candlelit stone room, rustic wooden table",
        "thematic_tags": "communion, blood of the covenant, hospitality, abundance, feast of grace, Last Supper",
        "scripture_anchors": "Matthew 26:27-29; Mark 14:23-24; Psalm 116:13; Isaiah 25:6",
        "soul_halt_tags": "Grace & Forgiveness, Fellowship, Peace & Calm",
        "short_hook_archetypes": "1st-Century Hospitality, Passover Symbolism",
    },
    {
        "broll_id": "FHG-BR-045",
        "title": "Placing Bread, Fish, Figs & Olives on Table",
        "src_16x9": "Woman_placing_food_on_table_7d872c24.mp4",
        "src_9x16": None,
        "prompt": "Hands in coarse linen sleeves setting a wooden platter of unleavened flatbread, whole fish, fresh figs, and olives onto a scarred wooden table.",
        "visual_search_terms": "wooden platter with flatbread, whole fish, halved figs, olives placed on rustic table, 1st-century meal",
        "thematic_tags": "fellowship meal, breaking bread, daily provision, hospitality, feeding the five thousand, table in the wilderness",
        "scripture_anchors": "Acts 2:46; Luke 24:30-43; John 21:12-13; Matthew 6:11; Deuteronomy 8:8",
        "soul_halt_tags": "Hungry & Empty, Loneliness & Presence, Gratitude & Provision",
        "short_hook_archetypes": "1st-Century Judean Diet & Table Fellowship, Personal Application",
    },
    {
        "broll_id": "FHG-BR-046",
        "title": "Hospitality at the Doorway ('Peace Be With You')",
        "src_16x9": "Person_walking_toward_doorway_4998c368.mp4",
        "src_9x16": None,
        "prompt": "First-century Judean woman in a simple linen tunic stepping to the open wooden doorway of a stone house and welcoming the guest with 'Peace be with you. Please, come and share our table.'",
        "visual_search_terms": "first-century woman at stone house doorway welcoming guest, rustic table inside, peace be with you greeting",
        "thematic_tags": "biblical hospitality, welcoming the stranger, Martha and Mary, Shunammite woman, peace be to this house, fellowship",
        "scripture_anchors": "Luke 10:5-7; Hebrews 13:2; Romans 12:13; 2 Kings 4:8-10; Acts 16:15",
        "soul_halt_tags": "Lonely & Abandoned, Fellowship & Belonging, Kindness & Love",
        "short_hook_archetypes": "1st-Century Hospitality Customs, Dialogue Scene",
    },
    {
        "broll_id": "FHG-BR-047",
        "title": "Jesus Teaching Disciples in Olive Grove ('Peace I Leave With You')",
        "src_16x9": "Group_sitting_in_olive_grove_6e127202.mp4",
        "src_9x16": None,
        "prompt": "Camera pans across ancient gnarled olive trees in sunlit Judea to Jesus seated on the ground with His disciples, speaking gently: 'Peace I leave with you. Do not be afraid.'",
        "visual_search_terms": "ancient olive grove pan to Jesus sitting with disciples on ground, teaching peace I leave with you",
        "thematic_tags": "peace of Christ, Mount of Olives, discipleship, overcoming fear and anxiety, John 14:27, rabbinic teaching",
        "scripture_anchors": "John 14:27; John 16:33; Matthew 24:3; Luke 22:39; Philippians 4:6-7",
        "soul_halt_tags": "Anxious & Overwhelmed, Peace & Calm, Guidance & Trust",
        "short_hook_archetypes": "Biblical CBT (Jesus on Anxiety), Spoken Scripture Scene",
    },
    {
        "broll_id": "FHG-BR-048",
        "title": "Storm Approaching the Sea of Galilee",
        "src_16x9": "Storm_approaching_Sea_of_Galilee_4f2385a9.mp4",
        "src_9x16": None,
        "prompt": "Wide cinematic shot of dark, heavy storm clouds rolling over the surrounding hills and churning waves of the Sea of Galilee.",
        "visual_search_terms": "dark storm clouds gathering over Sea of Galilee lake, churning waves, wind over water, dramatic sky",
        "thematic_tags": "calming the storm, trials, fear vs faith, walking on water, peace be still, sudden crisis",
        "scripture_anchors": "Mark 4:37-39; Matthew 8:24-26; Matthew 14:24-32; Psalm 107:28-29; Isaiah 43:2",
        "soul_halt_tags": "Anxious & Overwhelmed, Fear & Uncertainty, Hope & Courage",
        "short_hook_archetypes": "Historical Geography (Why Sudden Storms Hit the Sea of Galilee), Tension_Context",
    },
    {
        "broll_id": "FHG-BR-049",
        "title": "Wooden Fishing Boat Floating on Calm Galilee Waters",
        "src_16x9": "Boat_floating_on_calm_waters_dfb6f8aa.mp4",
        "src_9x16": None,
        "prompt": "A first-century wooden fishing boat resting gently on calm, sunlit waters of the Sea of Galilee after the storm.",
        "visual_search_terms": "ancient wooden fishing boat floating on calm sunlit lake water, Sea of Galilee hills, peaceful reflection",
        "thematic_tags": "peace after the storm, stillness, rest with Jesus, Galilee morning, waiting on God",
        "scripture_anchors": "Mark 4:39; Psalm 107:29-30; Psalm 23:2; Luke 5:3; John 6:21",
        "soul_halt_tags": "Peace & Calm, Rest & Fatigue, Stillness",
        "short_hook_archetypes": "Climax_Reveal, Loop_Bridge",
    },
    {
        "broll_id": "FHG-BR-050",
        "title": "Fishermen Hauling Dragnet onto Galilee Shore (Establishing)",
        "src_16x9": "Static_wide_establishing_shot._1st-century_2f2f95dd.mp4",
        "src_9x16": None,
        "prompt": "Static wide establishing shot of two first-century fishermen hauling a heavy dragnet onto the pebble shoreline of the Sea of Galilee beside a moored wooden sailboat at sunrise.",
        "visual_search_terms": "two fishermen pulling net onto rocky shore, wooden sailboat anchored on Sea of Galilee, golden sunrise",
        "thematic_tags": "calling the first disciples, fishers of men, Kingdom dragnet, morning by the sea, resurrection breakfast",
        "scripture_anchors": "Matthew 4:18-22; Matthew 13:47-48; John 21:4-8; Mark 1:16-18",
        "soul_halt_tags": "Purpose & Calling, Perseverance, Hope & Courage",
        "short_hook_archetypes": "1st-Century Galilean Fishing Context, Hook_0_3s",
    },
    {
        "broll_id": "FHG-BR-051",
        "title": "Fishermen Pulling Dragnet in Surf",
        "src_16x9": "Fishermen_pulling_drag_net_92dd6274.mp4",
        "src_9x16": None,
        "prompt": "First-century Galilean fishermen straining together to haul a wet hemp dragnet through the shallow shoreline surf.",
        "visual_search_terms": "Galilean fishermen pulling heavy dragnet in shallow waves, teamwork, wet hemp net, coastline",
        "thematic_tags": "shared labor, fellowship in ministry, perseverance, Kingdom harvest, Galatians 6:9",
        "scripture_anchors": "Luke 5:6-7; John 21:8-11; Galatians 6:9; Ecclesiastes 4:9-10",
        "soul_halt_tags": "Tired & Exhausted, Fellowship, Perseverance",
        "short_hook_archetypes": "1st-Century Galilean Context, Tension_Context",
    },
    {
        "broll_id": "FHG-BR-052",
        "title": "Donkey Walking Down Dusty Judean Path",
        "src_16x9": "Donkey_walking_down_dusty_path_4ca07531.mp4",
        "src_9x16": None,
        "prompt": "A humble brown donkey walking steadily along a sunlit, dusty stone-walled country road in first-century Judea.",
        "visual_search_terms": "brown donkey walking down dusty Judean path, dry stone walls, olive trees, humble beast of burden",
        "thematic_tags": "humble king, Palm Sunday, Good Samaritan, journey to Bethlehem, gentleness and meekness, Zechariah 9:9",
        "scripture_anchors": "Zechariah 9:9; Matthew 21:2-5; Luke 10:34; Luke 2:4-5; Numbers 22:28",
        "soul_halt_tags": "Humility, Patience & Waiting, Burden-Bearing",
        "short_hook_archetypes": "Pagan vs Biblical Nuance (Why a King Rode a Donkey Instead of a Warhorse)",
    },
    {
        "broll_id": "FHG-BR-053",
        "title": "Birds Taking Flight from Ancient Olive Trees",
        "src_16x9": "Birds_taking_flight_from_trees_a44402a8.mp4",
        "src_9x16": None,
        "prompt": "A flock of small birds lifting off from the branches of sunlit olive trees into the clear Judean sky.",
        "visual_search_terms": "birds taking flight from olive tree branches, warm morning sunlight, clear sky, wings",
        "thematic_tags": "freedom from worry, birds of the air, mustard tree branches, God's provision, deliverance",
        "scripture_anchors": "Matthew 6:26; Matthew 13:32; Psalm 124:7; Psalm 104:12",
        "soul_halt_tags": "Anxious & Overwhelmed, Peace & Calm, Freedom",
        "short_hook_archetypes": "Biblical CBT (Look at the Birds of the Air), Climax_Reveal",
    },
    {
        "broll_id": "FHG-BR-054",
        "title": "Goat Grazing on Terraced Judean Hill",
        "src_16x9": "Goat_eating_grass_on_hill_ca5bb9f7.mp4",
        "src_9x16": None,
        "prompt": "A dark Levantine goat grazing on dry brush along a sunlit, rocky Judean hillside.",
        "visual_search_terms": "Middle Eastern goat eating grass on rocky hillside, Judean pasture, pastoral landscape",
        "thematic_tags": "sheep and goats, Day of Atonement scapegoat, pastoral life, wilderness provision, Proverbs 27:27",
        "scripture_anchors": "Matthew 25:32-33; Leviticus 16:21-22; Proverbs 27:26-27; Psalm 104:18",
        "soul_halt_tags": "Guidance & Trust, Spiritual Discernment, Daily Provision",
        "short_hook_archetypes": "1st-Century Shepherd Context (Why Sheep and Goats Were Separated at Dusk)",
    },
    {
        "broll_id": "FHG-BR-055",
        "title": "Camera Moving Down Ancient Jerusalem Stone Street",
        "src_16x9": "Camera_moving_down_Jerusalem_street_d54131af (1).mp4",
        "src_9x16": None,
        "prompt": "Smooth forward tracking shot moving down a narrow, sunlit limestone-walled street in first-century Jerusalem.",
        "visual_search_terms": "POV camera walking down narrow ancient Jerusalem limestone street, stone arches, warm sunlight",
        "thematic_tags": "Jerusalem, Via Dolorosa, pilgrimage, Psalms of Ascent, walking in the light, ancient paths",
        "scripture_anchors": "Jeremiah 6:16; Psalm 122:1-2; Luke 19:41; John 5:2; Acts 3:1",
        "soul_halt_tags": "Guidance & Trust, Direction, Peace & Calm",
        "short_hook_archetypes": "Historical Geography (1st-Century Jerusalem Streets), Tension_Context",
    },
    {
        "broll_id": "FHG-BR-056",
        "title": "Biblical Traveler Walking Down Dirt Trail",
        "src_16x9": "Biblical_figure_walking_down_path_7d34dc2f.mp4",
        "src_9x16": None,
        "prompt": "Rear tracking shot of a solitary first-century figure in homespun wool robes walking steadily along a winding dirt trail through the Judean hills.",
        "visual_search_terms": "solitary biblical figure walking down dirt trail from behind, wool cloak, Judean hills",
        "thematic_tags": "pilgrimage, Road to Emmaus, walking by faith, solitude with God, endurance, narrow path",
        "scripture_anchors": "Luke 24:13-15; 2 Corinthians 5:7; Matthew 7:14; Psalm 23:3-4; Micah 6:8",
        "soul_halt_tags": "Lonely & Abandoned, Guidance & Trust, Perseverance",
        "short_hook_archetypes": "Hook_0_3s, Personal Application",
    },
    {
        "broll_id": "FHG-BR-057",
        "title": "Man Walking on Sunlit Judean Dirt Path",
        "src_16x9": "Man_walking_on_dirt_path_806b1082.mp4",
        "src_9x16": None,
        "prompt": "Cinematic tracking shot of a first-century man in a woven tunic walking along a dusty countryside path bordered by dry stone walls and olive trees.",
        "visual_search_terms": "man in first-century tunic walking on dirt path, olive trees, stone wall, countryside walk",
        "thematic_tags": "daily walk with God, discipleship, parable of the Good Samaritan road, obedience, step by step",
        "scripture_anchors": "Psalm 119:105; Proverbs 3:5-6; Luke 10:30; Galatians 5:16",
        "soul_halt_tags": "Guidance & Trust, Peace & Calm, Patience & Waiting",
        "short_hook_archetypes": "Tension_Context, Personal Application",
    },
    {
        "broll_id": "FHG-BR-058",
        "title": "Walking Along Winding Wilderness Trail (POV)",
        "src_16x9": "Walking_along_dirt_trail_73e58820.mp4",
        "src_9x16": None,
        "prompt": "Forward-moving POV shot advancing along a quiet, sun-dappled dirt trail through rocky Judean terrain.",
        "visual_search_terms": "POV walking forward along dirt trail, rocky Judean hills, warm afternoon light",
        "thematic_tags": "the narrow road, wilderness journey, following the Shepherd, forward faith, new mercies",
        "scripture_anchors": "Isaiah 30:21; Psalm 16:11; Proverbs 4:18; Matthew 7:14",
        "soul_halt_tags": "Guidance & Trust, Hope & Courage, Peace & Calm",
        "short_hook_archetypes": "Loop_Bridge, Tension_Context",
    },
]


def main() -> None:
    catalog = json.loads(CATALOG_JSON.read_text(encoding="utf-8-sig"))
    items_by_id = {it["broll_id"]: it for it in catalog.get("items", [])}

    # 1. Master and update the 8 newly fulfilled CSV B-roll clips
    print("=== STEP 1: Mastering 8 Newly Fulfilled CSV B-Roll Prompts (1080p 16:9, 9:16, 1:1) ===")
    for bid, info in CSV_FULFILLMENTS.items():
        src16 = BROLE_DIR / info["src_16x9"] if info["src_16x9"] else None
        src9 = BROLE_DIR / info["src_9x16"] if info["src_9x16"] else None
        masters = master_clip_1080p(bid, info["title"], src16, src9)
        if bid in items_by_id and masters:
            it = items_by_id[bid]
            it["status"] = "MASTERED_1080P_ALL_CHANNELS"
            it["dam_master_16x9_1080p"] = masters["master_16x9_1080p"]
            it["dam_vertical_9x16_1080p"] = masters["vertical_9x16_1080p"]
            it["dam_square_1x1_1080p"] = masters["square_1x1_1080p"]

    # 2. Master and append the 22 brand-new Biblical Scene & Symbol clips (FHG-BR-037 .. FHG-BR-058)
    print("\n=== STEP 2: Mastering 22 Brand-New 1st-Century Biblical Clips (FHG-BR-037..058) ===")
    for clip in NEW_BROLL_CLIPS:
        bid = clip["broll_id"]
        src16 = BROLE_DIR / clip["src_16x9"] if clip["src_16x9"] else None
        src9 = BROLE_DIR / clip["src_9x16"] if clip["src_9x16"] else None
        masters = master_clip_1080p(bid, clip["title"], src16, src9)
        entry = {
            "broll_id": bid,
            "title": clip["title"],
            "prompt": clip["prompt"],
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

    # 3. Deduplicate and vault all unique .jpg still plates in fhg-brole
    print("\n=== STEP 3: Cataloging Unique Still Plates (.jpg) in fhg-brole ===")
    seen_img_sha = set()
    unique_stills = []
    for jpg in sorted(BROLE_DIR.glob("*.jpg")):
        sha = hashlib.sha256(jpg.read_bytes()).hexdigest()
        if sha in seen_img_sha:
            continue
        seen_img_sha.add(sha)
        idx = len(unique_stills) + 1
        sid = f"FHG-STILL-{idx:03d}"
        dest = DAM_STILLS_DIR / f"{sid}_{jpg.name}"
        if not dest.exists():
            shutil.copy2(jpg, dest)
        unique_stills.append({
            "still_id": sid,
            "source_filename": jpg.name,
            "dam_path": str(dest),
            "sha256": sha,
        })
    print(f"  Vaulted {len(unique_stills)} unique photorealistic reference stills in {DAM_STILLS_DIR}")

    # Save updated FHG_BROLL_DAM_CATALOG.json
    ordered_items = [items_by_id[k] for k in sorted(items_by_id.keys())]
    catalog["items"] = ordered_items
    catalog["total_prompts"] = len(ordered_items)
    catalog["total_rendered_1080p_items"] = sum(
        1 for x in ordered_items if x.get("dam_master_16x9_1080p") or x.get("dam_vertical_9x16_1080p")
    )
    catalog["unique_reference_stills"] = unique_stills
    CATALOG_JSON.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")

    # Update FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv
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
                "QA_Notes": "1080p All-Channel Ready" if it.get("dam_master_16x9_1080p") else "Pending 16:9 1080p render.",
            })

    print(
        f"\n=== DONE ===\n"
        f"Total Cataloged Clips: {len(ordered_items)}\n"
        f"Total Mastered 1080p Clips: {catalog['total_rendered_1080p_items']}\n"
        f"Updated CSV: {CSV_PATH}\n"
        f"Updated JSON: {CATALOG_JSON}"
    )


if __name__ == "__main__":
    main()
