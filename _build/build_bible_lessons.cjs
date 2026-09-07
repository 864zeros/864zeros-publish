// build_bible_lessons.js — Compiles all 66 books and 660 actionable life lessons into shared/bible/
const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const sharedBibleDir = path.join(root, 'shared', 'bible');

// Load all parts
const ot1 = require('./bible_data/ot_part1.cjs');
const ot2 = require('./bible_data/ot_part2.cjs');
const ot3 = require('./bible_data/ot_part3.cjs');
const ot4 = require('./bible_data/ot_part4.cjs');
const nt1 = require('./bible_data/nt_part1.cjs');
const nt2 = require('./bible_data/nt_part2.cjs');
const nt3 = require('./bible_data/nt_part3.cjs');

const allBooks = [...ot1, ...ot2, ...ot3, ...ot4, ...nt1, ...nt2, ...nt3];

console.log(`Loaded ${allBooks.length} books total.`);

// Validation
if (allBooks.length !== 66) {
  throw new Error(`Expected 66 books, but got ${allBooks.length}`);
}

let totalLessons = 0;
allBooks.forEach((b, idx) => {
  if (b.order !== idx + 1) {
    throw new Error(`Book ${b.book} order mismatch: expected ${idx + 1}, got ${b.order}`);
  }
  if (!b.overview || b.overview.length < 50) {
    throw new Error(`Book ${b.book} overview is too short or missing.`);
  }
  if (!Array.isArray(b.key_themes) || b.key_themes.length === 0) {
    throw new Error(`Book ${b.book} key_themes missing or empty.`);
  }
  if (!Array.isArray(b.lessons) || b.lessons.length !== 10) {
    throw new Error(`Book ${b.book} does not have exactly 10 lessons (found ${b.lessons ? b.lessons.length : 0})`);
  }
  b.lessons.forEach((l, lidx) => {
    if (l.number !== lidx + 1) {
      throw new Error(`Book ${b.book} lesson ${lidx} number mismatch.`);
    }
    if (!l.title || !l.citation || !l.scripture_text || !l.lesson || !l.application) {
      throw new Error(`Book ${b.book} lesson ${l.number} has missing fields.`);
    }
    totalLessons++;
  });
});

console.log(`Validation passed: 66 books, 660 total lessons.`);

// Create Master JSON Asset
const masterDoc = {
  _meta: {
    title: "864zeros Bible Study Library: Book Overviews & 10 Actionable Life Lessons",
    role: "Comprehensive study dataset covering all 66 canonical books of the Holy Bible.",
    testaments: {
      old_testament: { books: 39, lessons: 390 },
      new_testament: { books: 27, lessons: 270 }
    },
    total_books: 66,
    total_lessons: totalLessons,
    license: "Public domain scripture anchors (KJV/WEB); original 864zeros theological overviews, lessons, and applications.",
    generated: "2026-09-01",
    version: 1
  },
  books: allBooks
};

const jsonPath = path.join(sharedBibleDir, 'bible_study_lessons.json');
fs.writeFileSync(jsonPath, JSON.stringify(masterDoc, null, 2), 'utf8');
console.log(`Wrote JSON master asset to: ${jsonPath} (${(fs.statSync(jsonPath).size / 1024).toFixed(1)} KB)`);

// Generate Comprehensive Markdown Companion
let md = `# 864zeros Bible Study Library — Book Overviews & 10 Life Lessons

**Comprehensive 66-Book Study Dataset** authored for the 864zeros central content store. Every book in the canonical Bible is presented with a high-level theological overview, core themes, and **10 actionable life lessons / behavioral rules** grounded in scripture.

- **Total Books:** 66 (OT: 39 · NT: 27)
- **Total Actionable Lessons:** 660
- **Master JSON Asset:** [\`bible_study_lessons.json\`](bible_study_lessons.json)

---

## Canonical Table of Contents

| # | Book | Testament | Category | Lessons |
|---|---|---|---|:---:|
`;

allBooks.forEach(b => {
  md += `| ${b.order} | **[${b.book}](#${b.book.toLowerCase().replace(/\\s+/g, '-')})** | ${b.testament} | ${b.category} | ${b.lessons.length} |\n`;
});

md += `\n---\n\n`;

allBooks.forEach(b => {
  md += `## ${b.order}. ${b.book}\n\n`;
  md += `**Testament:** ${b.testament === 'OT' ? 'Old Testament' : 'New Testament'} · **Category:** ${b.category}\n\n`;
  md += `### Book Overview\n${b.overview}\n\n`;
  md += `**Key Themes:** ${b.key_themes.join(' · ')}\n\n`;
  md += `### 10 Actionable Life Lessons\n\n`;

  b.lessons.forEach(l => {
    md += `#### ${l.number}. ${l.title} (\`${l.citation}\`)\n`;
    md += `> *"${l.scripture_text}"*\n\n`;
    md += `**Principle / Rule:** ${l.lesson}\n\n`;
    md += `**Daily Application:** ${l.application}\n\n`;
  });

  md += `---\n\n`;
});

md += `\n*864zeros LLC · central content store · JSON is truth, SQLite is derived.*\n`;

const mdPath = path.join(sharedBibleDir, 'BIBLE_STUDY_LESSONS.md');
fs.writeFileSync(mdPath, md, 'utf8');
console.log(`Wrote Markdown companion to: ${mdPath} (${(fs.statSync(mdPath).size / 1024).toFixed(1)} KB)`);

// Generate 100% Self-Contained HTML Study Viewer (Works directly from file:// with zero CORS issues)
const htmlViewer = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>864zeros Bible Study Library — 66 Books &amp; 10 Life Lessons</title>
<style>
  :root {
    --bg: #f5f4ef; --panel: #ffffff; --ink: #1f2328; --muted: #656d76; --line: #e1ded6;
    --accent: #2e6245; --accent-light: #eaf2ec; --accent-dark: #1b3d2b;
    --gold: #b38600; --gold-soft: #fef8e7;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: var(--bg); color: var(--ink); }
  .app { display: grid; grid-template-columns: 310px 1fr; height: 100vh; overflow: hidden; }
  
  /* Sidebar */
  aside { background: var(--panel); border-right: 1px solid var(--line); overflow-y: auto; display: flex; flex-direction: column; }
  .sidebar-header { padding: 18px 20px 14px; border-bottom: 1px solid var(--line); position: sticky; top: 0; background: var(--panel); z-index: 10; }
  .brand-tag { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--accent); }
  .sidebar-header h1 { margin: 4px 0 2px; font-size: 16px; font-weight: 700; }
  .sidebar-header .sub { font-size: 12px; color: var(--muted); }
  .search-box { padding: 10px 16px; border-bottom: 1px solid var(--line); background: var(--bg); position: sticky; top: 75px; z-index: 9; }
  .search-box input { width: 100%; padding: 8px 12px; font-size: 13px; border: 1px solid var(--line); border-radius: 6px; outline: none; background: #fff; }
  .search-box input:focus { border-color: var(--accent); }
  
  .book-list { list-style: none; margin: 0; padding: 6px 0; }
  .section-label { padding: 12px 18px 4px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); }
  .book-item { display: flex; justify-content: space-between; align-items: center; padding: 7px 18px; cursor: pointer; font-size: 13.5px; border-left: 3px solid transparent; transition: background 0.15s; }
  .book-item:hover { background: var(--accent-light); }
  .book-item.active { background: var(--accent-light); border-left-color: var(--accent); font-weight: 600; color: var(--accent-dark); }
  .book-num { font-size: 11.5px; color: var(--muted); font-variant-numeric: tabular-nums; }
  
  /* Main Content */
  main { overflow-y: auto; padding: 32px 40px 100px; }
  .container { max-width: 900px; margin: 0 auto; }
  
  .book-banner { background: var(--panel); border: 1px solid var(--line); border-radius: 12px; padding: 28px 32px; margin-bottom: 28px; box-shadow: 0 2px 6px rgba(0,0,0,0.03); }
  .book-meta-row { display: flex; gap: 8px; align-items: center; margin-bottom: 10px; }
  .pill { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 3px 9px; border-radius: 999px; background: var(--accent-light); color: var(--accent-dark); }
  .pill.category { background: #eef1f6; color: #3b5998; }
  .book-title { margin: 0 0 12px; font-size: 28px; font-weight: 800; color: var(--ink); }
  .book-overview { font-size: 15.5px; line-height: 1.65; color: #333; margin: 0 0 18px; }
  
  .themes-title { font-size: 11.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 6px; }
  .theme-chips { display: flex; flex-wrap: wrap; gap: 6px; }
  .theme-chip { font-size: 12px; background: var(--gold-soft); color: #7a5c00; border: 1px solid #fae7a5; padding: 3px 10px; border-radius: 6px; font-weight: 500; }
  
  .lessons-heading { font-size: 18px; font-weight: 700; margin: 0 0 16px; display: flex; align-items: center; justify-content: space-between; }
  .lessons-heading span { font-size: 13px; font-weight: 400; color: var(--muted); }
  
  .lessons-grid { display: flex; flex-direction: column; gap: 16px; }
  .lesson-card { background: var(--panel); border: 1px solid var(--line); border-radius: 10px; padding: 22px 26px; box-shadow: 0 1px 4px rgba(0,0,0,0.02); }
  .lesson-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 10px; }
  .lesson-title-wrap { display: flex; align-items: baseline; gap: 10px; }
  .lesson-badge { background: var(--accent); color: #fff; font-size: 12px; font-weight: 700; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .lesson-title { font-size: 16px; font-weight: 700; color: var(--ink); margin: 0; }
  .lesson-citation { font-size: 12px; font-weight: 700; color: var(--accent); background: var(--accent-light); padding: 3px 8px; border-radius: 4px; white-space: nowrap; }
  
  .scripture-quote { margin: 10px 0 14px; padding: 10px 16px; background: #faf9f6; border-left: 3px solid var(--accent); font-family: Georgia, serif; font-size: 14.5px; font-style: italic; color: #2d2a26; line-height: 1.6; }
  
  .lesson-section { margin-top: 10px; }
  .section-tag { font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 3px; }
  .principle-text { font-size: 14px; line-height: 1.55; color: #222; margin: 0 0 10px; font-weight: 500; }
  .app-box { background: var(--accent-light); border-radius: 6px; padding: 10px 14px; }
  .app-box .section-tag { color: var(--accent-dark); }
  .app-text { font-size: 13.5px; color: var(--accent-dark); margin: 0; line-height: 1.5; }

  @media (max-width: 800px) {
    .app { grid-template-columns: 1fr; height: auto; }
    aside { height: 350px; }
    main { padding: 20px; }
  }
</style>
</head>
<body>

<div class="app">
  <aside>
    <div class="sidebar-header">
      <div class="brand-tag">864zeros Publish</div>
      <h1>Bible Study Library</h1>
      <div class="sub">66 Books · 660 Actionable Lessons</div>
    </div>
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="Search books, lessons, or topics..." oninput="handleSearch()" />
    </div>
    <div id="sidebarList"></div>
  </aside>

  <main>
    <div class="container" id="mainContainer"></div>
  </main>
</div>

<script>
const studyData = ${JSON.stringify(masterDoc)};
let currentBookIndex = 0;

function init() {
  renderSidebar();
  renderBook(0);
}

function renderSidebar(filteredBooks = null) {
  const booksToRender = filteredBooks || studyData.books;
  const listEl = document.getElementById('sidebarList');
  listEl.innerHTML = '';

  let currentCategory = '';
  const ul = document.createElement('ul');
  ul.className = 'book-list';

  booksToRender.forEach((b) => {
    const origIndex = studyData.books.findIndex(item => item.book === b.book);
    if (!filteredBooks && b.category !== currentCategory) {
      currentCategory = b.category;
      const catHeader = document.createElement('div');
      catHeader.className = 'section-label';
      catHeader.textContent = \`\${b.testament === 'OT' ? 'Old Testament' : 'New Testament'} · \${b.category}\`;
      ul.appendChild(catHeader);
    }

    const li = document.createElement('li');
    li.className = \`book-item \${origIndex === currentBookIndex ? 'active' : ''}\`;
    li.onclick = () => {
      currentBookIndex = origIndex;
      renderBook(origIndex);
      document.querySelectorAll('.book-item').forEach(el => el.classList.remove('active'));
      li.classList.add('active');
    };
    li.innerHTML = \`<span>\${b.book}</span><span class="book-num">\${b.order}</span>\`;
    ul.appendChild(li);
  });

  listEl.appendChild(ul);
}

function renderBook(index) {
  const b = studyData.books[index];
  if (!b) return;
  
  const container = document.getElementById('mainContainer');
  
  let html = \`
    <div class="book-banner">
      <div class="book-meta-row">
        <span class="pill">\${b.testament === 'OT' ? 'Old Testament' : 'New Testament'}</span>
        <span class="pill category">\${b.category}</span>
        <span style="color:var(--muted); font-size:12px; margin-left:auto;">Book \${b.order} of 66</span>
      </div>
      <h1 class="book-title">\${b.book}</h1>
      <p class="book-overview">\${b.overview}</p>
      
      <div class="themes-title">Core Themes</div>
      <div class="theme-chips">
        \${b.key_themes.map(t => \`<span class="theme-chip">\${t}</span>\`).join('')}
      </div>
    </div>

    <div class="lessons-heading">
      <div>10 Actionable Life Lessons</div>
      <span>\${b.lessons.length} Scripture Principles</span>
    </div>

    <div class="lessons-grid">
      \${b.lessons.map(l => \`
        <div class="lesson-card">
          <div class="lesson-head">
            <div class="lesson-title-wrap">
              <div class="lesson-badge">\${l.number}</div>
              <h3 class="lesson-title">\${l.title}</h3>
            </div>
            <span class="lesson-citation">\${l.citation}</span>
          </div>
          
          <div class="scripture-quote">"\${l.scripture_text}"</div>
          
          <div class="lesson-section">
            <div class="section-tag">Behavioral Principle / Rule</div>
            <p class="principle-text">\${l.lesson}</p>
          </div>

          <div class="app-box">
            <div class="section-tag">Daily Action Prompt</div>
            <p class="app-text">\${l.application}</p>
          </div>
        </div>
      \`).join('')}
    </div>
  \`;

  container.innerHTML = html;
  container.parentElement.scrollTop = 0;
}

function handleSearch() {
  const query = document.getElementById('searchInput').value.toLowerCase().trim();
  if (!query) {
    renderSidebar();
    renderBook(currentBookIndex);
    return;
  }

  const matchingBooks = studyData.books.filter(b => {
    if (b.book.toLowerCase().includes(query)) return true;
    if (b.overview.toLowerCase().includes(query)) return true;
    if (b.key_themes.some(t => t.toLowerCase().includes(query))) return true;
    if (b.lessons.some(l => 
      l.title.toLowerCase().includes(query) || 
      l.lesson.toLowerCase().includes(query) || 
      l.application.toLowerCase().includes(query) ||
      l.citation.toLowerCase().includes(query)
    )) return true;
    return false;
  });

  renderSidebar(matchingBooks);
  if (matchingBooks.length > 0) {
    const firstIdx = studyData.books.findIndex(b => b.book === matchingBooks[0].book);
    currentBookIndex = firstIdx;
    renderBook(firstIdx);
  } else {
    document.getElementById('mainContainer').innerHTML = \`<div style="text-align:center; padding:60px; color:var(--muted);">No books or lessons match "<b>\${query}</b>"</div>\`;
  }
}

window.onload = init;
</script>

</body>
</html>
`;

const viewerPath = path.join(sharedBibleDir, 'bible_study_viewer.html');
fs.writeFileSync(viewerPath, htmlViewer, 'utf8');
console.log(`Wrote self-contained HTML viewer to: ${viewerPath} (${(fs.statSync(viewerPath).size / 1024).toFixed(1)} KB)`);

