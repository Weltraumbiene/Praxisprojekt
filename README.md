# Praxisprojekt
Die Entwicklung einer Python basierten Anwendung zur 
automatisierten Überprüfung von Webseiten im Sinne der Barrierefreiheit.
---------------------------------------------------------------------------------------------------------------
Dev-Data:
Windows Shell/Terminal ---> pip install fastapi uvicorn

Link zum Projekt: cd C:\Users\b****eck\Desktop\Praxisprojekt\Anwendung
Link zum Python-Ordner: cd C:\Users\b****eck\Desktop\Praxisprojekt\Anwendung\python

Start des Python-Servers: python -m uvicorn main:app --reload
Stopp des Servers: strg+c
überprüfen, ob der Server aktiv ist: tasklist | findstr uvicorn



Server-Test: http://127.0.0.1:8000
API-Test: http://127.0.0.1:8000/docs
API-Test CURL (WICHTIG CMD!): curl -X 'POST' 'http://127.0.0.1:8000/check' -H 'Content-Type: application/json' -d '{ "url": "https://example.com" }'
API-Test CURL (Shell): Invoke-RestMethod -Uri "http://127.0.0.1:8000/check" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"url": "https://example.com"}'


install Node.JS (Nodejs.org) (wichtig: NPM muss auch installiert werden!)
win+x ausführen terminal als admin
führe aus: Set-ExecutionPolicy Unrestricted -Scope CurrentUser
teste im terminal: node -v und npm-v (es sollten Versionen angezeigt werden)


anschließend: npm install puppeteer axe-core
Hinweis: Eventuell sind Updates verfügbar:
npm notice To update run: npm install -g npm@11.2.0
npm notice
PS C:\Users\bfranneck> npm install -g npm@11.2.0



FastAPI läuft in Python daher: 
pip install playwright
playwright install


Testen der API:
Invoke-RestMethod -Uri "http://127.0.0.1:8000/check" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"url": "https://www.beispiel.de"}'
---------------------------------------------------------------------------------------------------------------
03.04.2025 - 8Uhr - 9 Uhr
Erste Zusammenfassung und Beschreibung des geplanten Projekts
Grundaufbau der Arbeitsschritte und Planung (Beschreibung.docx)


03.04.2025 - 9Uhr -11.30 Uhr
Detaillierter Aufbau der Arbeitsschritte (Arbeitsplan.docx)


04.04.2025 - 8.30 - 10.30
Erstellen einer To-Do-List und Aufbaustruktur zur Erstellung der Anwendung

04.04.2025 - 11.00 - 13.00
Erstellen eines MVP Minimum Viable Product

07.04.2025 - 7Uhr - 9.30Uhr 
Einrichten eines Repository auf Git