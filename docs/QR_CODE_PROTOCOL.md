# 864zeros Deterministic QR Code Protocol (`864z://cs/entry`)

**Document Version:** `1.0.0`  
**Owner:** 864zeros Publishing House & ClearStreak Edge Engineering  
**Scope:** 5"×8" Softback Companion Journals, ClearStreak Offline Camera Scanner (`android_arm64` / `iOS`), and Physical-to-Digital Handwritten Entry Ingestion.

---

## 1. Architectural Purpose

Every printed page in an **864zeros 5"×8" Softback Companion Journal** carries a deterministic, bottom-right vector QR code anchor alongside four corner fiducial alignment marks. When a reader writes a handwritten reflection on the physical paper page and scans it with the **ClearStreak** companion app camera:

1. **Zero-Lookup Context Resolution:** The QR payload immediately identifies the exact content pack (`book`), physical page number (`page`), HALT affect state (`trigger`), and canonical passage (`ref`) completely offline—requiring zero cloud database queries.
2. **Geometric Homography & Deskew:** The QR finder patterns combined with the page-frame fiducials define the exact bounding box of the 12 ruled handwriting lines (`y = 4.30in` to `y = 7.15in`), enabling fast perspective rectification prior to on-device OCR.
3. **Sovereign Ledger Sync:** The extracted handwritten text (or encrypted page crop on low-RAM devices) is attached directly to the user's local ClearStreak habit & affect ledger under the exact `entry_id` and `trigger_key`.

---

## 2. Canonical URI Payload Specification

### 2.1 Native Custom Scheme (Primary Print Payload)

```text
864z://cs/entry?book={book_id}&page={page_num}&trigger={trigger}&ref={entry_id}
```

### 2.2 Universal HTTPS App Link Wrapper (OS Camera Fallback)

When scanned from a native OS camera app outside ClearStreak, Android App Links (`assetlinks.json`) and iOS Universal Links (`apple-app-site-association`) route the HTTPS equivalent directly into the local app or display a lightweight static companion card:

```text
https://864zeros.com/cs/entry?book={book_id}&page={page_num}&trigger={trigger}&ref={entry_id}
```

### 2.3 Query Parameter Schema

| Parameter | Type | Constraints / Regex | Example | Description |
| :--- | :--- | :--- | :--- | :--- |
| `book` | `string` | `^[a-z0-9_]+$` | `864z_scripture_core_kjv` | Canonical `pack_id` from `content_pack.schema.json`. |
| `page` | `integer` | `^[1-9][0-9]{0,3}$` | `5` | 1-indexed physical journal page number within the edition. |
| `trigger` | `enum` | `HUNGRY\|ANGRY\|LONELY\|TIRED\|STRESSED\|HOPELESS` | `ANGRY` | Active HALT affect category associated with the page. |
| `ref` | `string` | `^[a-z0-9_]+$` | `kjv_angry_01` | Unique `entry_id` within the content pack. |

---

## 3. Print & Optical Engineering Specifications (5"×8" KDP Softback)

| Specification | Standard Value | Rationale |
| :--- | :--- | :--- |
| **Trim Size** | `5.00 in × 8.00 in` (`127 mm × 203.2 mm`) | Portable bedside/carry companion format with low KDP print unit cost. |
| **Safe Margin / Bleed** | `0.50 in` inside gutter, `0.375 in` outer/top/bottom | Prevents QR clipping during KDP perfect-binding guillotine trim (`±0.0625 in` variance). |
| **QR Bounding Box** | `0.65 in × 0.65 in` (`16.5 mm × 16.5 mm`) | Placed at bottom-right margin (`x = 3.95 in`, `y = 6.95 in`) with a mandatory `4-module` quiet zone. |
| **Error Correction Level** | **ECC Level M (15%)** default; **Level Q (25%)** for cream stock | Survives smudge, graphite pencil graze, or slight thumb occlusion during handheld scanning. |
| **Module Matrix Size** | `29 × 29` to `37 × 37` modules (Version 3–5) | Ensures each module is `>= 0.42 mm` wide at 300/600 DPI KDP monochrome laser press resolution. |
| **Ink & Stock Contrast** | `100% K` (`#000000`) on uncoated White or Cream (`#FAF6EE`) | Achieves PCS (Print Contrast Signal) `>= 0.82`, well above ISO/IEC 15415 Grade A (`0.70`). |
| **Vector Rendering** | Crisp SVG `<rect>` path matrix (`shape-rendering="crispEdges"`) | Eliminates raster anti-aliasing blur during PDF/X-1a print RIP rasterization. |

---

## 4. Offline Camera Pairing & Ingestion Sequence

```
[Physical 5"x8" Journal Page]
       │
       ▼ (1. User opens ClearStreak Camera Scanner)
[Single-Frame Capture: QR + Ruled Handwriting Region]
       │
       ├──► (2a. Fast QR Decode < 18ms via ML Kit Barcode / ZXing)
       │         Extracts: book_id, page_num, trigger, entry_id
       │
       ├──► (2b. Corner Fiducial Homography Transform)
       │         Crops & deskews the 12 ruled handwriting lines
       │
       ▼ (3. Hardware Capability Router — see HARDWARE_BENCHMARKS.md)
  ┌────┴───────────────────────────────────────────────────┐
  │ Tier A (>= 8GB RAM): Quantized Gemma 3 / LiteRT-LM     │
  │ Tier B (4GB–6GB RAM): Google ML Kit Text Rec v2 (4.5MB)│
  │ Tier C (< 4GB RAM): Encrypted Local Crop + Drive Sync  │
  └────┬───────────────────────────────────────────────────┘
       │
       ▼ (4. Local SQLite / IndexedDB Ledger Commit)
[Entry linked to HALT Trigger + Micro-Action Streak Credited]
```
