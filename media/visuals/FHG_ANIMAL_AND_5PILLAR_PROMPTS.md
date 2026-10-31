# For His Grace & 864zeros Media Library — Indigenous Biblical Animals (`G1 + H2 + Minimal Blotchy`) & Filter Source Matrix

- **Owner:** Orion Kai (`MEDIA-001`) & Sloane Sterling (`STUDIO-001`)
- **Canonical Registry JSON (Media Dept):** [`C:\dev\864zeros-publish\media\visuals\FHG_VISUAL_SPEC_REGISTRY.json`](file:///C:/dev/864zeros-publish/media/visuals/FHG_VISUAL_SPEC_REGISTRY.json)
- **Canonical Registry JSON (Bible Shared):** [`C:\dev\864zeros-publish\shared\bible\FHG_VISUAL_SPEC_REGISTRY.json`](file:///C:/dev/864zeros-publish/shared/bible/FHG_VISUAL_SPEC_REGISTRY.json)

---

## 1. Upstream Sketch Source Matrix (Which Sketch Version Feeds Which Filter?)

| Filter Edition | Output Suffix | Upstream Input Sketch Used | Stage Flag in `apply_fhg_human_filter.py` | Why This Upstream Source Is Used |
| :--- | :--- | :--- | :--- | :--- |
| **✒️ Contour (`G2`)** | `_g2_s2.jpg` | **🎨 Base Draft (`_base.jpg`)** | `G2+S2` (or `G2+S3`) | Needs pure un-blotched line work from `_base.jpg` so 1px Zhang-Suen skeletonization & 2.5px chiseled chords operate cleanly on pen strokes without wash blotches. |
| **📐 Angular (`G4`)** | `_straight_g4.jpg` | **🎨 Base Draft (`_base.jpg`)** | `G4` | Needs pure contour line work from `_base.jpg` to convert curves into 9.5px planar straight-edge segments with zero blotch interference. |
| **✨ Blotchy (`B1`)** | `_b1_g2_s2.jpg` | **🎨 Base Draft (`_base.jpg`)** | `G2+S2+B1` | Converts translucent washes/line clusters into 3-tier sumi-e/walnut blotch daubs + clears outer 5.8% parchment margins. **Serves as the master tonal plate for C1–C4.** |
| **🌲 Terra/Pine (`C1`)** | `_c1_riso_terra_pine.jpg` | **✨ Blotchy (`B1` / `_b1_g2_s2.jpg`)** | `C1` | Separates the **B1 blotchy wash tiers** into angled Terracotta Clay (`35°`) & Sage-Slate (`75°`) Risograph halftone screens while keeping Deep Forest Pine contours. |
| **★ Riso Earth (`C2`)** | `_c2_riso_earth.jpg` | **✨ Blotchy (`B1` / `_b1_g2_s2.jpg`)** | `C2` | Separates the **B1 blotchy wash tiers** into 3-color Earth Risograph halftone screens: Golden Ochre (`18°`), Sage Olive (`52°`), and Terracotta Rust (`78°`) + Raw Umber ink. |
| **★ Ukiyo-e (`C3`)** | `_c3_ukiyoe_riso.jpg` | **✨ Blotchy (`B1` / `_b1_g2_s2.jpg`)** | `C3` | Uses the **B1** upper ridge for the framed Terracotta-Amber Ukiyo-e bokashi sky gradient and converts the lower **B1** wash blotches into 3-color Earth Risograph screens. |
| **🌊 Prussian (`C4`)** | `_c4_ukiyoe_prussian.jpg` | **✨ Blotchy (`B1` / `_b1_g2_s2.jpg`)** | `C4` | Adds a top-down Prussian Blue (`#183858`) Ukiyo-e bokashi sky fade and tints the **B1** ink-wash blotch zones with flat mineral woodblock pigments. |

---

## 2. Master Prompt Template (`G1 + H2 + Minimal Blotchy`)

```text
Minimalist hand-drawn biblical field sketch of {subject}. Style & Filter Spec (G1 + H2 + Minimal Blotchy): G1 (Sparse Contour Line): Ultra-simple, single-pass sepia fountain-pen and reed-pen contour line work with open broken-stroke intervals, zero dense cross-hatching, zero fur/feather rendering, and zero heavy shading. H2 (Hand-Drawn Humanizer): Natural human wrist micro-tremor, slight pen-lift hesitation at turns, and tiny organic ink pooling where the nib pauses. Minimal Blotchy Wash (B1-Lite): Only 1 to 2 very light, translucent warm walnut-ink and raw-umber watercolor tea-wash blotches loosely brushed behind the main silhouette with soft water-bloom edges, keeping 70-75% of the warm cream cotton parchment (#F5EFE2) completely untouched. Strict Constraints: Square 1:1 composition, generous negative space around the border, NO human faces, NO text, NO letters, NO signatures, NO watermarks.
```

---

## 3. All 10 Indigenous Biblical Animal Prompts (`study_fauna_01` – `10`)

### 1. `study_fauna_01_awassi_sheep_pasture` — Awassi Fat-Tailed Sheep (Judean Pasture)
```text
Minimalist hand-drawn biblical field sketch of two indigenous Middle Eastern fat-tailed Awassi sheep grazing quietly beside a low dry-stone fieldstone wall in an open Judean hill pasture. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Ultra-sparse single-pass sepia fountain-pen contour lines (G1) with natural human wrist tremor and slight nib ink pooling at stroke ends (H2). Apply only a minimal, translucent warm walnut and olive-earth watercolor blotch wash behind the sheep's backs, leaving 70% of the warm cream cotton parchment (#F5EFE2) completely open and unshaded. Zero dense hatching, zero fur detail, no text, no signature, no watermark.
```

### 2. `study_fauna_02_lost_lamb_crags` — Solitary Lost Lamb in Limestone Crags
```text
Minimalist hand-drawn biblical field sketch of a solitary young lamb resting quietly in the shelter of a cleft weathered limestone rock along a quiet wilderness ravine trail. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Ultra-sparse single-pass sepia fountain-pen contour lines (G1) with gentle hand-drawn wrist tremor and broken contour intervals (H2). Apply a single minimal, soft raw-umber and warm ochre ink-wash blotch in the rock cleft shadow behind the lamb, leaving 70% of the warm cream parchment (#F5EFE2) untouched. Zero dense cross-hatching, no text, no signature, no watermark.
```

### 3. `study_fauna_03_engedi_ibex_goats` — En-Gedi Nubian Ibex / Syrian Mountain Goats
```text
Minimalist hand-drawn biblical field sketch of a sure-footed Nubian ibex with sweeping curved horns standing poised on a high stepped limestone crag overlooking the En-Gedi desert canyon. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Economy-of-line single-pass sepia reed-pen contour drawing (G1) with authentic hand-drawn micro-tremor and slight ink pooling at corners (H2). Apply only a minimal, airy warm walnut and terracotta tea-wash blotch along the cliff ledge, keeping 70% of the warm cream parchment (#F5EFE2) open negative space. Zero heavy shading, no text, no signature, no watermark.
```

### 4. `study_fauna_04_turtledoves_olive` — Pair of Turtledoves on an Olive Branch
```text
Minimalist hand-drawn biblical field sketch of two Levantine turtledoves—one perched quietly on a gnarled olive branch and one rising in gentle flight with an olive leaf. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Ultra-simple, continuous sepia fountain-pen contour lines (G1) with loose hand-drawn wrist flow and slight nib pauses (H2). Apply only 1 or 2 minimal, pale olive-sage and warm walnut watercolor blotches behind the wings and leaves, leaving 75% of the warm cream cotton parchment (#F5EFE2) completely bare. Zero feather detailing, no text, no signature, no watermark.
```

### 5. `study_fauna_05_sparrows_stone_wall` — Two House Sparrows on a Dry-Stone Wall
```text
Minimalist hand-drawn biblical field sketch of two small biblical house sparrows perched side by side on a weathered dry-stone courtyard wall beside a single dry grass stem. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Whisper-light, single-pass sepia fountain-pen contour lines (G1) with natural human hand tremor and broken-line simplicity (H2). Apply a single minimal, translucent warm sepia tea-wash blotch across the top stone under the sparrows, keeping 75% of the warm cream parchment (#F5EFE2) open and clean. Zero cross-hatching, no text, no signature, no watermark.
```

### 6. `study_fauna_06_ravens_brook_cherith` — Ravens Soaring Over Brook Cherith
```text
Minimalist hand-drawn biblical field sketch of two ravens gliding on open wings above a narrow rocky desert wadi stream and limestone gorge at Brook Cherith. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Sparse, gestural single-pass dark sepia ink contour lines (G1) with organic hand-drawn wrist variation and ink-nib endpoints (H2). Apply only a minimal, soft diluted walnut-ink blotch wash along the canyon rim and stream bend, leaving 70% of the warm cream parchment (#F5EFE2) open negative space. Zero heavy feather rendering, no text, no signature, no watermark.
```

### 7. `study_fauna_07_soaring_eagle_thermals` — Griffon Eagle Soaring on Thermal Winds
```text
Minimalist hand-drawn biblical field sketch of a solitary Griffon eagle soaring effortlessly with outstretched wings high above a distant Judean mountain ridge. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Ultra-clean, single-pass sepia fountain-pen contour silhouette (G1) with subtle hand-drawn line weight variation and natural wrist tremor (H2). Apply a single minimal, airy warm ochre and diluted umber watercolor blotch beneath the wing and ridge line, leaving 75% of the warm cream parchment (#F5EFE2) untouched sky. Zero dense hatching, no text, no signature, no watermark.
```

### 8. `study_fauna_08_humble_donkey_olive` — Humble Donkey on an Ancient Stone Trail
```text
Minimalist hand-drawn biblical field sketch of a humble pack donkey walking calmly along a quiet ancient footpath bordered by stacked fieldstones and a small olive tree. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Simple, unhurried single-pass sepia fountain-pen contour lines (G1) with organic hand-drawn imperfection and broken line intervals (H2). Apply only a minimal, pale raw-umber and sage tea-wash blotch along the stone wall and trail shadow, keeping 70% of the warm cream parchment (#F5EFE2) open. Zero photorealistic shading, no text, no signature, no watermark.
```

### 9. `study_fauna_09_plowing_oxen_yoke` — Plowing Oxen & Wooden Yoke in a Turned Field
```text
Minimalist hand-drawn biblical field sketch of a pair of oxen seen from the side/back wearing a simple hand-hewn wooden yoke, standing quietly beside shallow plowed earth furrows and distant hills. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Sparse, architectural single-pass sepia reed-pen contour lines (G1) with authentic hand-drawn wrist tremor and slight ink pooling at joints (H2). Apply a minimal, translucent warm terracotta-earth and walnut watercolor blotch across the wooden yoke and foreground furrow, leaving 70% of the warm cream parchment (#F5EFE2) open. Zero heavy cross-hatching, no text, no signature, no watermark.
```

### 10. `study_fauna_10_galilee_fish_net` — Galilean St. Peter's Fish & Draped Linen Net
```text
Minimalist hand-drawn biblical field sketch of three indigenous Sea of Galilee St. Peter's tilapia fish swimming beneath gentle water ripples beside the corner of a draped linen fishing net on a flat shoreline stone. Style & Filter Spec (G1 + H2 + Minimal Blotchy): Flowing, minimalist single-pass sepia fountain-pen contour curves (G1) with natural hand-drawn tremor and light pen-lift breaks (H2). Apply only a minimal, pale Prussian-slate and warm walnut watercolor blotch wash along the water ripple, keeping 75% of the warm cream parchment (#F5EFE2) open and breathable. Zero scale detailing, no text, no signature, no watermark.
```
