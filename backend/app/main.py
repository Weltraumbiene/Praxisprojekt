# Anwendung\backend\app\main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

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

# CORS für Frontend erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ggf. später anpassen
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datamodell für den Scan-Request
class ScanRequest(BaseModel):
    url: str

# POST /scan: Führt alle Prüfungen durch und speichert die Ergebnisse
@app.post("/scan")
async def scan_website(scan_request: ScanRequest):
    try:
        result = crawl_website(scan_request.url)
        issues = []

        for page in result['pages']:
            url = page['url']
            soup = page['soup']

            issues.extend(check_contrast(url, soup))
            issues.extend(check_image_alt(url, soup))
            issues.extend(check_links(url, soup))
            issues.extend(check_buttons(url, soup))
            issues.extend(check_labels(url, soup))
            issues.extend(check_headings(url, soup))
            issues.extend(check_aria_roles(url, soup))

        # Deduplizieren nach (type, snippet)
        seen = set()
        unique_issues = []
        for issue in issues:
            key = (issue.get("type"), issue.get("snippet"))
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)

        # Ergebnisse speichern
        save_latest_scan(unique_issues, scan_request.url)
        return {"issues": unique_issues}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /download-csv: Liefert den letzten Bericht als CSV
@app.get("/download-csv")
async def download_csv():
    try:
        return generate_csv()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /download-html: Liefert den letzten Bericht als HTML
@app.get("/download-html")
async def download_html():
    try:
        return generate_html()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
