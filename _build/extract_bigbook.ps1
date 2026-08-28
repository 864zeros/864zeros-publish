# Extracts the 1939 (public-domain) text of the Big Book from the Dover EPUB
# into a structured big_book.json for the ClearStreak reader.
# Deliberately EXCLUDES Dover's modern (copyrighted) additions:
#   Introduction to the Dover Edition, About Bill W, cover/title/copyright/contents/dividers.

# Store paths (864zeros-publish). $outApp is the downstream consuming app (clearStreak repo) — deploy target.
$epub    = "C:\dev\864zeros-publish\sources\aa-bigbook-1939-full-PD.epub"
$outMain = "C:\dev\864zeros-publish\apps\clearstreak\big_book.json"
$outApp  = "C:\dev\clearStreak\app\src\main\assets\big_book.json"

Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead($epub)
function Read-Entry($name){
    $e = $zip.Entries | Where-Object { $_.FullName -eq $name }
    if (-not $e) { return "" }
    $sr = New-Object System.IO.StreamReader($e.Open())
    $t = $sr.ReadToEnd(); $sr.Close(); $t
}

# file (relative to OEBPS/) -> [title, section]. Order here defines reading order.
$plan = @(
    @{ file="html/0486480593_05_fore.html";     id="foreword";        title="Foreword";                      section="front"   },
    @{ file="html/0486480593_07_part01a.html";  id="doctors-opinion"; title="The Doctor's Opinion";          section="front"   },
    @{ file="html/0486480593_08_chapter01.html";id="ch01"; title="I. Bill's Story";              section="main" },
    @{ file="html/0486480593_09_chapter02.html";id="ch02"; title="II. There Is a Solution";      section="main" },
    @{ file="html/0486480593_10_chapter03.html";id="ch03"; title="III. More About Alcoholism";   section="main" },
    @{ file="html/0486480593_11_chapter04.html";id="ch04"; title="IV. We Agnostics";             section="main" },
    @{ file="html/0486480593_12_chapter05.html";id="ch05"; title="V. How It Works";              section="main" },
    @{ file="html/0486480593_13_chapter06.html";id="ch06"; title="VI. Into Action";              section="main" },
    @{ file="html/0486480593_14_chapter07.html";id="ch07"; title="VII. Working With Others";     section="main" },
    @{ file="html/0486480593_15_chapter08.html";id="ch08"; title="VIII. To Wives";               section="main" },
    @{ file="html/0486480593_16_chapter09.html";id="ch09"; title="IX. The Family Afterward";     section="main" },
    @{ file="html/0486480593_17_chapter10.html";id="ch10"; title="X. To Employers";              section="main" },
    @{ file="html/0486480593_18_chapter11.html";id="ch11"; title="XI. A Vision for You";         section="main" },
    @{ file="html/0486480593_20_chapter12.html";id="st01"; title="The Doctor's Nightmare";       section="stories" },
    @{ file="html/0486480593_21_chapter13.html";id="st02"; title="The Unbeliever";               section="stories" },
    @{ file="html/0486480593_22_chapter14.html";id="st03"; title="The European Drinker";         section="stories" },
    @{ file="html/0486480593_23_chapter15.html";id="st04"; title="A Feminine Victory";           section="stories" },
    @{ file="html/0486480593_24_chapter16.html";id="st05"; title="Our Southern Friend";          section="stories" },
    @{ file="html/0486480593_25_chapter17.html";id="st06"; title="A Business Man's Recovery";    section="stories" },
    @{ file="html/0486480593_26_chapter18.html";id="st07"; title="A Different Slant";            section="stories" },
    @{ file="html/0486480593_27_chapter19.html";id="st08"; title="Traveler, Editor, Scholar";   section="stories" },
    @{ file="html/0486480593_28_chapter20.html";id="st09"; title="The Back-Slider";              section="stories" },
    @{ file="html/0486480593_29_chapter21.html";id="st10"; title="Home Brewmeister";             section="stories" },
    @{ file="html/0486480593_30_chapter22.html";id="st11"; title="The Seventh Month Slip";       section="stories" },
    @{ file="html/0486480593_31_chapter23.html";id="st12"; title="My Wife and I";                section="stories" },
    @{ file="html/0486480593_32_chapter24.html";id="st13"; title="A Ward of the Probate Court";  section="stories" },
    @{ file="html/0486480593_33_chapter25.html";id="st14"; title="Riding the Rods";              section="stories" },
    @{ file="html/0486480593_34_chapter26.html";id="st15"; title="The Salesman";                 section="stories" },
    @{ file="html/0486480593_35_chapter27.html";id="st16"; title="Fired Again";                  section="stories" },
    @{ file="html/0486480593_36_chapter28.html";id="st17"; title="The Fearful One";              section="stories" },
    @{ file="html/0486480593_37_chapter29.html";id="st18"; title="Truth Freed Me!";              section="stories" },
    @{ file="html/0486480593_38_chapter30.html";id="st19"; title="Smile With Me, at Me";        section="stories" },
    @{ file="html/0486480593_39_chapter31.html";id="st20"; title="A Close Shave";                section="stories" },
    @{ file="html/0486480593_40_chapter32.html";id="st21"; title="Educated Agnostic";           section="stories" },
    @{ file="html/0486480593_41_chapter33.html";id="st22"; title="Another Prodigal Story";      section="stories" },
    @{ file="html/0486480593_42_chapter34.html";id="st23"; title="The Car Smasher";             section="stories" },
    @{ file="html/0486480593_43_chapter35.html";id="st24"; title="Hindsight";                    section="stories" },
    @{ file="html/0486480593_44_chapter36.html";id="st25"; title="On His Way";                   section="stories" },
    @{ file="html/0486480593_45_chapter37.html";id="st26"; title="An Alcoholic's Wife";          section="stories" },
    @{ file="html/0486480593_46_chapter38.html";id="st27"; title="An Artist's Concept";          section="stories" },
    @{ file="html/0486480593_47_chapter39.html";id="st28"; title="The Rolling Stone";            section="stories" },
    @{ file="html/0486480593_48_chapter40.html";id="st29"; title="Lone Endeavor";               section="stories" }
)

function Clean-Paragraphs($html) {
    # body only
    $m = [regex]::Match($html, '(?s)<body[^>]*>(.*?)</body>')
    $body = if ($m.Success) { $m.Groups[1].Value } else { $html }
    # drop page-anchor spans
    $body = [regex]::Replace($body, '<a\s+id="page_[^"]*"\s*/>', '')
    # collect only <p> blocks (skip h2/h4 headings — title stored separately)
    $paras = @()
    foreach ($pm in [regex]::Matches($body, '(?s)<p\b[^>]*>(.*?)</p>')) {
        $t = $pm.Groups[1].Value
        $t = [regex]::Replace($t, '<[^>]+>', '')           # strip inline tags
        $t = [System.Net.WebUtility]::HtmlDecode($t)
        $t = [regex]::Replace($t, '\s+', ' ').Trim()        # collapse whitespace
        if ($t.Length -gt 0) { $paras += $t }
    }
    ,$paras
}

$chapters = @()
$order = 1
$totalParas = 0
foreach ($item in $plan) {
    $html = Read-Entry ("OEBPS/" + $item.file)
    if ($html -eq "") { Write-Warning "MISSING: $($item.file)"; continue }
    $paras = Clean-Paragraphs $html
    $totalParas += $paras.Count
    $chapters += [ordered]@{
        id         = $item.id
        order      = $order
        section    = $item.section
        title      = $item.title
        paragraphs = $paras
    }
    "{0,2}. [{1,-7}] {2,-32} {3,4} paragraphs" -f $order, $item.section, $item.title, $paras.Count | Write-Output
    $order++
}
$zip.Dispose()

$doc = [ordered]@{
    title      = "Alcoholics Anonymous"
    subtitle   = "The Original 1939 Edition"
    edition    = "First Edition (1939)"
    rights     = "Public domain (original 1939 text). Dover-edition editorial additions excluded."
    source     = "aa-bigbook-1939-full-PD.epub (Dover reprint)"
    chapterCount = $chapters.Count
    chapters   = $chapters
}

$json = $doc | ConvertTo-Json -Depth 6
$utf8 = New-Object System.Text.UTF8Encoding($false)   # no BOM
[System.IO.File]::WriteAllText($outMain, $json, $utf8)
[System.IO.File]::WriteAllText($outApp,  $json, $utf8)

"`n--- DONE ---" | Write-Output
"Chapters: $($chapters.Count)   Paragraphs: $totalParas" | Write-Output
"Wrote: $outMain  ($([Math]::Round((Get-Item $outMain).Length/1KB,1)) KB)" | Write-Output
"Wrote: $outApp" | Write-Output
