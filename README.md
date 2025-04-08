Praxisprojekt
Projektübersicht

Entwicklung einer Python-basierten Anwendung zur automatisierten Überprüfung von Webseiten im Hinblick auf Barrierefreiheit.
Entwicklungsumgebung
Voraussetzungen

    Python 3.x installiert

    Node.js (inkl. NPM) installiert

Python-Setup

    Installiere die benötigten Python-Bibliotheken:

pip install fastapi uvicorn

Installiere Playwright für das Testen der API:

    pip install playwright
    playwright install

Projektordner

    Link zum Projektordner:
    cd C:\Users\b-----eck\Desktop\Praxisprojekt\Anwendung

    Link zum Python-Ordner:
    cd C:\Users\b-----eck\Desktop\Praxisprojekt\Anwendung\python

Server starten

    Starte den Python-Server:

python -m uvicorn main:app --reload

Server stoppen mit: Ctrl + C

Überprüfen, ob der Server aktiv ist:

    tasklist | findstr uvicorn

Testen der API
Server-Test

    Teste, ob der Server läuft:

    http://127.0.0.1:8000

API-Test (Web-Dokumentation)

    API-Dokumentation aufrufen:

    http://127.0.0.1:8000/docs

API-Test via CURL (CMD)

    CURL-Request (Windows CMD):

    curl -X 'POST' 'http://127.0.0.1:8000/check' -H 'Content-Type: application/json' -d '{ "url": "https://example.com" }'

API-Test via CURL (PowerShell)

    CURL-Request (Windows PowerShell):

    Invoke-RestMethod -Uri "http://127.0.0.1:8000/check" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"url": "https://example.com"}'

Node.js-Setup

    Installiere Node.js (inkl. NPM):

        Node.js Download

    Setze Execution Policy auf "Unrestricted" (PowerShell als Administrator ausführen):

Set-ExecutionPolicy Unrestricted -Scope CurrentUser

Teste die Installation:

node -v
npm -v

Installiere die benötigten Node.js-Pakete:

    npm install puppeteer axe-core

Weitere Tests

    FastAPI läuft in Python daher:

pip install playwright
playwright install

Testen der API (PowerShell):

    Invoke-RestMethod -Uri "http://127.0.0.1:8000/check" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"url": "https://www.beispiel.de"}'

Projekt-Zeitleiste
03.04.2025 - 8:00 - 9:00

Erste Zusammenfassung und Beschreibung des geplanten Projekts (Beschreibung.docx)
03.04.2025 - 9:00 - 11:30

Detaillierter Aufbau der Arbeitsschritte (Arbeitsplan.docx)
04.04.2025 - 8:30 - 10:30

Erstellen einer To-Do-Liste und Aufbaustruktur zur Erstellung der Anwendung
04.04.2025 - 11:00 - 13:00

Erstellen eines MVP (Minimum Viable Product)
07.04.2025 - 7:00 - 9:30

Einrichten eines Repositorys auf Git, Erstellen von Dokumenten zum Praxisprojekt, Gitignore
07.04.2025 - 9:30 - 19.00 Uhr

Erweiterung der bestehenden Basis-Funktion für lokale HTML und CSS-Dateien
Konsolentests
Basis-Konsolentest für URL

Invoke-RestMethod -Method POST http://localhost:8000/check -Headers @{ "Content-Type" = "application/json" } -Body '{ "html": "" }'

08.04.2025 - 7:00 - 
Spezifischer Test (lokaleHTML-Datei)

$htmlContent = Get-Content "C:\Users\bfranneck\Desktop\Projekte\sparmillionaer\index.html" -Raw
$body = @{

    html = [string]$htmlContent
} | ConvertTo-Json
Invoke-RestMethod -Method POST http://localhost:8000/check `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body $body

    Schwierigkeiten: Die Überprüfung von klassichen HTML Dateien verläuft problemlos, aber Fragmente 
    und SPA Routes werden nicht überprüft und lösen einen Fehler aus. Ich habe die Funktion erweitert und es wird nun automatisch ein HTML-Head eingefügt, um die Datei lesbar zu machen. Sollte es aber zu Fehlern in der HTML selbst kommen, wird weiterhin der Fehler 400 ausgegeben. Es ist mir bisher nicht möglich gewesen, dieses Problem zu beheben.

    Es ist jetzt aber möglich auch ganze (Projekt)-Ordner zu überprüfen, so das alle HTML Dateien geladen werden.
