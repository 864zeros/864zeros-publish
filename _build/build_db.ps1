# build_db.ps1 — Generate the DERIVED SQLite store from the JSON source-of-truth.
#
# JSON is authoritative. This DB is disposable, git-ignored, and safe to rebuild anytime.
# Usage:  pwsh _build/build_db.ps1
#   - always writes db/store.sql
#   - if sqlite3.exe is on PATH, also builds db/store.db from it
#
# Tables:
#   bible(book, chapter, citation, text, plain)
#   passages(id, reader_text, surface_text, faith_optional, moment, halt, urge_level,
#            stage, function, applies_to, reading_time, chapter_id, page, needs_clinical_review)

$ErrorActionPreference = "Stop"
$root     = Split-Path $PSScriptRoot -Parent
$bibleDir = Join-Path $root "shared\bible"
$csDir    = Join-Path $root "apps\clearstreak"
$dbDir    = Join-Path $root "db"
New-Item -ItemType Directory -Force -Path $dbDir | Out-Null
$sqlPath  = Join-Path $dbDir "store.sql"
$dbPath   = Join-Path $dbDir "store.db"

function Esc($s) { if ($null -eq $s) { return "" } return ($s -replace "'", "''") }

$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine("PRAGMA journal_mode=OFF; BEGIN;")
[void]$sb.AppendLine("DROP TABLE IF EXISTS bible;")
[void]$sb.AppendLine("DROP TABLE IF EXISTS passages;")
[void]$sb.AppendLine("CREATE TABLE passages(id TEXT PRIMARY KEY, reader_text TEXT, surface_text TEXT, faith_optional TEXT, moment TEXT, halt TEXT, urge_level TEXT, stage TEXT, function TEXT, applies_to TEXT, reading_time TEXT, chapter_id TEXT, page INT, needs_clinical_review INT);")
[void]$sb.AppendLine("DROP TABLE IF EXISTS bible_applications;
CREATE TABLE bible_applications(id TEXT PRIMARY KEY, chapter INT, citation TEXT, verbatim_text TEXT, plain_text TEXT, principle TEXT, takeaway TEXT, action_prompt TEXT, moments TEXT, domain TEXT, theme TEXT);
DROP TABLE IF EXISTS bible_study_books;
CREATE TABLE bible_study_books(book_order INT PRIMARY KEY, book TEXT, testament TEXT, category TEXT, overview TEXT, key_themes TEXT);
DROP TABLE IF EXISTS bible_study_lessons;
CREATE TABLE bible_study_lessons(book TEXT, lesson_number INT, title TEXT, citation TEXT, scripture_text TEXT, lesson TEXT, application TEXT, PRIMARY KEY(book, lesson_number));")

# --- shared/bible (walk the manifest) ---
$idx = Get-Content (Join-Path $bibleDir "bible_index.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$bcount = 0
$seen = New-Object System.Collections.Generic.HashSet[string]
foreach ($b in $idx.books) {
  # Multiple manifest entries can share one file+arrayKey (e.g. the 4 gospels all live in
  # gospels_daily.json). Load each physical array exactly once.
  if (-not $seen.Add("$($b.file)|$($b.arrayKey)")) { continue }
  $f = Join-Path $bibleDir $b.file
  if (-not (Test-Path $f)) { Write-Warning "missing bible file: $($b.file)"; continue }
  $data = Get-Content $f -Raw -Encoding UTF8 | ConvertFrom-Json
  $arr  = $data.($b.arrayKey)
  foreach ($v in $arr) {
    $ch = 0; [int]::TryParse("$($v.chapter)", [ref]$ch) | Out-Null
    [void]$sb.AppendLine("INSERT INTO bible VALUES('$(Esc $v.book)',$ch,'$(Esc $v.citation)','$(Esc $v.text)','$(Esc $v.plain)');")
    $bcount++
  }
}

# --- shared/bible real-world applications ---
$genAppFile = Join-Path $bibleDir "genesis_applications.json"
$appCount = 0
if (Test-Path $genAppFile) {
  $genApps = Get-Content $genAppFile -Raw -Encoding UTF8 | ConvertFrom-Json
  foreach ($a in $genApps.applications) {
    $moms = ($a.labels.moment -join "|")
    [void]$sb.AppendLine("INSERT OR REPLACE INTO bible_applications VALUES('$(Esc $a.id)',$($a.chapter),'$(Esc $a.citation)','$(Esc $a.verbatim_text)','$(Esc $a.plain_text)','$(Esc $a.real_world_function.principle)','$(Esc $a.real_world_function.takeaway)','$(Esc $a.real_world_function.action_prompt)','$(Esc $moms)','$(Esc $a.labels.domain)','$(Esc $a.labels.theme)');")
    $appCount++
  }
}

# --- shared/bible 66-book study lessons ---
$studyFile = Join-Path $bibleDir "bible_study_lessons.json"
$studyBookCount = 0
$studyLessonCount = 0
if (Test-Path $studyFile) {
  $studyData = Get-Content $studyFile -Raw -Encoding UTF8 | ConvertFrom-Json
  foreach ($b in $studyData.books) {
    $themes = ($b.key_themes -join " | ")
    [void]$sb.AppendLine("INSERT OR REPLACE INTO bible_study_books VALUES($($b.order),'$(Esc $b.book)','$(Esc $b.testament)','$(Esc $b.category)','$(Esc $b.overview)','$(Esc $themes)');")
    $studyBookCount++
    foreach ($l in $b.lessons) {
      [void]$sb.AppendLine("INSERT OR REPLACE INTO bible_study_lessons VALUES('$(Esc $b.book)',$($l.number),'$(Esc $l.title)','$(Esc $l.citation)','$(Esc $l.scripture_text)','$(Esc $l.lesson)','$(Esc $l.application)');")
      $studyLessonCount++
    }
  }
}

# --- apps/clearstreak passages ---
$pc    = Get-Content (Join-Path $csDir "passages_core.json") -Raw -Encoding UTF8 | ConvertFrom-Json
$plist = if ($pc.passages) { $pc.passages } else { $pc }
$pcount = 0
foreach ($p in $plist) {
  $mom = ($p.labels.moment -join "|")
  $app = ($p.applies_to -join "|")
  $ncr = if ($p.needs_clinical_review) { 1 } else { 0 }
  $pg  = 0; [int]::TryParse("$($p.source.page)", [ref]$pg) | Out-Null
  [void]$sb.AppendLine("INSERT OR REPLACE INTO passages VALUES('$(Esc $p.id)','$(Esc $p.reader_text)','$(Esc $p.surface_text)','$(Esc $p.faith_optional)','$(Esc $mom)','$(Esc $p.labels.halt)','$(Esc $p.labels.urge_level)','$(Esc $p.labels.stage)','$(Esc $p.labels.function)','$(Esc $app)','$(Esc $p.reading_time)','$(Esc $p.source.chapter_id)',$pg,$ncr);")
  $pcount++
}

[void]$sb.AppendLine("COMMIT;")
Set-Content -LiteralPath $sqlPath -Value $sb.ToString() -Encoding UTF8
"wrote $sqlPath  (bible=$bcount, applications=$appCount, study_books=$studyBookCount, study_lessons=$studyLessonCount, passages=$pcount)"

$sqlite = Get-Command sqlite3 -ErrorAction SilentlyContinue
if ($sqlite) {
  if (Test-Path $dbPath) { Remove-Item $dbPath -Force }
  Get-Content $sqlPath -Raw | & sqlite3 $dbPath
  "built $dbPath via sqlite3"
} else {
  "sqlite3 not on PATH - to build the db run:  sqlite3 db/store.db `".read db/store.sql`""
}
