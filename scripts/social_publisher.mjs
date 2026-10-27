#!/usr/bin/env node
/**
 * 864zeros LLC — 10-Platform Social & Vulture Strike Publisher (Stage C Engine)
 * Enforces the ratified 3-Bucket AI Persona Compliance Policy:
 *   Bucket 1 (AI Persona Allowed): YouTube, X, Instagram, TikTok, Threads -> appends 🤖 AI Persona disclosure + synthetic media flag
 *   Bucket 2 (Real Human / Company Page Only): LinkedIn, Facebook -> routes under 864zeros LLC Company Page or Jeff Conn
 *   Bucket 3 (Single Builder Identity Only): Reddit (/u/864zeros-builder), Hacker News (jeff-864zeros), Product Hunt (@864zeros)
 */

import fs from 'fs';
import path from 'path';

export const PLATFORM_MATRIX = {
  youtube:     { bucket: 1, handle: '@864zeros',           email: '864zeros@gmail.com',    aiAllowed: true,  syntheticFlag: 'selfDeclaredMadeForKids=false, containsSyntheticMedia=true' },
  x:           { bucket: 1, handle: '@864zeros',           email: 'contact@864zeros.com',  aiAllowed: true,  personaHandles: { kate: '@kate864zeros', prya: '@prya864zeros', zane: '@zane864zeros' } },
  instagram:   { bucket: 1, handle: '@864zeros',           email: 'contact@864zeros.com',  aiAllowed: true,  personaHandles: { kate: '@kate864zeros', prya: '@prya864zeros' } },
  tiktok:      { bucket: 1, handle: '@864zeros',           email: 'contact@864zeros.com',  aiAllowed: true,  personaHandles: { kate: '@kate864zeros', prya: '@prya864zeros' } },
  threads:     { bucket: 1, handle: '@864zeros',           email: 'contact@864zeros.com',  aiAllowed: true,  personaHandles: { kate: '@kate864zeros', prya: '@prya864zeros' } },
  linkedin:    { bucket: 2, handle: '864zeros LLC',        email: 'jeff@864zeros.com',     aiAllowed: false, note: 'Company Page & Real Human Founder Profile Only' },
  facebook:    { bucket: 2, handle: '864zeros',            email: 'jeff@864zeros.com',     aiAllowed: false, note: 'Official Brand Page under Founder Profile Only' },
  reddit:      { bucket: 3, handle: '/u/864zeros-builder', email: 'contact@864zeros.com',  aiAllowed: false, note: 'Single Builder Account Only (Zero Sockpuppeting)' },
  hackernews:  { bucket: 3, handle: 'jeff-864zeros',       email: 'jeff@864zeros.com',     aiAllowed: false, note: 'Single Builder Show HN Identity Only' },
  producthunt: { bucket: 3, handle: '@864zeros',           email: 'contact@864zeros.com',  aiAllowed: false, note: 'Maker Launch Identity' }
};

export function formatCompliantCopy(platform, rawText, persona = 'brand') {
  const cfg = PLATFORM_MATRIX[platform];
  if (!cfg) return rawText;
  if (cfg.bucket === 1 && persona !== 'brand' && persona !== 'jeff') {
    const badge = `\n\n🤖 AI Persona (${persona.toUpperCase()} · 864zeros Studio)`;
    return rawText.includes('🤖') ? rawText : `${rawText}${badge}`;
  }
  return rawText;
}

if (import.meta.url === `file://${process.argv[1].replace(/\\/g, '/')}`) {
  console.log('864zeros 10-Platform Matrix Ready:', JSON.stringify(PLATFORM_MATRIX, null, 2));
}
