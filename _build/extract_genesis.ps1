# extract_genesis.ps1 — Extracts Genesis chapters 1-10 from getbible.net (KJV, book 1)
# Staging raw chapters into _build/_src/ for real-world application authoring.

$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
$srcDir = Join-Path $PSScriptRoot "_src"
if (-not (Test-Path $srcDir)) { New-Item -ItemType Directory -Force -Path $srcDir | Out-Null }

Write-Host "Fetching Genesis (Book 1) KJV from getbible.net..."
$url = "https://api.getbible.net/v2/kjv/1.json"
$book = Invoke-RestMethod -Uri $url

Write-Host "Staging chapters 1 through 10 in $srcDir..."
for ($ch = 1; $ch -le 10; $ch++) {
    $chapData = $book.chapters | Where-Object { $_.chapter -eq $ch }
    if ($chapData) {
        $outFile = Join-Path $srcDir ("gen_ch{0:D2}.json" -f $ch)
        $chapData | ConvertTo-Json -Depth 5 | Set-Content -Path $outFile -Encoding UTF8
        Write-Host "  Wrote $outFile ($($chapData.verses.Count) verses)"
    }
}
Write-Host "Genesis 1-10 staging complete."
