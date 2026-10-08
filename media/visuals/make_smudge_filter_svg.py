import os

src_svg = r"C:\dev\864zeros-publish\media\visuals\rendered_art\gestalt_raw_freehand_clean_strokes.svg"
dst_svg = r"C:\dev\864zeros-publish\media\visuals\tablet_vector_pack_s8_ultra\gestalt_native_svg_filter.svg"

with open(src_svg, "r", encoding="utf-8") as f:
    content = f.read()

filter_header = """<?xml version="1.0" encoding="UTF-8"?>
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" style="background:#ffffff;">
<defs>
  <!-- Charcoal / Graphite Advection Smudge Filter -->
  <filter id="charcoal_smudge" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB">
    <!-- 1. Directional Smear (simulating 45-degree finger/stump drag) -->
    <feGaussianBlur in="SourceGraphic" stdDeviation="8 3" result="directional_smear" />
    
    <!-- 2. Paper grain tooth (turbulence noise) -->
    <feTurbulence type="fractalNoise" baseFrequency="0.045" numOctaves="3" result="paper_tooth" />
    
    <!-- 3. Displace the smear along paper grain fibers -->
    <feDisplacementMap in="directional_smear" in2="paper_tooth" scale="10" xChannelSelector="R" yChannelSelector="G" result="textured_smudge" />
    
    <!-- 4. Soften and tone the dragged charcoal trail -->
    <feColorMatrix in="textured_smudge" type="matrix" 
      values="0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0 0.12  0 0 0 0.55 0" result="charcoal_haze" />
              
    <!-- 5. Layer crisp original ink on top of the soft graphite bed -->
    <feMerge>
      <feMergeNode in="charcoal_haze" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>

  <!-- Lighter Stumping / Tortillon Blur Filter -->
  <filter id="tortillon_stump" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="5 5" result="blur" />
    <feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="2" result="noise" />
    <feDisplacementMap in="blur" in2="noise" scale="5" result="displaced" />
    <feColorMatrix in="displaced" type="matrix"
      values="0 0 0 0 0.1  0 0 0 0 0.1  0 0 0 0 0.1  0 0 0 0.4 0" result="haze" />
    <feMerge>
      <feMergeNode in="haze" />
      <feMergeNode in="SourceGraphic" />
    </feMerge>
  </filter>
</defs>
<g id="artwork" filter="url(#charcoal_smudge)">
"""

first_path = content.find("<path")
body = content[first_path:]

if body.rstrip().endswith("</svg>"):
    body = body.rstrip()[:-6] + "</g>\n</svg>"

new_content = filter_header + body

with open(dst_svg, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Created native filter SVG: {dst_svg} ({os.path.getsize(dst_svg) / 1024:.1f} KB)")
