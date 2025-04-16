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

pip install -r requirements.txt


Installiere Playwright für das Testen der API:

    pip install playwright
    playwright install

anschließend:
    pip install tinycss2 colormath


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

08.04.2025 - 7:00 - 11 Uhr
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

08.04.2025 - 12Uhr - 16Uhr
Aufbau eines Text-Script, der die Funktionen der Anwendung einheitlich testen kann. ".\python\test-api.ps1"

09.04.2025 - 8Uhr - 12 Uhr
Test des Testscripts. Erfolgreich.
Beginn der Front-End Entwicklung mit React VITE (Typescripe)

09.04.2025 12- 14 Uhr
Absprache mit einen Kollegen. Klärung von Fragen. Abgleichen der jeweiligen Arbeit. Ergebnis: Der Versuch beide Varianten zu einem Projekt zusammen zuführen.

09.04.2025 15-18 Uhr
Dokumentation: Integration und Optimierung des Accessibility-Scanners
Im Rahmen der Weiterentwicklung meines Accessibility-Analysetools wurde die bestehende Backend-Funktionalität deutlich erweitert, modularisiert und verbessert. Ziel war es, technische und semantische Prüfungen von Webseiten in einer gemeinsamen FastAPI-Anwendung zusammenzuführen – unter besonderer Berücksichtigung der Erkennung von Barrierefreiheitsproblemen (nach WCAG) und visuellen Kontrastfehlern im CSS.

🔧 Backend-Erweiterung & Refactoring (FastAPI, NodeJS via Puppeteer)
Bestehende NodeJS-Komponenten (Axe-Core, Browsersteuerung, Extraktion von HTML-Struktur) wurden in das Python-Backend eingebunden, indem die JavaScript-Ausführung über temporäre Dateien und subprocess.run() umgesetzt wurde.

Der bestehende Endpunkt /check wurde überarbeitet:

HTML-Laden per Puppeteer

AXE-Analyse für WCAG 2.1 A/AA und Best Practices

Strukturelle Validierung: z. B. <h1>-Existenz, Alt-Attribute bei Bildern etc.

CSS-Kontrastanalyse wurde neu implementiert (basierend auf TinyCSS2):

Analyse von color vs. background-color oder background

Unterstützung für #hex, rgb(), rgba(), und (in Teilen) Farbnamen

Abfangen von ungeeigneten Werten wie linear-gradient() oder url(...)

Der alte Ansatz, CSS-Dateien über requests.get() herunterzuladen, wurde ersetzt durch:

eine komplette Extraktion aus dem DOM-Kontext des Browsers

Nutzung von page.evaluate(...) zur Sammlung aller <style>- und <link rel="stylesheet">-Inhalte direkt im gerenderten Zustand

Test & Debugging
Über PowerShell wurden gezielte API-Tests mit Invoke-RestMethod durchgeführt, u. a. mit realer Zielseite https://www.benclaus.de

Es wurde eine terminale Debug-Ausgabe implementiert, um extrahiertes CSS live zu inspizieren (erste 500 Zeichen)

Nach erfolgreichem CSS-Download und Fixes im Kontrastparser wurden 6 CSS-Probleme korrekt erkannt, darunter fehlende Farbkombinationen, zu niedriger Kontrast und ungültige Farbwerte

AXE-Analyse erkannte parallel Fehler wie:

leere Überschriften (empty-heading)

fehlende Landmark-Struktur (region)

unvollständige Farbangaben (color-contrast als "incomplete")

Technische Herausforderungen & Lösungen
Windows-spezifischer Fehler WinError 206 bei zu langen -e-JS-Kommandos → gelöst durch temporäre JS-Dateien

Analyse von Fehlerursachen per traceback.print_exc() im FastAPI-Errorhandling

🌐 Probleme mit fetch(...)-Barrieren (z. B. CSP oder CORS) wurden über try/catch im JS-Code abgefangen

16.04.2025 - 7.30
Pflege des GitProfils. Aufräumen von Junk-Dateien. In den letzten Tagen nicht viel gemacht, da andere Arbeit vorang hatte.
Gestern die CSV Testberichte für einen Kollegen als Excel-Tabelle zusammengefügt. Teammeeting über die Pro's und Contra's der aktuellen
Testberichte. Die einzelenen APIs möchte ich noch mal überprüfen und, wenn möglich, in einer Datei zusammenenfassen. Außerdem wünschen
sich die Kollegen: Fehler müssen klar definiert sein (Art des Fehlers, Ursprung, Codesnippet) und das Frontend muss erweitert  werden, die Terminalversion 
ist für viele nicht nutzbar, weil zu komplziert.
Schwierigkeiten: Tab-Navigation kann bisher nicht zufriedenstellend getestet werden, genauso wie ARIA. Kommunikation zwischen Frontend und BackEnd ist holprig.