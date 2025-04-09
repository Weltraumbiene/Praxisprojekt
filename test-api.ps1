# UTF-8 für PowerShell-Ausgabe aktivieren
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$baseUrl = "http://127.0.0.1:8000"

# Hilfsfunktion für schöne Ausgabe
function Write-Section($title) {
    Write-Host "`n▶ $title"
}

# Test 1: GET /
Write-Section "Test 1: GET /"
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/" -Method GET
    $response | ConvertTo-Json -Depth 3
    Write-Host "✅ API erreichbar"
} catch {
    Write-Host "❌ API NICHT erreichbar: $($_.Exception.Message)"
}

# Test 2: Schlechter Kontrast
Write-Section "Test 2: POST /check mit schlechtem Kontrast"
$body1 = @{
    html = "<p>Hello World</p>"
    css  = "p { color: #000; background-color: #000; }"
} | ConvertTo-Json -Depth 3
$response = Invoke-RestMethod -Uri "$baseUrl/check" -Method POST -ContentType "application/json" -Body $body1
$response | ConvertTo-Json -Depth 3
Write-Host "⚠️  Test 2 hat Probleme:"
Write-Host "   ❌ Fehler: $($response.errors)"
Write-Host "   ⚠️  Warnungen: $($response.warnings)"
if ($response.css_issues) {
    Write-Host "   🎨 CSS-Issues:"
    foreach ($issue in $response.css_issues) {
        Write-Host "      - $issue"
    }
}

# Test 3: Guter Kontrast + semantisch korrekteres HTML
Write-Section "Test 3: POST /check mit verbessertem HTML"
$body2 = @{
    html = "<main><h1>Hello World</h1><p>Ein Absatz.</p></main>"
    css  = "p { color: #000; background-color: #fff; }"
} | ConvertTo-Json -Depth 3
$response = Invoke-RestMethod -Uri "$baseUrl/check" -Method POST -ContentType "application/json" -Body $body2
$response | ConvertTo-Json -Depth 3
Write-Host "⚠️  Test 3:"
Write-Host "   ❌ Fehler: $($response.errors)"
Write-Host "   ⚠️  Warnungen: $($response.warnings)"

$body_alt_url = @{
    url = "https://example.com"  # Verwende hier eine URL, von der du weißt, dass sie korrekt geladen wird.
    filter = @("headings", "images")
} | ConvertTo-Json -Depth 3 -Compress

# Lese den Inhalt der Datei als reinen Text (Raw)
$filepath = "C:\Users\bfranneck\Desktop\Projekte\sparmillionaer\index.html"
$htmlContent = Get-Content $filepath -Raw

# Erstelle den JSON-Payload ohne den Filter-Parameter
$body_real = @{
    html = $htmlContent
} | ConvertTo-Json -Depth 3 -Compress

Write-Section "Alternativer Test 4a: POST /extract-elements mit real existierender Datei"
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/extract-elements" -Method POST -ContentType "application/json" -Body $body_real
    $response | ConvertTo-Json -Depth 3
    # Hier prüfen wir, ob mindestens eine Überschrift extrahiert wurde (Anpassung je nach erwarteten Elementen)
    if ($response.headings.Count -ge 1) {
        Write-Host "✅ Alternativer Test 4a bestanden!"
    } else {
        Write-Host "❌ Alternativer Test 4a fehlgeschlagen: Elemente stimmen nicht überein."
    }
} catch {
    Write-Host "❌ Alternativer Test 4a Fehler: $($_.Exception.Message)"
}


Write-Section "Alternativer Test 4b: POST /extract-elements mit URL statt HTML"
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/extract-elements" -Method POST -ContentType "application/json" -Body $body_alt_url
    $response | ConvertTo-Json -Depth 3
    if ($response.headings.Count -ge 1) {
        Write-Host "✅ Alternativer Test 4b bestanden!"
    } else {
        Write-Host "❌ Alternativer Test 4b fehlgeschlagen: Keine Überschriften gefunden."
    }
} catch {
    Write-Host "❌ Alternativer Test 4b Fehler: $($_.Exception.Message)"
}

# Test 5: Fehlerfall – leeres JSON
Write-Section "Test 5: POST /check ohne Eingabe"
try {
    $body4 = @{} | ConvertTo-Json -Depth 3
    Invoke-RestMethod -Uri "$baseUrl/check" -Method POST -ContentType "application/json" -Body $body4
} catch {
    Write-Host "✅ Test 5 bestanden: Erwarteter Fehler -> $($_.Exception.Message)"
}