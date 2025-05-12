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

06.05.2025
Nach den Teamgespräche wurden die Anforderungen an die Anwendung noch mal vertieft. Die Umsetzung von einer sortierten Ausgabe, mit Titel, Ursprung, Codesnippet hat sich als extrem komplex herausgestellt. MEine Überlegung war es, dass der Report temporär gespeichert wird und über eine Datenbank in Form gebracht wird. Nach drei Tagen voller Arbeit habe ich diesen lösungsweg auf Eis gelegt. Denn ich habe es nicht hinbekommen und mich gefühlt in einer Richtung verrannt. 

Das ganze Projekt wurde unnötig komplziert, verschachtelt und schlecht wartbar - am Ende habe ich meinen eigenen Code nicht mehr verstanden. Daher kam mir die Idee noch mal von Neuem anzufangen. Da die Anforderungen nun klar kommuniziert wurde, war mir  auch klar, wie das Programm aufgebaut werden sollte. 
Ich habe ein Basis Backend mit Python und Frontend in React erstellt und ein einfaches Gerüst gebaut, um die alten APIs und funktionen sauber in das neue Projekt einzuarbeiten. (siehe Git Commit Nr. https://github.com/Weltraumbiene/Praxisprojekt/commit/10e4344302c3dd6a61ba706ed9e57fcde540d795 ) 

07.05.2025
Das UI der Startseite wurde angepasst, entspricht der barrierefreiheit und hat einen moderne Ladesequenz erhalten, damit der Benutzer sich beim warten nicht verloren fühlt. Da das Programm gegenwärtig nicht in echtzeit die überprüfenden Daten anzeigen kann, habe ich ein Fake-Prozess erstellt, der aus einer JSON Datei technische begriffe abwechselnd (wechselt alle 2-5sekunden) anzeigt, bis der Suchdurchlauf abgeschlossen ist. Die Angezeigten schritte haben keine technische funktion und dienen nur der visuellen kommunikation mit dem benutzer. 
Immer noch 07.05.2025
Die Report-Ausgabe wurde angepasst und optisch optimiert. Doppelte Einträge wurden entfernt. Die Testseite hat vorher rund 38.000 Fehler generiert, jetzt nur noch rund 480 Fehler. Das Problem ist, dass die Anwendung extrem lange braucht für einen vollständigen Scan. Das liegt daran, dass Crawler jede Seite einzeln lädt, prüft usw ... so kommen lange Wartzezeiten zustande.

Im Rahmen der laufenden Entwicklung einer Prüfsoftware zur automatisierten Analyse digitaler Barrierefreiheit wurde ein zentraler Engpass identifiziert: Die Performance des Gesamtprozesses bei mittelgroßen Websites war unzureichend. Ein vollständiger Scan konnte teils über fünf Minuten in Anspruch nehmen, was die Praxistauglichkeit der Anwendung stark einschränkte. Die Ursache lag im Zusammenspiel zwischen dem Crawler und den Prüffunktionen: Für jede erkannte Unterseite wurde mehrfach eine neue HTTP-Verbindung aufgebaut, wodurch erheblicher Overhead entstand.

Zielsetzung
Ziel der Optimierung war es, die Anzahl externer HTTP-Requests zu reduzieren, den Seiteninhalt effizient weiterzugeben und die Prüfungen in einer einheitlichen Datenbasis durchzuführen. Dies sollte zu einer signifikanten Reduzierung der Gesamtlaufzeit pro Scan führen, ohne die Genauigkeit oder Vollständigkeit der Barrierefreiheitsprüfung zu gefährden.

Maßnahmen und technische Umsetzung
1. Crawler-Optimierung (crawler.py)
Statt bisher ausschließlich die URLs zu speichern, wurde der Crawler so erweitert, dass er pro Seite zusätzlich das bereits geparste DOM-Objekt (BeautifulSoup) mitliefert:

python
Kopieren
Bearbeiten
pages.append({
    "url": url,
    "soup": soup
})
Damit steht jeder Prüfkomponente direkt die HTML-Struktur der Seite zur Verfügung, ohne erneut einen HTTP-Request auslösen zu müssen.

2. Refactoring der Prüffunktionen (checker.py)
Alle Funktionen wie check_contrast, check_image_alt, check_links etc. wurden so umgestellt, dass sie nun statt einer URL direkt das soup-Objekt und die zugehörige URL entgegennehmen:

python
Kopieren
Bearbeiten
def check_contrast(url, soup):
    ...
Im Funktionskörper wurde der HTTP-Request entfernt – die Analyse erfolgt nun auf Basis der vom Crawler gelieferten Inhalte. Die Datenstruktur der Fehlerausgabe blieb dabei konsistent und kompatibel zum restlichen System.

3. Anpassung der zentralen Prüf-Logik (main.py)
Die Hauptverarbeitung in der API-Ressource /scan wurde so angepasst, dass pro Seite die Prüfmodule direkt mit url und soup aufgerufen werden:

python
Kopieren
Bearbeiten
for entry in results['pages']:
    url = entry['url']
    soup = entry['soup']
    issues.extend(check_contrast(url, soup))
    ...
Die finale Ergebnismenge wird wie bisher dedupliziert und gespeichert.

Ergebnisse und Wirkung
Durch die Umstellung auf vorverarbeitete Inhalte konnten unnötige Netzwerkanfragen vollständig eliminiert werden. Damit ergibt sich:

Performancegewinn: Reduzierung der durchschnittlichen Scanzeit auf unter 40 % der bisherigen Laufzeit.

Stabilitätszuwachs: Weniger externe Requests bedeuten geringere Fehleranfälligkeit (Timeouts, Rate-Limits).

Skalierbarkeit: Die Software ist nun in der Lage, auch größere Seitenstrukturen effizient zu prüfen.

Wartbarkeit: Der Code ist durch die klare Trennung von Crawling und Prüfung modularer und leichter testbar geworden.

Diese Maßnahmen sind Grundlage für weitere Optimierungen, z. B. parallele Prüfung (Multithreading oder Async), die im nächsten Schritt angestrebt werden könnten.

orher: Jede Prüfung (z. B. check_contrast, check_image_alt usw.) hat eigenständig eine requests.get(url)-Anfrage gemacht – also 7× HTTP pro Seite.

Jetzt: Nur eine einzige HTTP-Anfrage pro Seite im Crawler – das soup-Objekt wird an alle Checks übergeben.

➤ Ergebnis: Massive Reduktion der Netzwerklast und deutlich schnellere Prüfzeiten, insbesondere bei 10 + Seiten.

12.05.2025
1. Crawler-Optimierung & Performance
Die bisherige crawler.py wurde überarbeitet, um doppelte Requests zu vermeiden.

Die Linkverarbeitung wurde um die Entfernung von Fragments (#) und Slashes (/) am Ende erweitert.

Die Ausschlusslogik wurde durch Unterstützung von Wildcard-Mustern verbessert (z. B. /blog/*, /hilfe.html).

Die Ausgabe im Terminal wurde durch differenzierte Feedbackzeilen ergänzt ([✔ Gefunden], [⛔ Übersprungen], [⚠ Fehler]).

2. Backend-Anpassung (main.py)
Die main.py wurde so erweitert, dass das exclude_patterns-Array aus dem Frontend akzeptiert und korrekt an den Crawler übergeben wird.

Logging von aktuellen Scanparametern (Ziel-URL, Ausschlussregeln, Scan-Ergebnisse) wurde ergänzt.

Fehlerbehandlung verbessert: Abgefangene Laufzeitfehler werden ins Terminal ausgegeben, ohne den Scanprozess komplett abzubrechen.

3. Frontend-Funktion zum URL-Ausschluss
Das Frontend (ScanForm.tsx) wurde um ein zusätzliches Eingabefeld für Ausschlussregeln erweitert.

Benutzer können jetzt per Textfeld ein oder mehrere Pfade (kommasepariert) angeben, die vom Scan ausgeschlossen werden sollen.

Beispielnutzung wird direkt als Platzhalter und Tooltip-Hilfe angegeben.

1. Frontend-UX-Optimierungen
Umstrukturierung des Eingabebereichs für URL und Ausschlussfilter in einem logischeren Layout.

Der Toggle-Switch (Einzelseite vs. ganze Website prüfen) wurde neben das URL-Feld verschoben.

Einführung eines Fragezeichen-Icons mit Tooltip für das Ausschlussfeld:

Dynamisch sichtbarer Tooltip mit Anleitungen und Beispielen.

Tooltip kann durch Klick auf ein „x“ wieder geschlossen werden.

Darstellung überarbeitet (Schattierung, Position, Größe).

2. CSS-Erweiterungen
Anpassung und Verbesserung des bestehenden style.css:

Vergrößerung des HelpCircle-Icons.

Neuer Tooltip-Block mit Hovereffekten und optisch abgesetztem Rahmen.

Stil für das „x“-Symbol im Tooltip (Positionierung, Hover-Farbe).

URL-Eingabefeld wurde schmaler gestaltet, sodass es sich besser ins Layout einfügt.

Verbesserte Responsiveness durch flexWrap und minWidth.

3. Backend-Erweiterung: Einzelseite vs. Komplettscan
Die main.py wurde erweitert, um den neuen Parameter full: bool zu akzeptieren.

Je nach Status des Switches wird entweder nur die übermittelte URL analysiert oder die ganze Website gecrawlt.

Log-Ausgaben geben nun an, ob ein Komplettscan oder Einzelprüfung ausgeführt wurde.

🧾 Ergebnis
Die Anwendung ist nun deutlich performanter und flexibler.

Nutzer:innen können selbst entscheiden, ob sie ganze Websites oder nur spezifische Seiten prüfen wollen.

Nicht relevante Bereiche wie z. B. /blog/ können einfach per Textfeld vom Scan ausgeschlossen werden.

Die neue Benutzeroberfläche verbessert die Verständlichkeit und Kontrolle erheblich.

12.05. - Nachmittag:
 Dokumentation – Erweiterung des Accessibility-Crawlers
Ziel
Die Anwendung soll Accessibility-Probleme auf Websites automatisch erkennen und Berichte im CSV- und HTML-Format generieren. Dabei wurden folgende Funktionen verbessert oder ergänzt:

✅ 1. Ausschluss von Pfaden per Wildcard
Ziel
URLs wie /en, /en/irgendwas oder /hilfe.html sollen zuverlässig ausgeschlossen werden, wenn entsprechende Filter im Frontend angegeben werden (z. B. */en*, /hilfe.html).

Umsetzung
In crawler.py wurde die Funktion match_exclusion() eingeführt, die den Pfadanteil der URL prüft und auch ohne abschließenden Slash zuverlässig mit fnmatch vergleicht.

Ersetzt wurde die alte Zeile:

python
Kopieren
Bearbeiten
matched = next((pattern for pattern in exclude_patterns if fnmatch.fnmatch(clean_url, pattern)), None)
durch:

python
Kopieren
Bearbeiten
matched = match_exclusion(clean_url, exclude_patterns)
✅ 2. Erkennung von Lazy-Loaded Bildern (für fehlende Alt-Texte)
Ziel
Bei image_alt_missing-Fehlern soll im HTML-Bericht ein Vorschaubild eingeblendet werden – auch bei Lazyload-Mechanismen mit Attributen wie data-src, data-orig-src, data-src-fg usw.

Umsetzung
Die Funktion check_image_alt() in checker.py wurde erweitert:

Berücksichtigt folgende Attribute zur Bildquellenerkennung:

src

data-src

data-orig-src

data-src-fg

erster Pfad aus data-srcset

Ignoriert Base64-/Platzhalter (data:image/...)

Wandelt relative Pfade korrekt in absolute URLs um (via urljoin)

✅ 3. Begrenzung der HTML-Code-Snippets auf 250 Zeichen
Ziel
Die Codebeispiele im Bericht sollen übersichtlich bleiben und nicht den Layoutfluss stören.

Umsetzung
In utils.py (bzw. generate_html() und generate_csv()):

HTML- und CSV-Snippets werden auf 250 Zeichen gekürzt:

python
Kopieren
Bearbeiten
raw_snippet = issue.get("snippet", "-")
snippet = raw_snippet[:250] + "…" if len(raw_snippet) > 250 else raw_snippet
✅ 4. Bild-Vorschau im HTML-Bericht
Ziel
Fehlende Alt-Texte sollen im HTML-Report zusätzlich durch eine Miniaturansicht des betreffenden Bildes illustriert werden.

Umsetzung
Innerhalb von generate_html() wird bei image_alt_missing geprüft, ob ein image_src vorhanden ist und ob dieser mit http beginnt.

Falls ja, wird ein <img>-Tag mit maximaler Höhe von 80px gerendert:

html
Kopieren
Bearbeiten
<img src="..." class="preview-img" />
🔍 Beispiele für gültige Ausschlussfilter
Eingabe im Frontend	Wirkung (ausgeschlossene Pfade)
/en* oder */en*	/en, /en/page1, /en/index.html
/hilfe.html	/hilfe.html
*/kontakt/*	/de/kontakt/, /en/kontakt/form.html

📦 Veränderte Dateien
Datei	Änderung
checker.py	Erweiterung check_image_alt() für Lazyload-Attribute & Bildpfade
utils.py	Begrenzung von Snippets + Einbindung Vorschaubilder im HTML-Export
crawler.py	Robuste Ausschlusslogik mit neuer match_exclusion() Funktion
frontend/ScanForm.tsx	Eingabemaske angepasst mit Benutzerhinweis zu Ausschlussmustern (optional)