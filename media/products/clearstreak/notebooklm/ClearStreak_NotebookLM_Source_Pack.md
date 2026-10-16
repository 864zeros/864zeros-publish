# ClearStreak — Google NotebookLM Deep-Dive & Audio Overview Source Pack

> **How to use this file in NotebookLM:** Upload this single markdown document (`ClearStreak_NotebookLM_Source_Pack.md`) into a new Google NotebookLM notebook. Use the **Custom Audio Overview Prompt** below when clicking "Generate" in NotebookLM Studio to produce a compelling, natural two-host podcast or deep-dive briefing on ClearStreak.

---

## 🎙️ Custom Prompt to Paste into NotebookLM "Customize Audio Overview"

```text
Focus on how ClearStreak redefines habit and streak tracking for ANY personal journey — both "Days Doing" a positive daily discipline (like morning workouts, deep work, fasting, or prayer) AND "Days Not Doing" a habit or vice you want to leave behind (like doomscrolling, sugar, vaping, alcohol, or impulse spending). Highlight three big breakthroughs:
1. "Data Over Shame": Why wiping a user's streak to zero after one missed day is psychologically destructive (the Abstinence Violation Effect), and how ClearStreak preserves your Lifetime Days, Personal Bests, and Milestone Coins forever even when today's counter resets.
2. "Private by Architecture": Why intimate daily habits and struggles should never live on a startup's cloud server, and how ClearStreak runs 100% offline with hardware-bound AES-256 encryption, biometric unlock, and anti-screenshot protection.
3. "Eyes-Free Grounding & Fair Ownership": How the Tactile Pocket Anchor and 4x4 Haptic Breather let you ride out restlessness in your pocket without staring at a screen, backed by a 7-day free trial and a single one-time lifetime unlock instead of a $60–$120/year subscription trap.
```

---

## 1. The Core Premise: One Private Companion for *Any* Journey

Most people are working on two kinds of personal growth at the exact same time:
1. **Streaks of Days DOING Something (Building):** Showing up for a morning run, reading 20 pages, practicing deep work, intermittent fasting, daily prayer/meditation, or completing a 30-day physical challenge.
2. **Streaks of Days NOT DOING Something (Breaking):** Stepping away from late-night doomscrolling, sugar, vaping, alcohol, unplanned online shopping, or screen compulsion.

Yet the app store forces people into an artificial split: either download a noisy, gamified "productivity checklist" that sells your behavioral telemetry to ad networks, or download a clinical "sobriety app" that demands a cloud account, charges $40 to $120 a year in recurring subscriptions, and shames you the moment you have an off day.

**ClearStreak** (`https://864zeros.com/products/clearstreak`), built by **864zeros**, unifies both directions into a single, dignified, **100% offline mobile companion** that lives entirely on your phone.

---

## 2. Pillar 1: "Data Over Shame" vs. The Streak-Zero Trap

### The Problem: The Abstinence Violation Effect
In behavioral psychology, there is a well-documented phenomenon called the **Abstinence Violation Effect (AVE)**. When a person builds a 45-day streak — whether that's 45 days of consistent workouts or 45 days without vaping — and has a single off day, traditional habit trackers wipe their big hero number back to a glaring, red **`0`**.
- Psychologically, the brain reads `0` as: *"All 45 days of effort were just erased. I failed, so today doesn't matter anymore."*
- Instead of encouraging consistency, the streak-zero wipe triggers an all-or-nothing spiral.

### How ClearStreak Solves It: The Permanent Ledger
ClearStreak is built on **Data Over Shame**:
- **Today's Counter vs. Lifetime Ledger:** If you have an off day, only your *current active run* resets to Day 1. Your **Cumulative Lifetime Days**, your **Longest Personal Best Stretch**, your **Total Money Saved ($)**, and your **Ceremonial Milestone Coins** (`24 Hours`, `7 Days`, `30 Days`, `90 Days`, `1 Year`) are **permanently preserved**.
- **Immediate Contextual Encouragement:** When a reset is logged, ClearStreak never uses words like *"failed"*, *"broken"*, or *"lost"*. Instead, its ledger calculates: *"Your record is 45 days. You have 112 lifetime days banked, and you are already on Day 1 toward beating your record."*

---

## 3. Pillar 2: Private by Architecture (If It Isn't on Your Phone, It Doesn't Exist)

When you track the habits you are trying to build or the vices you are privately trying to break, you are recording the most intimate timestamps of your life: when you feel stressed, when you feel lonely, what triggers you at 11:30 PM, and what you write in your private reflection journal.

In recent years, major venture-backed wellness and recovery apps have been caught sharing user habit and recovery data with third-party advertising trackers or suffering cloud database breaches.

### ClearStreak's Zero-Cloud Sovereignty
- **Zero Accounts, Zero Servers:** You never enter an email address, phone number, or name. 864zeros operates zero user databases.
- **Hardware-Bound AES-256 Encryption (`SQLCipher`):** Your check-ins and journal reflections are encrypted on-device using SQLCipher AES-256. The decryption key is bound directly to your phone's secure hardware (`Android StrongBox / Trusted Execution Environment`) and unlocked only by your **Fingerprint, Face, or Device PIN**.
- **`FLAG_SECURE` Visual Privacy:** ClearStreak blocks screenshots, blocks screen recordings, and masks the app window in your phone's Recent Apps switcher so someone glancing over your shoulder never sees your private dashboard.

---

## 4. Pillar 3: Eyes-Free Somatosensory Reset (The "Pocket Anchor")

When a wave of restlessness, distraction, or craving hits — whether you're tempted to doomscroll during a meeting or break a dietary/habit streak — the last thing you need is a wall of preachy text advice on a bright screen.

ClearStreak replaces text lectures with **somatosensory haptics and working-memory disruption**:
1. **The Tactile Pocket Anchor (1–60 Minutes):** Activate a timed grounding session and rest your hand on your phone (or hold it at your side). ClearStreak delivers a calm, rhythmic dual-pulse vibration every 60 seconds (micro-time-chunking) so your nervous system feels time passing safely without looking at the screen.
2. **4×4×4×4 Haptic Box Breather & 4-7-8 Breathing Circle:** Uses smooth haptic intensity ramps on the inhale, subtle 1-second micro-ticks on the hold, and a decaying wave on the exhale — allowing completely eyes-free, silent-mode breath pacing.
3. **3 Offline Visuospatial Mini-Games (`Tile Merge 2048`, `Block Drop`, `Pattern Echo`):** Grounded in **Elaborated Intrusion Theory**, 3 to 5 minutes of spatial working-memory engagement occupies the exact visual bandwidth the brain uses to loop on a craving or distraction. Built natively in Jetpack Compose Canvas with zero ads, zero gambling mechanics, and a gentle 3-minute check-in banner.
4. **Offline Reflect Vault:** An optional, 100% offline library containing **365 emotion-tagged KJV Scripture verses**, **130 original reflection passages**, and **100 daily affirmations**.
5. **Always-Free One-Tap Rescue Hub:** If a moment ever becomes overwhelming, a single tap opens a calm, high-contrast Rescue screen putting your personal ally/sponsor and confidential national lifelines (`988`, `SAMHSA`, `Crisis Text Line`) one tap away via native `tel://` dialers. **Ethical Line:** The Rescue Hub is 100% free forever and never sits behind a paywall.

---

## 5. Pillar 4: Anti-SaaS Fair Ownership

- **The Incumbent Subscription Trap:** Competing habit and sobriety apps charge **$39.99/year to $119.99/year** forever just to increment an integer on your screen.
- **The 864zeros Model:** ClearStreak gives you a **7-day full-featured free trial** (no credit card required upfront), followed by a single **one-time lifetime unlock**. Pay once, own it on your device forever.

---

## 6. Quick Fact Sheet for Hosts & Reviewers

- **Product Name:** ClearStreak — The Private Habit, Streak & Journey Companion
- **Creator:** 864zeros LLC (`https://864zeros.com/products/clearstreak`)
- **Platform:** Android (`com.eight64zeros.clearstreak`, Jetpack Compose + SQLCipher AES-256 + Android Keystore StrongBox)
- **Use Cases:** Any Journey — **Streak Doing** (fitness, deep work, fasting, prayer, reading) + **Days Not Doing** (doomscrolling, vaping, alcohol, sugar, late-night spending)
- **Pricing:** 7-Day Free Trial → One-Time Lifetime Unlock ($0/month recurring; Rescue Hub always 100% free)
