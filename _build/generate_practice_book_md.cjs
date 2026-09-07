const fs = require('fs');
const book = JSON.parse(fs.readFileSync('shared/practice_books/foundations_of_resilience/practice_book_10_lessons.json', 'utf8'));

function centerText(str, width) {
  if (str.length >= width) return str;
  const left = Math.floor((width - str.length) / 2);
  const right = width - str.length - left;
  return ' '.repeat(left) + str + ' '.repeat(right);
}

let md = '# ' + book.title + '\n';
md += '### ' + book.subtitle + '\n';
md += '*Published by ' + book.author + ' · Version ' + book.version + ' (' + book.published_date + ')*  \n';
md += '*Visual Style: ' + book.art_style.recipe + '*\n\n---\n\n';

md += '## Introduction & Practice Philosophy\n\n';
md += 'The **Foundations of Resilience Practice Book** combines four distinct disciplines into a daily practice routine:\n\n';
md += '1. **Timeless Scripture:** Grounded in public-domain scripture (KJV and WEB) paired with clear, modern 2026 plain-language renderings.\n';
md += '2. **Extracted Intent:** Distilling theological passages into direct, actionable cognitive and behavioral principles.\n';
md += '3. **Visual-DAGR Humanizer Art (`jeff_sketch`):** Expressive minimalist fountain pen line art embodying authentic line economy. Hand-drawn calligraphic stroke dynamics, 75% interior reduction, 20% random line-weight accents, and vast stark white negative space.\n';
md += '4. **Superimposed Reflection & Action:** Pairing typography directly over art plates to create memorable mental anchors, backed by guided journaling and concrete micro-practices.\n\n---\n\n';

md += '```mermaid\ngraph LR\n    A["1. Public-Domain Scripture"] --> B["2. Extracted Behavioral Intent"]\n    B --> C["3. Visual-DAGR Humanizer Metaphor"]\n    C --> D["4. Superimposed Art Card"]\n    D --> E["5. Daily Reflection and Practice"]\n```\n\n---\n\n';

md += '## Table of Contents\n';
book.lessons.forEach(l => {
  md += (l.lesson_num) + '. [Lesson ' + l.lesson_num + ': ' + l.title + ' (' + l.scripture.reference + ')](#lesson-' + l.lesson_num + '-' + l.id.replace('lesson-' + String(l.lesson_num).padStart(2,'0') + '-', '') + ')\n';
});
md += '\n---\n\n';

book.lessons.forEach(l => {
  const pad = String(l.lesson_num).padStart(2, '0');
  md += '## Lesson ' + l.lesson_num + ': ' + l.title + '\n\n';
  md += '> **Theme:** ' + l.theme + ' · **Reference:** ' + l.scripture.reference + '\n\n';
  md += '### Visual Plate & Superimposed Concept\n';
  md += '![Lesson ' + l.lesson_num + ': ' + l.title + '](../../../media/visuals/practice_book/lesson_' + pad + '.jpg)\n\n';
  
  md += '```text\n';
  md += '┌──────────────────────────────────────────────────────────────────────────┐\n';
  md += '│ [SUPERIMPOSED CARD OVERLAY]                                              │\n';
  md += '│                                                                          │\n';
  md += '│ THEME: ' + l.overlay_config.theme_tag.padEnd(65, ' ') + ' │\n';
  md += '│                                                                          │\n';
  md += '│ ' + centerText(l.overlay_config.headline, 72) + ' │\n';
  md += '│                                                                          │\n';
  md += '│ ' + centerText(l.overlay_config.scripture_quote, 72) + ' │\n';
  md += '│ ' + centerText('— ' + l.overlay_config.citation, 72) + ' │\n';
  md += '│                                                                          │\n';
  md += '│ * Intent: ' + l.overlay_config.intent_callout.padEnd(62, ' ') + ' * │\n';
  md += '└──────────────────────────────────────────────────────────────────────────┘\n';
  md += '```\n\n';

  md += '* **Visual Concept:** ' + l.visual_concept + '\n';
  md += '* **LoRA Master Prompt:** `' + l.jeff_sketch_prompt + '`\n\n';

  md += '### Dual Scripture Pairing\n';
  md += '* **King James Version (KJV):** *"' + l.scripture.text_kjv + '"*\n';
  md += '* **World English Bible (WEB):** *"' + l.scripture.text_web + '"*\n';
  md += '* **Plain Language (2026):** *"' + l.scripture.plain + '"*\n\n';

  md += '### Extracted Intent\n';
  md += l.extracted_intent + '\n\n';

  md += '### Daily Reflection Journal\n';
  md += '1. *' + l.reflection_prompt + '*\n\n';
  md += '   _________________________________________________________________________________________________\n\n';
  md += '   _________________________________________________________________________________________________\n\n';

  md += '### Actionable Micro-Practice\n';
  md += '* **' + l.actionable_practice + '**\n\n';
  md += '---\n\n';
});

fs.writeFileSync('shared/practice_books/foundations_of_resilience/PRACTICE_BOOK_10_LESSONS.md', md, 'utf8');
console.log('Successfully regenerated PRACTICE_BOOK_10_LESSONS.md');
