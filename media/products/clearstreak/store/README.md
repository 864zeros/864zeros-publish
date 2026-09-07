# ClearStreak store assets

Rendered Play Store graphics live here (source of truth; the web publish step copies the icon +
screenshots into `864zeros-web/products/assets/`).

## Required files
| File | Spec | Used by |
|---|---|---|
| `clearstreak.png` | app icon (rounded square, ~512²) | web page icon + homepage tile |
| `store-icon.png` | 512×512 PNG (32-bit, alpha) | Play listing icon |
| `feature-graphic.png` | 1024×500 | Play feature graphic |
| `clearstreak-1.png` … `-3.png` | phone screenshots, 9:16 (min 320px) | web page figures + Play |
| `clearstreak-4.png` … (optional) | more phone screenshots | Play only (up to 8) |

## ⚠️ Screenshots are blocked by FLAG_SECURE
The app sets `WindowManager.LayoutParams.FLAG_SECURE`, so **screenshots and screen recording are
blocked** on normal builds — you cannot capture these images from `coreDebug` or `storeRelease`.

**Workaround (built — clearStreak `28c2ecf`):** the app gates `FLAG_SECURE` behind
`BuildConfig.ALLOW_CAPTURE` (default false). Build a capture APK, install, take the screenshots on a
device/emulator, then delete that build:

```bash
# in C:\dev\clearStreak
gradle assembleCoreDebug -Pcapture     # ALLOW_CAPTURE=true in DEBUG only → FLAG_SECURE off
# install app/build/outputs/apk/core/debug/*.apk, capture, then uninstall
```

`-Pcapture` only takes effect in debug; release always enforces `FLAG_SECURE`, so no capturable
build can ever ship.

Until these are produced, the generated web page will reference missing images (the generator logs a
`WARN … referenced asset missing`), and the page is not launch-ready.
