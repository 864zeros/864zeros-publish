#!/usr/bin/env python3
"""
864zeros Edge OCR & QR Companion Ingestion Pipeline (`src/ocr/litert_pipeline.py`)
==================================================================================
Implements the realistic 3-Tier `android_arm64` hardware capability cascade for ClearStreak's
5"x8" Softback Companion Journal scanner:
  - Tier A (>= 8GB RAM + NPU/Vulkan FP16): Quantized Gemma 3 4B INT4 (`LiteRT-LM`)
  - Tier B (4GB - 6GB RAM): Offline Google ML Kit Text Recognition v2 (4.5MB TFLite bundle)
  - Tier C (< 4GB RAM or lowMemory state): QR Deep-Link Decode + Encrypted Local Image Vault
    + Optional User-Owned Google Drive OAuth (`drive.appdata`) offload (zero metered cloud billing).
"""

import re
import urllib.parse
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class DeviceHardwareProfile:
    device_id: str
    device_name: str
    arch: str
    total_ram_gb: float
    available_ram_mb: int
    has_npu_or_vulkan_fp16: bool
    os_low_memory_flag: bool = False


@dataclass
class QRContextMetadata:
    raw_uri: str
    scheme: str
    book_id: str
    page_num: int
    trigger_key: str
    entry_id: str
    valid: bool


@dataclass
class OCRPipelineRouteDecision:
    device_id: str
    device_name: str
    arch: str
    total_ram_gb: float
    available_ram_mb: int
    selected_tier: str
    engine_id: str
    model_footprint_mb: float
    peak_ram_delta_mb: float
    estimated_latency_ms: int
    expected_cer_percent: float
    sovereign_storage_mode: str
    metered_cloud_api_calls: int
    oom_safety_status: str


QR_URI_REGEX = re.compile(
    r"^(864z://cs/entry|https://864zeros\.com/cs/entry)\?book=([a-z0-9_]+)&page=(\d+)&trigger=(HUNGRY|ANGRY|LONELY|TIRED|STRESSED|HOPELESS)&ref=([a-z0-9_]+)$"
)


def parse_qr_payload(uri: str) -> QRContextMetadata:
    match = QR_URI_REGEX.match(uri.strip())
    if not match:
        return QRContextMetadata(
            raw_uri=uri,
            scheme="INVALID",
            book_id="",
            page_num=0,
            trigger_key="",
            entry_id="",
            valid=False,
        )
    scheme, book_id, page_str, trigger_key, entry_id = match.groups()
    return QRContextMetadata(
        raw_uri=uri,
        scheme=scheme,
        book_id=book_id,
        page_num=int(page_str),
        trigger_key=trigger_key,
        entry_id=entry_id,
        valid=True,
    )


def select_ocr_tier(profile: DeviceHardwareProfile) -> OCRPipelineRouteDecision:
    """
    Deterministic 3-Tier routing logic preventing OOM on 4GB/2GB devices while unlocking
    on-device multimodal LiteRT-LM on >= 8GB flagship devices.
    """
    if (
        profile.total_ram_gb >= 7.5
        and profile.available_ram_mb >= 3200
        and profile.has_npu_or_vulkan_fp16
        and not profile.os_low_memory_flag
    ):
        return OCRPipelineRouteDecision(
            device_id=profile.device_id,
            device_name=profile.device_name,
            arch=profile.arch,
            total_ram_gb=profile.total_ram_gb,
            available_ram_mb=profile.available_ram_mb,
            selected_tier="TIER_A",
            engine_id="LiteRT-LM Gemma-3-4B-IT-INT4 (On-Device NPU/GPU)",
            model_footprint_mb=2340.0,
            peak_ram_delta_mb=2580.0,
            estimated_latency_ms=1420,
            expected_cer_percent=2.1,
            sovereign_storage_mode="Local SQLite + Full Semantic Handwriting Transcription",
            metered_cloud_api_calls=0,
            oom_safety_status="SAFE (Headroom >= 620MB above 2.58GB peak)",
        )

    if (
        profile.total_ram_gb >= 3.6
        and profile.available_ram_mb >= 350
        and not profile.os_low_memory_flag
    ):
        return OCRPipelineRouteDecision(
            device_id=profile.device_id,
            device_name=profile.device_name,
            arch=profile.arch,
            total_ram_gb=profile.total_ram_gb,
            available_ram_mb=profile.available_ram_mb,
            selected_tier="TIER_B",
            engine_id="Google ML Kit Text Recognition v2 (Bundled Offline TFLite) + Local HALT Keyword Tagger",
            model_footprint_mb=4.5,
            peak_ram_delta_mb=68.0,
            estimated_latency_ms=185,
            expected_cer_percent=4.8,
            sovereign_storage_mode="Local SQLite + Offline Line-by-Line OCR Extraction",
            metered_cloud_api_calls=0,
            oom_safety_status="SAFE (68MB peak fits comfortably inside 4GB RAM budget)",
        )

    return OCRPipelineRouteDecision(
        device_id=profile.device_id,
        device_name=profile.device_name,
        arch=profile.arch,
        total_ram_gb=profile.total_ram_gb,
        available_ram_mb=profile.available_ram_mb,
        selected_tier="TIER_C",
        engine_id="ZXing QR Metadata Decoder + AES-256-GCM Encrypted WebP Crop + User Google Drive OAuth Sync",
        model_footprint_mb=0.8,
        peak_ram_delta_mb=24.0,
        estimated_latency_ms=28,
        expected_cer_percent=0.0,
        sovereign_storage_mode="Local SQLite QR Link + User-Owned Google Drive (drive.appdata) Encrypted Crop",
        metered_cloud_api_calls=0,
        oom_safety_status="SAFE (VLM & OCR bypassed to prevent Android lmkd OOM kill)",
    )


def simulate_journal_page_scan(
    profile: DeviceHardwareProfile,
    qr_uri: str,
    simulated_handwriting: str,
) -> dict:
    qr_meta = parse_qr_payload(qr_uri)
    if not qr_meta.valid:
        raise ValueError(f"Invalid 864zeros QR payload: {qr_uri}")

    route = select_ocr_tier(profile)
    result = {
        "qr_metadata": asdict(qr_meta),
        "routing_decision": asdict(route),
        "extracted_text": None,
        "affect_tags_detected": [],
        "drive_oauth_queued": False,
    }

    if route.selected_tier in ("TIER_A", "TIER_B"):
        result["extracted_text"] = simulated_handwriting
        words = set(re.findall(r"[a-z]+", simulated_handwriting.lower()))
        tag_candidates = ["breath", "pause", "patience", "calm", "water", "rest", "gratitude", "boundary", "step"]
        result["affect_tags_detected"] = [t for t in tag_candidates if t in words]
    else:
        result["extracted_text"] = "[DEFERRED_TO_TIER_A_OR_VISUAL_CARD]"
        result["drive_oauth_queued"] = True

    return result


if __name__ == "__main__":
    sample_profile = DeviceHardwareProfile(
        device_id="midrange_4gb",
        device_name="Galaxy A15 5G (4GB Baseline)",
        arch="android_arm64",
        total_ram_gb=4.0,
        available_ram_mb=1150,
        has_npu_or_vulkan_fp16=False,
    )
    scan = simulate_journal_page_scan(
        sample_profile,
        "864z://cs/entry?book=864z_scripture_core_kjv&page=5&trigger=ANGRY&ref=kjv_angry_01",
        "Paused for ninety seconds, drank water, and let the heat settle before speaking with patience.",
    )
    print("Simulated Scan Output:", scan["routing_decision"]["selected_tier"], "->", scan["routing_decision"]["engine_id"])
