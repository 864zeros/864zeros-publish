# ClearStreak — Literature Mining Style Guide (READ FULLY BEFORE WRITING)

You are modernizing public-domain 1939 recovery text into help content for a 2026 mobile app used by people in active recovery, often in crisis. Your output helps vulnerable people. Precision and tone matter more than speed.

## Mission
From your assigned chapter's source paragraphs, mine the passages that carry a **durable, transferable insight, technique, hope, or self-recognition** and produce a modernized "passage" object for each. Skip pure narrative/biographical/transitional filler that offers no help value.

## THE THREE HARD RULES (never violate)
1. **Fidelity over brevity.** NEVER abbreviate or compress the message to save space. Preserve the FULL meaning. `reading_time` is metadata only, never a reason to trim.
2. **12 Steps are untouchable.** If your source file has a `no_touch` range (paragraph_index start..end), those paragraphs are the Twelve Steps. NEVER mine, reword, quote, or label them. Skip them entirely.
3. **Technique-only framework + optional faith.** Map AA doctrine into our own framework (table below). Do NOT preach. Never make faith mandatory — faith content goes ONLY in the `faith_optional` field, shown only if the user enables faith mode.

## Doctrine → our framework (re-map, do not delete)
| Source doctrine | Re-map to |
|---|---|
| powerless over alcohol | "you can't out-willpower a craving in the moment — but you can outlast it" |
| allergy / disease | "it's wiring, not willpower; one use flips a craving switch" |
| life unmanageable | "when it runs the show, life gets unmanageable — that's data, not shame" |
| Higher Power / God | "something bigger than the urge" (people, values, future self) → and the God-specific line goes to `faith_optional` |
| moral inventory | "honest self-review, written down" (expressive writing) |
| character defects / sin | "patterns that don't serve you" |
| confession | "saying it out loud to one person drains its power" |
| amends | "repair" |
| spiritual malady | "the restless, never-enough feeling" |

Remove moralizing words entirely: sin, defect, insanity, moral failure, broken. Gender-neutral throughout (no he/him default, no "wives"). No "you must."

## The TWO renderings (both preserve the full message — neither abbreviates)
- **`reader_text` — light touch.** Keep the 1939 voice and cadence. Change ONLY: gendered defaults, genuinely dated words (e.g. "pocketbook"→"security"), and doctrine (re-mapped per table). Faith-specific lines move to `faith_optional`. This is what a user reads in the book reader.
- **`surface_text` — re-voiced.** Same complete meaning and arc, rewritten in warm, plain, grounded 2026 language (~grade 6–8, second person "you"). This is what surfaces in a moment of need. Warm but not flippant; this person may be in pain.

## applies_to (multi-journey)
The app tracks alcohol, drugs, vape, gambling, behavioral journeys.
- If the message is substance-agnostic (resentment, fear, hope, honesty), set `applies_to: ["UNIVERSAL"]` and make `surface_text` say "use / act on the urge" rather than "drink."
- If the wording is inherently alcohol-specific, set `applies_to: ["ALCOHOL"]`.

## Allowed label values (use EXACTLY these strings)
- `moment` (>=1): starting-out, is-this-me, craving-now, after-a-slip, doubt-higher-power, resentment, fear, lonely, family-strain, work-strain, helping-others, staying-the-course
- `halt` (exactly 1): HUNGRY, ANGRY, LONELY, TIRED, STRESSED, HOPELESS, GENERAL
- `urge_level` (exactly 1): CLEAR, PASSING, WHITE_KNUCKLING, CRITICAL
- `stage` (exactly 1): contemplation, decision, action, maintenance, relapse-recovery
- `function` (exactly 1): foundational, instructional, identification, relational, spiritual
- `applies_to`: array from [UNIVERSAL, ALCOHOL, DRUGS, VAPE, GAMBLING, BEHAVIORAL, CUSTOM]
- `reading_time`: quick | medium | long  (quick = <=~15 sentences; metadata only)

## TIER 2 chapters (ch08 To Wives, ch09 The Family Afterward, ch10 To Employers)
These are the most dated (third-party framing, 1939 gender roles). Mine SELECTIVELY — only the few genuinely universal nuggets (family-strain, work-strain moments). Recast third-party framing to speak to the person in recovery directly. Expect only ~2–4 passages per chapter, not full coverage.

## Provenance (must be exact — do not invent)
For each passage, copy `paragraph_index` = the source paragraph's `i`, and `page` = the source paragraph's `page`. `quote_stub` = the first ~48 characters of the ORIGINAL source `text`, verbatim.

## OUTPUT
Write a JSON array (only) to `C:\dev\864zeros-publish\_build\_src\out_<chapter_id>.json`, and return a one-line summary (chapter_id + passage count). Each element:
```json
{
  "id": "lit_<chapter_id>_<n>",
  "reader_text": "…full light-touch message…",
  "surface_text": "…full re-voiced message…",
  "faith_optional": "…opt-in faith line, or null…",
  "labels": { "moment": ["…"], "halt": "…", "urge_level": "…", "stage": "…", "function": "…" },
  "applies_to": ["…"],
  "framework_map": "which doctrine you re-mapped, or 'none'",
  "reading_time": "quick|medium|long",
  "source": {
    "book": "AA-1939",
    "chapter_id": "<id>",
    "chapter_title": "<title from source file>",
    "page": <int>,
    "paragraph_index": <int>,
    "quote_stub": "first ~48 chars of original text"
  },
  "needs_clinical_review": true
}
```

---

## GOLD STANDARD — three approved passages (match this quality and voice exactly)

### Gold A — Doctor's Opinion, p.5, para#24 — craving-now / is-this-me
- reader_text: "People drink, essentially, because they like the effect produced by alcohol. The sensation is so elusive that, while they admit it is injurious, after a time they cannot tell the true from the false. To them, their drinking life seems the only normal one. They are restless, irritable and discontented unless they can again feel the sense of ease and comfort that comes at once from a few drinks — drinks they see others take with no consequence. Having given in to the craving again, as so many do, they pass through the familiar stages of a binge, emerging remorseful, with a firm resolve never to drink again. This is repeated over and over, and unless the person can undergo an entire inner change there is very little hope of their recovery."
- surface_text: "Here's the trap, in plain terms: you drink because you like how it feels — that fast sense of ease and comfort. The problem is the feeling is slippery. Even knowing it's hurting you, after a while you can't tell what's true anymore, and this life starts to look like the only normal one. So you're restless, on edge, never quite settled until the next few drinks — the same drinks you watch other people have with no fallout. You give in, the craving takes over, and you ride out the binge only to come out the other side full of regret, swearing it off for good. Then it happens again. And again. This isn't weak character — it's a real switch that flips once alcohol is in you. Breaking the loop takes an actual inner change, not just another promise to yourself."
- faith_optional: null
- framework_map: "allergy/disease → 'a real switch that flips'; removes moral-weakness framing"
- labels: moment=[is-this-me, craving-now], halt=GENERAL, urge_level=WHITE_KNUCKLING, stage=contemplation, function=foundational

### Gold B — How It Works, p.76, para#36 — resentment (HALT Angry)
- reader_text: "Resentment is the “number one” offender. It destroys more people in recovery than almost anything else. Left alone, it keeps you locked in the anger that feeds the urge — you stay off-balance, mentally and physically, until it is dealt with. So we deal with it on paper. We list the people, institutions, or principles we are angry at. We ask ourselves why we are angry. In most cases we find that our self-respect, our security, our ambitions, or our relationships were hurt or threatened. So we were sore. We were “burned up.”"
- surface_text: "Anger is the single biggest thing that talks people back into using — it convinces you that you're owed a drink. And it doesn't stay put; it circles in your head and keeps you on edge until you deal with it. So deal with it on paper. Write down who or what you're angry at — people, institutions, even ideas. Then write down why. Be honest: most of the time it's because something you care about got hurt or threatened — your self-respect, your sense of security, your ambitions, your relationships. That's what's really going on underneath the anger. Getting it out of your head and onto the page drains the pressure that pushes you toward a drink."
- faith_optional: null
- framework_map: "'spiritual disease/malady' → 'anger that feeds the urge'; moral-inventory → expressive writing (technique kept intact)"
- labels: moment=[resentment], halt=ANGRY, urge_level=WHITE_KNUCKLING, stage=action, function=instructional

### Gold C — Into Action, p.96, para#36 — the Promises (hopelessness / after-a-slip)
- reader_text: "If we are painstaking about this phase of our development, we will be amazed before we are half through. We are going to know a new freedom and a new happiness. We will not regret the past nor wish to shut the door on it. We will comprehend the word serenity and we will know peace. No matter how far down the scale we have gone, we will see how our experience can benefit others. That feeling of uselessness and self-pity will disappear. We will lose interest in selfish things and gain interest in our fellows. Self-seeking will slip away. Our whole attitude and outlook upon life will change. Fear of people and of economic insecurity will leave us. We will intuitively know how to handle situations which used to baffle us. We will suddenly realize that we are doing for ourselves what we never could alone."
- surface_text: "If you keep at this, honestly, you'll be amazed before you're even halfway. Here's what people describe: a new kind of freedom, and an actual happiness. You stop regretting the past — and you stop wanting to slam the door on it. You start to understand what serenity means, and you feel real peace. No matter how far down you went, you'll see how even that can help someone else. The uselessness and self-pity fade. You get out of your own head and start caring about other people. The constant self-focus loosens its grip. Your whole outlook shifts. The fear of people, and of not having enough, eases off. You start handling situations that used to floor you, almost without thinking. One day you realize you're doing for yourself what you never could on your own."
- faith_optional: "For many people this is the moment they realize it was never just willpower — that a power greater than themselves was doing for them what they couldn't do alone."
- framework_map: "closing 'God is doing for us' → moved to faith_optional; the Promises themselves kept universal"
- labels: moment=[hopelessness→use HOPELESS halt; moments after-a-slip, staying-the-course], halt=HOPELESS, urge_level=PASSING, stage=maintenance, function=identification
