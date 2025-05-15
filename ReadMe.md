Praxisprojekt: Barrierefreiheits-Scanner

Projektübersicht

Entwicklung einer Python-basierten Anwendung zur automatisierten Überprüfung von Webseiten im Hinblick auf digitale Barrierefreiheit nach WCAG 2.1-Standards.

Voraussetzungen & Setup

Python-Umgebung
Python 3.x installiert

Benötigte Bibliotheken:
pip install -r requirements.txt

Node.js
Node.js & npm installiert

Setze Execution Policy (PowerShell):
Set-ExecutionPolicy Unrestricted -Scope CurrentUser

Test:

node -v
npm -v

Pakete installieren:

npm install puppeteer axe-core

Projektstruktur & Start

\Anwendung\Frontend
\Anwendung\Backend

Serverstar: start.bat 


Projekt-Zeitleiste (Auszüge)

03.04.2025

08:00 - 09:00 Projektidee, erste Dokumentation

09:00 - 11:30 Arbeitsplan & Struktur

04.04.2025

08:30 - 10:30 To-Do-Liste & MVP erstellt

11:00 - 13:00 MVP entwickelt

07.04.2025

Git-Repo aufgesetzt, FastAPI-Basis und erste Tests

08.04.2025

Konsolentests lokal & per PowerShell

HTML-Fragmente verursachten Fehler (Workaround durch Dummy-HTML-Wrapper)

Erste Tests ganzer Projektordner

09.04.2025

Frontend-Start mit React (Vite, TypeScript)

Integration von AXE-Analyse, CSS-Scanner & Dokumentation

06.05.2025

Kompletter Refactor: Projektstart neu aufgrund technischer Schuld

Git-Commit: 10e4344

07.05.2025

Startseite UI optimiert, visuelles Lade-Feedback via JSON-Fake-Prozess

Berichte optimiert, Performanceprobleme bei großen Websites festgestellt

12.05.2025

Crawler-Optimierung: Keine doppelten HTTP-Requests, Weitergabe von soup

Prüffunktionen refactored: Direkte Analyse per soup

Frontend: Neues Ausschlussfeld für URL-Filter mit Tooltip-Hilfe

Backend: Einzel-/Vollscan via full: bool, Fehler-Logging verbessert

Berichtsfunktionen:

Lazy-Load-Bilder erkannt

Code-Snippets gekürzt (max. 250 Zeichen)

Bildvorschau im HTML-Bericht (max 80px)

Technische Details

Backend (FastAPI)

HTML-Analyse via Puppeteer + AXE-Core

CSS-Kontrastanalyse über TinyCSS2 & colormath

Analyse von:

Struktur (h1, alt, ARIA)

Kontrast (color vs. background)

Frontend (React)

Vite + TypeScript

Eingabemaske für URL & Ausschlussregeln

Visual Feedback während Scan (Fake-Progress)

Probleme & Lösungen

Problem

Lösung

HTML-Fragmente werfen Fehler

Dummy-HTML-Kopf eingefügt

WinError 206 (Windows)

subprocess-Aufrufe auf Dateien umgestellt

Zu lange Scans

Soup-Recycling + HTTP-Reduktion

Schlechte Wartbarkeit

Code-Refactor + Trennung von Crawler und Check-Logik

Ausblick

Parallele Analyse (Multithreading / async)

ARIA-Tests & Tab-Navigation verbessern

Frontend-Erweiterung: Sortier- und Filterfunktion für Fehlerberichte

Dieses Projekt wurde im Rahmen eines Praxisprojekts zur Webentwicklung und digitalen Barrierefreiheit entwickelt.