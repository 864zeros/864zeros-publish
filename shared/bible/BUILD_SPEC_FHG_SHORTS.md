# FHG Bible Shorts — 2026 Master Build Specification (`864zGenStudioNow`)

---

## Part I: 2026 Algorithmic Baseline & Production Specifications

Based on current 2026 data analyzing over 214,000 religious short-form clips, algorithmic gatekeeping has shifted entirely from swipe-rate to absolute watch-time and re-watch loops.

* **Length:** 30 to 45 seconds is the optimal sweet spot. Sub-15-second Shorts are actively demoted because they cannot clear the watch-time threshold even at 100% retention.
* **Retention Targets:** You must hit 65% average view duration for videos under 30 seconds, and 50–65% for videos between 30 and 60 seconds to break out of the initial algorithmic testing seed.
* **Framerate & Codec:** `1080x1920` (9:16 aspect ratio) exported via H.264 (`libx264`, `-crf 18`) at 30fps or 60fps. Ensure all TikTok watermarks are stripped, as YouTube aggressively demotes them.
* **Visual Pacing:** Implement a hard cut, zoom, or asset swap every 3 to 4 seconds (`3.5s` target). If the eye rests on a static frame for more than 4 seconds, the swipe rate spikes.

---

## Part II: Deep Engineering & Psychoacoustic Specifications

### 1. Script Architecture & Seamless Looping (30–45s)

**Second-by-Second Blueprint:**
* **0.0s – 2.0s (The Hook):** Mid-sentence, aggressive curiosity gap. Cut all intro frames, logos, greetings, or breaths. Start mid-action or with a direct, provocative question.
* **2.0s – 10.0s (Tension/Context Disruption):** Challenge a commonly held modern belief or present a historical contradiction.
* **10.0s – 25.0s (Historical/Biblical Reveal):** Deliver the theological payload (e.g., original Greek/Hebrew context, First-century cultural norm).
* **25.0s – 35.0s (Personal Application):** Pivot sharply to the viewer (*"What this means for your anxiety today..."*).
* **35.0s – 42.0s (The Seamless Loop):** Write the final sentence so it grammatically and tonally bridges directly into the `0.0s` hook without a breath (e.g., End: *"...and that is exactly why..."* $\rightarrow$ Hook: *"...you are reading the Book of Job completely wrong."*).

**Top 10 High-Converting Hook & Topic Templates (2026):**
1. **Translation Discrepancies:** *"The word 'meek' in the Bible doesn't mean weak; it means a sheathed sword."*
2. **First-Century Judean Context:** *"Why Jesus writing in the dirt (John 8) was actually a legal death threat."*
3. **Biblical Cognitive Behavioral Therapy:** Linking Philippians 4 to modern neurological anxiety.
4. **The 'Misunderstood' Verses:** *"Jeremiah 29:11 was not written to comfort you; it was written to a captive nation."*
5. **Historical Geography:** *"Golgotha wasn't a remote hill; it was a bustling highway intersection."*
6. **Angelic Accuracy:** *"Why Biblically accurate angels look terrifying, not like humans with wings."*
7. **The Silence of God:** Navigating spiritual dryness and the 400 silent years before the Gospels.
8. **Pagan vs. Biblical Nuance:** How the early church co-opted and redefined Roman societal norms.
9. **Stoicism vs. Christianity:** The precise philosophical differences in suffering.
10. **The Second Temple:** Architectural and political realities of the Pharisees.

---

### 2. Visual Choreography & Art-to-Motion Pacing

The 2026 "inauthentic content" policy aggressively penalizes generic AI-generated videos. Blending hand-sketched artwork with cinematic AI video circumvents this penalty by creating a unique visual fingerprint.

* **Pacing & Cut Dynamics:** The eye must never rest on a static frame for more than 4 seconds. Use a hard jump-cut or a major visual asset swap every **3.5 seconds**.
* **The Sketch-to-Video Dissolve:** Do not use hard cuts between the hand-sketched artwork and the AI video (Veo/Flow). Instead, use a **300ms luminance-based luma fade**, transitioning from the ink-wash sketch directly into the photorealistic AI render matching the same composition.
* **Ken Burns Parameters:** Set continuous scale keyframes from **102% to 108% over 4 seconds**. Never push past 110%, as rapid digital scaling degrades perceived resolution, which signals low-effort content to the algorithm.
* **Lighting Contrast:** Alternate between warm, dark parchment tones (backgrounds) and bright, highly saturated foreground subjects to create depth layering for mobile screens.

---

### 3. Voiceover Psychoacoustics & Cadence

* **Vocal Profile:** Warm, intimate, close-mic conversational baritone or tenor. It should sound like a deeply personal late-night conversation, completely stripping away the authoritative, booming "preaching" cadence.
* **Cadence Target:** **165–175 words per minute**. Push Kokoro-82M or Google Cloud TTS to `~1.15x` speed to eliminate dead air.
* **Micro-Pause Engineering (TTS Tuning):** To pass originality checks and build trust, insert a **250ms pause** (`<break time="250ms"/>`) and a **subtle pitch drop** directly before quoting Scripture. This mimics human reverence and psychological weight.
* **Originality Signals:** YouTube applies an algorithmic boost to channels under 50K subscribers using original audio. Avoid generic trending TikTok sounds; synthesize voiceovers locally.

---

### 4. Sound Design, Foley & LUFS Mixing

* **Loudness Standards:** Master final mix to exactly **-14 LUFS integrated** with a True Peak cap of **-1 dBTP**. Pushing louder results in YouTube's algorithm compressing and dulling the audio.
* **Ducking & EQ:** The `432Hz` ambient pad must be ducked **-18dB to -20dB** below the vocal track. Apply a dynamic EQ cut of **-4dB** in the music bed specifically between **300Hz and 3kHz** to carve out space for voiceover intelligibility on mobile phone speakers.
* **Micro-Foley Integration:** On the `3.5s` visual cuts, layer subtle, low-volume organic Foley (e.g., heavy leather Bible closing, dry parchment turning, distant wind, or a soft felt piano strike). This grounds the AI-generated visuals in physical reality, drastically increasing viewer retention.

---

### 5. Caption Typography, Safe Zones & Highlight Psychology

* **Safe Zone Coordinates (`1080x1920`):** Do not center text by eye. The right-side UI elements take up `192px`, while the left margin takes only `48px`. To optically center captions without UI overlap, anchor the text box at **`X = 468`**.
* **Y-Axis Placement:** The bottom `672px` are consumed by the title, channel info, and music attribution. Keep the bottom edge of the caption bounding box above **`Y = 1100`**.
* **Typography:** Heavy sans-serif font (**Montserrat Black** or **Proxima Nova Extrabold**) at **72pt+**. Apply a heavy drop shadow (`Opacity: 85%`, `Distance: 4px`, `Blur: 8px`) or a solid background block to separate text from complex AI visuals.
* **Highlight Psychology:** Static yellow text is visually fatiguing. Use a **Warm Ivory base (`#FFFFF0`)** and apply a **dynamic, word-by-word active highlight in Gold/Amber (`#FFBF00`)**. Limit the screen to **2–4 words at a time**.

---

### 6. 2026 YouTube Shorts Algorithm, Metadata & Originality Signals

* **Evading the Inauthentic Content Penalty:** Rotate **three distinct visual frameworks** (e.g., `Sketch-to-Real`, `Text-on-Parchment`, `B-roll-with-Overlay`) and slightly randomize the TTS pitch contour per video.
* **Metadata & SEO:** Shorts index heavily in YouTube Search via dedicated carousels. Use explicit, question-based titles (e.g., *"What does the Bible actually say about anxiety?"*).
* **Hashtags:** Restrict to **exactly 3 relevant hashtags** (e.g., `#BibleStudy`, `#Faith`, `#God`) to tightly cluster the topic for the algorithm.
* **Posting Schedule & Geo:** Peak engagement window for religious Shorts is **2 PM to 5 PM UTC (9 AM to 12 PM EST)**. Monday is the highest performing day. Target Tier-1 English regions (US, UK, CA, AU). Upload **1 to 2 Shorts per day at the exact same time**.
* **Micro-CTAs (Double-Dipping Loop Retention):** Do not ask for generic subscriptions. Use a **pinned comment** that asks an open-loop question directly related to the video's payload (e.g., *"Which translation did you grow up reading this verse in?"*). While the user types a reply, the video loops in the background, double-dipping retention metrics.

---

## Part III: `864zGenStudioNow` Automated Pipeline Integration

### 1. Content Generation (`JSONL` Schema)
Use Google AI Ultra to generate scripts in bulk using this JSONL structure (updated to include loop bridge, pinned comment CTA, and visual framework rotation):

```jsonl
{"short_id": "vid_001", "framework": "Sketch-to-Real", "title": "How are you supposed to read the Bible in context?", "hook_0_2s": "...you are reading the Bible completely wrong.", "script_body": "You are reading the Bible completely wrong. Most of us open it looking for an immediate answer to today's problem. But in the first century, Scripture was read aloud as one unified story leading to Jesus. <break time=\"250ms\"/> When Jesus said in John 5:39, 'These are the Scriptures that testify about me,' he wasn't talking about isolated daily fortune cookies. If you isolate one verse, you lose the weight of the entire chapter. Next time you open a page, ask 'what does this reveal about God' before you ask 'what does this fix for me,' because until you shift that lens...", "loop_bridge": "...until you shift that lens -> ...you are reading the Bible completely wrong.", "visual_prompts": ["Ink-wash sketch of ancient leather Bible opening -> 300ms luma dissolve to cinematic 9:16 tracking shot in dim library lighting"], "keywords": ["bible study tips", "christian advice", "understanding scripture"], "hashtags": ["#God", "#BibleStudy", "#Faith"], "pinned_comment": "Which verse did you grow up hearing quoted completely out of context?"}
```

### 2. Audio Processing (`Kokoro-82M` / Google TTS + `432Hz` Pad + Micro-Foley)
* Synthesize `script_body` at `~1.15x` (`165–175 WPM`) with a `250ms` pause and subtle pitch drop before Scripture quotes, plus slight per-video pitch contour randomization.
* Layer over a `432Hz` ambient pad ducked `-18dB to -20dB` below the vocal, with a `-4dB` EQ cut across `300Hz–3kHz`.
* Place subtle organic Foley (`parchment_turn.wav`, `leather_close.wav`, `felt_piano.wav`, `desert_wind.wav`) at each `3.5s` cut, and normalize final master via `loudnorm=I=-14:TP=-1.0:LRA=11`.

### 3. Compositing & Export (`FFmpeg` + ASS Active-Word Captions)
* `1080x1920` @ `60fps` (`libx264`, `-crf 18`, `aac 192k`).
* `3.5s` visual cuts with `300ms` luma dissolve (`xfade`) from Sketch to Veo and `102% -> 108%` Ken Burns (`zoompan`).
* Burned-in `.ass` subtitles anchored at `X = 468`, bottom edge above `Y = 1100`, `Montserrat Black 72pt+`, Warm Ivory (`#FFFFF0`) base with active word-by-word Gold/Amber (`#FFBF00`) highlight (2–4 words per frame).

---

## Part IV: Foundation Model Service Registry (`BRK-MEDIA-004` / `864zGenStudioNow`)

All generative video, multi-angle turnaround imaging, sketch restyling, and expressive audio synthesis across the `864zGenStudioNow` production line are governed by the **`BRK-MEDIA-004` Foundation Model Service Registry**:

### 1. Video Generation & Character-Locked Motion (`Veo 3 / 3.1 / 2.0`)
* **Registered Models:** `veo-3.0-generate-preview`, `veo-3.1-generate-preview`, `veo-2.0-generate-001`
* **Core Production Modes:**
  * **Image-to-Video (`image`):** Animating high-resolution Studio still plates (`9:16` vertical `1080x1920` and `16:9` widescreen `1920x1080`) with controlled camera dolly, orbital, and aerial fly-through motion.
  * **First-to-Last Frame Interpolation (`image` + `last_frame`):** Smoothly interpolating between two multi-angle character poses or state transitions (e.g., First-Century Jesus looking down in `Gemini_Generated_Image_a4jywwa4jywwa4jy.jpg` $\rightarrow$ looking up in `Gemini_Generated_Image_xyl7h6xyl7h6xyl7.jpg`, or ink-wash sketch frame $\rightarrow$ photorealistic First-Century frame).
  * **Reference "Ingredients" (`reference_images`):** Locking 1–3 character turnaround sheets as invariant reference ingredients so every generated clip preserves **100% facial, beard, hair, complexion, and First-Century wardrobe consistency** across cuts.

### 2. Multi-Angle Turnaround, Retouching & Sketch Restyling (`Imagen 3` & `Gemini 2.5 Flash Image`)
* **Registered Models:** `imagen-3.0-generate-002`, `imagen-3.0-capability-001`, `gemini-2.5-flash-image-preview`
* **Core Production Modes:**
  * **Multi-Angle Character Turnarounds:** Generating locked front, 3/4, profile, and orbital reference sheets from a single canonical character anchor.
  * **Inpainting & Historical Retouching:** Removing modern artifacts and enforcing First-Century Judean/Galilean architectural and wardrobe accuracy.
  * **Photoreal-to-Sketch Restyling:** Converting photorealistic First-Century keyframes into hand-drawn charcoal/sepia ink-wash plates to feed the `300ms` `Sketch-to-Real` luma dissolve (`xfade`).

### 3. Psychoacoustic Audio & Expressive Synthesis (`Lyria 2` & `Chirp 3 HD`)
* **Registered Models:** `lyria-002` (instrumental ambient beds & `432Hz` harmonic pads), `Chirp 3 HD` / `Kokoro-82M` / `en-US-AndrewMultilingualNeural` (warm, close-mic conversational baritone/tenor narration at `165–175 WPM` with `<break time="250ms"/>` pre-Scripture reverence pauses).

### 4. FinOps & Cost/Routing Governance (`$0 Marginal Bulk Video Rule`)
* **Tier 1 — Google Flow Web App (`jeff.m.conn@gmail.com` AI Ultra Subscription = `$0` Marginal Cost):** **MANDATORY** primary route for all bulk Veo 3 / 3.1 video generation, First-to-Last Frame interpolations, and Reference Ingredient shoots using included AI Ultra subscription credits.
* **Tier 2 — Metered Vertex AI (`project: oia-age-backend`) & Gemini API:** Reserved strictly for lightweight, low-cost image/retouching passes (`gemini-2.5-flash-image-preview`, `imagen-3.0`), TTS audio synthesis (`Chirp 3 HD`), and targeted programmatic orchestration.

---

## Part V: Locked First-Century Jesus Character Pack & Vaulted Veo Motion Inventory

To eliminate generic AI facial drift across religious Shorts, the Studio has vaulted a canonical, historically grounded **First-Century Judean Jesus Character Pack** and paired Veo motion library in `C:\dev\864zeros-publish`:

### 1. Canonical Character Turnaround & Pose Plates
**Vault Path:** `C:\dev\864zeros-publish\media\video\fhg_shorts\plates\jesus_character_pack\`
* **4 Single-Frame High-Res Angles (`2752x1536`):**
  * `Gemini_Generated_Image_a4jywwa4jywwa4jy.jpg` — Downcast / Contemplative 3/4 Close-Up (First-Frame interpolation anchor).
  * `Gemini_Generated_Image_n6l4wdn6l4wdn6l4.jpg` — Eye-Level 3/4 Close-Up Looking Left.
  * `Gemini_Generated_Image_xyl7h6xyl7h6xyl7.jpg` — Upward Reverent Gaze 3/4 Close-Up (Last-Frame interpolation target).
  * `Gemini_Generated_Image_mnmhmmmnmhmmmnmh.jpg` — Over-the-Shoulder / Rear-Profile Hooded Shot in Judean Street.
* **3 Side-by-Side Comparison Sheets (`3168x1344`):**
  * `Gemini_Generated_Image_jqwj89jqwj89jqwj.jpg` — 3/4 Looking Right (Left: cheek scratch, Right: clean retouched portrait).
  * `Gemini_Generated_Image_v6ndruv6ndruv6nd.jpg` — Side Profile Looking Right (Left: cheek scratch, Right: clean retouched profile).
  * `Gemini_Generated_Image_ocy5d7ocy5d7ocy5.jpg` — Mirrored Side Profile Sheet.
* **3 Vertical `9:16` Poses (`Screenshot *.png`):**
  * `Screenshot 2026-10-31 012543.png` — Full-Body Standing in Judean Village Street.
  * `Screenshot 2026-10-31 012629.png` — Backlit Morning Sun Direct-Gaze Close-Up.
  * `Screenshot 2026-10-31 012823.png` — High-Angle Seated on Ground (John 8 / Teaching Pose).

### 2. Vaulted Character-Locked Jesus Veo Motion Clips (`10.0s` @ `1280x720`)
**Vault Path:** `C:\dev\864zeros-publish\media\video\b_roll_loops\fhg_veo\jesus\`
* `Continuous_360-degree_orbital_camera_movement_2d61b5d5.mp4` — 360° orbital camera movement around Jesus in sunlit village courtyard.
* `Medium_shot,_centered_composition._A_6c5c8acc.mp4` — Centered backward dolly as Jesus walks forward between olive trees into a warm medium close-up.
* `Slow_lateral_tracking_shot_(dolly_1182e743.mp4` — Lateral dolly tracking walk left-to-right that arcs into a golden-hour 3/4 medium close-up.
* `Slow_lateral_tracking_shot_(dolly_a169b089.mp4` — Steady side-profile lateral dolly tracking Jesus walking across the village square.
