#!/usr/bin/env python3
"""
ZeroCloudDAM Ingest & Master Catalog Builder for For His Grace (FHG) Biblical Shorts B-Roll.
1. Vaults all unique clips from C:\\dev\\fhg-videos\\fhg-brole\\ into
   C:\\dev\\864zeros-publish\\media\\video\\b_roll_loops\\fhg_veo\\broll_library\\
2. Reads C:\\Users\\Jeff\\Downloads\\FHG Biblical Shorts B-Roll Prompts - Sheet1.csv
3. Appends the 3 earlier rendered prompts (Pouring Anointing Oil, Sandals in Cracked Wilderness, Hauling Fishing Net Rope)
4. Enriches all 33 B-roll rows with programmatic DAM & Search columns:
   - broll_id (FHG-BR-001 .. FHG-BR-033)
   - title
   - prompt
   - status (VAULTED_DAM vs QUEUED)
   - dam_files (canonical vaulted .mp4 filenames + aspect ratios)
   - usable_window_sec (QA-verified timecode window for 3.5s cuts)
   - thematic_tags (high-level theological & emotional themes, inkl. Soul/HALT states)
   - visual_search_terms (literal physical nouns, actions, textures, lighting for semantic/keyword search)
   - scripture_anchors (canonical Old & New Testament verse pairings)
   - short_hook_archetypes (which of the 10 2026 Short Hook archetypes this clip anchors)
"""

import csv
import hashlib
import json
import shutil
from pathlib import Path

SRC_BROLE_DIR = Path(r"C:\dev\fhg-videos\fhg-brole")
DOWNLOAD_CSV = Path(r"C:\Users\Jeff\Downloads\FHG Biblical Shorts B-Roll Prompts - Sheet1.csv")
DAM_DIR = Path(r"C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo")
DAM_LIB_DIR = DAM_DIR / "broll_library"
DAM_LIB_DIR.mkdir(parents=True, exist_ok=True)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


# Metadata & search/tag enrichment dictionary keyed by Title
ENRICHMENT_MAP = {
    "Crushed Grapes": {
        "thematic_tags": "sacrifice, covenant blood, communion, new wine, wrath and mercy, pruning, abundance, Passover",
        "visual_search_terms": "crushed red grapes, dark crimson juice dripping, rustic clay bowl, winepress, slow motion liquid drop, harvest fruit",
        "scripture_anchors": "Isaiah 63:2-3; Matthew 26:27-28; John 15:1-5; Joel 3:13; Luke 5:37-38",
        "soul_halt_tags": "Grief & Healing, Grace & Forgiveness, Sacred Worth",
        "short_hook_archetypes": "1st-Century Judean Context, Passover & Communion Symbolism",
        "rendered": []
    },
    "Falling Silver Coins": {
        "thematic_tags": "betrayal, greed, thirty pieces of silver, temple tax, wealth vs kingdom, stewardship, Judas, redemption price",
        "visual_search_terms": "ancient silver coins falling, Tyrian shekel, Roman denarius, dark stone temple floor, cold moonlight, metallic bounce, money",
        "scripture_anchors": "Matthew 26:14-15; Matthew 27:3-6; Zechariah 11:12-13; Mark 12:15-17; 1 Timothy 6:10",
        "soul_halt_tags": "Letting Go, Guidance & Trust, Temptation & Integrity",
        "short_hook_archetypes": "1st-Century Judean Context, Translation & Currency Realities",
        "rendered": [
            {
                "src_name": "gemini_generated_video_29b4824a.mp4",
                "dam_name": "FHG-BR-002_falling-silver-coins_16x9.mp4",
                "aspect": "16:9 (1280x720)",
                "usable_window": "0:00.8 - 0:09.5 (Full 10s clean; 0:00.8-0:04.3 captures single coin edge-drop + cascade)"
            }
        ]
    },
    "Breaking Bread": {
        "thematic_tags": "communion, fellowship, provision, Last Supper, Road to Emmaus, hospitality, daily bread, Christ's body",
        "visual_search_terms": "calloused olive-skinned hands tearing bread, unleavened flatbread loaf, falling crumbs, bearded Jesus blurred background, warm table light",
        "scripture_anchors": "Luke 22:19; Luke 24:30-31; Matthew 6:11; John 6:35; Acts 2:42-46; 1 Corinthians 11:23-24",
        "soul_halt_tags": "Loneliness & Presence, Gratitude & Provision, Fellowship",
        "short_hook_archetypes": "1st-Century Hospitality, Misunderstood Verses (Daily Bread)",
        "rendered": [
            {
                "src_name": "gemini_generated_video_5252e4a0.mp4",
                "duplicate_src": "gemini_generated_video_ae08798a.mp4",
                "dam_name": "FHG-BR-003_breaking-bread_9x16.mp4",
                "aspect": "9:16 (720x1280)",
                "usable_window": "0:00.0 - 0:10.0 (10/10 clean; 0:02.0-0:05.5 crumbs falling, 0:06.0-0:09.5 loaf parting)"
            }
        ]
    },
    "Wind Blowing Chaff": {
        "thematic_tags": "judgment and discernment, winnowing floor, righteousness vs wicked, harvest, refinement, testing, Psalm 1",
        "visual_search_terms": "harvested golden wheat kernels, wind blowing chaff and husks, stone threshing floor, warm sunlight, grain separation",
        "scripture_anchors": "Psalm 1:4; Matthew 3:12; Luke 3:17; Ruth 3:2; Job 21:18; Hosea 13:3",
        "soul_halt_tags": "Guidance & Trust, Letting Go, Spiritual Discernment",
        "short_hook_archetypes": "1st-Century Agricultural Context, Translation Discrepancies",
        "rendered": [
            {
                "src_name": "gemini_generated_video_8a9b5edc.mp4",
                "dam_name": "FHG-BR-004_wind-blowing-chaff_16x9.mp4",
                "aspect": "16:9 (1280x720)",
                "usable_window": "0:00.0 - 0:08.5 (Main threshing shot) + 0:08.8 - 0:10.0 (Tight grain close-up)"
            }
        ]
    },
    "Potter's Clay": {
        "thematic_tags": "sovereignty, sanctification, shaping character, humility, broken vessels, creator, Isaiah 64, Jeremiah 18",
        "visual_search_terms": "wet muddy hands shaping clay, spinning wooden potter's wheel, earthenware vessel, olive skin artisan, tactile mud",
        "scripture_anchors": "Jeremiah 18:1-6; Isaiah 64:8; Romans 9:20-21; 2 Corinthians 4:7; Job 10:9",
        "soul_halt_tags": "Patience & Waiting, Sacred Worth, Surrender",
        "short_hook_archetypes": "Stoicism vs Christianity, Old Testament Prophetic Object Lessons",
        "rendered": []
    },
    "Glowing Embers": {
        "thematic_tags": "rekindling faith, spiritual dryness, Peter's charcoal fire, restoration, Holy Spirit fire, quiet vigil, Elijah",
        "visual_search_terms": "glowing red wood charcoal embers, white ash bark, popping orange sparks, night campfire in pitch darkness, rising flame",
        "scripture_anchors": "2 Timothy 1:6; John 18:18; John 21:9; Isaiah 6:6; Psalm 39:3; Proverbs 26:21",
        "soul_halt_tags": "Rest & Fatigue, Hope & Courage, Spiritual Dryness",
        "short_hook_archetypes": "The Silence of God, 1st-Century Judean Context (John 21 Charcoal Fire)",
        "rendered": [
            {
                "src_name": "gemini_generated_video_5d2dc0f9.mp4",
                "dam_name": "FHG-BR-006_glowing-embers_9x16.mp4",
                "aspect": "9:16 (720x1280)",
                "usable_window": "0:00.0 - 0:10.0 (10/10 clean; spark bursts at 0:02.0 and 0:06.0)"
            }
        ]
    },
    "Teardrop in Dust": {
        "thematic_tags": "grief, lament, compassion, Jesus wept, brokenhearted, prayer in sorrow, Psalms of lament, bottle of tears",
        "visual_search_terms": "single clear teardrop falling, dry cracked desert earth, microscopic dust splash, macro water droplet impact, sorrow",
        "scripture_anchors": "Psalm 56:8; John 11:35; Psalm 34:18; Psalm 126:5; Revelation 21:4; Ecclesiastes 3:4",
        "soul_halt_tags": "Healing & Comfort, Loneliness & Presence, Grief",
        "short_hook_archetypes": "Biblical Cognitive Behavioral Therapy, The Silence of God",
        "rendered": []
    },
    "Water Washing Feet": {
        "thematic_tags": "servant leadership, humility, cleansing, Upper Room, hospitality, forgiveness, Maundy Thursday",
        "visual_search_terms": "clear water pouring from clay pitcher, dusty calloused feet in leather sandals, washing feet, splashing water",
        "scripture_anchors": "John 13:4-15; Luke 7:38-44; Genesis 18:4; 1 Timothy 5:10; Ephesians 5:26",
        "soul_halt_tags": "Kindness & Love, Grace & Forgiveness, Humility",
        "short_hook_archetypes": "1st-Century Judean Context, Pagan vs Biblical Leadership",
        "rendered": []
    },
    "Twisting Thorns": {
        "thematic_tags": "curse of the fall, suffering, trials, thorn in the flesh, anxiety choking the word, Passion of Christ",
        "visual_search_terms": "long sharp thorns branch, calloused hands twisting briar, moody chiaroscuro lighting, prickly desert bramble",
        "scripture_anchors": "Genesis 3:18; Matthew 13:7, 22; 2 Corinthians 12:7-9; Mark 15:17",
        "soul_halt_tags": "Peace & Calm, Hope & Courage, Suffering & Endurance",
        "short_hook_archetypes": "Stoicism vs Christianity, Parable of the Sower",
        "rendered": []
    },
    "Pouring Salt": {
        "thematic_tags": "salt of the earth, covenant of salt, preservation, seasoned speech, purity, faithfulness, Dead Sea mineral",
        "visual_search_terms": "coarse unrefined sea salt crystals pouring, weathered brown leather pouch, white mineral grains falling",
        "scripture_anchors": "Matthew 5:13; Mark 9:50; Colossians 4:6; Leviticus 2:13; Numbers 18:19",
        "soul_halt_tags": "Sacred Worth, Guidance & Trust, Daily Witness",
        "short_hook_archetypes": "Translation & Cultural Discrepancies (Why Salt Mattered in the Ancient World)",
        "rendered": []
    },
    "Rolled Tomb Stone": {
        "thematic_tags": "resurrection, Easter, empty tomb, victory over death, light in darkness, hope, new creation",
        "visual_search_terms": "massive rough-hewn circular stone rolling away, blinding morning sunbeam piercing pitch-black cave tomb, dust motes",
        "scripture_anchors": "Matthew 28:2; Mark 16:4; Luke 24:2; John 20:1; John 1:5; Romans 8:11",
        "soul_halt_tags": "Hope & Courage, Joy & Gratitude, Resurrection Life",
        "short_hook_archetypes": "Historical Geography (1st-Century Rolling-Stone Tombs)",
        "rendered": []
    },
    "Mustard Seed": {
        "thematic_tags": "small beginnings, mountain-moving faith, Kingdom of God growth, unseen faithfulness, patience",
        "visual_search_terms": "tiny mustard seed pinched between dirt-stained fingers, olive skin working hand, extreme macro shallow depth of field",
        "scripture_anchors": "Matthew 13:31-32; Matthew 17:20; Luke 17:6; Mark 4:30-32; Zechariah 4:10",
        "soul_halt_tags": "Hope & Courage, Patience & Waiting, Small Steps",
        "short_hook_archetypes": "Misunderstood Verses (What 'Faith the Size of a Mustard Seed' Actually Means)",
        "rendered": []
    },
    "Wool on Briar": {
        "thematic_tags": "lost sheep, Good Shepherd, rescue, wandering, gentleness, Isaiah 53, Psalm 23",
        "visual_search_terms": "tuft of white sheep wool snagged on dark sharp briar thorn branch, blowing gently in wind, wilderness pasture",
        "scripture_anchors": "Luke 15:4-6; Isaiah 53:6; Psalm 119:176; Matthew 18:12-14; John 10:11",
        "soul_halt_tags": "Grace & Forgiveness, Loneliness & Presence, Being Found",
        "short_hook_archetypes": "1st-Century Shepherd Context, The Heart of God",
        "rendered": []
    },
    "Incense Smoke": {
        "thematic_tags": "prayer rising, intercession, temple worship, Day of Atonement, sacred stillness, evening sacrifice, holiness",
        "visual_search_terms": "thick fluid incense smoke rising, ancient bronze censer, pitch black sanctuary background, swirling aromatic vapor",
        "scripture_anchors": "Psalm 141:2; Revelation 5:8; Revelation 8:3-4; Luke 1:9-10; Exodus 30:7-8",
        "soul_halt_tags": "Peace & Calm, Rest & Fatigue, Stillness & Prayer",
        "short_hook_archetypes": "The Second Temple, Prayer & Neurobiology of Stillness",
        "rendered": []
    },
    "Iron Nail on Timber": {
        "thematic_tags": "crucifixion, atonement, canceled debt, Golgotha, cost of grace, suffering servant, cross",
        "visual_search_terms": "heavy rusted square-forged Roman iron nail, rough-hewn splintered wooden cross beam timber, dark moody texture",
        "scripture_anchors": "Colossians 2:14; John 20:25; Isaiah 53:5; Galatians 2:20; 1 Peter 2:24",
        "soul_halt_tags": "Grace & Forgiveness, Sacred Worth, Freedom from Shame",
        "short_hook_archetypes": "Historical Geography (Golgotha & Roman Crucifixion)",
        "rendered": []
    },
    "Olive Press Crushing": {
        "thematic_tags": "Gethsemane, crushing pressure producing oil, suffering into anointing, endurance, night of prayer",
        "visual_search_terms": "heavy circular limestone millstone crushing olives, golden-green olive oil seeping out, ancient stone press",
        "scripture_anchors": "Matthew 26:36-39; Luke 22:44; 2 Corinthians 4:8-9; Psalm 23:5; James 1:2-4",
        "soul_halt_tags": "Peace & Calm, Rest & Fatigue, Crushing Anxiety",
        "short_hook_archetypes": "Translation & Etymology (Why 'Gethsemane' Literally Means 'Oil Press')",
        "rendered": []
    },
    "Tearing the Veil": {
        "thematic_tags": "direct access to God, Holy of Holies, end of separation, finished work of Christ, boldness in prayer",
        "visual_search_terms": "thick ornate woven temple curtain fabric violently ripping down the middle, snapping threads, dramatic tension",
        "scripture_anchors": "Matthew 27:51; Mark 15:38; Hebrews 10:19-20; Hebrews 4:16; Exodus 26:31-33",
        "soul_halt_tags": "Grace & Forgiveness, Sacred Worth, Intimacy with God",
        "short_hook_archetypes": "The Second Temple (The 60-Foot Curtain of the Holy of Holies)",
        "rendered": []
    },
    "Locust on Leaf": {
        "thematic_tags": "plague, wasted years restored, wilderness diet of John the Baptist, judgment and repentance, Joel 2",
        "visual_search_terms": "desert locust chewing green leaf edge, insect mandibles macro, harsh wilderness sunlight, agricultural famine",
        "scripture_anchors": "Joel 2:25; Exodus 10:12-15; Matthew 3:4; 2 Chronicles 7:13-14; Proverbs 30:27",
        "soul_halt_tags": "Hope & Courage, Healing & Comfort, Restoring Lost Time",
        "short_hook_archetypes": "Misunderstood Verses ('I Will Restore the Years the Locust Has Eaten')",
        "rendered": []
    },
    "Fishing Net Underwater": {
        "thematic_tags": "calling of the disciples, Kingdom dragnet, miraculous catch, evangelism, abundance in obedience",
        "visual_search_terms": "underwater looking up at surface light shafts, coarse hemp fishing net plunging, silver fish trapped in mesh",
        "scripture_anchors": "Matthew 13:47-48; Luke 5:4-7; John 21:6-11; Matthew 4:19; Ezekiel 47:9-10",
        "soul_halt_tags": "Guidance & Trust, Hope & Courage, Purpose",
        "short_hook_archetypes": "1st-Century Galilean Context, Parables of the Kingdom",
        "rendered": []
    },
    "Scroll Unrolling": {
        "thematic_tags": "Word of God, prophecy fulfilled, Torah, Isaiah scroll in Nazareth, wisdom, eternal truth, study",
        "visual_search_terms": "aged dusty Hebrew parchment scroll unrolling, scarred wooden table, ancient manuscript ink texture",
        "scripture_anchors": "Luke 4:17-21; Isaiah 40:8; Psalm 119:105; 2 Timothy 3:16; Jeremiah 36:2; Revelation 5:1",
        "soul_halt_tags": "Guidance & Trust, Wisdom, Scripture Study",
        "short_hook_archetypes": "Translation Discrepancies, How Scripture Was Read in the 1st Century",
        "rendered": []
    },
    "Sand Through Fingers": {
        "thematic_tags": "brevity of life, numbering our days, letting go of control, Abraham's descendants, time slipping away, Ecclesiastes",
        "visual_search_terms": "coarse golden desert sand slipping through calloused olive-skinned fingers, grains falling in sunlight, time",
        "scripture_anchors": "Psalm 90:12; James 4:14; Ecclesiastes 3:1-2; Genesis 22:17; Psalm 103:14-16; Psalm 139:17-18",
        "soul_halt_tags": "Letting Go, Peace & Calm, Surrendering Control",
        "short_hook_archetypes": "Stoicism vs Christianity (Time, Mortality & Eternal Perspective)",
        "rendered": []
    },
    "Sparrow Landing": {
        "thematic_tags": "providence, God's care for the small, freedom from anxiety, worth to the Father, Sermon on the Mount",
        "visual_search_terms": "small brown sparrow bird landing on dusty ground, tiny puff of dirt, soft feathers in warm sunlight",
        "scripture_anchors": "Matthew 10:29-31; Luke 12:6-7; Psalm 84:3; Matthew 6:26",
        "soul_halt_tags": "Peace & Calm, Sacred Worth, Loneliness & Presence",
        "short_hook_archetypes": "Biblical Cognitive Behavioral Therapy (Jesus on Anxiety)",
        "rendered": []
    },
    "Crown of Thorns": {
        "thematic_tags": "suffering king, Good Friday, mockery turned to glory, substitutionary love, Isaiah 53, humility of Christ",
        "visual_search_terms": "woven crown of long brutal thorns resting on cold dark stone, single drop of crimson blood, Passion relic",
        "scripture_anchors": "Matthew 27:29; John 19:2-5; Isaiah 53:3-5; Philippians 2:8; Hebrews 2:9",
        "soul_halt_tags": "Grace & Forgiveness, Sacred Worth, Suffering & Love",
        "short_hook_archetypes": "Pagan vs Biblical Nuance (Roman Imperial Crowns vs The Crown of Thorns)",
        "rendered": []
    },
    "Washing Hands in Basin": {
        "thematic_tags": "innocence, confession, cleansing from guilt, Pilate's basin, pure heart, sanctuary laver, forgiveness",
        "visual_search_terms": "water pouring over olive-skinned hands into tarnished brass basin, rinsing away dust, ripples in metal bowl",
        "scripture_anchors": "Psalm 24:3-4; Psalm 26:6; Matthew 27:24; James 4:8; Isaiah 1:16; 1 John 1:9",
        "soul_halt_tags": "Grace & Forgiveness, Letting Go, Cleansing Guilt",
        "short_hook_archetypes": "1st-Century Ritual Purity vs Heart Purity",
        "rendered": []
    },
    "Alabaster Jar Breaking": {
        "thematic_tags": "extravagant worship, poured-out devotion, Bethany anointing, brokenness yielding fragrance, holding nothing back",
        "visual_search_terms": "white alabaster stone jar shattering on stone floor, thick fragrant nard oil spilling out, slow motion shards",
        "scripture_anchors": "Mark 14:3-9; Luke 7:37-38; John 12:3; 2 Corinthians 2:15; Psalm 51:17",
        "soul_halt_tags": "Joy & Gratitude, Sacred Worth, Wholehearted Devotion",
        "short_hook_archetypes": "1st-Century Judean Context (Why Breaking the Alabaster Flask Meant Total Surrender)",
        "rendered": []
    },
    "Dove Taking Flight": {
        "thematic_tags": "Holy Spirit descending, peace after the flood, baptism of Jesus, new beginning, freedom, gentle presence",
        "visual_search_terms": "white dove pushing off olive branch, wings spread in slow motion, golden hour sun backlight, feathers",
        "scripture_anchors": "Genesis 8:11; Matthew 3:16; John 1:32; Psalm 55:6; Song of Solomon 2:14; Galatians 5:22",
        "soul_halt_tags": "Peace & Calm, Hope & Courage, Spirit Presence",
        "short_hook_archetypes": "Translation & Symbolism (The Spirit Hovering Like a Dove from Genesis 1 to the Jordan)",
        "rendered": []
    },
    "Burning Bush": {
        "thematic_tags": "holy ground, calling of Moses, I AM WHO I AM, unconsumed presence of God, awe and reverence, Horeb",
        "visual_search_terms": "dry desert thorn bush engulfed in bright smokeless flames, green leaves unconsumed, Sinai wilderness fire",
        "scripture_anchors": "Exodus 3:2-14; Deuteronomy 33:16; Mark 12:26; Acts 7:30-33; Hebrews 12:29",
        "soul_halt_tags": "Guidance & Trust, Sacred Worth, Calling & Purpose",
        "short_hook_archetypes": "Translation Discrepancies ('I AM WHO I AM' in Hebrew)",
        "rendered": []
    },
    "Striking the Rock": {
        "thematic_tags": "living water in the wilderness, provision in dry places, Christ our Rock, Meribah, thirst satisfied",
        "visual_search_terms": "heavy wooden shepherd staff striking dry desert boulder, crystal clear water bursting outward in slow motion",
        "scripture_anchors": "Exodus 17:6; Numbers 20:11; 1 Corinthians 10:4; Psalm 78:15-16; John 4:14; John 7:37-38",
        "soul_halt_tags": "Rest & Fatigue, Healing & Comfort, Spiritual Thirst",
        "short_hook_archetypes": "The Silence of God & Wilderness Provision",
        "rendered": []
    },
    "Chains Falling": {
        "thematic_tags": "deliverance, freedom from bondage, Paul and Silas in prison, addiction recovery, redemption, Jubilee",
        "visual_search_terms": "heavy rusted iron shackles unlocking, chains dropping onto damp stone dungeon floor, liberation",
        "scripture_anchors": "Acts 12:7; Acts 16:26; Psalm 107:14; Isaiah 61:1; Galatians 5:1; Romans 8:1-2",
        "soul_halt_tags": "Hope & Courage, Letting Go, Freedom from Bondage",
        "short_hook_archetypes": "Biblical Cognitive Behavioral Therapy (Breaking Mental & Spiritual Strongholds)",
        "rendered": []
    },
    "Sower Casting Seeds": {
        "thematic_tags": "Parable of the Sower, receptive heart, sowing in tears and reaping in joy, generosity, preaching the Word",
        "visual_search_terms": "olive-skinned hand rhythmically throwing grain seeds from leather pouch, rocky soil furrow, golden sunlight",
        "scripture_anchors": "Matthew 13:3-9; Mark 4:3-8; Psalm 126:5-6; 2 Corinthians 9:6; Galatians 6:7-9; Ecclesiastes 11:6",
        "soul_halt_tags": "Patience & Waiting, Guidance & Trust, Faithfulness",
        "short_hook_archetypes": "1st-Century Agricultural Context (Why Ancient Sowers Scattered Seed Before Plowing)",
        "rendered": []
    },
    "Pouring Anointing Oil": {
        "thematic_tags": "anointing, Holy Spirit, consecration, healing, Psalm 23 cup overflows, setting apart, peace, sanctuary",
        "visual_search_terms": "golden olive oil pouring onto rough-hewn limestone altar slab, volumetric sunlight shaft, floating dust motes, viscous ripples",
        "scripture_anchors": "Psalm 23:5; 1 Samuel 16:13; James 5:14; 1 John 2:20, 27; Exodus 29:7; Isaiah 61:1-3",
        "soul_halt_tags": "Peace & Calm, Healing & Comfort, Sacred Worth",
        "short_hook_archetypes": "1st-Century Shepherd & Temple Context (Why Shepherds Poured Oil on Sheep's Heads)",
        "rendered": [
            {
                "src_name": "gemini_generated_video_28213441.mp4",
                "dam_name": "FHG-BR-031_pouring-anointing-oil_9x16.mp4",
                "aspect": "9:16 (720x1280)",
                "usable_window": "0:00.0 - 0:10.0 (10/10 clean; 0:00.8-0:04.3 first golden drop impact & ripple)"
            },
            {
                "src_name": "gemini_generated_video_fbcc0a19.mp4",
                "dam_name": "FHG-BR-031_pouring-anointing-oil_16x9.mp4",
                "aspect": "16:9 (1280x720)",
                "usable_window": "0:00.0 - 0:10.0 (9.5/10 clean; dead-center stream for 16:9 or 9:16 crop)"
            }
        ]
    },
    "Sandals in Cracked Wilderness": {
        "thematic_tags": "walking with God, wilderness season, perseverance, dusty discipleship road, holy ground, Enoch, Micah 6:8",
        "visual_search_terms": "leather-sandaled feet walking across parched cracked desert clay, billowing golden dust clouds, low-angle ground tracking",
        "scripture_anchors": "Micah 6:8; Genesis 5:24; Deuteronomy 8:2-4; Exodus 3:5; Matthew 4:1; Psalm 119:105; Luke 10:11",
        "soul_halt_tags": "Patience & Waiting, Rest & Fatigue, Guidance & Trust",
        "short_hook_archetypes": "1st-Century Rabbinic Context ('Covered in the Dust of Your Rabbi')",
        "rendered": [
            {
                "src_name": "gemini_generated_video_cb0b0d60.mp4",
                "dam_name": "FHG-BR-032_sandals-in-cracked-wilderness_16x9.mp4",
                "aspect": "16:9 (1280x720)",
                "usable_window": "0:00.0 - 0:10.0 (9.5/10 clean, 5 toes verified; 0:01.0-0:04.5 two footsteps + dust plumes)"
            }
        ]
    },
    "Hauling Fishing Net Rope": {
        "thematic_tags": "perseverance after exhaustion, casting the net again, Sea of Galilee storm, labor, discipleship, holding fast",
        "visual_search_terms": "weathered fisherman hand gripping wet twisted hemp rope, water dripping from knuckles, choppy dark sea waves, silver fish in net",
        "scripture_anchors": "Luke 5:4-6; John 21:6-11; Matthew 4:18-20; Mark 4:35-41; Galatians 6:9; Hebrews 10:23",
        "soul_halt_tags": "Rest & Fatigue, Hope & Courage, Perseverance",
        "short_hook_archetypes": "1st-Century Galilean Context (Night Fishing on the Sea of Galilee)",
        "rendered": [
            {
                "src_name": "gemini_generated_video_3896ebd6.mp4",
                "dam_name": "FHG-BR-033_hauling-fishing-net-rope_16x9.mp4",
                "aspect": "16:9 (1280x720)",
                "usable_window": "0:00.0 - 0:03.3 (Single hand hauling rope) + 0:03.5 - 0:05.5 (Fish in net) + 0:08.8 - 0:10.0 (Boat gunwale). TRIM OUT 0:06.0-0:08.5"
            }
        ]
    }
}

ADDITIONAL_PROMPTS = [
    (
        "Pouring Anointing Oil",
        "Extreme macro, 4k cinematic, slow motion, 16:9 aspect ratio, dead center framing. Thick golden olive oil pouring slowly onto a rough-hewn limestone altar slab in a shaft of warm volumetric sunlight with floating dust motes."
    ),
    (
        "Sandals in Cracked Wilderness",
        "Extreme close-up, 4k cinematic, slow motion, 16:9 aspect ratio, dead center framing. Low ground-level tracking shot of dusty First-Century leather-sandaled feet walking across parched, sun-baked cracked desert clay, kicking up clouds of fine golden dust."
    ),
    (
        "Hauling Fishing Net Rope",
        "Extreme close-up, 4k cinematic, slow motion, 16:9 aspect ratio, dead center framing. A weathered, olive-skinned fisherman's hand gripping and hauling a thick wet hemp net rope over dark choppy sea waves as water drips from the knuckles."
    )
]


def main():
    rows = []
    global_rules = ""
    with DOWNLOAD_CSV.open("r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for idx, r in enumerate(reader):
            if not r:
                continue
            if idx == 0 and r[0].strip().upper().startswith("GLOBAL CONTEXT"):
                global_rules = r[1].strip() if len(r) > 1 else ""
                continue
            rows.append((r[0].strip(), r[1].strip() if len(r) > 1 else ""))

    for title, prompt in ADDITIONAL_PROMPTS:
        if not any(t == title for t, _ in rows):
            rows.append((title, prompt))

    catalog_items = []
    vaulted_files_summary = []

    for i, (title, prompt) in enumerate(rows, start=1):
        broll_id = f"FHG-BR-{i:03d}"
        meta = ENRICHMENT_MAP.get(title, {})
        rendered_list = meta.get("rendered", [])
        dam_records = []

        for r_info in rendered_list:
            src_path = SRC_BROLE_DIR / r_info["src_name"]
            dam_path = DAM_LIB_DIR / r_info["dam_name"]
            if src_path.exists():
                shutil.copy2(src_path, dam_path)
                file_hash = sha256_file(dam_path)
                size_bytes = dam_path.stat().st_size
                rec = {
                    "dam_filename": r_info["dam_name"],
                    "dam_relative_path": f"media/video/b_roll_loops/fhg_veo/broll_library/{r_info['dam_name']}",
                    "source_filename": r_info["src_name"],
                    "duplicate_source_filename": r_info.get("duplicate_src"),
                    "aspect_ratio": r_info["aspect"],
                    "size_bytes": size_bytes,
                    "sha256": file_hash,
                    "usable_window_sec": r_info["usable_window"]
                }
                dam_records.append(rec)
                vaulted_files_summary.append(rec)

        status = "VAULTED_IN_DAM" if dam_records else "QUEUED_FOR_GENERATION"
        catalog_items.append({
            "broll_id": broll_id,
            "title": title,
            "prompt": prompt,
            "status": status,
            "thematic_tags": meta.get("thematic_tags", ""),
            "visual_search_terms": meta.get("visual_search_terms", ""),
            "scripture_anchors": meta.get("scripture_anchors", ""),
            "soul_halt_tags": meta.get("soul_halt_tags", ""),
            "short_hook_archetypes": meta.get("short_hook_archetypes", ""),
            "dam_assets": dam_records
        })

    # Write ZeroCloudDAM JSON Manifest
    manifest = {
        "schema_version": "1.0.0",
        "catalog_id": "fhg-biblical-shorts-broll-master-catalog",
        "google_sheet_id": "1tuit2aqK8NJI8yItK6QN9W50PmIQWKwOTFR2vrTAPdg",
        "global_context_and_rules": global_rules,
        "total_prompts": len(catalog_items),
        "total_vaulted_prompt_concepts": sum(1 for c in catalog_items if c["status"] == "VAULTED_IN_DAM"),
        "total_vaulted_mp4_files": len(vaulted_files_summary),
        "items": catalog_items
    }

    out_json = DAM_DIR / "FHG_BROLL_DAM_CATALOG.json"
    out_json.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write Enriched CSV (ready to import/paste into Google Sheets)
    csv_headers = [
        "B-Roll ID",
        "Clip Title",
        "Veo Master Prompt (16:9 Dead-Center)",
        "Production Status",
        "DAM Filename(s)",
        "Aspect Ratio(s)",
        "QA Usable Timecode Window",
        "Thematic & Theological Tags",
        "Visual & Sensory Search Terms",
        "Scripture Anchors (OT & NT)",
        "Soul / HALT State Tags",
        "Best Short Hook Archetype"
    ]

    for out_csv_path in [
        DAM_DIR / "FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv",
        Path(r"C:\dev\fhg-videos\FHG_Biblical_Shorts_B_Roll_Master_Catalog.csv")
    ]:
        with out_csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["GLOBAL CONTEXT & RULES", global_rules] + [""] * (len(csv_headers) - 2))
            w.writerow(csv_headers)
            for item in catalog_items:
                dam_names = " | ".join(a["dam_filename"] for a in item["dam_assets"])
                aspects = " | ".join(a["aspect_ratio"] for a in item["dam_assets"])
                windows = " | ".join(a["usable_window_sec"] for a in item["dam_assets"])
                w.writerow([
                    item["broll_id"],
                    item["title"],
                    item["prompt"],
                    item["status"],
                    dam_names,
                    aspects,
                    windows,
                    item["thematic_tags"],
                    item["visual_search_terms"],
                    item["scripture_anchors"],
                    item["soul_halt_tags"],
                    item["short_hook_archetypes"]
                ])

    print(f"SUCCESS: Vaulted {len(vaulted_files_summary)} unique MP4 files into {DAM_LIB_DIR}")
    print(f"SUCCESS: Wrote {out_json} ({len(catalog_items)} total B-roll concepts; {manifest['total_vaulted_prompt_concepts']} concepts rendered)")


if __name__ == "__main__":
    main()
