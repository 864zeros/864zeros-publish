---
node: 864zeros-publish
stream: 864zeros
role: engine
purpose: "Media/content PRODUCTION engine: authors source-of-truth assets, publishes via index.json manifest. Upstream of publish/activation; GTM consumes it, is not it."
entry: index.json
descriptor_backfilled: 2026-09-03
---

# 864zeros-publish

Media/content PRODUCTION engine: authors source-of-truth assets, publishes via index.json manifest. Upstream of publish/activation; GTM consumes it, is not it.

_Frontmatter above is this node's KG descriptor, read by `864scan` -> `graph.jsonld`. Backfilled 2026-09-03 from the code-truth survey; refine as the repo evolves._

## Locked Visual & Illustration Standards (`STUDIO-001` & `MEDIA-001`)

### Mode A — FHG (`For His Grace`) Canonical Biblical Sketch Standard
All Bible verse illustrations (`shared/bible/sketches/`), devotional plates, and scripture visual aids for **For His Grace (`FHG`)** are strictly locked to the 2-step FHG pipeline grounded in [`C:\dev\forhisgrace-web\images\fig-001-jeff-style.jpg`](file:///C:/dev/forhisgrace-web/images/fig-001-jeff-style.jpg):
1. **Step 1 (Single FHG Master Generation Prompt):**
   ```text
   jeff_sketch style, [ONE-SENTENCE ORGANIC BIBLICAL SUBJECT], authentic freehand black fountain-pen contour drawing on warm cream parchment paper (#F5EFE2). Framed inside a thin hand-drawn black ink square border near the outer margin with subtle overshooting (+) corner intersections. Expressive calligraphic line-weight modulation with bold thicker outer silhouette contours and delicate fine interior contour lines. All interior forms and sky remain 100% open unshaded warm parchment. Negative: shading, cross-hatching, stippling, grey washes, color fills, geometric or cubist blocks, ruler-straight CAD lines, text, watermarks, signatures.
   ```
2. **Step 2 (Mandatory Post-Process via `_build/tools/apply_fhg_human_filter.py`):**
   - **Nature & Objects (`fhg_sketch_spec`, ~90%):** **`G2 + S2`** (**Geometry G2** per-stroke straightening `epsilon=2.5px, overshoot=0.15px` + **Humanizer S2 (`stage2_master`)** — `baseFreq=0.045`, `octaves=3`, `scale=1.8`, `blur=(0.0, 0.0)`, `haze_opacity=0.0`).
   - **People Silhouettes from the Back (`fhg_sketch_people_spec`, ~10%):** **`G2 + S3`** (**Geometry G2** per-stroke straightening `epsilon=2.5px, overshoot=0.15px` + **Humanizer S3 (`stage3_apprentice`)** — `baseFreq=0.035`, `octaves=3`, `scale=3.8` [clamped to `1.6px` nib tooth in Fused Mode], `blur=(1.5, 1.0)`, `haze_opacity=0.35`, zero facial features; strictly seen from behind).
   - **Exclusive Canonical Signature Rule:** [`media/visuals/jeff_canonical_signature.png`](file:///C:/dev/864zeros-publish/media/visuals/jeff_canonical_signature.png) (extracted from `ebook_meditation_04_surrender_burden.jpg`) is the **ONLY** signature used across the studio, always stamped on the **bottom-right side** at `width = 0.18w`, `x_right = 0.942w`, `y_bottom = 0.971h` with a local parchment-clearing halo (`MaxFilter(7) + GaussianBlur(4.0)`).
   - **Spec Registry & Reference Guide:** [`shared/bible/FHG_VISUAL_SPEC_REGISTRY.json`](file:///C:/dev/864zeros-publish/shared/bible/FHG_VISUAL_SPEC_REGISTRY.json) & [`media/visuals/lora_overview_prompts_for_jeff_sketch.html`](file:///C:/dev/864zeros-publish/media/visuals/lora_overview_prompts_for_jeff_sketch.html)

