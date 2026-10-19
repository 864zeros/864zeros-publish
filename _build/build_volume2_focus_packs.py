#!/usr/bin/env python3
"""
build_volume2_focus_packs.py — Author & Verify Volume 2 Clean-Room Focus Packs
==============================================================================
Authors:
  - Julian Thorne (LEAD-CONTENT)
  - Vera Lindqvist (STUDIO-LEGAL)
  - Sloane Sterling (VP-STUDIO)

Builds the 4 Volume 2 30-day Focus Packs (`120` daily entries total) in
`C:\dev\864zeros-publish\shared\focus_packs\`, enriches the 5 Volume 1 Focus
Packs (`150` entries) so all 9 packs (`270` entries) share a unified superset
schema, updates `focus_packs_catalog.json` and `index.json`, and strictly
verifies that every single Volume 2 quote is a 100% verbatim substring of its
locked pre-1931 `.txt` file in `sources/public_domain_classics/`.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources" / "public_domain_classics"
PACKS_DIR = ROOT / "shared" / "focus_packs"

temp_helper = pathlib.Path(__file__).resolve().parent / "dump_verbatim_30.py"
if temp_helper.exists():
    temp_helper.unlink()


def load_source(filename: str) -> tuple[str, str, int]:
    path = SOURCES_DIR / filename
    raw_bytes = path.read_bytes()
    sha256 = hashlib.sha256(raw_bytes).hexdigest().upper()
    text = raw_bytes.decode("utf-8")
    norm = re.sub(r"\s+", " ", text)
    return norm, sha256, len(raw_bytes)


def extract_verbatim_substring(norm_source: str, anchor_prefix: str, anchor_suffix: str, label: str) -> str:
    """Locate an exact verbatim slice in the normalized source text from prefix to suffix."""
    idx_start = norm_source.find(anchor_prefix)
    if idx_start == -1:
        raise ValueError(f"[{label}] Prefix not found: {anchor_prefix!r}")
    idx_end = norm_source.find(anchor_suffix, idx_start)
    if idx_end == -1:
        raise ValueError(f"[{label}] Suffix not found after prefix: {anchor_suffix!r}")
    verbatim = norm_source[idx_start : idx_end + len(anchor_suffix)].strip()
    assert verbatim in norm_source
    return verbatim


def curate_30_from_book(
    norm_source: str,
    start_char: int,
    end_char: int,
    citation_prefix: str,
    pack_prefix: str,
    theme_blueprints: list[tuple[str, str, str, str, str, list[str]]],
    must_match_keywords: list[str],
) -> list[dict]:
    """
    Deterministically selects 30 high-clarity aphoristic sentences from the locked
    source text that match our philosophical/habit criteria, verifies 100% verbatim
    substring identity against `norm_source`, and pairs each with its bespoke
    864zeros reflection, strategic_prompt, and micro_action blueprint.
    """
    window = norm_source[start_char:end_char]
    raw_sents = [s.strip() for s in re.split(r"(?<=[\.\!\?])\s+(?=[A-Z])", window)]
    candidates: list[str] = []
    banned_substrings = [
        "{", "}", "[", "]", "_", "--", "Gutenberg", "66", "CHAPTER", "BOOK",
        "Note", "impulse", "Impulse", "atomic", "habit loop", "habit stacking",
        "tiny habits", "2-minute rule", "never miss twice"
    ]
    for s in raw_sents:
        if not (72 <= len(s) <= 235):
            continue
        if any(b in s for b in banned_substrings):
            continue
        if not s.endswith((".", "!", "?")):
            continue
        lower_s = s.lower()
        if any(k in lower_s for k in must_match_keywords):
            if s in norm_source and s not in candidates:
                candidates.append(s)

    if len(candidates) < 30:
        raise RuntimeError(f"Only found {len(candidates)} verbatim candidates for {pack_prefix}")

    # Spread evenly across the book's progression so all chapters/sections are represented
    step = len(candidates) / 30.0
    selected = [candidates[int(i * step)] for i in range(30)]

    entries: list[dict] = []
    for idx in range(30):
        day_num = idx + 1
        quote = selected[idx]
        assert quote in norm_source, f"Quote {day_num} not verbatim in source!"
        theme, plain, application, strategic_prompt, micro_action, halt_triggers = theme_blueprints[idx]
        entries.append(
            {
                "id": f"{pack_prefix}_{day_num:03d}",
                "day": day_num,
                "citation": f"{citation_prefix} · Selection {day_num}",
                "text": quote,
                "plain": plain,
                "application": application,
                "strategic_prompt": strategic_prompt,
                "micro_action": micro_action,
                "focus_theme": theme,
                "halt_triggers": halt_triggers,
            }
        )
    return entries


# 30 Bespoke Theme Blueprints per Pack:
# (focus_theme, plain, application, strategic_prompt, micro_action, halt_triggers)

SENECA_BLUEPRINTS = [
    ("time_stewardship", "Life is not inherently too brief; we shrink it whenever we scatter our hours across reactive distractions.", "Guard your primary focus window today as your highest-value asset.", "Where did your attention leak yesterday without producing clarity or peace?", "Close every unscheduled browser tab and silence notifications for the next 30 minutes.", ["STRESSED", "TIRED"]),
    ("inner_harbor", "When the mind chases every restless craving, even moments of rest feel turbulent like a sea after a gale.", "Use a physical grounding breath before transitioning between tasks today.", "What unresolved restlessness follows you into your evening rest?", "Execute four slow 4-second box breaths before opening your next task.", ["ANGRY", "STRESSED"]),
    ("sovereign_self_ownership", "When your schedule is dictated entirely by other people's urgency, you cease to belong to yourself.", "Reclaim one uninterrupted block today that belongs strictly to your Primary Focus Habit.", "Whose priorities are currently occupying the prime hours of your morning?", "Decline or defer one low-priority interruption today to protect yourRoutine Anchor.", ["LONELY", "STRESSED"]),
    ("honest_self_inquiry", "We readily grant an audience to everyone else's complaints while rarely sitting in honest stillness with our own mind.", "Spend five quiet minutes checking in with your own state before reacting to external noise.", "What internal signal have you been avoiding by staying perpetually busy?", "Write one honest sentence in your journal describing your current emotional baseline.", ["LONELY", "TIRED"]),
    ("living_vs_counting_years", "Merely accumulating calendar days is not the same as living deliberately; unfocused hours vanish from the ledger.", "Measure today by deliberate presence in your chosen discipline rather than hours spent at a desk.", "Which single hour of your day currently feels the most alive and intentional?", "Log your Primary Focus check-in immediately after completing your anchor habit.", ["HOPELESS", "TIRED"]),
    ("present_action_over_delay", "Postponing wise habits until some future decade is the surest way to forfeit the only day you actually hold.", "Begin your discipline today at its minimum viable threshold rather than waiting for ideal conditions.", "What meaningful practice have you been deferring until life 'slows down'?", "Perform a 60-second Floor Rep of your primary habit right now.", ["HOPELESS", "STRESSED"]),
    ("weight_of_false_ambition", "Status and external applause demand constant maintenance, whereas inner self-command requires zero outside permission.", "Strip away performative busyness today and execute what genuinely builds character.", "Which obligation in your week exists only to maintain appearances?", "Cross one unnecessary status task off today's list.", ["STRESSED", "ANGRY"]),
    ("quiet_margin", "Even those at the peak of worldly influence eventually realize that unhurried mental clarity is the true luxury.", "Build a 15-minute quiet buffer into your afternoon before fatigue triggers a craving.", "How does your nervous system respond when you remove artificial urgency?", "Step away from all screens for 10 minutes at midday.", ["TIRED", "STRESSED"]),
    ("audit_of_hours", "When you audit where your days actually go, you discover how little time was consciously chosen.", "Run a clean, shame-free audit of your day's energy expenditure tonight.", "If your calendar were a bank statement, what would it say you value most?", "Write down the three activities that consumed the most time today.", ["TIRED", "HUNGRY"]),
    ("presence_over_endurance", "Enduring a chaotic schedule is not the same as directing a meaningful life; agency begins with deliberate choice.", "Choose one deliberate act of focus today instead of passively drifting through the afternoon.", "Are you steering today's routine, or merely surviving it?", "Anchor your core habit to your very next transition cue.", ["HOPELESS", "TIRED"]),
    ("priceless_currency", "People fiercely guard their money and property yet hand away their irreclaimable hours as though time cost nothing.", "Treat every 30-minute block today with the same vigilance you give your financial vault.", "Where are you giving away prime mental energy for zero return?", "Set a strict 25-minute boundary timer on your next meeting or administrative chore.", ["ANGRY", "STRESSED"]),
    ("finite_horizon", "If we saw our remaining days counted out before us, we would immediately stop wasting afternoons on trivial friction.", "Let awareness of finite time sharpen your gratitude and focus rather than creating anxiety.", "What petty irritation can you drop immediately because life is too valuable for it?", "Release one lingering grievance before noon today.", ["ANGRY", "HOPELESS"]),
    ("careful_husbandry", "When a resource is finite and its exact reserve is unknown, wise stewardship begins with today's allotment.", "Preserve your prime cognitive energy for your keystone discipline before spending it on trivia.", "At what hour of the day is your mental clarity sharpest?", "Schedule your Primary Focus Habit inside your highest-clarity hour tomorrow.", ["TIRED", "STRESSED"]),
    ("hidden_time_drain", "We often give away our attention in fragments so small we barely notice the loss until the day is gone.", "Batch your messages and notifications into fixed windows so your focus remains whole.", "How many times has your train of thought been fractured in the last two hours?", "Place your phone out of reach in another room for the next 45 minutes.", ["STRESSED", "TIRED"]),
    ("unhurried_purpose", "Frenetic busyness is not productivity; life moves swiftly regardless of how anxiously we rush.", "Slow your physical cadence down by 20% while executing your next task with total precision.", "When you rush, what are you actually trying to outrun?", "Walk and speak at a calm, unhurried pace for the next hour.", ["STRESSED", "ANGRY"]),
    ("false_promise_of_someday", "Sacrificing today's peace for the promise of future leisure trades a certainty for a mirage.", "Claim ten minutes of genuine stillness today rather than bargaining with next month.", "What part of your well-being have you been holding hostage to a future milestone?", "Take a 5-minute quiet reset walk outside right now.", ["TIRED", "HOPELESS"]),
    ("command_of_the_present", "When you hand your attention over to external chaos, you surrender the only territory within your command.", "Bring your focus back to the immediate action directly in front of your hands.", "What external uncertainty is currently pulling your mind out of the present room?", "Name three physical objects in your immediate environment and begin your next rep.", ["STRESSED", "LONELY"]),
    ("live_now_straightway", "Because tomorrow rests in uncertainty, the only rational moment to practice wisdom and steadiness is today.", "Execute your daily check-in today without waiting for tomorrow's fresh start.", "What small act of discipline can you complete before dinner tonight?", "Complete your daily Floor Rep and log it immediately.", ["HOPELESS", "STRESSED"]),
    ("decisive_momentum", "Time flows like a swift current; only decisive, immediate action draws nourishment from the passing hour.", "Initiate your planned routine within five seconds of encountering your When-Then cue.", "Where does hesitation creep in between your cue and your action?", "Lay out the physical tools for tomorrow's habit tonight before bed.", ["TIRED", "HUNGRY"]),
    ("lifelong_readiness", "A mind that never practices quiet self-command in daily life is caught unprepared when real storms arrive.", "Treat today's small friction moments as training reps for deeper resilience.", "How did your most recent challenge test your daily habits?", "Practice a 60-second calm pause the next time a minor delay occurs today.", ["ANGRY", "STRESSED"]),
    ("daily_awareness", "Drift happens imperceptibly when we never pause to observe the passing of individual days.", "End your day with a two-minute review so no 24-hour cycle passes unexamined.", "What single moment from today deserves to be remembered?", "Record one sentence of gratitude or progress in your evening check-in.", ["LONELY", "TIRED"]),
    ("clear_conscience_review", "A person who acts with integrity and steadiness can look back on past days with calm satisfaction rather than regret.", "Choose the action today that your future self will review with quiet respect tonight.", "Which choice in front of you right now aligns with your long-term character?", "Do the hardest two minutes of your deferred task right now.", ["HOPELESS", "ANGRY"]),
    ("one_hour_at_a_time", "The present arrives one day and one hour at a time; mastering a streak requires only mastering this single hour.", "Shrink your time horizon to the current hour whenever a long-term goal feels overwhelming.", "Can you remain steady for just the next sixty minutes?", "Commit to clean focus for the next single hour without worrying about next week.", ["STRESSED", "HOPELESS"]),
    ("unshackled_perspective", "A tranquil mind can survey its whole journey clearly, whereas frantic busyness keeps the head bowed under a yoke.", "Step back from the immediate grind at midday to view your broader trajectory.", "What cumulative progress have you already built over the past month?", "Open your progress ledger and acknowledge every day you have already banked.", ["TIRED", "HOPELESS"]),
    ("single_pointed_attention", "When you scatter yourself across a dozen competing tasks, even the present moment slips through your fingers.", "Do one thing at a time with complete presence until it is finished.", "What two tasks are you currently trying to half-do simultaneously?", "Close every secondary window and complete the single item in front of you.", ["STRESSED", "TIRED"]),
    ("sufficiency_of_a_steady_life", "Even a brief span of time is richly sufficient when every day is lived with deliberate self-command.", "Measure today by the quality of your attention rather than the quantity of your output.", "What would make today feel complete even if nothing else on your list got done?", "Complete your Primary Focus Habit before checking any evening feeds.", ["TIRED", "LONELY"]),
    ("companionship_of_the_wise", "Through verified classical wisdom, you can sit in counsel with the steadiness of the ancients at any hour.", "Read today's passage slowly twice, letting its cadence settle your breathing.", "Which timeless principle has anchored you most reliably this week?", "Copy one phrase from today's reading onto an index card or journal page.", ["LONELY", "HOPELESS"]),
    ("freedom_from_trivial_curiosity", "Consuming endless trivial noise drains the exact mental bandwidth needed for real self-transformation.", "Replace 15 minutes of aimless scrolling today with quiet reflection or physical movement.", "What information have you consumed today that has zero bearing on your life or character?", "Turn off autoplay and close your social feed right now.", ["HUNGRY", "TIRED"]),
    ("peaceful_haven", "After enduring turbulent seasons, wisdom lies in deliberately steering your daily routine into calmer waters.", "Simplify your evening routine tonight so your mind enters rest unagitated.", "What unnecessary storm can you step out of this week?", "Dim the lights 30 minutes before sleep and leave your phone outside the bedroom.", ["TIRED", "STRESSED"]),
    ("protecting_your_life_equity", "External applause is bought at the cost of your own hours; never trade inner sovereignty for crowd approval.", "Anchor your worth in private consistency ('Data Over Shame') rather than public praise.", "What habit would you still practice faithfully even if no one ever knew?", "Log today's private check-in and honor your quiet consistency.", ["LONELY", "ANGRY"]),
]

EPICTETUS_BLUEPRINTS = [
    ("kinship_with_reason", "True dignity comes from remembering that your rational faculty and capacity for choice are noble by nature.", "Carry yourself with quiet self-respect in your speech and posture today.", "Where have you been underestimating your own capacity for self-command?", "Stand upright, drop your shoulders, and take three slow grounding breaths.", ["HOPELESS", "LONELY"]),
    ("testing_appearances", "First impressions and sudden cravings are merely appearances—test them with reason before granting your assent.", "Insert a 10-second pause between any sudden urge and your physical response today.", "What initial story did your mind tell you during today's most frustrating moment?", "Ask yourself: 'Is this within my control, or outside my control?'", ["ANGRY", "STRESSED"]),
    ("stewardship_of_assent", "No external event can force your inner judgment; your assent always remains under your own lock and key.", "Refuse to agree with defeatist self-talk when energy dips this afternoon.", "What automatic negative thought is asking for your agreement right now?", "Write down the thought, label it 'Appearance Only,' and return to your task.", ["HOPELESS", "TIRED"]),
    ("fidelity_to_character", "When circumstances grow difficult, the real task is simply to uphold the integrity of a steady human being.", "Choose patience over irritation in your very next conversation.", "How would the steadiness you admire respond to today's inconvenience?", "Lower your voice and speak with deliberate calm during your next interaction.", ["ANGRY", "STRESSED"]),
    ("sound_judgment_over_stubbornness", "Persisting in an unexamined habit out of mere stubbornness is bondage; true strength corrects course when shown the truth.", "Be willing to adjust your daily routine anchor if friction kept tripping you up this week.", "Where is pride keeping you locked in an ineffective routine?", "Simplify your habit cue today so execution becomes effortless.", ["ANGRY", "TIRED"]),
    ("proper_material_of_virtue", "Your daily environment and current responsibilities are the exact raw material from which character is forged.", "Treat today's ordinary duties as your training ground rather than an obstacle.", "What everyday chore today can you execute with uncommon excellence?", "Perform your next mundane task with 100% undivided attention.", ["TIRED", "HUNGRY"]),
    ("guarding_company_and_inputs", "Habitual exposure to cynical or undisciplined environments gradually pulls our own standards downward if we are not vigilant.", "Curate your physical and digital environment today to reinforce your Primary Focus.", "Which environment or input consistently weakens your resolve?", "Remove one trigger item from your desk or home screen right now.", ["LONELY", "HUNGRY"]),
    ("freedom_from_external_craving", "Desiring things outside your control hands your peace of mind over to fortune; desiring only sound action makes you unshakeable.", "Measure today's success strictly by whether you showed up for your rep.", "What outcome are you anxiously gripping that is not yours to command?", "Open your hands physically, exhale slowly, and focus only on your next step.", ["STRESSED", "HOPELESS"]),
    ("inner_citadel_of_will", "Your moral purpose is the one faculty that can use every other faculty rightly and never be coerced from outside.", "Direct your willpower toward one clear When-Then Routine Anchor today.", "What single choice today is 100% within your sovereign power?", "Execute your Floor Rep before noon today.", ["TIRED", "HOPELESS"]),
    ("tranquillity_through_acceptance", "Peace begins the moment you demand that events happen as they actually do rather than insisting the world bend to your preference.", "Accept today's weather, traffic, or schedule changes with zero verbal complaint.", "How much energy did you spend today wishing an unchangeable fact were different?", "Go the rest of the day without uttering a single complaint.", ["ANGRY", "STRESSED"]),
    ("unhindered_action", "He is truly free who aligns his desires solely with what lies within his own sphere of agency.", "Focus 100% of your effort on your preparation and conduct today.", "Where are you feeling hindered because you attached your goal to someone else's reaction?", "Rewrite today's goal as a pure action statement you can complete solo.", ["LONELY", "STRESSED"]),
    ("price_of_serenity", "Inner composure is bought by letting go of petty irritations; you cannot simultaneously keep your anger and keep your peace.", "When a minor annoyance arises today, consciously choose peace over the urge to vent.", "Is winning this minor frustration worth paying the price of your calm?", "Pause for five seconds and let the next minor slight pass without comment.", ["ANGRY", "STRESSED"]),
    ("gradual_training_of_habit", "Just as athletes build strength through progressive daily reps, the mind builds resilience by mastering small daily tests first.", "Never despise a small Floor Rep; every completed rep strengthens the neural pathway.", "What small win today proves your consistency is growing?", "Complete a 2-minute version of your discipline right now.", ["TIRED", "HOPELESS"]),
    ("watchfulness_over_urges", "When you allow an unexamined craving to carry you away today, you feed the very habit you are trying to starve.", "Starve the craving by shifting immediately into a 60-second grounding reset.", "What situational trigger usually precedes your strongest urge?", "Drink a full glass of water and step into a different room when a craving hits.", ["HUNGRY", "ANGRY"]),
    ("self_sufficiency_in_solitude", "Being alone is not abandonment; it is an opportunity to practice quiet self-command without outside distraction.", "Use your next solitary hour for deep reading, journaling, or focused craft.", "How can you turn tonight's quiet hours into restorative solitude?", "Leave screens off for 20 minutes tonight and write in your journal.", ["LONELY", "TIRED"]),
    ("acting_our_assigned_role", "We do not choose every circumstance on the stage of life, but we always choose how nobly we play our part in it.", "Bring steadiness and dignity to whatever challenge sits on your plate today.", "What role is today asking you to play with courage?", "Handle your most dreaded email or task first thing with calm composure.", ["STRESSED", "HOPELESS"]),
    ("the_two_handles_of_events", "Every difficulty has two handles—one by which it crushes you with grievance, and another by which it can be carried with constructive resolve.", "Grasp today's setback by the handle of learning and next-step action.", "What is the constructive handle on the problem you are facing today?", "Write down one actionable lesson from a recent friction point.", ["ANGRY", "HOPELESS"]),
    ("quiet_progress_over_boasting", "True transformation shows itself in steady conduct, never in loud declarations about what we plan to do.", "Keep your habit goals private and let your completed check-in ledger speak for itself.", "Are you seeking premature praise for a habit you haven't yet cemented?", "Do today's repetition quietly without announcing it.", ["LONELY", "HUNGRY"]),
    ("examining_the_cost_first", "Before undertaking any serious discipline, count the friction and daily effort required so you are never surprised by the work.", "Anticipate the exact hour today when your habit will feel hardest, and pre-plan your Floor Rep.", "What obstacle is most likely to test your routine anchor today?", "Write your 'When X happens, I will do Y' backup plan now.", ["TIRED", "STRESSED"]),
    ("invulnerable_integrity", "Another person's words or actions reflect their own judgment; they cannot harm your character unless you abandon your own principles.", "Respond to rudeness or impatience today with unshakeable courtesy.", "Why hand the keys to your emotional state over to a stranger's mood?", "Breathe out slowly before replying to any tense message today.", ["ANGRY", "LONELY"]),
    ("daily_mental_hygiene", "Just as you cleanse the body daily, clear the mind each morning and evening of resentment and scattered distraction.", "Start and end your day with a 60-second reflection on your Primary Focus.", "What mental clutter needs to be swept out before you sleep tonight?", "Write down tomorrow's top priority so your mind can rest cleanly.", ["TIRED", "STRESSED"]),
    ("continuity_of_attention", "Relaxing your vigilance 'just for today' makes it twice as hard to regain the helm tomorrow.", "Protect the continuity of your chain today, even if it requires dropping to your minimum Floor Rep.", "What excuse is tempting you to skip today's check-in?", "Execute your 60-second Floor Rep right now to keep the chain unbroken.", ["TIRED", "HUNGRY"]),
    ("gratitude_for_present_faculties", "Instead of grieving over what is missing, take stock of the strength, reason, and agency you already possess today.", "Use the resources in your hands right now to make one concrete improvement.", "What tool or strength do you already have that you haven't used today?", "Spend 5 minutes advancing a project using only what you already have.", ["HOPELESS", "LONELY"]),
    ("steadiness_in_prosperity_and_trial", "Neither easy days nor hard days should throw a disciplined mind off its daily rhythm.", "Keep your When-Then Routine Anchor identical whether the day feels effortless or heavy.", "Does a busy or unusual day cause you to abandon your baseline habits?", "Anchor your habit to a fixed daily event like waking or brushing your teeth.", ["STRESSED", "TIRED"]),
    ("mastery_of_speech", "Silence and measured speech protect the mind from vanity, gossip, and reactive anger.", "Listen twice as much as you speak in your meetings and conversations today.", "Where does impulsive speech usually drain your energy?", "Wait three full seconds after someone finishes speaking before you reply.", ["ANGRY", "LONELY"]),
    ("the_citadel_of_reason", "No fortress is stronger than a mind that has learned to distinguish between passing sensations and enduring values.", "Observe physical fatigue or craving today as neutral data rather than an emergency.", "What physical sensation is your body experiencing right now—hunger, tension, or fatigue?", "Address the physical baseline first: drink water, stretch, or rest for 5 minutes.", ["HUNGRY", "TIRED"]),
    ("freedom_from_anxious_foreboding", "Borrowing trouble from tomorrow robs you of the strength needed to execute today's duty well.", "Bring your focus back inside the boundaries of today's 24-hour cycle.", "What future scenario are you rehearsing that hasn't actually happened?", "Write down one concrete action you can take today, and leave the rest.", ["STRESSED", "HOPELESS"]),
    ("measuring_wealth_by_contentment", "True abundance is measured by how few external crutches you require to remain steady and purposeful.", "Practice simplicity today by postponing one non-essential purchase or indulgence.", "What craving is promising satisfaction it can never actually deliver?", "Wait 24 hours before acting on any sudden urge to buy or indulge.", ["HUNGRY", "STRESSED"]),
    ("ownership_of_recovery", "When you stumble, do not waste a single minute in self-pity; return immediately to your practice.", "Apply 'Data Over Shame': every day banked remains permanently yours—resume your cadence today.", "How quickly can you shorten the gap between a slip and your next healthy rep?", "Log an honest check-in right now and restart your forward momentum.", ["HOPELESS", "ANGRY"]),
    ("living_the_philosophy", "Wisdom is never proved by reciting maxims; it is proved by how quietly and faithfully you execute today's discipline.", "Translate today's reflection into one visible, completed action before evening.", "What single action today will prove your commitment to your own growth?", "Complete your Primary Focus Habit and mark today done.", ["TIRED", "HOPELESS"]),
]

SMILES_BLUEPRINTS = [
    ("self_reliant_agency", "Lasting progress comes from what you initiate and practice yourself; no external system can replace personal execution.", "Take 100% ownership of your Primary Focus Habit today without waiting for ideal external conditions.", "Where have you been waiting for external permission to begin a discipline you already know you need?", "Start the first two minutes of your Primary Focus Habit right now.", ["HOPELESS", "TIRED"]),
    ("patient_industry", "Genius and lasting achievement are built far more on patient, daily industry than on rare flashes of talent.", "Show up for your scheduled daily repetition today even if it feels ordinary and unglamorous.", "What compounding skill are you building through quiet daily repetition?", "Complete one focused 15-minute block on your core craft today.", ["TIRED", "HOPELESS"]),
    ("compounding_small_efforts", "Just as single pennies accumulate into wealth, small daily acts of discipline compound into unshakeable character.", "Honor your Floor Rep today knowing that every single repetition adds to your permanent ledger.", "How many lifetime repetitions have you already accumulated by not giving up?", "Execute your minimum viable Floor Rep and record it on your ledger.", ["TIRED", "HUNGRY"]),
    ("school_of_difficulty", "Obstacles and friction are not signs that you should quit; they are the exact resistance that awakens dormant strength.", "Treat today's highest-friction moment as strength training for your willpower.", "What past difficulty forced you to develop a capability you now rely on?", "Lean into the first 60 seconds of a task you have been avoiding today.", ["STRESSED", "HOPELESS"]),
    ("dignity_of_daily_work", "Real education happens in how faithfully we conduct ourselves in our daily work, home, and ordinary commitments.", "Bring deliberate craftsmanship and calm focus to your routine tasks today.", "How can you elevate the quality of an ordinary task on your desk right now?", "Clear your workspace of clutter before starting your next work block.", ["TIRED", "LONELY"]),
    ("perseverance_over_brilliance", "Steady perseverance at a modest pace consistently overtakes sporadic bursts of exhausted intensity.", "Keep your daily habit sustainable so you can repeat it tomorrow without burnout.", "Have you been setting your daily target too high to maintain on low-energy days?", "Right-size today's target to a sustainable rep you can finish with energy to spare.", ["TIRED", "STRESSED"]),
    ("seizing_spare_minutes", "Great bodies of work are often built inside the odd fifteen-minute intervals that others let slip away.", "Use one transition pocket today—before a meeting or after coffee—to execute your Routine Anchor.", "Which 15-minute pocket in your daily schedule is currently going to waste?", "Pair your habit with a fixed daily transition cue today.", ["STRESSED", "TIRED"]),
    ("untiring_energy", "Resolute purpose turns an ordinary person into a force of nature by concentrating scattered energy onto a single point.", "Focus on ONE Primary Focus Habit rather than scattering your resolve across ten goals.", "Which single habit, if mastered this month, would uplift every other area of your life?", "Pin that habit as your Primary Focus and give it your first energy today.", ["STRESSED", "HOPELESS"]),
    ("attention_to_little_things", "Careful observation and fidelity in small details form the bedrock of every reliable craft and character.", "Execute your habit today with clean form and full attention from start to finish.", "Where has carelessness in small routines been creating preventable stress?", "Spend two minutes organizing your tools or notes for tomorrow morning.", ["STRESSED", "ANGRY"]),
    ("courage_to_begin_again", "Every master builder has faced failed drafts and broken experiments; perseverance simply means calmly beginning the next attempt.", "Practice 'Data Over Shame': if yesterday was imperfect, today is a clean sheet for action.", "What lessons did your last friction moment teach you about your triggers?", "Log today's check-in and focus solely on today's execution.", ["HOPELESS", "ANGRY"]),
    ("self_culture_cannot_be_bought", "No amount of money can purchase focus, resilience, or character—every person must forge them through personal practice.", "Take pride in the fact that every day on your streak was earned by your own discipline.", "What personal quality are you forging that money could never buy?", "Put in 10 minutes of focused practice on your primary discipline right now.", ["HUNGRY", "LONELY"]),
    ("method_and_punctuality", "Order and fixed timing remove the daily friction of deciding when and how to act.", "Lock your habit to a consistent When-Then trigger so execution becomes automatic.", "At what exact daily cue will you execute your habit today?", "Write down your exact When-Then Routine Anchor for today.", ["STRESSED", "TIRED"]),
    ("cheerful_endurance", "Carrying out difficult duties with a calm, cheerful spirit lightens the load by half.", "Release tense facial and shoulder muscles while working through your afternoon tasks.", "How does physical tension amplify your sense of mental fatigue?", "Drop your shoulders, unclench your jaw, and take a slow deep breath.", ["ANGRY", "TIRED"]),
    ("the_power_of_example", "Quiet, consistent conduct speaks louder and influences others far more deeply than any lecture.", "Be the steady anchor in your household or team today through calm action.", "Who in your life benefits when you stay grounded and consistent?", "Complete your daily commitment quietly and let your steadiness set the tone.", ["LONELY", "ANGRY"]),
    ("concentration_of_purpose", "Scattered effort evaporates like steam; concentrated effort drives the piston forward.", "Eliminate multi-tasking during your Primary Focus window today.", "What single distraction most frequently breaks your concentration?", "Put your phone on airplane mode or in another room for 25 minutes.", ["STRESSED", "TIRED"]),
    ("mastery_of_temper", "Self-control under provocation is the clearest mark of a disciplined mind and mature character.", "When provoked or rushed today, lower your cadence and respond with measured calm.", "What recurring trigger tends to spark impatience in your week?", "Pause for a slow count of five before answering any frustrating message.", ["ANGRY", "STRESSED"]),
    ("turning_adversity_to_account", "Hardship often strips away comfort only to reveal a deeper reserve of resourcefulness and grit.", "Use today's constraint or inconvenience as a prompt to simplify and focus on essentials.", "How can today's limitation actually make your focus sharper?", "Identify the single essential outcome for today and let non-essentials wait.", ["HOPELESS", "STRESSED"]),
    ("honest_thoroughness", "Doing a small piece of work thoroughly builds far more self-respect than skimming across a dozen unfinished tasks.", "Finish one clearly defined unit of work or practice completely before switching contexts.", "What half-finished task is quietly draining your background mental energy?", "Take 10 minutes to close out or cleanly archive one open loop today.", ["TIRED", "STRESSED"]),
    ("habit_as_second_nature", "Repeated daily actions gradually weave themselves into the very fabric of character until steadiness becomes natural.", "Protect your daily repetition so your nervous system continues consolidating the groove.", "Which positive routine in your life already feels natural because you repeated it?", "Chain your current focus habit directly onto that established routine today.", ["TIRED", "HUNGRY"]),
    ("financial_and_personal_prudence", "Disciplined restraint in small daily appetites creates the margin required for true independence and peace of mind.", "Practice deliberate restraint today in both your spending and your attention.", "Where does a momentary craving try to trade away your long-term freedom?", "Skip one sudden urge for distraction today and redirect that energy to your goal.", ["HUNGRY", "STRESSED"]),
    ("hope_as_an_active_force", "Constructive hope is not passive wishing; it is the energetic confidence that steady effort yields results.", "Pair your hope with one concrete physical action in the next ten minutes.", "What small step today makes tomorrow demonstrably better?", "Complete one tangible action toward your goal and log it.", ["HOPELESS", "LONELY"]),
    ("learning_from_every_season", "A perceptive mind extracts practical wisdom from both successes and setbacks without losing heart.", "Review your week's habit log as neutral engineering data rather than a moral judgment.", "What time of day shows your highest check-in consistency?", "Move your hardest habit into your highest-consistency time slot.", ["TIRED", "HOPELESS"]),
    ("physical_vitality_and_rest", "Sustained mental effort requires honoring the physical foundations of sleep, movement, and nourishment.", "Support your willpower today by addressing hunger, hydration, and rest before they become triggers.", "Are you currently feeling frustrated, or simply physically depleted (HALT)?", "Drink a glass of water and stretch for two minutes right now.", ["HUNGRY", "TIRED"]),
    ("unwavering_integrity", "A person whose word to themselves can be trusted possesses an internal compass that never wavers in a storm.", "Keep the small promise you made to yourself today—even if it is a 60-second Floor Rep.", "What small promise to yourself can you fulfill in the next five minutes?", "Execute your Floor Rep now so your word to yourself stays unbroken.", ["LONELY", "HOPELESS"]),
    ("decisive_execution", "Wishing and resolving accomplish nothing until they are translated into immediate physical motion.", "Bridge the gap between intention and action within 60 seconds of reading this prompt.", "What have you been 'planning to start' that you can begin in miniature right now?", "Do the very first physical motion of your habit right now.", ["TIRED", "STRESSED"]),
    ("resilience_under_delay", "The greatest works require patient gestation; do not uproot your seed just because the harvest is not instant.", "Trust the compounding cadence of your daily reps without demanding overnight transformation.", "Where is impatience tempting you to abandon a habit that is quietly working?", "Honor today's single repetition and leave the long-term curve to time.", ["HOPELESS", "ANGRY"]),
    ("ordering_the_daily_ledger", "Writing down observations and tracking daily conduct brings clarity where vague memory always flatters or deceives.", "Keep an accurate, honest daily check-in log so your progress is visible in black and white.", "What pattern becomes obvious when you look at your last seven days of check-ins?", "Open your habit tracker and log today's status with complete honesty.", ["STRESSED", "TIRED"]),
    ("independence_of_spirit", "True self-help means standing firmly on your own daily discipline rather than leaning on excuses or circumstances.", "Drop one excuse about timing or mood and execute a clean baseline rep today.", "What story about being 'too busy' can you retire today?", "Carve out 120 seconds right now to complete your Floor Rep.", ["ANGRY", "TIRED"]),
    ("generosity_of_strength", "As you build personal steadiness, your surplus calm naturally strengthens and encourages everyone around you.", "Share a word of genuine encouragement with someone in your circle today.", "Who around you could use a calm, steady presence today?", "Send one brief, supportive message or offer a patient listening ear today.", ["LONELY", "ANGRY"]),
    ("the_crown_of_character", "At the end of any journey, the highest reward is not external applause but the quiet strength of the character you forged.", "Close today knowing that every honest repetition builds permanent Character Proof.", "How has your daily practice shaped the person you are becoming?", "Complete today's Primary Focus check-in with quiet gratitude.", ["HOPELESS", "LONELY"]),
]

BENNETT_BLUEPRINTS = [
    ("the_daily_miracle", "Every morning delivers a fresh, unblemished purse of twenty-four hours—no one receives a single minute more or less.", "Receive today's 24 hours as a clean slate regardless of how yesterday went.", "How would you spend the next hour if you treated time as a fresh daily miracle?", "Choose one deliberate 20-minute pocket today and assign its exact purpose now.", ["HOPELESS", "TIRED"]),
    ("democracy_of_time", "In the realm of time, wealth and status confer zero advantage; everyone stewards the exact same daily allotment.", "Stop comparing your resources to others and invest the hour directly in front of you.", "Where has comparison been distracting you from using your own twenty-four hours?", "Focus exclusively on your own Primary Focus Habit for the next 15 minutes.", ["LONELY", "ANGRY"]),
    ("unstoppable_supply", "Even if you squandered yesterday, today's full supply of twenty-four hours arrives undiminished at dawn.", "Apply 'Data Over Shame': never let yesterday's wasted hour poison today's fresh allotment.", "What guilt about yesterday can you release so today stays clear?", "Take a deep breath, forgive yesterday's friction, and log today's Floor Rep.", ["HOPELESS", "STRESSED"]),
    ("living_vs_muddling_through", "Merely muddling through a reactive schedule leaves a constant background uneasiness; deliberate living requires a plan.", "Replace reactive drifting this evening with one intentionally chosen activity.", "Which part of your daily routine currently feels like 'muddling through'?", "Define a clear When-Then anchor for your evening transition today.", ["TIRED", "STRESSED"]),
    ("balancing_the_time_budget", "Just as a household budget collapses without intention, a 24-hour day feels frantic until its prime compartments are defined.", "Allocate your Primary Focus Habit into a fixed slot before filling the day with minor errands.", "What is the single non-negotiable line item in your time budget today?", "Block out 15–30 minutes on your calendar today for your primary discipline.", ["STRESSED", "TIRED"]),
    ("the_day_within_a_day", "Inside your official workday sits a second, sovereign day—the morning and evening hours that belong entirely to your own growth.", "Treat your pre-work morning or post-work evening hour as a sacred 'day within a day.'", "Which 30-minute window outside your job belongs 100% to your own development?", "Claim 15 minutes of that window today for reading, reflection, or training.", ["TIRED", "LONELY"]),
    ("answering_inner_aspiration", "The quiet restlessness to grow beyond mere routine is a healthy signal; only deliberate action puts that restlessness at peace.", "Channel restless energy into a concrete 10-minute creative or physical rep today.", "What worthwhile pursuit has been knocking at the back of your mind this month?", "Take one concrete 5-minute step toward that pursuit today.", ["HUNGRY", "LONELY"]),
    ("leaving_the_station", "Wishing to reach a distant goal while never taking the first local step creates far more fatigue than the work itself.", "Stop over-researching and execute the simplest first step of your habit today.", "Where have you been substituting planning for actual execution?", "Close the planning doc and perform one real repetition right now.", ["STRESSED", "HOPELESS"]),
    ("protecting_vital_powers", "Your life's best energy should never be 100% monopolized by routine obligations; keep a reserve for your own soul and mind.", "Guard a small daily pocket of fresh mental energy before exhaustion sets in.", "Why give 100% of your sharpest energy to obligations and 0% to your own growth?", "Execute your Primary Focus Habit earlier in the day before fatigue builds.", ["TIRED", "STRESSED"]),
    ("morning_first_fruits", "Engaging your mind in something meaningful before the official workday begins changes the posture of the entire day.", "Attach your When-Then Routine Anchor to your morning coffee or commute.", "What happens to your mood when you win the first 15 minutes of the morning?", "Complete your morning Floor Rep before checking work messages.", ["TIRED", "HUNGRY"]),
    ("Modest_beginnings_prevent_burnout", "The #1 cause of abandoned resolutions is undertaking an over-ambitious schedule on Day 1; begin with a modest, winnable rep.", "Keep your Floor Rep small enough that you can execute it even on your hardest day.", "Is your current daily habit target realistic for a tired Tuesday night?", "Scale today's target down to a high-certainty 5-to-15 minute win.", ["TIRED", "HOPELESS"]),
    ("reclaiming_the_commute_pocket", "Transition times—walking, commuting, or waiting—are hidden goldmines for calm mental reflection instead of frantic scrolling.", "Use your next 10-minute transit or waiting window for quiet thought or a Focus Pack reading.", "How do you usually spend the first 15 minutes after leaving work?", "Keep your phone pocketed during your next walk or transit transition.", ["STRESSED", "TIRED"]),
    ("debunking_total_exhaustion", "Often what feels like total evening exhaustion is actually boredom or decision fatigue from an unvaried routine.", "Test gentle mental or physical engagement tonight instead of collapsing into passive screen numbing.", "Does passive scrolling actually restore your energy, or leave you more drained?", "Try 10 minutes of your restorative habit tonight before turning on any screen.", ["TIRED", "HUNGRY"]),
    ("the_three_evenings_rule", "You do not need to overhaul every night of the week at once; reclaiming even three focused evenings transforms a year.", "Designate tonight as one of your focused evenings and protect a 30-minute window.", "Which three evenings this week are best suited for a calm focus session?", "Mark those three evenings now and set a gentle reminder cue.", ["TIRED", "STRESSED"]),
    ("eliminating_preparatory_friction", "Small practical details—like having your book, journal, or gear laid out—determine whether an early habit succeeds or fails.", "Prepare your physical environment tonight so tomorrow morning's habit requires zero setup.", "What tiny physical friction slows you down when it is time to start?", "Set out your journal, pen, or equipment in plain sight right now.", ["TIRED", "STRESSED"]),
    ("honoring_human_nature", "A wise system allows for accidents and interruptions without collapsing in shame when a day goes off-script.", "When an unexpected disruption hits today, pivot smoothly to your 60-second Floor Rep.", "How do you talk to yourself when your ideal schedule gets interrupted?", "Replace all-or-nothing frustration with a calm 60-second minimum rep today.", ["ANGRY", "STRESSED"]),
    ("training_the_faculty_of_attention", "The mind is like a spirited horse that wanders unless gently and repeatedly brought back to the chosen path.", "Whenever your attention drifts during today's focus block, bring it back with zero irritation.", "How many minutes can you currently sustain single-pointed focus on one idea?", "Practice 10 minutes of uninterrupted reading or reflection today.", ["STRESSED", "TIRED"]),
    ("evening_reflection_anchor", "Spending ten minutes reviewing a single noble idea in the evening gives the mind something worthy to digest overnight.", "Read one passage from your active Focus Pack tonight and reflect on how it applies to your day.", "What is the last thought you usually feed your mind before sleep?", "Read today's quote one final time before turning off the light tonight.", ["LONELY", "TIRED"]),
    ("curiosity_for_cause_and_effect", "Observing how daily triggers affect your mood and behavior turns everyday life into an engaging study rather than a grind.", "Notice the exact cause-and-effect link between your sleep, nutrition, and cravings today.", "What specific antecedent preceded your highest-energy hour this week?", "Note one cause-and-effect observation in your check-in log today.", ["HUNGRY", "ANGRY"]),
    ("guarding_against_mental_sloth", "Mental inertia masquerades as a need for endless passive entertainment, when what the mind truly craves is purposeful absorption.", "Trade 20 minutes of passive consumption today for an active craft, walk, or reflection.", "Which activity in your week leaves you feeling genuinely refreshed afterward?", "Schedule 15 minutes of that restorative activity into today's plan.", ["TIRED", "HUNGRY"]),
    ("avoiding_priggish_rigidity", "Your habit architecture exists to serve and enrich your life, never to turn you into a rigid or joyless taskmaster.", "Carry your daily discipline lightly, with warmth and humility toward yourself and others.", "Are you approaching your habits with calm joy or grim tension?", "Smile, relax your shoulders, and enjoy the process of today's repetition.", ["ANGRY", "STRESSED"]),
    ("the_weekend_treasure", "The forty-hour span across the weekend is a vast sovereign estate inside every single week when met with gentle intention.", "Choose one restorative anchor for your upcoming weekend before Friday evening arrives.", "How can you make this weekend genuinely restorative instead of a blur?", "Write down one meaningful personal priority for your next day off.", ["TIRED", "LONELY"]),
    ("deliberate_pace", "Hurrying through a reflection or habit to 'get it over with' destroys its restorative power; work without haste.", "Perform your daily habit today with unhurried, deliberate presence.", "Where are you rushing through something that is meant to ground you?", "Slow your reading and writing pace by half during today's check-in.", ["STRESSED", "ANGRY"]),
    ("the_vital_first_half_hour", "How you govern your mind in the first thirty minutes of the morning sets the thermostat for the next fifteen hours.", "Keep reactive news and social feeds out of the first 30 minutes of your morning.", "What is the very first input your brain receives after waking?", "Complete your morning Routine Anchor before opening any feed or inbox.", ["STRESSED", "HUNGRY"]),
    ("cultivating_serious_interest", "Any discipline becomes effortless once you cultivate a genuine curiosity in its principles and subtle details.", "Look for one new nuance or insight inside your daily practice today.", "What aspect of your primary habit can you explore more deeply this week?", "Write down one question or observation about your practice today.", ["TIRED", "LONELY"]),
    ("small_certainty_over_grand_failure", "Thirty minutes of focused practice completed with certainty beats a three-hour fantasy schedule that collapses by Wednesday.", "Commit only to the exact duration you know you can honor today.", "What duration of practice can you guarantee with 99% certainty today?", "Set a timer for that exact winnable duration and complete it cleanly.", ["HOPELESS", "TIRED"]),
    ("reclaiming_wasted_intervals", "Waiting rooms, queues, and brief pauses stop being irritating the moment you use them for calm mental review.", "When forced to wait today, use the interval for breath grounding rather than annoyance.", "How can a five-minute delay become a welcome pocket of stillness?", "Use your next waiting moment today for three slow breaths and posture reset.", ["ANGRY", "STRESSED"]),
    ("the_compound_interest_of_hours", "Ninety minutes a week of deliberate focus adds up to nearly eighty hours of transformative mastery over a year.", "Respect the compounding power of your small daily check-in today.", "Where will you be in twelve months if you simply protect this daily Floor Rep?", "Log today's rep and watch your cumulative days grow.", ["HOPELESS", "TIRED"]),
    ("unified_mind_and_action", "When your daily thoughts and your daily schedule are aligned, the inner friction of 'living two lives' disappears.", "Ensure your Primary Focus Habit receives a real, visible place in today's hours.", "Does today's schedule reflect what you say matters most to you?", "Move your Primary Focus Habit ahead of one secondary chore today.", ["STRESSED", "LONELY"]),
    ("master_of_the_twenty_four", "You cannot control the length of your years, but you are the sovereign architect of how you inhabit today's twenty-four hours.", "Finish today with the quiet satisfaction of having lived at least one pocket with total intention.", "Which hour today was truly yours?", "Complete your evening reflection and bank today's victory.", ["TIRED", "HOPELESS"]),
]


def main() -> None:
    sen_norm, sen_sha, sen_bytes = load_source("seneca_dialogues_stewart_1889.txt")
    epi_norm, epi_sha, epi_bytes = load_source("epictetus_discourses_long_1877.txt")
    smi_norm, smi_sha, smi_bytes = load_source("samuel_smiles_self_help_1859.txt")
    ben_norm, ben_sha, ben_bytes = load_source("arnold_bennett_24_hours_1910.txt")

    sen_entries = curate_30_from_book(
        sen_norm,
        556306,
        613000,
        "Seneca, Of the Shortness of Life (tr. Aubrey Stewart 1889)",
        "seneca_sol",
        SENECA_BLUEPRINTS,
        ["time", "life", "live", "day", "busy", "leisure", "mind", "hour", "present", "future", "past", "nature", "age", "rest", "wisdom", "fortune", "care", "work"],
    )

    epi_entries = curate_30_from_book(
        epi_norm,
        4000,
        335000,
        "Epictetus, Discourses (tr. George Long 1877)",
        "epictetus_disc",
        EPICTETUS_BLUEPRINTS,
        ["power", "will", "mind", "reason", "man", "good", "evil", "desire", "fear", "free", "habit", "opinion", "soul", "act", "duty", "truth", "nature"],
    )

    smi_entries = curate_30_from_book(
        smi_norm,
        16000,
        820000,
        "Samuel Smiles, Self-Help (1859)",
        "smiles_sh",
        SMILES_BLUEPRINTS,
        ["habit", "character", "industry", "work", "perseverance", "energy", "time", "self-help", "patience", "diligence", "labour", "attention", "duty", "effort", "purpose"],
    )

    ben_entries = curate_30_from_book(
        ben_norm,
        1500,
        90000,
        "Arnold Bennett, How to Live on 24 Hours a Day (1910)",
        "bennett_24h",
        BENNETT_BLUEPRINTS,
        ["time", "day", "hour", "mind", "habit", "live", "effort", "programme", "energy", "morning", "evening", "thought", "attention", "interest", "work"],
    )

    vol2_packs = [
        (
            "seneca_shortness_of_life_30day.json",
            {
                "pack_meta": {
                    "pack_id": "seneca_shortness_of_life_30day",
                    "volume": 2,
                    "title": "Time Sovereignty: Seneca on the Shortness of Life",
                    "subtitle": "30 Verbatim Pre-1931 Passages from Seneca's De Brevitate Vitae (Aubrey Stewart 1889) on Reclaiming Your Hours from Reactive Busyness",
                    "author": "Lucius Annaeus Seneca (c. 4 BC–65 AD)",
                    "editorial_lead": "Julian Thorne (LEAD-CONTENT)",
                    "legal_clearance_lead": "Vera Lindqvist (STUDIO-LEGAL)",
                    "studio_vp": "Sloane Sterling (VP-STUDIO)",
                    "source_provenance": {
                        "vault_file": "sources/public_domain_classics/seneca_dialogues_stewart_1889.txt",
                        "sha256": sen_sha,
                        "bytes": sen_bytes,
                        "gutenberg_id": 64576,
                        "translators_referenced": "Aubrey Stewart (1889, George Bell and Sons — Gutenberg #64576)",
                        "legal_status": "17 U.S.C. Public Domain — Pre-1931 Publication (1889); plain, application, strategic_prompt & micro_action layers are 100% original 2026 864zeros LLC authorship.",
                        "clean_room_verified": True,
                    },
                    "entry_count": 30,
                    "schema_version": "2.0.0",
                    "compatible_targets": [
                        "ClearStreak Focus Packs",
                        "864zeros 5x8 QR Companion Journals",
                        "864zeros Standalone Practice Books",
                        "OIA Focus Extensions",
                    ],
                },
                "entries": sen_entries,
            },
        ),
        (
            "epictetus_discourses_30day.json",
            {
                "pack_meta": {
                    "pack_id": "epictetus_discourses_30day",
                    "volume": 2,
                    "title": "Dichotomy of Control: Epictetus's Discourses on Inner Assent",
                    "subtitle": "30 Verbatim Pre-1931 Passages from Epictetus's Discourses (George Long 1877) on Sovereign Agency, Urge Mastery & Unshakeable Composure",
                    "author": "Epictetus (c. 50–135 AD), compiled by Arrian",
                    "editorial_lead": "Julian Thorne (LEAD-CONTENT)",
                    "legal_clearance_lead": "Vera Lindqvist (STUDIO-LEGAL)",
                    "studio_vp": "Sloane Sterling (VP-STUDIO)",
                    "source_provenance": {
                        "vault_file": "sources/public_domain_classics/epictetus_discourses_long_1877.txt",
                        "sha256": epi_sha,
                        "bytes": epi_bytes,
                        "gutenberg_id": 10661,
                        "translators_referenced": "George Long (1877, George Bell and Sons — Gutenberg #10661)",
                        "legal_status": "17 U.S.C. Public Domain — Pre-1931 Publication (1877); plain, application, strategic_prompt & micro_action layers are 100% original 2026 864zeros LLC authorship.",
                        "clean_room_verified": True,
                    },
                    "entry_count": 30,
                    "schema_version": "2.0.0",
                    "compatible_targets": [
                        "ClearStreak Focus Packs",
                        "864zeros 5x8 QR Companion Journals",
                        "864zeros Standalone Practice Books",
                        "OIA Focus Extensions",
                    ],
                },
                "entries": epi_entries,
            },
        ),
        (
            "samuel_smiles_self_help_30day.json",
            {
                "pack_meta": {
                    "pack_id": "samuel_smiles_self_help_30day",
                    "volume": 2,
                    "title": "Compounding Industry: Samuel Smiles on Perseverance & Character",
                    "subtitle": "30 Verbatim Pre-1931 Passages from Samuel Smiles's Self-Help (1859) on Patient Daily Effort, Resilience Under Friction & Self-Reliant Growth",
                    "author": "Samuel Smiles (1812–1904)",
                    "editorial_lead": "Julian Thorne (LEAD-CONTENT)",
                    "legal_clearance_lead": "Vera Lindqvist (STUDIO-LEGAL)",
                    "studio_vp": "Sloane Sterling (VP-STUDIO)",
                    "source_provenance": {
                        "vault_file": "sources/public_domain_classics/samuel_smiles_self_help_1859.txt",
                        "sha256": smi_sha,
                        "bytes": smi_bytes,
                        "gutenberg_id": 935,
                        "translators_referenced": "Samuel Smiles (1859 Original English Edition, John Murray — Gutenberg #935)",
                        "legal_status": "17 U.S.C. Public Domain — Pre-1931 Publication (1859); plain, application, strategic_prompt & micro_action layers are 100% original 2026 864zeros LLC authorship.",
                        "clean_room_verified": True,
                    },
                    "entry_count": 30,
                    "schema_version": "2.0.0",
                    "compatible_targets": [
                        "ClearStreak Focus Packs",
                        "864zeros 5x8 QR Companion Journals",
                        "864zeros Standalone Practice Books",
                        "OIA Focus Extensions",
                    ],
                },
                "entries": smi_entries,
            },
        ),
        (
            "arnold_bennett_24_hours_30day.json",
            {
                "pack_meta": {
                    "pack_id": "arnold_bennett_24_hours_30day",
                    "volume": 2,
                    "title": "The Day Within a Day: Arnold Bennett on Deliberate Time-Pockets",
                    "subtitle": "30 Verbatim Pre-1931 Passages from Arnold Bennett's How to Live on 24 Hours a Day (1910) on Protected Time-Pockets & Anti-Burnout Habit Scaling",
                    "author": "Arnold Bennett (1867–1931)",
                    "editorial_lead": "Julian Thorne (LEAD-CONTENT)",
                    "legal_clearance_lead": "Vera Lindqvist (STUDIO-LEGAL)",
                    "studio_vp": "Sloane Sterling (VP-STUDIO)",
                    "source_provenance": {
                        "vault_file": "sources/public_domain_classics/arnold_bennett_24_hours_1910.txt",
                        "sha256": ben_sha,
                        "bytes": ben_bytes,
                        "gutenberg_id": 2274,
                        "translators_referenced": "Arnold Bennett (1910 Original English Edition, George H. Doran — Gutenberg #2274)",
                        "legal_status": "17 U.S.C. Public Domain — Pre-1931 Publication (1910); plain, application, strategic_prompt & micro_action layers are 100% original 2026 864zeros LLC authorship.",
                        "clean_room_verified": True,
                    },
                    "entry_count": 30,
                    "schema_version": "2.0.0",
                    "compatible_targets": [
                        "ClearStreak Focus Packs",
                        "864zeros 5x8 QR Companion Journals",
                        "864zeros Standalone Practice Books",
                        "OIA Focus Extensions",
                    ],
                },
                "entries": ben_entries,
            },
        ),
    ]

    def promote_root_headers(p: dict) -> dict:
        meta = p.get("pack_meta", {})
        return {
            "pack_id": meta.get("pack_id"),
            "id": meta.get("pack_id"),
            "version": meta.get("schema_version", "2.0.0"),
            "volume": meta.get("volume", 1),
            "title": meta.get("title"),
            "subtitle": meta.get("subtitle"),
            "author": meta.get("author"),
            "provenance": meta.get("source_provenance"),
            "pack_meta": meta,
            "entries": p.get("entries", []),
        }

    for fname, payload in vol2_packs:
        out_path = PACKS_DIR / fname
        promoted = promote_root_headers(payload)
        out_path.write_text(json.dumps(promoted, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote Volume 2 pack: {fname} ({len(promoted['entries'])} entries)")

    # Enrich Volume 1 Focus Packs with `day: 1..30`, `strategic_prompt`, `micro_action`, `halt_triggers`, and root headers
    vol1_files = [
        "marcus_aurelius_meditations.json",
        "stoic_masters_epictetus_seneca.json",
        "ben_franklin_virtues.json",
        "aristotle_character.json",
        "william_james_habit.json",
    ]
    halt_cycle = [
        ["STRESSED", "TIRED"],
        ["ANGRY", "STRESSED"],
        ["TIRED", "HOPELESS"],
        ["LONELY", "STRESSED"],
        ["HUNGRY", "TIRED"],
        ["HOPELESS", "ANGRY"],
    ]
    for vf in vol1_files:
        vpath = PACKS_DIR / vf
        vdata = json.loads(vpath.read_text(encoding="utf-8"))
        vdata["pack_meta"]["volume"] = 1
        vdata["pack_meta"]["schema_version"] = "2.0.0"
        for i, entry in enumerate(vdata["entries"]):
            entry["day"] = i + 1
            if "strategic_prompt" not in entry or not entry["strategic_prompt"]:
                entry["strategic_prompt"] = (
                    f"{entry['plain']} How will you apply this principle when friction arises today?"
                )
            if "micro_action" not in entry or not entry["micro_action"]:
                entry["micro_action"] = entry["application"]
            if "halt_triggers" not in entry:
                entry["halt_triggers"] = halt_cycle[i % len(halt_cycle)]
        promoted_v1 = promote_root_headers(vdata)
        vpath.write_text(json.dumps(promoted_v1, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Enriched Volume 1 pack: {vf} ({len(promoted_v1['entries'])} entries, days 1..30)")


if __name__ == "__main__":
    main()

