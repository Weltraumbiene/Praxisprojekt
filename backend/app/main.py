#Anwendung\backend\app\main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .crawler import crawl_website
from .checker import check_contrast, check_image_alt, check_links
from .utils import generate_csv, generate_html, save_latest_scan

app = FastAPI()

# CORS für Frontend erlauben
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Datamodell für den Scan-Request
class ScanRequest(BaseModel):
    url: str

# Webseite scannen
@app.post("/scan")
async def scan_website(scan_request: ScanRequest):
    try:
        # Crawl die Seite und sammle Unterseiten
        results = crawl_website(scan_request.url)
        issues = []

        # Für jede gefundene Seite Prüfungen durchführen
        for page_url in results['pages']:
            issues.extend(check_contrast(page_url))
            issues.extend(check_image_alt(page_url))
            issues.extend(check_links(page_url))

        # Ergebnisse für spätere Berichte speichern
        save_latest_scan(issues, scan_request.url)

        # Ergebnisse zurückgeben
        return {"issues": issues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# CSV-Report generieren
@app.get("/download-csv")
async def download_csv():
    try:
        return generate_csv()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# HTML-Report generieren
@app.get("/download-html")
async def download_html():
    try:
        return generate_html()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
