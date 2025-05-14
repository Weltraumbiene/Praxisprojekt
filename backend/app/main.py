from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import traceback
import requests
from bs4 import BeautifulSoup
import asyncio

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
from .logs import log_message, get_log_buffer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScanRequest(BaseModel):
    url: str
    exclude: Optional[List[str]] = []
    full: Optional[bool] = False
    max_depth: Optional[int] = 3

@app.post("/scan")
async def scan_website(scan_request: ScanRequest):
    log_message(f"\n[🚀 Scan gestartet] Ziel: {scan_request.url}")
    log_message(f"[⚙️  Crawltiefe eingestellt]: {scan_request.max_depth} Ebene(n)")

    if scan_request.exclude:
        log_message(f"[⚙️  Ausschlussregeln aktiv]: {', '.join(scan_request.exclude)}")
    if not scan_request.full:
        log_message("[⚙️  Modus: Nur eingegebene URL wird geprüft]")

    try:
        if not scan_request.full:
            result = {"pages": [{"url": scan_request.url, "soup": None}]}
        else:
            result = crawl_website(
                scan_request.url,
                exclude_patterns=scan_request.exclude,
                max_depth=scan_request.max_depth
            )

        issues = []
        log_message(f"[🔍 Crawler] {len(result['pages'])} Seiten gesammelt.")

        for page in result['pages']:
            url = page['url']
            soup = page['soup']

            if not soup:
                try:
                    response = requests.get(url, timeout=5)
                    soup = BeautifulSoup(response.text, 'html.parser')
                except Exception:
                    log_message(f"[❌ Fehler beim Laden der URL: {url}]")
                    traceback.print_exc()
                    continue

            log_message(f"\n[📝 Prüfe Seite] {url}")
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
                    log_message(f"  → {label}...")
                    await asyncio.sleep(0.1)
                    new_issues = check_func(url, soup)
                    log_message(f"     ↳ {len(new_issues)} Problem(e) erkannt.")
                    issues.extend(new_issues)

                log_message(f"[✅ Abgeschlossen] {url}")
            except Exception:
                log_message(f"[⚠️ Fehler bei Analyse] {url}")
                traceback.print_exc()

        seen = set()
        unique_issues = []
        for issue in issues:
            key = (issue.get("type"), issue.get("snippet"))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        log_message(f"\n[📊 Scan abgeschlossen] Insgesamt {len(unique_issues)} eindeutige Probleme gefunden.")
        save_latest_scan(unique_issues, scan_request.url)
        return {"issues": unique_issues}

    except Exception:
        log_message("\n[❌ Scan fehlgeschlagen]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Scan fehlgeschlagen.")

@app.get("/download-csv")
async def download_csv():
    try:
        log_message("[💾 CSV-Export] Generiere Datei...")
        return generate_csv()
    except Exception:
        log_message("[❌ CSV-Fehler]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="CSV-Export fehlgeschlagen.")

@app.get("/download-html")
async def download_html():
    try:
        log_message("[💾 HTML-Export] Generiere Datei...")
        return generate_html()
    except Exception:
        log_message("[❌ HTML-Fehler]")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="HTML-Export fehlgeschlagen.")

@app.get("/log-buffer")
async def get_logs():
    return JSONResponse(content={"logs": get_log_buffer()})
