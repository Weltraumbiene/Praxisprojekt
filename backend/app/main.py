# Anwendung\backend\app\main.py

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import traceback

from .crawler import crawl_website
from .checker import (
    check_contrast,
    check_image_alt,
    check_links,
    check_buttons,
    check_labels,
    check_headings,
    check_aria_roles,
)
from .utils import generate_csv, generate_html, save_latest_scan

app = FastAPI()

# CORS-Konfiguration für lokale Entwicklung
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datenmodell für Anfragen
class ScanRequest(BaseModel):
    url: str
    exclude: Optional[List[str]] = []

# POST /scan: Website-Prüfung mit Logging und Fehlerausgabe
@app.post("/scan")
async def scan_website(scan_request: ScanRequest):
    print(f"\n[🚀 Scan gestartet] Ziel: {scan_request.url}")
    if scan_request.exclude:
        print(f"[⚙️  Ausschlussregeln aktiv]: {', '.join(scan_request.exclude)}")

    try:
        result = crawl_website(scan_request.url, exclude_patterns=scan_request.exclude)
        issues = []
        print(f"[🔍 Crawler] {len(result['pages'])} Seiten gesammelt.")

        for page in result['pages']:
            url = page['url']
            soup = page['soup']
            print(f"\n[📝 Prüfe Seite] {url}")

            try:
                for check_func, label in [
                    (check_contrast, "Kontraste"),
                    (check_image_alt, "Bildbeschreibungen"),
                    (check_links, "Linkstruktur"),
                    (check_buttons, "Buttons"),
                    (check_labels, "Formulare"),
                    (check_headings, "Überschriften"),
                    (check_aria_roles, "ARIA")
                ]:
                    print(f"  → {label}...")
                    new_issues = check_func(url, soup)
                    print(f"     ↳ {len(new_issues)} Problem(e) erkannt.")
                    issues.extend(new_issues)

                print(f"[✅ Abgeschlossen] {url}")

            except Exception as step_err:
                print(f"[⚠️ Fehler bei Analyse] {url}")
                traceback.print_exc()

        # Duplikate entfernen
        seen = set()
        unique_issues = []
        for issue in issues:
            key = (issue.get("type"), issue.get("snippet"))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        print(f"\n[📊 Scan abgeschlossen] Insgesamt {len(unique_issues)} eindeutige Probleme gefunden.")
        save_latest_scan(unique_issues, scan_request.url)
        return {"issues": unique_issues}

    except Exception as e:
        print("\n[❌ Scan fehlgeschlagen]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# CSV-Export
@app.get("/download-csv")
async def download_csv():
    try:
        print("[💾 CSV-Export] Generiere Datei...")
        return generate_csv()
    except Exception as e:
        print("[❌ CSV-Fehler]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# HTML-Export
@app.get("/download-html")
async def download_html():
    try:
        print("[💾 HTML-Export] Generiere Datei...")
        return generate_html()
    except Exception as e:
        print("[❌ HTML-Fehler]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
