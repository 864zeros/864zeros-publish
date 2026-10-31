# build_bible_questions.ps1 - Merge & validate the 6 canonical Question Engine shards into
# shared/bible/bible_questions.json, shared/bible/BIBLE_QUESTIONS.md, and bible_questions_viewer.html.

$ErrorActionPreference = "Stop"
$root     = Split-Path $PSScriptRoot -Parent
$srcDir   = Join-Path $PSScriptRoot "_src"
$bibleDir = Join-Path $root "shared\bible"

$shards = @(
  "questions_shard_a_books_01_10.json",
  "questions_shard_b_books_11_22.json",
  "questions_shard_c_books_23_39.json",
  "questions_shard_d_books_40_44.json",
  "questions_shard_e_books_45_55.json",
  "questions_shard_f_books_56_66.json",
  "questions_shard_g1_ot_geography.json",
  "questions_shard_g2_nt_geography.json"
)

$validCategories = @(
  "GEOGRAPHY_AND_PLACES",
  "DECISION_UNDER_PRESSURE",
  "HUMAN_NATURE_AND_MOTIVE",
  "PARADOX_AND_CONSEQUENCE",
  "RELATIONAL_FRICTION",
  "CORE_ARGUMENT_AND_LAW",
  "BIG_PICTURE_ARC"
)

$allQuestions = New-Object System.Collections.Generic.List[object]
$seenQids     = New-Object System.Collections.Generic.HashSet[string]
$catCounts    = @{}
foreach ($c in $validCategories) { $catCounts[$c] = 0 }
$idxCounts    = @{ 0 = 0; 1 = 0; 2 = 0; 3 = 0 }
$diffCounts   = @{ 1 = 0; 2 = 0; 3 = 0 }
$bookSet      = New-Object System.Collections.Generic.HashSet[string]

foreach ($s in $shards) {
  $p = Join-Path $srcDir $s
  if (-not (Test-Path $p)) { throw "Missing shard: $p" }
  $data = Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json
  $qlist = if ($data.questions) { $data.questions } else { $data }
  foreach ($q in $qlist) {
    if (-not $q.qid) { throw "Missing qid in $s" }
    if (-not $seenQids.Add($q.qid)) {
      throw "Duplicate qid: $($q.qid) in $s"
    }
    if ($validCategories -notcontains $q.category) {
      throw "Invalid category '$($q.category)' on $($q.qid) in $s"
    }
    if ($q.options.Count -ne 4) {
      throw "Question $($q.qid) does not have exactly 4 options"
    }
    if ($q.correct_index -lt 0 -or $q.correct_index -gt 3) {
      throw "Invalid correct_index $($q.correct_index) on $($q.qid)"
    }
    if ($q.difficulty -lt 1 -or $q.difficulty -gt 3) {
      throw "Invalid difficulty $($q.difficulty) on $($q.qid)"
    }
    $catCounts[$q.category]++
    $idxCounts[[int]$q.correct_index]++
    $diffCounts[[int]$q.difficulty]++
    [void]$bookSet.Add($q.book)
    $allQuestions.Add($q)
  }
}

$sorted = $allQuestions | Sort-Object book_order, chapter, verse_start, difficulty, qid

$otCount = ($sorted | Where-Object { $_.testament -eq "OT" }).Count
$ntCount = ($sorted | Where-Object { $_.testament -eq "NT" }).Count

$master = [ordered]@{
  _meta = [ordered]@{
    title           = "864zeros Bible Question Engine - Comprehension & Real-World Trivia Dataset"
    role            = "Self-contained, translation-agnostic multiple-choice cards serving both post-reading chapter/book comprehension quizzes and standalone Trivial Pursuit-style trivia decks across Easy (1), Medium (2), and Hard (3) tiers."
    schema_version  = "1.1"
    generated       = "2026-10-27"
    governance      = "Sloane Sterling (VP-STUDIO) & Julian Thorne (LEAD-CONTENT)"
    license         = "Original 864zeros authorship anchored to public-domain biblical narratives (17 U.S.C. Public Domain)."
    total_books     = $bookSet.Count
    total_questions = $sorted.Count
    ot_questions    = $otCount
    nt_questions    = $ntCount
    difficulty_counts = [ordered]@{
      "1_easy"   = $diffCounts[1]
      "2_medium" = $diffCounts[2]
      "3_hard"   = $diffCounts[3]
    }
    categories      = $validCategories
    category_counts = $catCounts
    answer_index_distribution = [ordered]@{
      "0" = $idxCounts[0]
      "1" = $idxCounts[1]
      "2" = $idxCounts[2]
      "3" = $idxCounts[3]
    }
    phase_2_roadmap = "Geography & Real-World Biblical Locations Question Pack (scheduled next after 66-book 3-tier completion)"
  }
  questions = $sorted
}

$outJsonPath = Join-Path $bibleDir "bible_questions.json"
$master | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $outJsonPath -Encoding UTF8

# Generate human-readable companion doc shared/bible/BIBLE_QUESTIONS.md
$md = New-Object System.Text.StringBuilder
[void]$md.AppendLine('# 864zeros Bible Question Engine - Canonical Dataset (`bible_questions.json`)')
[void]$md.AppendLine("")
[void]$md.AppendLine("**Self-contained, translation-agnostic comprehension & Trivial Pursuit-style trivia dataset** authored in the 864zeros real-world voice across all **$($bookSet.Count) canonical books** of the Bible, balanced across **Easy (`1` - ultra-simplified language)**, **Medium (`2` - human motive & tension)**, and **Hard (`3` - deep cross-scripture synthesis)**.")
[void]$md.AppendLine("")
[void]$md.AppendLine('- **Master JSON Asset:** [`bible_questions.json`](bible_questions.json)')
[void]$md.AppendLine('- **Interactive HTML Viewer:** [`bible_questions_viewer.html`](bible_questions_viewer.html)')
[void]$md.AppendLine('- **System Prompt & Schema Spec:** [`../../_build/_src/BIBLE_QUESTION_ENGINE_PROMPT.md`](../../_build/_src/BIBLE_QUESTION_ENGINE_PROMPT.md)')
[void]$md.AppendLine("- **Total Questions:** **$($sorted.Count)** (OT: $otCount | NT: $ntCount)")
[void]$md.AppendLine("- **Difficulty Split:** Easy (`1`): **$($diffCounts[1])** | Medium (`2`): **$($diffCounts[2])** | Hard (`3`): **$($diffCounts[3])**")
[void]$md.AppendLine("- **Total Books Covered:** **$($bookSet.Count) / 66**")
[void]$md.AppendLine("- **Phase 2 Roadmap Note:** Dedicated *Geography & Real-World Locations* Question Pack queued next.")
[void]$md.AppendLine("")
[void]$md.AppendLine("## 6-Category Trivial Pursuit Distribution")
[void]$md.AppendLine("")
[void]$md.AppendLine("| Category Enum | Count |")
[void]$md.AppendLine("|---|---:|")
foreach ($c in $validCategories) {
  [void]$md.AppendLine("| ``$c`` | $($catCounts[$c]) |")
}
[void]$md.AppendLine("")
[void]$md.AppendLine("## Per-Book Question & Difficulty Breakdown")
[void]$md.AppendLine("")
[void]$md.AppendLine("| # | Book | Testament | Total | Easy (1) | Medium (2) | Hard (3) |")
[void]$md.AppendLine("|---:|---|---:|---:|---:|---:|---:|")

$byBook = $sorted | Group-Object book_order | Sort-Object { [int]$_.Name }
foreach ($g in $byBook) {
  $first = $g.Group[0]
  $e1 = ($g.Group | Where-Object { $_.difficulty -eq 1 }).Count
  $m2 = ($g.Group | Where-Object { $_.difficulty -eq 2 }).Count
  $h3 = ($g.Group | Where-Object { $_.difficulty -eq 3 }).Count
  [void]$md.AppendLine("| $($first.book_order) | **$($first.book)** | $($first.testament) | **$($g.Count)** | $e1 | $m2 | $h3 |")
}

$outMdPath = Join-Path $bibleDir "BIBLE_QUESTIONS.md"
Set-Content -LiteralPath $outMdPath -Value $md.ToString() -Encoding UTF8

# Generate interactive HTML viewer shared/bible/bible_questions_viewer.html
$tplPath = Join-Path $srcDir "bible_questions_viewer_template.html"
if (Test-Path $tplPath) {
  $tpl = Get-Content -LiteralPath $tplPath -Raw -Encoding UTF8
  $compactJson = $master | ConvertTo-Json -Depth 10 -Compress
  $htmlOut = $tpl.Replace("{{QUESTIONS_JSON}}", $compactJson)
  $outHtmlPath = Join-Path $bibleDir "bible_questions_viewer.html"
  Set-Content -LiteralPath $outHtmlPath -Value $htmlOut -Encoding UTF8
}

"Built $outJsonPath ($($sorted.Count) questions: Easy=$($diffCounts[1]), Med=$($diffCounts[2]), Hard=$($diffCounts[3]) across $($bookSet.Count) books), $outMdPath, and bible_questions_viewer.html"
