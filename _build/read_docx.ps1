Add-Type -AssemblyName System.IO.Compression.FileSystem
function Read-Docx($path) {
    $zip = [System.IO.Compression.ZipFile]::OpenRead((Resolve-Path $path))
    $entry = $zip.Entries | Where-Object { $_.FullName -eq 'word/document.xml' }
    $stream = $entry.Open()
    $reader = New-Object System.IO.StreamReader($stream)
    $text = $reader.ReadToEnd()
    $reader.Close()
    $stream.Close()
    $zip.Dispose()
    [xml]$xml = $text
    $xml.document.body.p | ForEach-Object { $_.InnerText }
}

Write-Host "--- Bible {prompts} v1.docx ---"
Read-Docx "sources/Bible {prompts} v1.docx"

Write-Host "`n--- {Bible notation} Feb15.docx ---"
(Read-Docx "sources/{Bible notation} Feb15.docx" | Select-Object -First 30)
