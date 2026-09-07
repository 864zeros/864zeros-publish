# OmniClip Store Assets

Rendered graphics and screenshots for OmniClip live here.
The build generator (`864z-build-kit/tools/gen-product-pages.cjs`) copies the web-referenced assets into `864zeros-web/products/assets/`.

## Required Files

| File | Spec | Used By |
|---|---|---|
| `omniclip.png` | App icon (rounded square, ~512×512) | Web page icon + catalog tile |
| `omniclip.svg` | Vector source icon | Vector asset |
| `omniclip-1.png` | 1280×800 screenshot / Slide 1 | Web page figure 1 (Pitch) |
| `omniclip-2.png` | 1280×800 screenshot / Slide 2 | Web page figure 2 (Differentiator) |
| `omniclip-3.png` | 1280×800 screenshot / Slide 3 | Web page figure 3 (Word Trimmer & Privacy) |

## Capturing Screenshots

1. Open `store/store-screenshots.html` in Google Chrome.
2. Open Chrome DevTools (F12).
3. In the Elements panel, locate `#slide-1`, right-click and select **"Capture node screenshot"**.
4. Save as `omniclip-1.png` in this directory.
5. Repeat for `#slide-2` (`omniclip-2.png`) and `#slide-3` (`omniclip-3.png`).
