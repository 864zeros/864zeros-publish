#!/usr/bin/env python3
"""
864zeros Studio — Master Focus Pack & Provenance Lock Validator
(`C:\\dev\\864zeros-publish\\scripts\\validate_focus_packs.py`)

Verifies:
1. All 20 locked pre-1931 Public Domain source files in `sources/public_domain_classics/PROVENANCE_LOCK.json`
   match their exact on-disk byte sizes and SHA-256 digests.
2. All 9 Focus Packs (270 total daily cards across Volume 1 + Volume 2) in `shared/focus_packs/`
   conform to the unified v2.0 Focus Pack schema:
   - Required pack headers (`pack_id`, `version`, `title`, `subtitle`, `provenance`, `entries`)
   - Exact 30-day continuity (`day: 1..30`, 30 entries per pack)
   - Required non-empty entry fields (`id`, `day`, `citation`, `text`, `plain`, `application`,
     `strategic_prompt`, `micro_action`, `focus_theme`, `halt_triggers`)
3. Verbatim source verification: every single quote in the 4 Volume 2 Focus Packs (120 entries)
   is verified as an exact normalized substring of its locked pre-1931 Project Gutenberg `.txt` source.
4. Clean-Room Guardrail: zero modern translators, zero banned pop-habit phrases, zero `66-day` myth,
   and zero occurrences of the word `impulse` inside `plain`, `application`, `strategic_prompt`,
   or `micro_action` fields.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources" / "public_domain_classics"
PROVENANCE_FILE = SOURCES_DIR / "PROVENANCE_LOCK.json"
FOCUS_PACKS_DIR = ROOT / "shared" / "focus_packs"
CATALOG_FILE = FOCUS_PACKS_DIR / "focus_packs_catalog.json"

VOLUME_1_PACKS = [
    "marcus_aurelius_meditations.json",
    "stoic_masters_epictetus_seneca.json",
    "ben_franklin_virtues.json",
    "aristotle_character.json",
    "william_james_habit.json",
]

VOLUME_2_PACKS = {
    "seneca_shortness_of_life_30day.json": "seneca_dialogues_stewart_1889.txt",
    "epictetus_discourses_30day.json": "epictetus_discourses_long_1877.txt",
    "samuel_smiles_self_help_30day.json": "samuel_smiles_self_help_1859.txt",
    "arnold_bennett_24_hours_30day.json": "arnold_bennett_24_hours_1910.txt",
}

BANNED_TRANSLATORS_AND_TERMS = [
    "gregory hays",
    "robin waterfield",
    "ryan holiday",
    "donald robertson",
    "massimo pigliucci",
    "robert dobbs",
    "a.a. long",
    "atomic habits",
    "james clear",
    "tiny habits",
    "bj fogg",
    "charles duhigg",
    "habit loop",
    "habit stacking",
    "2-minute rule",
    "two-minute rule",
    "never miss twice",
    "1% better",
    "66 days",
    "66-day",
]

VALID_HALT_TRIGGERS = {"HUNGRY", "ANGRY", "LONELY", "TIRED", "STRESSED", "HOPELESS"}


def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def validate_provenance_lock() -> tuple[int, list[str]]:
    errors: list[str] = []
    if not PROVENANCE_FILE.exists():
        return 0, [f"Missing {PROVENANCE_FILE}"]

    data = json.loads(PROVENANCE_FILE.read_text(encoding="utf-8"))
    sources = data.get("verified_sources") or data.get("sources") or []
    if len(sources) < 20:
        errors.append(f"Expected >= 20 locked PD sources in PROVENANCE_LOCK.json, found {len(sources)}")

    verified_count = 0
    for src in sources:
        fname = src.get("file")
        expected_sha = src.get("sha256", "").upper()
        expected_bytes = src.get("bytes")
        fpath = SOURCES_DIR / fname
        if not fpath.exists():
            errors.append(f"Missing locked PD source file on disk: {fname}")
            continue
        raw = fpath.read_bytes()
        actual_bytes = len(raw)
        actual_sha = hashlib.sha256(raw).hexdigest().upper()
        if actual_bytes != expected_bytes:
            errors.append(f"{fname}: byte mismatch (lock={expected_bytes}, disk={actual_bytes})")
        if actual_sha != expected_sha:
            errors.append(f"{fname}: SHA-256 mismatch (lock={expected_sha}, disk={actual_sha})")
        if src.get("publication_year", 9999) >= 1931:
            errors.append(f"{fname}: publication_year {src.get('publication_year')} is not pre-1931")
        verified_count += 1

    return verified_count, errors


def validate_pack_file(pack_name: str, source_txt_name: str | None = None) -> tuple[int, list[str]]:
    errors: list[str] = []
    fpath = FOCUS_PACKS_DIR / pack_name
    if not fpath.exists():
        return 0, [f"Missing Focus Pack file: {fpath}"]

    data = json.loads(fpath.read_text(encoding="utf-8"))
    for req_header in ("pack_id", "version", "title", "subtitle", "provenance", "entries"):
        if req_header not in data or not data[req_header]:
            errors.append(f"{pack_name}: missing or empty header '{req_header}'")

    entries = data.get("entries", [])
    if len(entries) != 30:
        errors.append(f"{pack_name}: expected 30 entries, found {len(entries)}")

    source_norm = None
    if source_txt_name:
        src_path = SOURCES_DIR / source_txt_name
        if not src_path.exists():
            errors.append(f"{pack_name}: source file {source_txt_name} missing")
        else:
            source_norm = normalize_ws(src_path.read_text(encoding="utf-8-sig"))

    seen_ids: set[str] = set()
    days: list[int] = []

    for idx, entry in enumerate(entries, start=1):
        eid = entry.get("id", "")
        if not eid:
            errors.append(f"{pack_name} entry #{idx}: missing 'id'")
        elif eid in seen_ids:
            errors.append(f"{pack_name} entry #{idx}: duplicate id '{eid}'")
        seen_ids.add(eid)

        day_val = entry.get("day")
        days.append(day_val)

        for field in (
            "citation",
            "text",
            "plain",
            "application",
            "strategic_prompt",
            "micro_action",
            "focus_theme",
        ):
            val = entry.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"{pack_name} ({eid}): missing or blank field '{field}'")

        halt_list = entry.get("halt_triggers")
        if not isinstance(halt_list, list) or not halt_list:
            errors.append(f"{pack_name} ({eid}): missing or empty 'halt_triggers'")
        else:
            invalid_triggers = set(halt_list) - VALID_HALT_TRIGGERS
            if invalid_triggers:
                errors.append(f"{pack_name} ({eid}): invalid HALT triggers {invalid_triggers}")

        # Verbatim check for Volume 2 packs against locked .txt source
        if source_norm is not None:
            quote_norm = normalize_ws(entry.get("text", ""))
            if quote_norm not in source_norm:
                errors.append(
                    f"{pack_name} ({eid}): quote not found verbatim in {source_txt_name}: {quote_norm[:80]}..."
                )

        # Clean-room & banned terms check across all authored fields
        authored_blob = " ".join(
            str(entry.get(k, ""))
            for k in ("plain", "application", "strategic_prompt", "micro_action", "citation")
        ).lower()

        for banned in BANNED_TRANSLATORS_AND_TERMS:
            if banned in authored_blob:
                errors.append(f"{pack_name} ({eid}): contains banned term '{banned}'")

        if re.search(r"\bimpulse\b|\bimpulses\b", authored_blob):
            errors.append(f"{pack_name} ({eid}): authored commentary contains banned word 'impulse'")

    if days != list(range(1, 31)):
        errors.append(f"{pack_name}: day numbering is not 1..30 sequential: {days}")

    return len(entries), errors


def main() -> int:
    print("=" * 78)
    print("864zeros Studio — Focus Pack & Provenance Lock Validation Suite")
    print("=" * 78)

    all_errors: list[str] = []

    locked_count, prov_errors = validate_provenance_lock()
    all_errors.extend(prov_errors)
    print(f"[PROVENANCE_LOCK] Verified {locked_count} pre-1931 Public Domain source files (errors: {len(prov_errors)})")

    total_cards = 0
    all_packs = [(p, None) for p in VOLUME_1_PACKS] + list(VOLUME_2_PACKS.items())

    for pack_name, src_txt in all_packs:
        count, p_errors = validate_pack_file(pack_name, src_txt)
        total_cards += count
        all_errors.extend(p_errors)
        vol_tag = "Vol 2 (Verbatim + Schema)" if src_txt else "Vol 1 (Enriched Schema)"
        status = "PASS" if not p_errors else f"FAIL ({len(p_errors)} errors)"
        print(f"  - {pack_name:<38} [{vol_tag}] -> {count} cards | {status}")

    print("-" * 78)
    print(f"Total Focus Packs Validated: {len(all_packs)} packs | Total Daily Cards: {total_cards}")

    if all_errors:
        print("\nVALIDATION ERRORS FOUND:")
        for err in all_errors:
            print(f"  [!] {err}")
        return 1

    print("ALL CHECKS PASSED: 100% Schema Compliant, 1..30 Continuous, Verbatim PD Locked, Clean-Room Verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
